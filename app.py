import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import numpy as np
import pyodbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY, 'https://use.fontawesome.com/releases/v5.9.0/css/all.css'])

sql_query = ('''
                        SELECT DISTINCT  
                T1.[TFTDoc] AS TIPO_ID,
                T1.[TFCedu] AS ID,
                T2.[MPNOMC] AS NOMBRE,
                T1.[TFFchI] AS FECHA_INGRESO,
                T1.[TFHorI] AS HORA_INGRESO,
                T1.[MPFEsH] AS FECHA_SALIDA,
                T3.[DMNomb] AS DESCRIPCION, 
                T1.[TFEstP] AS DX_INGRESO,
                DATEDIFF([mi], T1.[MPFEsH], getdate()) AS Op_Mins
            FROM       
                TMPFAC T1
            WITH 
                (NOLOCK)
            INNER JOIN 
                CAPBAS T2
            WITH
                (NOLOCK)
            ON
                T2.MPCedu = T1.TFCedu
            LEFT JOIN
                MAEDIA T3
            WITH
                (NOLOCK)
            ON
                T3.[DMCodi] = T1.[TFDi1I]
            WHERE      
                T1.ClaPro = '3'
            AND
                T1.TFViaI = 5
            AND 
                TFFchI >= CAST(GETDATE() as DATE)
            ORDER BY Op_Mins DESC
                '''
            )

server = '10.20.8.12' 
database = 'HOSVITAL' 
username = 'sa' 
password = 'HosvitIbg20' 
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

df = pd.read_sql(sql_query,conn)
     
df = df.apply(lambda x: x.str.strip() 
                if x.dtype == "object" else x)  # Trim whitespaces

def connectSQLServer(conn):
    connSQLServer = conn
    return connSQLServer

def getData():
    df2 = pd.DataFrame()
    for idx in range(10):
        data  = pd.read_sql(sql_query,conn)
        df2 = df2.append(data, ignore_index=True)
        df2 = df2.drop_duplicates().sort_index()
    return df2.to_dict('records')

tblcols=[{'name': 'TIPO_ID', 'id': 'TIPO_ID'},
         {'name': 'ID', 'id': 'ID'},
         {'name': 'NOMBRE', 'id': 'NOMBRE'}, 
         {'name': 'FECHA_INGRESO', 'id': 'FECHA_INGRESO'}, 
         {'name': 'HORA_INGRESO', 'id': 'HORA_INGRESO'}, 
         {'name': 'FECHA_SALIDA', 'id': 'FECHA_SALIDA'}, 
         {'name': 'DESCRIPCION', 'id': 'DESCRIPCION'}, 
         {'name': 'DX_INGRESO', 'id': 'DX_INGRESO'}, 
         {'name': 'Op_Mins', 'id': 'Op_Mins'}
         ]

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url('logo.png'), height="65px")),
                    dbc.Col(dbc.NavbarBrand("Oportunidad Triage", className="ml-4", style={
                            'position': 'relative',
                            'left': '50%',
                            'transform': 'translateX(-50%)',
                            }
                            )
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="#",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
    ],
    color="primary",
    dark=True,
)

count_row = df.shape[0]

badge = dbc.Button(
    ["Total:", dbc.Badge(count_row, color="secondary", className="ml-1")],
    color="primary",style={'position':'absolute'}
)

footer = dbc.Container(
    dbc.Row(
        dbc.Col(
            html.P(
                [
                    html.Span('Clínica Nuestra Ibagué', className='mr-2'), 
                    html.A(html.I(className='fas fa-envelope-square mr-1'), href='mailto:<ti.ibague>@<clinicanuestra>.com'),
                ], 
                className='lead'
            )
        )
    )
)


app.layout = html.Div([
      navbar,
      html.H4('Tablero CN'),
      dcc.Interval('graph-update', interval = 5000, n_intervals = 0),
      dash_table.DataTable(
          id = 'table',
          data = getData(),
          columns=tblcols,
        style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
         },
         style_cell={
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0,
        },
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['Date', 'Region']
        ],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'rgb(120, 194, 173)',
            'fontWeight': 'bold'
        },
          export_format='xlsx',
          export_headers='display',),
        badge,
        footer,],
)

@app.callback(
        dash.dependencies.Output('table','data'),
        [dash.dependencies.Input('graph-update', 'n_intervals')])
def updateTable(n):
     return getData()

if __name__ == '__main__':
     app.run_server(debug=False)



