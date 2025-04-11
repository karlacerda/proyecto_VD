import base64
import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from wordcloud import WordCloud
import io
import numpy as np
from PIL import Image
import matplotlib
from plotly.io import read_json
matplotlib.use('Agg')

# Imagen
image_path = os.path.expanduser(r"C:\Users\karla\OneDrive\Escritorio\hola\logo UFRO.png")
with open(image_path, "rb") as f:
    encoded_image = base64.b64encode(f.read()).decode()

# Cargar datos
df1 = pd.read_excel("BD WOS 2023.xlsx", sheet_name="Hoja1")
df2 = pd.read_excel("BD WOS 2023.xlsx", sheet_name="Hoja2")
df3 = pd.read_excel("BD WOS 2023.xlsx", sheet_name="Hoja3")
df2.columns = df2.columns.str.strip().str.lower()

# Serie de tiempo
articulos_por_anio = df2[["año", "cantidad de articulos"]].dropna().sort_values("año")
fig_serie_tiempo = px.line(articulos_por_anio, x='año', y='cantidad de articulos', markers=True,
    labels={'año': 'Año', 'cantidad de articulos': 'Cantidad'}
)
fig_serie_tiempo.update_traces(line=dict(width=3), marker=dict(size=8))
fig_serie_tiempo.update_layout(margin=dict(t=100))

# Torta cuartiles
cuartil_counts = df1["Cuartil"].value_counts().reset_index()
cuartil_counts.columns = ["Cuartil", "Cantidad"]

# Correlación
correlacion_data = df1[["Cuartil", "ES UFRO?"]].dropna()
correlacion_data["ES UFRO?"] = correlacion_data["ES UFRO?"].replace({1: "Sí", 0: "No"}).astype(str).str.capitalize()
grouped_counts = correlacion_data.value_counts().reset_index()
grouped_counts.columns = ["Cuartil", "ES UFRO?", "Cantidad"]
fig_correlacion = px.bar(grouped_counts, x="Cuartil", y="Cantidad", color="ES UFRO?", barmode="group",
    labels={"Cantidad": "Número de artículos"},
    category_orders={"Cuartil": ["Q1", "Q2", "Q3", "Q4", "S/Q"]}
)

# Treemap
treemap_data = df1[["Cuartil", "REVISTA"]].dropna()
treemap_data = treemap_data.groupby(["Cuartil", "REVISTA"]).size().reset_index(name='Cantidad')
fig_treemap = px.treemap(treemap_data, path=["Cuartil", "REVISTA"], values="Cantidad")
fig_treemap.update_traces(
    root_color="lightgrey",
    hovertemplate='<b>Cuartil:</b> %{parent}<br><b>Revista:</b> %{label}<br><b>Cantidad:</b> %{value}<extra></extra>'
)

# Top 5 editoriales 
df_editoriales = df1[["EDITORIAL"]].dropna()
df_editoriales = df_editoriales[df_editoriales["EDITORIAL"] != ""]
top_editoriales = df_editoriales["EDITORIAL"].value_counts().nlargest(5).reset_index()
top_editoriales.columns = ["Editorial", "Cantidad"]

fig_editoriales = px.bar(
    top_editoriales,
    x="Editorial",
    y="Cantidad",
    labels={"Editorial": "Editorial", "Cantidad": "Número de publicaciones"}
)
fig_editoriales.update_layout(margin=dict(t=80, l=40, r=40, b=40))
fig_editoriales.update_xaxes(categoryorder="total descending")

# App
app = Dash(__name__)
app.title = "Dashboard Publicaciones"

