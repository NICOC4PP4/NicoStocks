import reflex as rx
from reflex_app.state import State
from reflex_app.components.add_transaction_modal import add_transaction_modal


def row_item(row: dict):
    """Fila de la tabla de holdings con PnL condicional."""
    pnl = row["pnl_pct"].to(float)
    pnl_color = rx.cond(pnl >= 0, "green", "red")
    pnl_prefix = rx.cond(pnl >= 0, "+", "")

    pe_val = row["pe_ntm"].to(float)
    pe_color = rx.cond(
        pe_val < 15,
        "green",
        rx.cond(pe_val > 25, "red", "orange"),
    )

    return rx.table.row(
        rx.table.cell(rx.text(row["ticker"], font_weight="bold")),
        rx.table.cell(row["shares"]),
        rx.table.cell(f"${row['avg_buy']}"),
        rx.table.cell(f"${row['price']}"),
        rx.table.cell(f"${row['value']}"),
        rx.table.cell(
            rx.text(
                rx.text.span(pnl_prefix, row["pnl_pct"], "%"),
                color=pnl_color,
                font_weight="bold",
            )
        ),
        rx.table.cell(
            rx.text(str(row["pe_ntm"]), color=pe_color, font_weight="bold")
        ),
        rx.table.cell(f"${row['fcf_share']}"),
    )


def portfolio_page():
    return rx.vstack(
        rx.flex(
            rx.heading("Active Holdings", size="6"),
            add_transaction_modal(),
            justify="between",
            align="center",
            width="100%",
        ),
        rx.cond(
            State.total_value > 0,
            rx.flex(
                rx.badge(
                    f"Total: ${State.total_value}",
                    color_scheme="blue",
                    size="2",
                ),
                rx.badge(
                    rx.text.span("PnL: ", State.total_pnl, "%"),
                    color_scheme=rx.cond(State.total_pnl >= 0, "green", "red"),
                    size="2",
                ),
                spacing="2",
            ),
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Ticker"),
                    rx.table.column_header_cell("Shares"),
                    rx.table.column_header_cell("Avg. Buy"),
                    rx.table.column_header_cell("Current"),
                    rx.table.column_header_cell("Value"),
                    rx.table.column_header_cell("PnL %"),
                    rx.table.column_header_cell("PE NTM"),
                    rx.table.column_header_cell("FCF/Share"),
                )
            ),
            rx.table.body(rx.foreach(State.holdings, row_item)),
            width="100%",
        ),
        rx.cond(
            State.holdings.length() == 0,
            rx.callout(
                "No holdings yet. Click '➕ Add Transaction' to get started!",
                icon="info",
                color_scheme="blue",
            ),
        ),
        on_mount=State.load_data,
        spacing="4",
        padding="5",
    )
