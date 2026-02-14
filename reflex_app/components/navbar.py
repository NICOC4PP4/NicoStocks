
import reflex as rx

def navbar():
    return rx.flex(
        rx.heading("SmartFolio", size="8"),
        rx.spacer(),
        rx.link("Dashboard", href="/dashboard", padding_x="2"),
        rx.link("Portfolio", href="/portfolio", padding_x="2"),
        rx.link("Watchlist", href="/watchlist", padding_x="2"),
        width="100%",
        padding="4",
        border_bottom="1px solid #eaeaea",
    )
