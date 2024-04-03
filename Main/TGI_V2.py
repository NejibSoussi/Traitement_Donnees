import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import webbrowser
from tkinter import filedialog
import os

# Create a Dash web application
app = dash.Dash(__name__)

# Load the CSV file directly without prompting the user
csv_file_path = filedialog.askopenfilename(title="Select the CSV file", filetypes=[("CSV Files", "*.csv")])

# If no file selected, stop the code
if not csv_file_path or not os.path.isfile(csv_file_path):
    print("No valid CSV file selected. Action terminated.")
    exit()

# Load the CSV into the DataFrame
df = pd.read_csv(csv_file_path)

# Define the layout
app.layout = html.Div([
    dcc.Dropdown(
        id='graph-type-dropdown',
        options=[
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Histogram', 'value': 'histogram'},
            {'label': 'Stacked Histogram', 'value': 'stacked_histogram'},
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Box Plot', 'value': 'box'},
            {'label': 'Violin Plot', 'value': 'violin'},
            {'label': '3D Scatter Plot', 'value': 'scatter_3d'},
            {'label': 'Pie Chart', 'value': 'pie'},
            {'label': 'Donut Chart', 'value': 'donut'}
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
        placeholder="Select filter columns",
        style={'width': '50%'}
    ),

    dcc.Dropdown(
        id='filter-data-dropdown',
        multi=True,
        placeholder="Select filter data",
        style={'width': '50%'}
    ),

    dcc.Graph(id='graph-output')
])

# Callback to update filter data options based on selected filter columns
@app.callback(
    Output('filter-data-dropdown', 'options'),
    [Input('filter-column-dropdown', 'value')]
)
def update_filter_data_dropdown(selected_columns):
    if not selected_columns:
        return []

    options = [{'label': str(val), 'value': val} for col in selected_columns for val in df[col].dropna().unique()]
    return options

# Callback to reset selected filter data when filter columns are changed
@app.callback(
    Output('filter-data-dropdown', 'value'),
    [Input('filter-column-dropdown', 'options')]
)
def reset_filter_data_dropdown(_):
    return []

# Callback to update the graph based on user selections and filters
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

    # Apply filters based on selected columns
    if filter_columns and filter_data:
        for col, values in zip(filter_columns, [filter_data] if isinstance(filter_data, str) else [filter_data]):
            if col in filtered_df.columns:
                # Use .isin() to filter the DataFrame based on multiple values for the same column
                filtered_df = filtered_df[filtered_df[col].isin(values)]

    if graph_type == 'scatter' and selected_variable_x and selected_variable_secondary_x:
        fig = px.scatter(filtered_df, x=selected_variable_x, y=selected_variable_secondary_x, title=f"{selected_variable_x} vs {selected_variable_secondary_x}")
        return fig
    elif graph_type == 'histogram' and selected_variable_x:
        selected_variables = [v for v in [selected_variable_x, selected_variable_secondary_x, selected_variable_third_x] if v is not None]

        # Dynamically generate color sequence for each selected variable
        color_sequence = px.colors.qualitative.Set1[:len(selected_variables)-1]

        # Create a dictionary specifying color for each variable
        color_mapping = {var: color for var, color in zip(selected_variables[1:], color_sequence)}

        # Create subplots along the x-axis for additional variables
        fig = px.histogram(filtered_df, x=selected_variable_x, color=selected_variable_secondary_x, facet_col=selected_variable_third_x,
                        title=f"Histogram with {', '.join(selected_variables[1:])} subdivisions",
                        color_discrete_map=color_mapping)
        return fig
    elif graph_type == 'stacked_histogram' and selected_variable_x and selected_variable_secondary_x:

        # Filter data for third x-variable if present
        if selected_variable_third_x:
            grouped_df = filtered_df.groupby([selected_variable_x, selected_variable_third_x, selected_variable_secondary_x]).size().reset_index(name='Count')

            # Calculate sum for each x-value
            grouped_df['Total'] = grouped_df.groupby([selected_variable_x, selected_variable_third_x])['Count'].transform('sum')

            # Calculate percentage
            grouped_df['Percentage'] = grouped_df['Count'] / grouped_df['Total'] * 100

            fig = px.bar(grouped_df, x=selected_variable_x, y='Percentage', color=selected_variable_secondary_x, facet_col=selected_variable_third_x,
                        labels={selected_variable_x: selected_variable_x, 'Percentage': 'Percentage (%)'},
                        title=f"{selected_variable_x} with {selected_variable_secondary_x} subdivisions (Stacked Columns at 100%)")

            return fig
        else:
            # If no third x-variable selected
            if selected_variable_secondary_x:
                grouped_df = filtered_df.groupby([selected_variable_x, selected_variable_secondary_x]).size().reset_index(name='Count')
            else:
                # If only one x-variable selected, calculate occurrences
                grouped_df = filtered_df.groupby(selected_variable_x).size().reset_index(name='Count')

            # Calculate sum for each x-value
            grouped_df['Total'] = grouped_df.groupby(selected_variable_x)['Count'].transform('sum')

            # Calculate percentage
            grouped_df['Percentage'] = grouped_df['Count'] / grouped_df['Total'] * 100

            # If two variables selected, use stacked bar chart at 100%
            fig = px.bar(grouped_df, x=selected_variable_x, y='Percentage', color=selected_variable_secondary_x,
                        labels={selected_variable_x: selected_variable_x, 'Percentage': 'Percentage (%)'},
                        title=f"{selected_variable_x} with {selected_variable_secondary_x} subdivisions (Stacked Columns at 100%)")

            return fig
    elif graph_type == 'pie' and selected_variable_x:
        fig = px.pie(filtered_df, names=selected_variable_x, title=f"Pie Chart of {selected_variable_x}")
        return fig
    elif graph_type == 'donut' and selected_variable_x:
        fig = px.pie(filtered_df, names=selected_variable_x, title=f"Donut Chart of {selected_variable_x}", hole=0.3)
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

# Run the Dash application
webbrowser.open('http://127.0.0.1:8050/')
app.run_server(debug=True)
