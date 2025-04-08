import base64
import os
import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px

#incorporar imagen para el banner de la pagina web
image_path = os.path.expanduser(r"C:\Users\karla\Downloads\logo UFRO.png")

with open(image_path, "rb") as f:
    encoded_image = base64.b64encode(f.read()).decode()


#leer archivo excel 
df = pd.read_excel("BD WOS 2023.xlsx", sheet_name="Hoja1")
cuartil_counts = df["Cuartil"].value_counts().reset_index()
cuartil_counts.columns = ["Cuartil", "Cantidad"]

#crear Dash
app = Dash(__name__)
app.title = "Dashboard Publicaciones"

app.layout = html.Div([
    # Banner con imagen
    html.Div([
        html.Img(
            src='data:image/png;base64,{}'.format(encoded_image),
            style={'maxWidth': '300px', 'margin': 'auto'}
        )
    ], style={'textAlign': 'center', 'backgroundColor': '#f9f9f9', 'padding': '20px'}),

    # Título
    html.H1("Análisis de Publicaciones WoS UFRO 2023", style={'textAlign': 'center'}),

    # Párrafo
    html.Div([
    html.P(
        "El presente dashboard viene a entregar información respecto a las publicaciones " \
        "científicas de la Web of Science (WoS) de la Universidad de La Frontera (UFRO) registradas por la Agencia Nacional de Investigación y Desarrollo (ANID) durante el 2023. \n \n" \
        "Con estos antecedentes, aspiramos a brindar una mirada general respecto de la productividad de la Institución en el periodo mencionado, " \
        "destacando el trabajo de cada Facultad, Departamento o Unidad. \n \n " \
        "Para la elaboración de este dashboard se ha considerado que la fuente primaria de información la constituye el listado de publicaciones WoS con afiliación a la" \
        "Universidad de La Frontera elaborado por ANID, con datos desde enero a diciembre del 2023.",
        style={
            'whiteSpace': 'pre-line',
            'textAlign': 'justify',
            'fontSize': '16px',
            'maxWidth': '1000px',
            'margin': '0 auto',
            'padding': '15px'
        }
    )
    ]),


    # Gráfico de torta
    dcc.Graph(
        id='grafico-cuartiles',
        figure=px.pie(cuartil_counts, names='Cuartil', values='Cantidad', title='Cantidad de artículos por cuartil')
    )
])



if __name__ == '__main__':
    app.run(debug=True)

    