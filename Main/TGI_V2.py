import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import webbrowser
from tkinter import filedialog
import os

# Créer une application web Dash
app = dash.Dash(__name__)

# Charger le fichier CSV directement sans demander à l'utilisateur
csv_file_path = filedialog.askopenfilename(title="Sélectionner le fichier CSV", filetypes=[("Fichiers CSV", "*.csv")])

# Si aucun fichier sélectionné, arrêter le code
if not csv_file_path or not os.path.isfile(csv_file_path):
    print("Aucun fichier CSV valide sélectionné. Action terminée.")
    exit()

# Charger le CSV dans le DataFrame
df = pd.read_csv(csv_file_path)

# Définir la mise en page
app.layout = html.Div([
    dcc.Dropdown(
        id='graph-type-dropdown',
        options=[
            {'label': 'Nuage de points', 'value': 'scatter'},
            {'label': 'Histogramme', 'value': 'histogram'},
            {'label': 'Histogramme Empilé', 'value': 'stacked_histogram'},
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Box Plot', 'value': 'box'},
            {'label': 'Violin Plot', 'value': 'violin'},
            {'label': '3D Scatter Plot', 'value': 'scatter_3d'},
            {'label': 'Graphique Circulaire', 'value': 'pie'},
            {'label': 'Graphique Donut', 'value': 'donut'}
        ],
        value='scatter',
        style={'width': '50%'}
    ),
    
    dcc.Dropdown(
        id='x-axis-dropdown',
        options=[{'label': col, 'value': col} for col in df.columns],
        value=df.columns[0] if not df.empty and len(df.columns) > 0 else None,
        style={'width': '50%'}
    ),

    dcc.Dropdown(
        id='secondary-x-axis-dropdown',
        options=[{'label': col, 'value': col} for col in df.columns],
        value=None,
        style={'width': '50%'}
    ),

    dcc.Dropdown(
        id='third-x-axis-dropdown',
        options=[{'label': col, 'value': col} for col in df.columns],
        value=None,
        style={'width': '50%'}
    ),

    dcc.Dropdown(
        id='filter-column-dropdown',
        options=[{'label': col, 'value': col} for col in df.columns],
        multi=True,
        placeholder="Sélectionner les colonnes de filtre",
        style={'width': '50%'}
    ),

    dcc.Dropdown(
        id='filter-data-dropdown',
        multi=True,
        placeholder="Sélectionner les données de filtre",
        style={'width': '50%'}
    ),

    dcc.Graph(id='graph-output')
])

# Callback pour mettre à jour les options de données de filtre en fonction des colonnes de filtre sélectionnées
@app.callback(
    Output('filter-data-dropdown', 'options'),
    [Input('filter-column-dropdown', 'value')]
)
def update_filter_data_dropdown(selected_columns):
    if not selected_columns:
        return []

    options = [{'label': str(val), 'value': val} for col in selected_columns for val in df[col].dropna().unique()]
    return options

# Callback pour réinitialiser les données de filtre sélectionnées lorsque les colonnes de filtre sont modifiées
@app.callback(
    Output('filter-data-dropdown', 'value'),
    [Input('filter-column-dropdown', 'options')]
)
def reset_filter_data_dropdown(_):
    return []

