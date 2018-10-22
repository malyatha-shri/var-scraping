# coding: utf-8

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash(__name__)
server = app.server

# read data for tables (one df per table)
df_mr_var = pd.read_csv('test1_2.csv')
df_mr_ear = pd.read_csv('ear.csv')
df_mr_ear_table = pd.read_csv('ear_table.csv').dropna(how='all')
df_mr_other = pd.read_csv('test8_3.csv')
df_cr_metrics = pd.read_csv('capital1.csv')

app.config.suppress_callback_exceptions = True

# Describe the layout, or the UI, of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# Update page
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname == '/market-risk':
        return market_risk
    elif pathname == '/capital-risk':
        return capital_risk


# reusable components
def make_dash_table(df):
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table


def print_button():
    printButton = html.A(['Print PDF'], className="button no-print print",
                         style={'position': "absolute", 'top': '-40', 'right': '0'})
    return printButton


# includes page/full view
def get_logo():
    logo = html.Div([

        html.Div([
            html.Img(src='http://logonoid.com/images/vanguard-logo.png', height='40', width='160')
        ], className="ten columns padded"),

        html.Div([
            dcc.Link('Full View   ', href='/full-view')
        ], className="two columns page-view no-print")

    ], className="row gs-header")
    return logo


def get_header():
    header = html.Div([

        html.Div([
            html.H5(
                'JPMorgan Chase Risk Measures')
        ], className="twelve columns padded")

    ], className="row gs-header gs-text-header")
    return header


def get_menu():
    menu = html.Div([

        dcc.Link('Market Risk Management   ', href='/market-risk', className="tab first"),

        dcc.Link('Investment Portfolio Risk Management  ', href='/portfolio-risk', className="tab"),

        dcc.Link('Capital Risk Management   ', href='/capital-risk', className="tab"),

        dcc.Link('Liquidity Risk Management   ', href='/liquidity-risk', className="tab"),

        dcc.Link('Country Risk Management   ', href='/country-risk', className="tab")

    ], className="row ")
    return menu


# Page Layouts
market_risk = html.Div([  # page 1

    print_button(),

    html.Div([

        get_header(),
        html.Br([]),
        get_menu(),

        html.Div([

            html.H1('Total VaR using 95% Confidence Level'),

            html.Br([]),

            html.Div([
                dcc.Dropdown(
                    id='risk-type',
                    options=[{'label': i, 'value': i} for i in df_mr_var['risk_type'].unique()],
                    value='Total VaR'
                )
            ],
                style={'width': '30%', 'display': 'inline-block'}),

            dcc.Graph(id='var_graph'),
            html.Div(id='text')

        ])]),

    html.Br([]),

    html.Div([

        html.H1(children='12-Months Earnings-at-Risk Sensitivity Profiles'),

        html.Div([
            html.Table(make_dash_table(df_mr_ear_table))
        ]),

        dcc.Graph(id='graph',

                  figure={
                      'data': [
                          go.Scatter(
                              x=df_mr_ear[df_mr_ear['date'] == i]['rates_change'],
                              y=df_mr_ear[df_mr_ear['date'] == i]['ear'],
                              mode='markers',
                              opacity=0.7,
                              marker={
                                  'size': 15,
                                  'line': {'width': 0.5, 'color': 'white'}
                              },
                              name=i
                          ) for i in df_mr_ear.date.unique()
                      ],
                      'layout': go.Layout(
                          xaxis={'title': 'Instantaneous change in rates (bps)'},
                          yaxis={'title': 'Earning-at-Risk USD (in Billions)'},
                          margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                          legend={'x': 0, 'y': 1},
                          hovermode='closest'
                      )
                  })]),
    html.Div([

        html.H1(children='Potential Impact to Net Revenue for market-risk sensitive instruments'),

        html.Div([

            dcc.Dropdown(
                id='activity',
                options=[{'label': i, 'value': i} for i in df_mr_other.Activity_spec.unique()]),
        ],
            style={'width': '30%', 'display': 'inline-block'}),

        html.Div(id='mr-other-description'),
        dcc.Graph(id='mr-other-graph')])

])

capital_risk = html.Div([  # page 1

    print_button(),
    get_header(),
    html.Br([]),
    get_menu(),

    html.Div([

        html.H1('Capital Metrics',
                className="gs-header gs-text-header padded"),

        html.Br([]),

        html.Div([

            dcc.RadioItems(
                id='capital-metric-basel_measure',
                options=[{'label': i, 'value': i} for i in df_cr_metrics.basel_measure.unique()]),

            html.Div([
                dcc.Dropdown(
                    id='capital-metric-type',
                    options=[{'label': i, 'value': i} for i in df_cr_metrics.capital_metric_type.unique()]
                )
            ],
                style={'width': '20%', 'display': 'inline-block'})]),

        dcc.Graph(id='cap_graph'),
        html.P("\
                Note: As of March 31, 2018, and December 31, 2017, the lower of the Standardized or \
                Advanced capital ratios under each of the Transitional and Fully Phased-In approaches \
                in the table above represents the Firm’s Collins Floor.\
                (a) Adjusted average assets, for purposes of calculating the Tier 1 leverage ratio, \
                    includes total quarterly average assets adjusted for on-balance sheet assets \
                    that are subject to deduction from Tier 1 capital, predominantly goodwill and \
                    other intangible assets. \
                (b) Effective January 1, 2018, the SLR was fully phased-in under Basel III.")])])


