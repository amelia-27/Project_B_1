import dash
from dash import Dash, html, dcc, Input, Output, State, no_update
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from pandas_datareader import wb
import plotly.graph_objects as go

##need to change the theme later!
app = Dash(__name__, external_stylesheets= [dbc.themes.CERULEAN])

#may be missing some. Delete unused when complete
indicators = {
    "NY.GDP.PETR.RT.ZS": "Oil rents (% of GDP)",
    "TX.VAL.FUEL.ZS.UN": "Fuel exports (% of merchandise exports)",
}
indicators_2 = {
    # "SH.STA.AIRP.P5": "Mortality rate attributed to household and ambient air pollution, age-standardized (per 100,000 population)",
    # "EN.ATM.PM25.MC.M3": "PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)",
    # "EN.ATM.PM25.MC.ZS": "PM2.5 air pollution, population exposed to levels exceeding WHO guideline value (% of total)",
    # "SP.URB.TOTL.IN.ZS": "Urban population (% of total population)",
    "EG.ELC.PETR.ZS": "Electricity production from oil sources (% of total)",
    "EN.ATM.PM25.MC.M3": "PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)",
}

#get country name and ISO id for mapping
countries = wb.get_countries()

african_countries = countries[countries["region"].isin(["Sub-Saharan Africa ", "Middle East & North Africa"])]

#countries["capitalCity"].replace({"": None}, inplace = True)
#countries.dropna(subset=["capitalCity"], inplace = True) #countries without a capital city are dropped

african_countries = african_countries[["name", "iso3c"]] #inclusion of the country id codes
african_countries = african_countries.rename(columns = {"name": "country"}) #reference column to countries now labeled "country"

def update_wb_data():
    all_indicators = list(indicators.keys()) + list(indicators_2.keys())
    df = wb.download(
        indicator= all_indicators,
        country = african_countries['iso3c'].tolist(),
        start = 1970,
        end = 2023

    )
    df = df.reset_index()
    df["year"] = df["year"].astype(int)

    df = pd.merge(df,african_countries, on = "country")
    all_indicators_dict = {**indicators, **indicators_2}
    df = df.rename(columns = all_indicators_dict)

    available_years = list(range(1976, 2022, 5))

    return df, available_years

df_data, available_years = update_wb_data()

#need initial figure - set up here:
def create_initial_figure():
    default_indicator = list(indicators.values())[0]
    df_non_null = df_data.dropna(subset=[default_indicator])

    if df_non_null.empty: #will not display if inct_chosen doesn't have data in the latest year
        print(f"No data available for {default_indicator}")
        return go.Figure()
    default_year = available_years[0]
    dff = df_non_null[df_non_null["year"] == default_year]

    if dff.empty:
        print (f"no data available")
        return go.Figure()


    fig = px.choropleth(
        data_frame=dff,
        locations="iso3c",
        color=default_indicator,
        hover_name = "country",
        scope ="africa",
        labels = {default_indicator: default_indicator},
        color_continuous_scale = "viridis",
    )

    fig.update_layout(
        margin = dict(l = 50, r=50, t=50, b=50),
        #height = "100%"
    )
    return fig