# Callback pour mettre à jour le graphique en fonction des sélections de l'utilisateur et des filtres
@app.callback(
    Output('graph-output', 'figure'),
    [Input('graph-type-dropdown', 'value'),
     Input('x-axis-dropdown', 'value'),
     Input('secondary-x-axis-dropdown', 'value'),
     Input('third-x-axis-dropdown', 'value'),
     Input('filter-column-dropdown', 'value'),
     Input('filter-data-dropdown', 'value')]
)
def update_graph(graph_type, selected_variable_x, selected_variable_secondary_x, selected_variable_third_x, filter_columns, filter_data):
    filtered_df = df.copy()

    # Appliquer des filtres en fonction des colonnes sélectionnées
    if filter_columns and filter_data:
        for col, values in zip(filter_columns, [filter_data] if isinstance(filter_data, str) else [filter_data]):
            if col in filtered_df.columns:
                # Utiliser .isin() pour filtrer le DataFrame en fonction de plusieurs valeurs pour la même colonne
                filtered_df = filtered_df[filtered_df[col].isin(values)]

    if graph_type == 'scatter' and selected_variable_x and selected_variable_secondary_x:
        fig = px.scatter(filtered_df, x=selected_variable_x, y=selected_variable_secondary_x, title=f"{selected_variable_x} vs {selected_variable_secondary_x}")
        return fig
    elif graph_type == 'histogram' and selected_variable_x:
        selected_variables = [v for v in [selected_variable_x, selected_variable_secondary_x, selected_variable_third_x] if v is not None]

        # Générer dynamiquement la séquence de couleurs pour chaque variable sélectionnée
        color_sequence = px.colors.qualitative.Set1[:len(selected_variables)-1]

        # Créer un dictionnaire spécifiant la couleur pour chaque variable
        color_mapping = {var: color for var, color in zip(selected_variables[1:], color_sequence)}

        # Créer des sous-graphiques le long de l'axe des x pour les variables supplémentaires
        fig = px.histogram(filtered_df, x=selected_variable_x, color=selected_variable_secondary_x, facet_col=selected_variable_third_x,
                        title=f"Histogramme avec {', '.join(selected_variables[1:])} subdivisions",
                        color_discrete_map=color_mapping)
        return fig
    elif graph_type == 'stacked_histogram' and selected_variable_x and selected_variable_secondary_x:

        # Filtrer les données pour la troisième variable x si elle est présente
        if selected_variable_third_x:
            grouped_df = filtered_df.groupby([selected_variable_x, selected_variable_third_x, selected_variable_secondary_x]).size().reset_index(name='Count')

            # Calculer la somme pour chaque valeur de la variable x
            grouped_df['Total'] = grouped_df.groupby([selected_variable_x, selected_variable_third_x])['Count'].transform('sum')

            # Calculer le pourcentage
            grouped_df['Percentage'] = grouped_df['Count'] / grouped_df['Total'] * 100

            fig = px.bar(grouped_df, x=selected_variable_x, y='Percentage', color=selected_variable_secondary_x, facet_col=selected_variable_third_x,
                        labels={selected_variable_x: selected_variable_x, 'Percentage': 'Pourcentage (%)'},
                        title=f"{selected_variable_x} avec {selected_variable_secondary_x} subdivisions (Colonnes empilées à 100%)")

            return fig
        else:
            # Si aucune troisième variable x n'est sélectionnée
            if selected_variable_secondary_x:
                grouped_df = filtered_df.groupby([selected_variable_x, selected_variable_secondary_x]).size().reset_index(name='Count')
            else:
                # Si seulement une variable x est sélectionnée, calculer le nombre d'occurrences
                grouped_df = filtered_df.groupby(selected_variable_x).size().reset_index(name='Count')

            # Calculer la somme pour chaque valeur de la variable x
            grouped_df['Total'] = grouped_df.groupby(selected_variable_x)['Count'].transform('sum')

            # Calculer le pourcentage
            grouped_df['Percentage'] = grouped_df['Count'] / grouped_df['Total'] * 100

            # Si deux variables sont sélectionnées, utiliser un graphique empilé à 100%
            fig = px.bar(grouped_df, x=selected_variable_x, y='Percentage', color=selected_variable_secondary_x,
                        labels={selected_variable_x: selected_variable_x, 'Percentage': 'Pourcentage (%)'},
                        title=f"{selected_variable_x} avec {selected_variable_secondary_x} subdivisions (Colonnes empilées à 100%)")

            return fig
    elif graph_type == 'pie' and selected_variable_x:
        fig = px.pie(filtered_df, names=selected_variable_x, title=f"Graphique Circulaire de {selected_variable_x}")
        return fig
    elif graph_type == 'donut' and selected_variable_x:
        fig = px.pie(filtered_df, names=selected_variable_x, title=f"Graphique Donut de {selected_variable_x}", hole=0.3)
        return fig
    elif graph_type == 'line' and selected_variable_x and selected_variable_secondary_x:
        fig = px.line(filtered_df, x=selected_variable_x, y=selected_variable_secondary_x, title=f"{selected_variable_x} vs {selected_variable_secondary_x}")
        return fig
    elif graph_type == 'box' and selected_variable_x and selected_variable_secondary_x:
        fig = px.box(filtered_df, x=selected_variable_x, y=selected_variable_secondary_x, title=f"{selected_variable_x} vs {selected_variable_secondary_x}")
        return fig
    elif graph_type == 'violin' and selected_variable_x and selected_variable_secondary_x:
        fig = px.violin(filtered_df, x=selected_variable_x, y=selected_variable_secondary_x, title=f"{selected_variable_x} vs {selected_variable_secondary_x}")
        return fig
    elif graph_type == 'scatter_3d' and selected_variable_x and selected_variable_secondary_x and selected_variable_third_x:
        fig = px.scatter_3d(filtered_df, x=selected_variable_x, y=selected_variable_secondary_x, z=selected_variable_third_x, title=f"3D Scatter Plot of {selected_variable_x}, {selected_variable_secondary_x}, {selected_variable_third_x}")
        return fig
    else:
        return px.scatter()

# Exécuter l'application Dash
webbrowser.open('http://127.0.0.1:8050/')
app.run_server(debug=True)