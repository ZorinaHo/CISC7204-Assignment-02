#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CISC7204 Assignment 02, Module 05 Final Project, Part 2.

XYZAutomotives: Interactive dashboard with Plotly and Dash.
Complete implementation of TASK 2.1–TASK 2.6 in the provided skeleton.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

BASE_DIR = Path(__file__).resolve().parent
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def load_data(csv_path=None):
    """Load the bundled dataset; replace this CSV with the teacher's file if available."""
    path = Path(csv_path) if csv_path is not None else BASE_DIR / 'automobile-sales.csv'
    if not path.is_file():
        raise FileNotFoundError(f'Missing data: {path}. Keep automobile-sales.csv beside this script.')
    df = pd.read_csv(path)
    # Original course material uses lower-case unemployment_rate.
    if 'Unemployment_Rate' in df.columns and 'unemployment_rate' not in df.columns:
        df = df.rename(columns={'Unemployment_Rate': 'unemployment_rate'})
    required = [
        'Year', 'Month', 'Recession', 'Automobile_Sales', 'Vehicle_Type',
        'Advertising_Expenditure', 'unemployment_rate'
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f'The CSV is missing required columns: {missing}')
    for col in ['Year', 'Recession', 'Automobile_Sales', 'Advertising_Expenditure', 'unemployment_rate']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=required).copy()
    df['Year'] = df['Year'].astype(int)
    df['Recession'] = df['Recession'].astype(int)
    # Respect the chronological order of months in the report.
    m = df['Month'].astype(str).str.strip().str[:3].str.title()
    df['Month'] = pd.Categorical(m, categories=MONTHS, ordered=True)
    return df


def style_figure(fig, x_title=None, y_title=None):
    """Keep both sets of dashboard plots consistent and readable."""
    fig.update_layout(
        template='plotly_white',
        title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 17}},
        margin=dict(l=55, r=28, t=68, b=55),
        font=dict(family='Arial, sans-serif', size=12, color='#334155'),
        paper_bgcolor='white', plot_bgcolor='white',
        legend=dict(orientation='h', y=-0.25),
    )
    if x_title is not None:
        fig.update_xaxes(title_text=x_title)
    if y_title is not None:
        fig.update_yaxes(title_text=y_title)
    return fig


def make_recession_figures(df):
    """TASK 2.5: the four plots in the Recession Period Statistics report."""
    recession_data = df.loc[df['Recession'] == 1].copy()

    # Plot 1: year-wise average automobile sales during recessions (line).
    yearly_rec = recession_data.groupby('Year', as_index=False, observed=True)['Automobile_Sales'].mean()
    r1 = px.line(yearly_rec, x='Year', y='Automobile_Sales', markers=True,
                 title='Average Automobile Sales During Recession Years')
    style_figure(r1, 'Year', 'Average Automobile Sales')

    # Plot 2: mean automobile sales for each vehicle type (bar).
    average_sales = recession_data.groupby('Vehicle_Type', as_index=False, observed=True)['Automobile_Sales'].mean()
    r2 = px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales',
                color='Vehicle_Type', title='Average Vehicles Sold by Vehicle Type')
    style_figure(r2, 'Vehicle Type', 'Average Automobile Sales')
    r2.update_layout(showlegend=False)

    # Plot 3: advertising expenditure by vehicle type (pie).
    exp_rec = recession_data.groupby('Vehicle_Type', as_index=False, observed=True)['Advertising_Expenditure'].sum()
    r3 = px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type',
                title='Advertising Expenditure Share During Recessions', hole=0)
    style_figure(r3)
    r3.update_traces(textinfo='percent', textposition='inside')
    r3.update_layout(legend=dict(orientation='v', x=1.01, y=1))

    # Plot 4: unemployment, vehicle category, mean sales (grouped bar).
    unemp_data = recession_data.groupby(
        ['unemployment_rate', 'Vehicle_Type'], as_index=False, observed=True
    )['Automobile_Sales'].mean()
    unemp_data['Unemployment Rate'] = unemp_data['unemployment_rate'].map(lambda x: f'{x:.1f}%')
    r4 = px.bar(unemp_data, x='Unemployment Rate', y='Automobile_Sales',
                color='Vehicle_Type', barmode='group',
                title='Effect of Unemployment Rate on Vehicle Type and Sales')
    style_figure(r4, 'Unemployment Rate', 'Average Automobile Sales')
    r4.update_layout(legend_title_text='Vehicle Type')
    return [r1, r2, r3, r4]


