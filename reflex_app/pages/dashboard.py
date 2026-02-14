import reflex as rx
from reflex_app.state import State
import plotly.express as px
import plotly.graph_objects as go

def kpi_card(title, value, subtext, color):
    return rx.card(
        rx.vstack(
            rx.text(title, font_size="0.8em", color="gray"),
            rx.text(value, font_size="2em", font_weight="bold", color=color),
            rx.text(subtext, font_size="0.8em"),
        )
    )

def plot_component():
    # Mock data para el gráfico SPY vs Portfolio
    # En prod: State.benchmark_data
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=[100, 105, 102, 110], name="Portfolio"))
    fig.add_trace(go.Scatter(y=[100, 101, 103, 104], name="S&P 500 (SPY)"))
    return rx.plotly(data=fig, height="400px")

def dashboard_page():
    return rx.vstack(
        rx.heading("SmartFolio Dashboard", size="8"),
        rx.divider(),
        rx.flex(
            kpi_card("Total Value", f"${State.total_value}", "+2.4% Today", "green"),
            kpi_card("TWR (YTD)", f"{State.twr_metric}%", "Vs SPY 8.2%", "blue"),
            kpi_card("Cash", "$1,200", "Buying Power", "gray"),
            spacing="4",
            width="100%"
        ),
        rx.box(
            plot_component(),
            width="100%",
            padding_y="4"
        ),
        on_mount=State.load_data,
        spacing="5",
        padding="5",
    )
