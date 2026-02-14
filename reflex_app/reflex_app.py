import reflex as rx
from reflex_app.pages import dashboard, portfolio, watchlist # Importación de páginas
from reflex_app.state import State

def index():
    return dashboard.dashboard_page()

app = rx.App()
app.add_page(index, route="/")
app.add_page(dashboard.dashboard_page, route="/dashboard")
app.add_page(portfolio.portfolio_page, route="/portfolio")
app.add_page(watchlist.watchlist_page, route="/watchlist")
