import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

# Criar a instância do aplicativo Dash
app = dash.Dash(__name__)

# Carregar o DataFrame e renomear colunas para compatibilidade
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df.rename(columns={'Payload Mass (kg)': 'PayloadMass'}, inplace=True)

# Definir opções para o dropdown de sites de lançamento
launch_sites = [
    {'label': 'All Sites',     'value': 'ALL'},
    {'label': 'CCAFS LC-40',   'value': 'CCAFS LC-40'},
    {'label': 'VAFB SLC-4E',   'value': 'VAFB SLC-4E'},
    {'label': 'KSC LC-39A',    'value': 'KSC LC-39A'},
    {'label': 'CCAFS SLC-40',  'value': 'CCAFS SLC-40'}
]

# Layout do aplicativo
app.layout = html.Div([
    html.H1("SpaceX Launch Data Analysis", style={'text-align': 'center'}),

    dcc.Dropdown(
        id='site-dropdown',
        options=launch_sites,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True,
        style={'width': '50%', 'padding': '3px',
               'font-size': '18px', 'margin': '10px auto'}
    ),

    dcc.Graph(id='success-pie-chart', style={'height': '400px'}),

    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[0, 4000],
    ),

    dcc.Graph(id='success-payload-scatter-chart', style={'height': '400px'})
])

# Callback para o gráfico de pizza
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        df_filtered = spacex_df
        title = 'Total Success vs Failure for All Sites'
    else:
        df_filtered = spacex_df[spacex_df['Launch Site'] == entered_site]
        title = f'Success vs Failure for {entered_site}'

    # Se não houver dados, aborta a atualização
    if df_filtered.empty:
        raise PreventUpdate()

    fig = px.pie(df_filtered, names='class', title=title)
    return fig

# Callback para o gráfico de dispersão
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter_chart(entered_site, payload_range):
    # Filtrar por site
    if entered_site == 'ALL':
        df_filtered = spacex_df
    else:
        df_filtered = spacex_df[spacex_df['Launch Site'] == entered_site]

    # Filtrar pela faixa de payload
    min_p, max_p = payload_range
    df_filtered = df_filtered[
        (df_filtered['PayloadMass'] >= min_p) &
        (df_filtered['PayloadMass'] <= max_p)
    ]

    # Se não houver dados, aborta a atualização
    if df_filtered.empty:
        raise PreventUpdate()

    # Criar gráfico de dispersão
    fig = px.scatter(
        df_filtered,
        x='PayloadMass',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs Success for {entered_site}'
    )
    return fig

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True)