@app.callback(
    dash.dependencies.Output('var_graph', 'figure'),
    [dash.dependencies.Input('risk-type', 'value')])
def update_mkt_figure(selected_risk_type):
    filtered_df = df_mr_var[df_mr_var.risk_type == selected_risk_type]
    traces = []
    for item in filtered_df.stat_measure.unique():
        df_by_stat_measure = filtered_df[filtered_df['stat_measure'] == item]
        traces.append(go.Scatter(
            x=df_by_stat_measure['date'],
            y=df_by_stat_measure['var'],
            text=df_by_stat_measure['var'],
            mode='markers',
            opacity=1.2,
            marker={
                'size': 10,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=item
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': '3 Months Ended'},
            yaxis={'title': 'VaR (in Millions)'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            hovermode='closest'
        )
    }


@app.callback(
    dash.dependencies.Output('text', 'children'),
    [dash.dependencies.Input('risk-type', 'value'),
     ])
def update_text(selected_risk_type):
    cleaned_type = selected_risk_type.lower()
    text_output = ''
    if 'diversification' in cleaned_type:
        text_output = "\
                      (a) Average portfolio VaR is less than the sum of the VaR of the \
                        components described above, which is due to portfolio diversification. \
                        The diversification effect reflects that the risks are not perfectly correlated.\
                      (b) Diversification benefit represents the difference between the total VaR \
                        and each reported level and the sum of its individual components. \
                        Diversification benefit reflects the non-additive nature of VaR due to imperfect \
                        correlation across lines of business and risk types. The maximum and minimum VaR for \
                        each portfolio may have occurred on different trading days than the components and \
                        consequently diversification benefit is not meaningful."
    return text_output


@app.callback(
    dash.dependencies.Output('mr-other-graph', 'figure'),

    [dash.dependencies.Input('activity', 'value')
     ])
def update_mr_other_figure(activity):
    filtered_df = df_mr_other[df_mr_other.Activity_spec == activity]
    print filtered_df
    sens_measure = filtered_df.iloc[0]['sens_measure']

    bar_charts = []

    bar_charts.append(

        go.Bar(
            x=filtered_df.Date.unique(),
            y=filtered_df.Val.unique(),
            marker={
                "color": "rgb(53, 83, 255)",
                "line": {
                    "color": "rgb(255, 255, 255)",
                    "width": 2
                }
            }
        ))

    return {
        'data': bar_charts,
        'layout': go.Layout(

            title=sens_measure,

            xaxis=dict(
                title='End Of Months',
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
            yaxis=dict(
                title='Gain or Loss in USD (millions)',
                titlefont=dict(
                    size=16,
                    color='rgb(107, 107, 107)'
                ),
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ))
    }


@app.callback(
    dash.dependencies.Output('mr-other-description', 'children'),

    [dash.dependencies.Input('activity', 'value')
     ])
def update_mr_other_text(activity):
    filtered_df = df_mr_other[df_mr_other.Activity_spec == activity]
    activity_type = filtered_df.iloc[0]['Activity_type']
    desc = filtered_df.iloc[0]['Description']
    return activity_type + '-' + desc


@app.callback(
    dash.dependencies.Output('cap_graph', 'figure'),
    [dash.dependencies.Input('capital-metric-basel_measure', 'value'),
     dash.dependencies.Input('capital-metric-type', 'value')
     ])
def update_cap_figure(basel_measure_type, basel_metric_type):
    filtered_df_measure = df_cr_metrics[df_cr_metrics.basel_measure == basel_measure_type]
    filtered_df_metric = filtered_df_measure[filtered_df_measure.capital_metric_type == basel_metric_type]

    approaches = filtered_df_metric.approach.unique()

    bar_charts = []

    bar_charts.append(

        go.Bar(
            x=filtered_df_metric.date.unique(),
            y=filtered_df_metric[filtered_df_measure.approach == approaches[0]]['value'].unique(),
            marker={
                "color": "rgb(53, 83, 255)",
                "line": {
                    "color": "rgb(255, 255, 255)",
                    "width": 3
                }
            },
            name=approaches[0]
        ))

    bar_charts.append(
        go.Bar(
            x=filtered_df_metric.date.unique(),
            y=filtered_df_metric[filtered_df_measure.approach == approaches[1]]['value'].unique(),
            marker={
                "color": "rgb(255, 225, 53)",
                "line": {
                    "color": "rgb(255, 255, 255)",
                    "width": 3
                }
            },
            name=approaches[1]
        ))

    return {
        'data': bar_charts,
        'layout': go.Layout(

            xaxis=dict(
                title='End Of Months',
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
            yaxis=dict(
                title='In USD (millions), except ratios',
                titlefont=dict(
                    size=16,
                    color='rgb(107, 107, 107)'
                ),
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
            barmode='group')
    }


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "https://codepen.io/bcd/pen/KQrXdb.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ["https://code.jquery.com/jquery-3.2.1.min.js",
               "https://codepen.io/bcd/pen/YaXojL.js"]

for js in external_js:
    app.scripts.append_script({"external_url": js})

if __name__ == '__main__':
    app.run_server(debug=True)
