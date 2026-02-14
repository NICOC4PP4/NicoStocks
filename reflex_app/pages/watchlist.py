import reflex as rx
from reflex_app.state import State

def watchlist_page():
    return rx.vstack(
        rx.heading("Watchlist"),
        rx.text("Lista de seguimiento en construcción..."),
        rx.button("Refresh", on_click=State.fetch_watchlist),
        on_mount=State.fetch_watchlist,
        padding="5"
    )