def make_yearly_figures(df, selected_year):
    """TASK 2.6: the four plots in the Yearly Statistics report."""
    selected_year = int(selected_year)
    yearly_data = df.loc[df['Year'] == selected_year].copy()
    if yearly_data.empty:
        raise ValueError(f'No automobile sales data available for year {selected_year}')

    # Plot 1: full-period, year-wise mean automobile sales (line).
    yas = df.groupby('Year', as_index=False, observed=True)['Automobile_Sales'].mean()
    y1 = px.line(yas, x='Year', y='Automobile_Sales', markers=True,
                 title='Yearly Average Automobile Sales (Entire Period)')
    style_figure(y1, 'Year', 'Average Automobile Sales')
    y1.add_vline(x=selected_year, line_dash='dot', line_color='#d97706')

    # Plot 2: monthly total automobile sales in the SELECTED YEAR (not all years).
    mas = yearly_data.groupby('Month', as_index=False, observed=True)['Automobile_Sales'].sum()
    y2 = px.line(mas, x='Month', y='Automobile_Sales', markers=True,
                 category_orders={'Month': MONTHS},
                 title=f'Total Monthly Automobile Sales — {selected_year}')
    style_figure(y2, 'Month', 'Total Automobile Sales')

    # Plot 3: average automobile sales by vehicle type in the selected year.
    avr_vdata = yearly_data.groupby('Vehicle_Type', as_index=False, observed=True)['Automobile_Sales'].mean()
    y3 = px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales', color='Vehicle_Type',
                title=f'Average Vehicles Sold by Vehicle Type — {selected_year}')
    style_figure(y3, 'Vehicle Type', 'Average Automobile Sales')
    y3.update_layout(showlegend=False)

    # Plot 4: advertising expenditure by vehicle type in the selected year.
    exp_data = yearly_data.groupby('Vehicle_Type', as_index=False, observed=True)['Advertising_Expenditure'].sum()
    y4 = px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type',
                title=f'Advertisement Expenditure by Vehicle Type — {selected_year}')
    style_figure(y4)
    y4.update_traces(textinfo='percent', textposition='inside')
    y4.update_layout(legend=dict(orientation='v', x=1.01, y=1))
    return [y1, y2, y3, y4]


data = load_data()
year_list = [year for year in range(1980, 2024) if year in set(data['Year'])]
DEFAULT_YEAR = 2008 if 2008 in year_list else year_list[0]

# TASK 2.1: Create a Dash app and the required title.
app = dash.Dash(__name__)
app.title = 'Automobile Sales Statistics Dashboard'
server = app.server

# TASK 2.2: Separate dropdowns for report type and year.
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'},
]
app.layout = html.Div(className='dashboard-container', children=[
    html.H1(
        'Automobile Sales Statistics Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': '24px'},
    ),
    html.P('XYZAutomotives  |  Historical Automobile Sales Analysis',
           className='dashboard-subtitle'),
    html.Div(className='filter-row', children=[
        html.Div(className='filter-group', children=[
            html.Label('Select Statistics:'),
            dcc.Dropdown(
                id='dropdown-statistics',
                options=dropdown_options,
                value='Yearly Statistics',
                placeholder='Select a report type',
                clearable=False,
                style={'width': '100%', 'fontSize': '16px'},
            ),
        ]),
        html.Div(className='filter-group', children=[
            html.Label('Select Year:'),
            dcc.Dropdown(
                id='select-year',
                options=[{'label': str(i), 'value': i} for i in year_list],
                value=DEFAULT_YEAR,
                placeholder='Select-year',
                clearable=False,
                disabled=False,
                style={'width': '100%', 'fontSize': '16px'},
            ),
        ]),
    ]),
    # TASK 2.3: output display container with the required id, class and style.
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex'})
    ]),
    html.Footer('Educational project • Synthetic exercise dataset', className='footer-note'),
])

# TASK 2.4 (callback 1): disable year dropdown for recession report.
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value'),
)
def update_input_container(selected_statistics):
    return selected_statistics != 'Yearly Statistics'


def four_chart_grid(figures):
    """Four Plotly figures arranged in exactly two rows and two columns."""
    charts = [dcc.Graph(figure=f, config={'responsive': True, 'displayModeBar': False}) for f in figures]
    return [
        html.Div(className='chart-row', children=[
            html.Div(className='chart-item', children=[charts[0]]),
            html.Div(className='chart-item', children=[charts[1]]),
        ]),
        html.Div(className='chart-row', children=[
            html.Div(className='chart-item', children=[charts[2]]),
            html.Div(className='chart-item', children=[charts[3]]),
        ]),
    ]

# TASK 2.4 (callback 2), TASK 2.5 and TASK 2.6: interactive report selection.
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')],
)
def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'Recession Period Statistics':
        return four_chart_grid(make_recession_figures(data))
    elif selected_statistics == 'Yearly Statistics' and input_year is not None:
        return four_chart_grid(make_yearly_figures(data, input_year))
    return html.P('Please select a report and a year.', className='empty-message')

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8050)
