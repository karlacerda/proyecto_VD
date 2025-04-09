import base64
import os
import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px

# Imagen banner
image_path = os.path.expanduser(r"C:\Users\karla\OneDrive\Escritorio\hola\logo UFRO.png")

with open(image_path, "rb") as f:
    encoded_image = base64.b64encode(f.read()).decode()

# Leer Excel
df1 = pd.read_excel("BD WOS 2023.xlsx", sheet_name="Hoja1")
df2 = pd.read_excel("BD WOS 2023.xlsx", sheet_name="Hoja2")

# Gráfico de torta (cuartiles)
cuartil_counts = df1["Cuartil"].value_counts().reset_index()
cuartil_counts.columns = ["Cuartil", "Cantidad"]

# Normalizar columnas de Hoja2
df2.columns = df2.columns.str.strip().str.lower()

if "año" in df2.columns and "cantidad de articulos" in df2.columns:
    articulos_por_anio = df2[["año", "cantidad de articulos"]].dropna()
    articulos_por_anio = articulos_por_anio.sort_values("año")
else:
    articulos_por_anio = pd.DataFrame(columns=["año", "cantidad de articulos"])

# Gráfico de serie de tiempo (línea)
fig_serie_tiempo = px.line(
    articulos_por_anio,
    x='año',
    y='cantidad de articulos',
    markers=True,
    title='Cantidad de artículos por año',
    labels={'año': 'Año', 'cantidad de articulos': 'Cantidad'}
)

fig_serie_tiempo.update_traces(line=dict(width=3), marker=dict(size=8))
fig_serie_tiempo.update_layout(
    margin=dict(t=100),
    yaxis=dict(range=[0, articulos_por_anio["cantidad de articulos"].max() * 1.2])
)

# Gráfico de correlación: Cuartil vs. ES UFRO?
if "Cuartil" in df1.columns and "ES UFRO?" in df1.columns:
    correlacion_data = df1[["Cuartil", "ES UFRO?"]].dropna()

    correlacion_data["ES UFRO?"] = correlacion_data["ES UFRO?"].replace({1: "Sí", 0: "No"})
    correlacion_data["ES UFRO?"] = correlacion_data["ES UFRO?"].astype(str).str.capitalize()

    grouped_counts = correlacion_data.value_counts().reset_index()
    grouped_counts.columns = ["Cuartil", "ES UFRO?", "Cantidad"]

    cuartil_ordenado = ["Q1", "Q2", "Q3", "Q4", "S/Q"]

    fig_correlacion = px.bar(
        grouped_counts,
        x="Cuartil",
        y="Cantidad",
        color="ES UFRO?",
        barmode="group",
        title="Distribución de liderazgos UFRO por cuartil",
        labels={"Cantidad": "Número de artículos"},
        category_orders={"Cuartil": cuartil_ordenado}
    )
else:
    fig_correlacion = px.scatter(title="No hay datos válidos para el gráfico de correlación")

# Gráfico Tree Map por Cuartil y Revista
if "Cuartil" in df1.columns and "REVISTA" in df1.columns:
    treemap_data = df1[["Cuartil", "REVISTA"]].dropna()
    treemap_data = treemap_data.groupby(["Cuartil", "REVISTA"]).size().reset_index(name='Cantidad')

    fig_treemap = px.treemap(
        treemap_data,
        path=["Cuartil", "REVISTA"],
        values="Cantidad",
        title="Distribución de revistas por cuartil"
    )

    fig_treemap.update_traces(
        root_color="lightgrey",
        hovertemplate='<b>Cuartil:</b> %{parent}<br><b>Revista:</b> %{label}<br><b>Cantidad:</b> %{value}<extra></extra>'
    )
else:
    fig_treemap = px.scatter(title="No hay datos válidos para el gráfico Treemap")

# App Dash
app = Dash(__name__)
app.title = "Dashboard Publicaciones"

app.layout = html.Div([

    # Banner
    html.Div([
        html.Img(
            src='data:image/png;base64,{}'.format(encoded_image),
            style={'maxWidth': '300px', 'margin': 'auto'}
        )
    ], style={'textAlign': 'center', 'backgroundColor': '#f9f9f9', 'padding': '20px'}),

    html.H1("Análisis de Publicaciones WoS UFRO 2023", style={'textAlign': 'center'}),

    html.Div([
        html.P(
            "El presente dashboard viene a entregar información respecto a las publicaciones "
            "científicas de la Web of Science (WoS) de la Universidad de La Frontera (UFRO) registradas por la Agencia Nacional de Investigación y Desarrollo (ANID) durante el 2023. \n \n"
            "Con estos antecedentes, aspiramos a brindar una mirada general respecto de la productividad de la Institución en el periodo mencionado."
            "\n \n "
            "Para la elaboración de este dashboard se ha considerado que la fuente primaria de información la constituye el listado de publicaciones WoS con afiliación a la "
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

    # Gráfico de serie de tiempo
    dcc.Graph(
        id='grafico-serie-tiempo',
        figure=fig_serie_tiempo
    ),

    # Gráfico de cuartiles (torta)
    dcc.Graph(
        id='grafico-cuartiles',
        figure=px.pie(
            cuartil_counts,
            names='Cuartil',
            values='Cantidad',
            title='Cantidad de artículos por cuartil'
        )
    ),

    # Texto explicativo del cuartil
    html.Div([
        html.P(
            "*El cuartil es un indicador que sirve para evaluar la importancia relativa de una revista dentro del total de revistas de su área.",
            style={
                'fontStyle': 'italic',
                'textAlign': 'center',
                'fontSize': '14px',
                'color': '#333',
                'maxWidth': '800px',
                'margin': '10px auto'
            }
        )
    ]),

    # Gráfico de correlación
    dcc.Graph(
        id='grafico-correlacion',
        figure=fig_correlacion
    ),

    # Gráfico Tree Map
    dcc.Graph(
        id='grafico-treemap',
        figure=fig_treemap
    )
])

if __name__ == '__main__':
    app.run(debug=True)