def create_initial_figure_2():
    default_indicator = list(indicators_2.values())[0]
    df_non_null = df_data.dropna(subset=[default_indicator])

    if df_non_null.empty: #will not display if inct_chosen doesn't have data in the latest year
        print(f"No data available for {default_indicator}")
        return go.Figure()
    default_year = available_years[0]
    dff = df_non_null[df_non_null["year"] == default_year]

    if dff.empty:
        print (f"no data available")
        return go.Figure()


    fig = px.choropleth(
        data_frame=dff,
        locations="iso3c",
        color=default_indicator,
        hover_name = "country",
        scope ="africa",
        labels = {default_indicator: default_indicator},
        color_continuous_scale = "viridis",
    )

    fig.update_layout(
        margin = dict(l = 50, r=50, t=50, b=50),
        #height = "100%"
    )
    return fig

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1( #title
                    "Investigating Africa Air Quality Causes",
                    style = {"textAlign": "center"},
                ),
                width = 12,
            ),
            justify = "center",
        ),
        dbc.Row(
            dbc.Col(
                html.H3(
                    "Socioeconomic Development: Oil & Exports",
                    style = {"textAlign": "center", "margin-top": "20px"},
                ),
                width = 12,
            ),
            justify = "center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label(
                            "Left Graph Display",
                            className="fw-bold",
                            style={"textDecoration": "underline", "fontSize": 20, "textAlign": "center"},
                        ),
                        dcc.Dropdown(
                            id="dropdown",
                            options=[{"label": v, "value": v} for v in indicators.values()],
                            value=list(indicators.values())[0],
                            clearable= False,
                            style={"width": "100%"}
                        ),
                    ],
                    width = 4
                ),
                dbc.Col(
                    [
                        dbc.Label(
                            "Right Graph Display",
                            className="fw-bold",
                            style={"textDecoration": "underline", "fontSize": 20, "textAlign": "center"},
                        ),
                        dcc.Dropdown(
                            id="dropdown-second",
                            options=[{"label": v, "value": v} for v in indicators_2.values()],
                            value=list(indicators_2.values())[0],
                            clearable=False,
                            style={"width": "100%"}
                        ),
                    ],
                    width=4
                ),
            ],
            justify = "center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id = "my-choropleth", figure = create_initial_figure()),
                    ],
                    width = 6,
                ),
                dbc.Col(
                    [
                        dcc.Graph(id="my-choropleth-2", figure=create_initial_figure_2()),
                    ],
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            dbc.Col(
                [
                    dbc.Label(
                        "Years:",
                        className = "fw-bold",
                        style={"fontSize": 20},
                    ),
                    dcc.Slider(
                        id = "year-slider",
                        min = available_years[0], #more dynamic this way
                        max = available_years[-1],
                        step = 5,
                        value = available_years[0],
                        marks ={
                            year: str(year) for year in available_years
                        },
                    ),
                ],
                width = 6,
            ),
            justify="center",
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.Div(
                        [
                            dbc.Label(
                                "Animate Progression",
                                className = "fw-bold",
                                style = {"fontSize": 20, "textDecoration": "underline", "margin-right": "20px"},
                            ),
                            dcc.RadioItems(
                                id = "Animate Progression",
                                options=[
                                    {"label": "Off", "value": "Off"},
                                    {"label": "On", "value": "On"},
                                ],
                                value ="Off",
                                labelStyle={"display": "incline-block", "margin-right": "20px"},
                                style={"display": "inline-block"},
                            ),
                        ],
                       # style = {"textAlign": "center"},
                    ),
                ],
                width = 6,
            ),
            justify= "center",
        ),
        dcc.Interval(
            id= "animation-interval",
            interval= 450,
            n_intervals = 0,
            disabled = True,
        ),
        dbc.Row(
            dbc.Col(
                [
                    dbc.Label(
                        "Graph Details for Selected Country",
                        className="fw-bold",
                        style={"textDecoration": "underline", "fontSize": 20, "textAlign": "center"},
                    ),
                    dcc.Graph(
                        id="country-detail-graph"
                    ),
                ],
                width=12,
            ),
        ),
    ],
    fluid = True,
)

#call back for the animation
@app.callback(
    Output("animation-interval", "disabled"),
    Input("Animate Progression", "value")
)
#animation plays as long as animation is selected.
def toggle_animation(animation_status):
    return False if animation_status == "On" else True

@app.callback(
    Output("year-slider", "value"),
    Input("animation-interval", "n_intervals"),
    State("year-slider", "value"),
    State("year-slider", "min"),
    State("year-slider", "max"),
    State("Animate Progression", "value"),
)

def update_slider(n_intervals, current_year, min_year, max_year, animation_status):
    if animation_status == "Off":
        return current_year

    years = available_years

    #finding the current year and propelling animation
    if current_year in years:
        idx = years.index(current_year)
        #incriments years, stops at maximum
        if idx + 1 < len(years):
            next_year = years [idx + 1]
        else:
            next_year = years[-1]
    else:
        #if current year is not in the list, start from the first year
        next_year = years[0]
    return next_year


