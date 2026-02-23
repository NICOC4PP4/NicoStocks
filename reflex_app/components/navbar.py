import reflex as rx

def navbar() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.hstack(
                rx.icon(tag="activity", size=24, color="blue"),
                rx.heading("SmartFolio", size="6", font_weight="bold"),
                spacing="2",
                align="center",
            ),
            rx.hstack(
                rx.link("Dashboard", href="/", color_scheme="gray"),
                rx.link("Portfolio", href="/portfolio", color_scheme="gray"),
                rx.link("Watchlist", href="/watchlist", color_scheme="gray"),
                spacing="6",
                margin_right="2em",
            ),
            justify="between",
            align="center",
            width="100%",
            padding_x="5",
            padding_y="3",
        ),
        background_color="rgba(0,0,0,0.2)",
        backdrop_filter="blur(10px)",
        border_bottom="1px solid rgba(255,255,255,0.1)",
        position="sticky",
        top="0",
        z_index="1000",
        width="100%",
    )
