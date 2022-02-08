import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input

external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?'
                'family=Lato:wght@400;700&display=swap',
        'rel': 'stylesheet',
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Social Audio - Analytics'

data = pd.read_csv('ch_analytics_dashboard.csv')
# data = data.query('Club == "The Green Buttwhole"')
data['Date'] = data['Event'].str.split(' ').str[0]
data['Date'] = pd.to_datetime(data['Date'], format="%Y/%m/%d")
data = data.sort_values('Date')
# data = data.head(75)

metrics = ['Duration', 'Users', 'Max Room Size', 'Moderators', 'Speakers', 'Listeners',
           'Bounce', 'Stickiness', 'Total User Time', 'Avg User Time',
           'Avg User Time [New Members]', 'Avg User Time [Old Members]', 'Avg Speaker Time',
           'Avg Listener Time', 'New Users', 'New Users Pct', 'Old Users', 'Old Users Pct']

methods = ['Median', 'Mean', 'Minimum', 'Maximum']

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children='Social Audio - Analytics',

                    className='header-title',
                ),
                html.P(
                    children='Analyze patterns of social audio rooms'
                             ' and the number of users'
                             ' between March and June of 2021',
                    className='header-description',
                ),
            ],
            className='header',
        ),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children='Club', className='menu-title'),
                        dcc.Dropdown(
                            id='club-filter',
                            options=[
                                {'label': club, 'value': club}
                                for club in np.sort(data.Club.unique())
                            ],
                            value='The Green Buttwhole',
                            clearable=False,
                            className='dropdown',
                        ),
                    ]
                ),

                html.Div(
                    children=[
                        html.Div(children='Metric', className='menu-title'),
                        dcc.Dropdown(
                            id='metric-filter',
                            options=[
                                {'label': metric, 'value': metric}
                                for metric in metrics
                            ],
                            value='Users',
                            clearable=False,
                            searchable=False,
                            className='dropdown',
                        ),
                    ],
                ),

                html.Div(
                    children=[
                        html.Div(children='Method', className='menu-title'),
                        dcc.Dropdown(
                            id='method-filter',
                            options=[
                                {'label': method, 'value': method}
                                for method in methods
                            ],
                            value='Median',
                            clearable=False,
                            searchable=False,
                            className='dropdown',
                        ),
                    ],
                ),

                html.Div(
                    children=[
                        html.Div(
                            children='Date Range', className='menu-title'
                        ),
                        dcc.DatePickerRange(
                            id='date-range',
                            min_date_allowed=data.Date.min().date(),
                            max_date_allowed=data.Date.max().date(),
                            start_date=data.Date.min().date(),
                            end_date=data.Date.max().date(),
                        ),
                    ]
                ),
            ],
            className='menu',
        ),

        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='agg-chart',
                        config={'displayModeBar': True},
                    ),
                    className='card',
                ),
            ],
            className='wrapper',
        ),

        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='club-chart',
                        config={'displayModeBar': True},
                    ),
                    className='card',
                ),
            ],
            className='wrapper',
        ),
    ],
)


@app.callback([Output('agg-chart', 'figure'), Output('club-chart', 'figure')],
              [
                  Input('club-filter', 'value'),
                  Input('metric-filter', 'value'),
                  Input('method-filter', 'value'),
                  Input('date-range', 'start_date'),
                  Input('date-range', 'end_date'),
              ],
              )

def update_charts(club, metric, method, start_date, end_date):

    mask = (
            (data.Club == club)
            # & (data.type == avocado_type)
            & (data.Date >= start_date)
            & (data.Date <= end_date)
    )

    filtered_data = data.loc[mask, :]
    # filtered_data = filtered_data.dropna(axis=1, subset=metric)
    filtered_data = filtered_data[filtered_data[metric] > 0]

    # label_lenght = filtered_data['Title'].max()
    # label_lenght = label_lenght + 5

    agg_chart_figure = {
        'data': [
            {
                'x': filtered_data['Title'],
                'y': filtered_data[metric],
                'type': 'bar',
                'hovertemplate': '%{y:.2f}<extra></extra>',
            },
        ],
        'layout': {
            'title': {
                'text': club + ' - ' + metric,
                'x': 0.05,
                'xanchor': 'left',
            },
            'height': 820,
            'xaxis': {
                'fixedrange': True,
                'automargin': True,
                'tickangle': 80,
            },
            'yaxis': {'fixedrange': True},
            # 'margin': {'b': 200},
            'colorway': ['#17B897'],
        },
    }

    if method == 'Maximum':
        grouped = data.groupby(by='Club', as_index=False).max(numeric_only=True)
        grouped = grouped.sort_values(by=metric)

    elif method == 'Minimum':
        grouped = data.groupby(by='Club', as_index=False).min(numeric_only=True)
        grouped = grouped.sort_values(by=metric)

    elif method == 'Median':
        grouped = data.groupby(by='Club', as_index=False).median(numeric_only=True)
        grouped = grouped.sort_values(by=metric)

    else:
        grouped = data.groupby(by='Club', as_index=False)
        grouped = grouped.mean(numeric_only=True)
        grouped = grouped.sort_values(by=metric)

    grouped = grouped[grouped[metric] > 0]

    club_chart_figure = {
        'data': [
            {
                'x': grouped['Club'],
                'y': grouped[metric],
                'type': 'bar',
                'hovertemplate': '%{y:.2f}<extra></extra>',
            },
        ],
        'layout': {
            'title': {
                'text': metric + ' - ' + method,
                'x': 0.05,
                'xanchor': 'left',
            },
            'height': 540,
            'xaxis': {
                'fixedrange': True,
                'automargin': True,
                'tickangle': 80,
            },
            'yaxis': {'fixedrange': True},
            'colorway': ['#17B897'],
        },
    }

    # club_chart_figure = [club_chart_figure]
    # agg_chart_figure = [agg_chart_figure]

    return agg_chart_figure, club_chart_figure


if __name__ == '__main__':
    app.run_server(debug=True)