app.layout = html.Div([
    html.Div([
        html.Img(
            src='data:image/png;base64,{}'.format(encoded_image),
            style={'maxWidth': '300px', 'margin': 'auto'}
        )
    ], style={'textAlign': 'center', 'backgroundColor': '#f9f9f9', 'padding': '20px'}),

    html.H1("Análisis de Publicaciones WoS UFRO 2023", style={'textAlign': 'center'}),

    html.Div([
        html.P(
            "El presente dashboard viene a entregar información respecto a las publicaciones científicas de la Web of Science (WoS) de la Universidad de La Frontera (UFRO) registradas por ANID durante el 2023. \n \n"
            "Con estos antecedentes, se brinda una mirada general respecto a la productividad de la Institución para que autoridades, académicos y profesionales puedan contar con información clara respecto al listado y clasificación de publicaciones WoS con afiliación UFRO.\n \n",
                 
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

    html.H3("Cantidad de artículos por año", style={'marginLeft': '60px'}),
    html.P("La gráfica muestra la evolución anual del número de publicaciones científicas indexadas en la Web of Science (WoS) con afiliación a la Universidad de La Frontera (UFRO), registradas por ANID.", 
           style={
                'whiteSpace': 'pre-line',
                'textAlign': 'justify',
                'fontSize': '16px',
                'maxWidth': '1000px',
                'margin': '0 auto',
                'padding': '15px'
                  
                  
                  }),
    dcc.Graph(id='grafico-serie-tiempo', figure=fig_serie_tiempo),

    html.H3("Cantidad de artículos por cuartil", style={'marginLeft': '60px'}),
    html.P("La gráfica muestra la distribución de las publicaciones científicas de la UFRO durante 2023 según el cuartil de la revista, conforme al Journal Citation Reports (JCR). Los cuartiles dividen a las revistas en cuatro grupos según su factor de impacto, siendo Q1 el de mayor prestigio. También se incluye una categoría S/Q para revistas sin cuartil asignado. \n \n", 
           style={
                'whiteSpace': 'pre-line',
                'textAlign': 'justify',
                'fontSize': '16px',
                'maxWidth': '1000px',
                'margin': '0 auto',
                'padding': '15px'               
                  
                  }),
    dcc.Graph(id='grafico-cuartiles',
              figure=px.pie(cuartil_counts, names='Cuartil', values='Cantidad')),

    html.H3("Distribución geográfica de artículos por país", style={'marginLeft': '60px'}),
    html.P("La visualización presenta la distribución geográfica de las publicaciones científicas de la UFRO durante el año 2023, identificando los países de afiliación de los coautores registrados en la Web of Science. Este mapa permite observar el alcance internacional de las colaboraciones científicas desarrolladas por investigadores de la universidad. \n \n", 
           style={
                'whiteSpace': 'pre-line',
                'textAlign': 'justify',
                'fontSize': '16px',
                'maxWidth': '1000px',
                'margin': '0 auto',
                'padding': '15px'
                  
                  
                  }),
    html.Div([
        html.Label("Filtrar por país:", style={
            'fontWeight': 'bold', 'fontSize': '16px', 'color': '#003865', 'marginRight': '10px'
        }),
        dcc.Dropdown(
            id='filtro-pais',
            options=[{"label": pais, "value": pais} for pais in sorted(df3["Pais_Edit"].dropna().unique())],
            placeholder="Selecciona un país",
            clearable=True,
            style={
                'width': '300px', 'borderRadius': '8px', 'padding': '6px',
                'border': '1px solid #ccc', 'boxShadow': '1px 1px 6px rgba(0,0,0,0.1)',
                'backgroundColor': '#f5f5f5', 'color': '#003865', 'fontWeight': 'bold'
            }
        )
    ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px',
              'marginLeft': '60px', 'marginBottom': '20px'}),
    dcc.Graph(id='grafico-mapa'),

    html.H3("Distribución de liderazgos UFRO por cuartil", style={'marginLeft': '60px'}),
    html.P("Esta gráfica muestra la cantidad de publicaciones lideradas por investigadores de la UFRO en 2023, segmentadas según el cuartil de la revista. Se considera liderazgo cuando el autor principal o de correspondencia pertenece a la institución, implicando un rol activo en la conducción del estudio. \n \n", 
           style={
                'whiteSpace': 'pre-line',
                'textAlign': 'justify',
                'fontSize': '16px',
                'maxWidth': '1000px',
                'margin': '0 auto',
                'padding': '15px'
                  
                  
                  }),
    dcc.Graph(id='grafico-correlacion', figure=fig_correlacion),

    html.H3("Distribución de revistas por cuartil", style={'marginLeft': '60px'}),
    html.P("La gráfica permite visualizar la variedad de revistas científicas en las que publicó la UFRO durante 2023, lo que entrega una perspectiva sobre la amplitud de los espacios editoriales utilizados por la institución. La presencia de una gran cantidad de revistas distintas indica una estrategia de difusión diversa, que abarca múltiples áreas del conocimiento. \n \n ", 
           style={
                'whiteSpace': 'pre-line',
                'textAlign': 'justify',
                'fontSize': '16px',
                'maxWidth': '1000px',
                'margin': '0 auto',
                'padding': '15px'
                  
                  
                  }),
    dcc.Graph(id='grafico-treemap', figure=fig_treemap),

    html.H3("Top 5 editoriales por número de publicaciones", style={'marginLeft': '60px'}),
    html.P("La gráfica muestra las cinco editoriales científicas con mayor número de publicaciones afiliadas a la UFRO durante 2023. Destaca ampliamente MDPI, con una diferencia considerable respecto del resto, lo que refleja una fuerte presencia institucional en esta plataforma. Le siguen Elsevier, la Sociedad Chilena de Anatomía, Frontiers Media SA y Wiley, todas editoriales de reconocida trayectoria. \n \n ", 
           style={
                'whiteSpace': 'pre-line',
                'textAlign': 'justify',
                'fontSize': '16px',
                'maxWidth': '1000px',
                'margin': '0 auto',
                'padding': '15px'
               
               }),
    dcc.Graph(id='grafico-editoriales', figure=fig_editoriales),

    html.H3("Nube de palabras clave", style={'marginLeft': '60px'}),
    html.P("La nube recoge los principales conceptos asociados a las publicaciones científicas de la UFRO durante 2023, permitiendo identificar las temáticas más recurrentes en la actividad investigativa. Entre las palabras más destacadas se encuentran salud, microbiología, nutrición, medioambiente, biotecnología, plantas y cáncer, lo que da cuenta de una fuerte orientación hacia problemáticas de impacto biomédico, ambiental y social. \n \n", 
           style={
                'whiteSpace': 'pre-line',
                'textAlign': 'justify',
                'fontSize': '16px',
                'maxWidth': '1000px',
                'margin': '0 auto',
                'padding': '15px'
               
                  
                  
                  }),
    html.Div([
        html.Label("Filtrar por cuartil:", style={
            'fontWeight': 'bold', 'fontSize': '16px', 'color': '#003865', 'marginRight': '10px'
        }),
        dcc.Dropdown(
            id='filtro-cuartil-nube',
            options=[{"label": c, "value": c} for c in sorted(df1["Cuartil"].dropna().unique())],
            placeholder="Selecciona un cuartil",
            clearable=True,
            style={
                'width': '300px', 'borderRadius': '8px', 'padding': '6px',
                'border': '1px solid #ccc', 'boxShadow': '1px 1px 6px rgba(0,0,0,0.1)',
                'backgroundColor': '#f5f5f5', 'color': '#003865', 'fontWeight': 'bold'
            }
        )
    ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px',
              'marginLeft': '60px', 'marginBottom': '20px'}),
    dcc.Graph(id='grafico-nube-palabras')
])

@app.callback(
    Output('grafico-mapa', 'figure'),
    Input('filtro-pais', 'value')
)
def actualizar_mapa(pais_seleccionado):
    conteo = df3['Pais_Edit'].value_counts().reset_index()
    conteo.columns = ['Pais', 'Articulos']
    if pais_seleccionado:
        conteo = conteo[conteo['Pais'] == pais_seleccionado]
    fig = px.choropleth(
        conteo,
        locations='Pais',
        locationmode='country names',
        color='Articulos',
        color_continuous_scale='YlOrRd',
        projection='natural earth'
    )
    fig.update_layout(geo=dict(showframe=False, showcoastlines=True),
                      margin=dict(t=20, l=20, r=20, b=20))
    return fig

@app.callback(
    Output('grafico-nube-palabras', 'figure'),
    Input('filtro-cuartil-nube', 'value')
)
def actualizar_nube(cuartil):
    if "PALABRAS CLAVE" not in df1.columns:
        return px.scatter(title="No hay datos de palabras clave disponibles.")
    df_filtrado = df1[df1["Cuartil"] == cuartil] if cuartil else df1.copy()
    palabras = df_filtrado["PALABRAS CLAVE"].dropna().astype(str).str.cat(sep='; ').replace(';', ' ')
    wordcloud = WordCloud(width=1000, height=400,
                          background_color='white', colormap='viridis').generate(palabras)
    image = wordcloud.to_image()
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    image_array = np.array(Image.open(buffer))
    buffer.close()
    fig = px.imshow(image_array)
    fig.update_layout(xaxis=dict(showticklabels=False),
                      yaxis=dict(showticklabels=False),
                      margin=dict(t=20, l=40, r=40, b=40))
    return fig

if __name__ == '__main__':
    app.run(debug=True)