@app.callback(
    Output("my-choropleth", "figure"),
    Input("year-slider", "value"),
    Input("dropdown", "value"),
)

def update_graph (selected_year, selected_indicator):
    indct_chosen = selected_indicator

    df_non_null = df_data.dropna(subset=[indct_chosen])

    if df_non_null.empty:
        print(f"indicator '{indct_chosen}' not found in data."),
        return go.Figure()

    dff = df_non_null[df_non_null["year"] == selected_year]

    if dff.empty:
        print(f"no data available for {indct_chosen}")
        return go.Figure()

    fig = px.choropleth(
        data_frame = dff,
        locations = "iso3c",
        hover_name = "country",
        scope = "africa",
        color = indct_chosen,
        labels={indct_chosen: indct_chosen},
        color_continuous_scale = "Viridis",
    )

    fig.update_layout(
        geo = {"projection": {"type": "natural earth"}},
        margin = dict(l=50, r=50, t=50, b=50),
    )
    return fig
#same callback and graph update but for a second graph and dropdown
@app.callback(
    Output("my-choropleth-2", "figure"),
    Input("year-slider", "value"),
    Input("dropdown-second", "value"),
)

def update_graph_2 (selected_year, selected_indicator):
    indct_chosen = selected_indicator

    df_non_null = df_data.dropna(subset=[indct_chosen])

    if df_non_null.empty:
        print(f"indicator '{indct_chosen}' not found in data."),
        return go.Figure()

    dff = df_non_null[df_non_null["year"] == selected_year]

    if dff.empty:
        print(f"no data available for {indct_chosen}")
        return go.Figure()

    fig = px.choropleth(
        data_frame = dff,
        locations = "iso3c",
        hover_name = "country",
        scope = "africa",
        color = indct_chosen,
        labels={indct_chosen: indct_chosen},
        color_continuous_scale = "Viridis",
    )

    fig.update_layout(
        geo = {"projection": {"type": "natural earth"}},
        margin = dict(l=50, r=50, t=50, b=50),
    )
    return fig

#call back and function for my graph that will appear
@app.callback(
    Output("country-detail-graph", "figure"),
    [Input("my-choropleth", "clickData"),
     Input("dropdown", "value"),
     Input("my-choropleth-2", "clickData"),
     Input("dropdown-second", "value")]
)

def update_country_graphs(clickData1, selected_indicator1, clickData2, selected_indicator2):
    ctx = dash.callback_context

    if not ctx.triggered:
        fig = go.Figure()
        fig.add_annotation(
            x = 0.5, y = 0.5,
            text = "Click on a country on one of the maps to see a graph!",
            showarrow = False,
            xref = "paper", yref = "paper",
            font = dict(size = 16)
        )
        return fig

    clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if clicked_id == "my-choropleth" and clickData1 is not None:
        clickData = clickData1
        selected_indicator = selected_indicator1
    elif clicked_id == "my-choropleth-2" and clickData2 is not None:
        clickData = clickData2
        selected_indicator = selected_indicator2
    else:
        fig = go.Figure()
        fig.add_annotation(
            x = 0.5, y=0.5,
            text = "Click on a country on one of the maps to see a graph!",
            showarrow = False,
            xref = "paper", yref = "paper",
            font = dict(size = 16)
        )
        return fig

    country_iso = clickData["points"][0]["location"]
    country_data = df_data[df_data["iso3c"] == country_iso]

    if country_data.empty or selected_indicator not in country_data.columns:
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="No data available for the selected country.",
            showarrow=False,
            xref="paper", yref="paper",
            font=dict(size=16)
        )
        return fig

    fig = px.line(
        country_data,
        x = "year",
        y = selected_indicator,
        title = f"{selected_indicator} Over Time for  {country_data.iloc[0]['country']}",
        labels = {"year": "Year", selected_indicator: selected_indicator},
    )

    fig.update_layout(
        xaxis_title = "Year",
        yaxis_title = selected_indicator,
        template = "plotly_white",
    )

    return fig

if __name__ == "__main__":
    app.run_server(debug = True)