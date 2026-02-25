import reflex as rx
from reflex_app.state import State


def kpi_card(label: str, value: rx.Component, subtext: rx.Component, icon_tag: str, icon_color: str = "text-blue-400") -> rx.Component:
    return rx.el.div(
        # Decorative background icon
        rx.el.div(
            rx.icon(tag=icon_tag, size=64, class_name=f"{icon_color} opacity-10 group-hover:opacity-20 transition-opacity"),
            class_name="absolute right-1 top-1 pointer-events-none",
        ),
        # Content
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-medium text-slate-400"),
            rx.el.div(value, class_name="text-2xl font-bold text-white mt-1"),
            rx.el.div(subtext, class_name="mt-2"),
            class_name="relative z-10",
        ),
        class_name=(
            "bg-[#18222c] p-5 rounded-xl border border-slate-800 shadow-sm "
            "relative overflow-hidden group"
        ),
    )


def kpi_sentiment() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="absolute inset-0 bg-blue-500/10 pointer-events-none"),
        rx.el.div(
            rx.icon(tag="brain", size=64, class_name="text-white opacity-10"),
            class_name="absolute right-1 top-1 pointer-events-none",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span("AI Market Sentiment", class_name="text-sm font-medium text-indigo-200"),
                rx.el.span(
                    "BETA",
                    class_name="bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs px-2 py-0.5 rounded",
                ),
                class_name="flex justify-between items-start",
            ),
            rx.el.p("Bullish", class_name="text-2xl font-bold text-white mt-1"),
            rx.el.div(
                rx.el.div(class_name="h-1.5 rounded-full bg-indigo-400 w-[78%]"),
                class_name="w-full bg-slate-700 rounded-full h-1.5 mt-3",
            ),
            rx.el.p("Confidence Score: 7.8/10", class_name="text-xs text-indigo-200 mt-1"),
            class_name="relative z-10",
        ),
        class_name=(
            "bg-gradient-to-br from-indigo-900 to-slate-900 p-5 rounded-xl "
            "border border-slate-700 shadow-sm relative overflow-hidden"
        ),
    )


def kpi_cards_grid() -> rx.Component:
    return rx.el.div(
        # Total Value
        kpi_card(
            label="Total Portfolio Value",
            value=rx.el.span(
                "$",
                rx.cond(
                    State.total_portfolio_value > 0,
                    State.total_portfolio_value,
                    "0.00"
                )
            ),
            subtext=rx.el.div(
                rx.cond(
                    State.daily_pnl >= 0,
                    rx.icon(tag="trending-up", size=14, class_name="text-green-400"),
                    rx.icon(tag="trending-down", size=14, class_name="text-red-400"),
                ),
                rx.cond(
                    State.daily_pnl >= 0,
                    rx.el.span("+", State.daily_pnl, " (", State.daily_pnl_percent, "%)", class_name="text-green-400 text-sm font-medium"),
                    rx.el.span(State.daily_pnl, " (", State.daily_pnl_percent, "%)", class_name="text-red-400 text-sm font-medium"),
                ),
                class_name="flex items-center gap-1",
            ),
            icon_tag="wallet",
        ),
        # Daily P&L
        kpi_card(
            label="Daily P&L",
            value=rx.cond(
                State.daily_pnl >= 0,
                rx.el.span("+$", State.daily_pnl, class_name="text-green-400"),
                rx.el.span("$", State.daily_pnl, class_name="text-red-400"),
            ),
            subtext=rx.el.div(
                rx.cond(
                    State.daily_pnl >= 0,
                    rx.el.span(class_name="w-2 h-2 rounded-full bg-green-400 inline-block"),
                    rx.el.span(class_name="w-2 h-2 rounded-full bg-red-400 inline-block"),
                ),
                rx.el.span("vs Yesterday", class_name="text-slate-400 text-sm"),
                class_name="flex items-center gap-2",
            ),
            icon_tag="trending-up",
            icon_color="text-green-400",
        ),
        # TWR
        kpi_card(
            label="TWR Return (YTD)",
            value=rx.el.span("+", State.twr_metric, "%"),
            subtext=rx.el.span("Beating SPY by 4.2%", class_name="text-green-400 text-sm font-medium"),
            icon_tag="percent",
        ),
        # AI Sentiment
        kpi_sentiment(),
        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
    )
