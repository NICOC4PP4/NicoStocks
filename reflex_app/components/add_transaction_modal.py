import reflex as rx
from reflex_app.state import State


def add_transaction_modal() -> rx.Component:
    """Modal para registrar una nueva transacción de compra."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.el.button(
                rx.html('<span class="material-icons text-sm mr-2">add</span>'),
                "Add Transaction",
                on_click=State.open_modal,
                type="button",
                class_name="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
            )
        ),
        rx.dialog.content(
            rx.dialog.title("Register Purchase"),
            rx.dialog.description("Add a new stock purchase to your portfolio."),
            rx.vstack(
                # ── Ticker ──
                rx.text("Ticker Symbol", font_weight="bold", size="2"),
                rx.input(
                    placeholder="e.g. NVDA",
                    value=State.form_ticker,
                    on_change=State.set_form_ticker,
                    size="3",
                    width="100%",
                ),
                # ── Date ──
                rx.text("Purchase Date", font_weight="bold", size="2"),
                rx.input(
                    type="date",
                    value=State.form_date,
                    on_change=State.set_form_date,
                    size="3",
                    width="100%",
                ),
                # ── Shares ──
                rx.text("Shares", font_weight="bold", size="2"),
                rx.input(
                    placeholder="e.g. 10",
                    type="number",
                    value=State.form_shares,
                    on_change=State.set_form_shares,
                    size="3",
                    width="100%",
                ),
                # ── Price ──
                rx.text("Price per Share (USD)", font_weight="bold", size="2"),
                rx.input(
                    placeholder="e.g. 125.50",
                    type="number",
                    value=State.form_price,
                    on_change=State.set_form_price,
                    size="3",
                    width="100%",
                ),
                # ── Error Message ──
                rx.cond(
                    State.form_error != "",
                    rx.callout(
                        State.form_error,
                        icon="triangle_alert",
                        color_scheme="red",
                        width="100%",
                    ),
                ),
                # ── Buttons ──
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Cancel",
                            variant="soft",
                            color_scheme="gray",
                            on_click=State.close_modal,
                        ),
                    ),
                    rx.button(
                        rx.cond(State.form_loading, "Processing...", "Register Purchase"),
                        color_scheme="green",
                        disabled=State.form_loading,
                        on_click=State.add_transaction,
                    ),
                    spacing="3",
                    justify="end",
                    width="100%",
                ),
                spacing="3",
                width="100%",
                padding_y="3",
            ),
            max_width="480px",
        ),
        open=State.show_modal,
        on_open_change=State.toggle_modal,
    )
