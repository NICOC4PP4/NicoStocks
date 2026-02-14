import reflex as rx
from reflex_app.state import State

def row_item(row: dict):
    # Formato condicional
    # Asegurar que pe_ntm es float para comparacion, puede venir como None o string si hay error
    # Calculo de color usando rx.cond (Lógica reactiva)
    pe_val = row["pe_ntm"].to(float)
    pe_color = rx.cond(
        pe_val < 15,
        "green",
        rx.cond(
            pe_val > 25,
            "red",
            "orange"
        )
    )

    
    return rx.table.row(
        rx.table.cell(row["ticker"]),
        rx.table.cell(row["shares"]),
        rx.table.cell(f"${row['price']}"),
        rx.table.cell(f"${row['value']}"),
        rx.table.cell(rx.text(str(row["pe_ntm"]), color=pe_color, font_weight="bold")),
        rx.table.cell(f"${row['fcf_share']}"),
    )


def portfolio_page():
    return rx.vstack(
        rx.heading("Active Holdings"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Ticker"),
                    rx.table.column_header_cell("Shares"),
                    rx.table.column_header_cell("Price"),
                    rx.table.column_header_cell("Value"),
                    rx.table.column_header_cell("PE NTM"),
                    rx.table.column_header_cell("FCF/Share"),
                )
            ),
            rx.table.body(
                rx.foreach(State.holdings, row_item)
            ),
            width="100%"
        ),
        on_mount=State.load_data,
        padding="5"
    )
