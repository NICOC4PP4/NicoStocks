import reflex as rx
from reflex_app.pages import dashboard, portfolio, watchlist, research # Importación de páginas
from reflex_app.state import State

def index():
    return dashboard.dashboard_page()

tailwind_config_script = """
function configureTailwind() {
    if (typeof tailwind !== 'undefined') {
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        primary: '#2b8cee',
                        'background-light': '#f6f7f8',
                        'background-dark': '#101922',
                        'surface-dark': '#18222c',
                        'surface-light': '#ffffff',
                        success: '#10B981',
                        danger: '#EF4444'
                    }
                }
            }
        };
    } else {
        setTimeout(configureTailwind, 50);
    }
}
configureTailwind();
"""

app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap",
        "https://fonts.googleapis.com/icon?family=Material+Icons",
        "https://fonts.googleapis.com/icon?family=Material+Icons+Outlined",
        "https://fonts.googleapis.com/icon?family=Material+Icons+Round"
    ],
    head_components=[
        rx.script(src="https://cdn.tailwindcss.com?plugins=forms,container-queries"),
        rx.script(tailwind_config_script)
    ]
)
app.add_page(index, route="/")
app.add_page(dashboard.dashboard_page, route="/dashboard")
app.add_page(portfolio.portfolio_page, route="/portfolio")
app.add_page(watchlist.watchlist_page, route="/watchlist")
app.add_page(research.research_page, route="/research")
