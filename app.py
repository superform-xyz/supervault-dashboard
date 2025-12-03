import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import os
from layouts.dashboard import create_dashboard_layout

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"property": "og:image", "content": "/assets/superform.png"}
    ],
    assets_folder="assets",
    suppress_callback_exceptions=True
)

# Set the favicon directly
app._favicon = "superform.png"

server = app.server
app.title = "SuperVaults v2"

# Define the navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="/assets/superform.png", height="30px"), width="auto"),
                        dbc.Col(dbc.NavbarBrand("SuperVaults v2", className="ms-2")),
                    ],
                    align="center",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
                        dbc.NavItem(
                            dbc.NavLink(
                                "Docs", 
                                href="https://docs.superform.xyz/what-is-superform/superform-protocol/supervaults", 
                                external_link=True,
                                target="_blank"
                            )
                        ),
                        dbc.NavItem(
                            dbc.NavLink(
                                "GitHub", 
                                href="https://github.com/superform-xyz/supervault-dashboard", 
                                external_link=True,
                                target="_blank"
                            )
                        ),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ]
    ),
    color="primary",
    dark=True,
    className="mb-4",
)

# Define the app layout
# Add ClipboardJS for copy functionality
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <!-- Add clipboard.js -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.11/clipboard.min.js"></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', className='container'),
    # Include our custom clipboard script
    html.Script(src='/assets/clipboard.js')
])

# Define callback to render the different pages
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    return create_dashboard_layout()

# Run the app
if __name__ == '__main__':
    from utils.config import Config
    port = int(os.environ.get('PORT', 8050))
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=port)
