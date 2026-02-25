import reflex as rx
from reflex_app.state import State
from reflex_app.components.sidebar import sidebar
from reflex_app.components.topbar import topbar
from reflex_app.components.kpi_cards import kpi_cards_grid
from reflex_app.components.add_transaction_modal import add_transaction_modal
import plotly.graph_objects as go


# ── Chart ──────────────────────────────────────────────────────────────────────

def portfolio_chart() -> rx.Component:
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#94a3b8", "family": "Inter, sans-serif"},
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        legend={"orientation": "h", "y": 1.1},
        xaxis={"gridcolor": "rgba(255,255,255,0.05)", "showgrid": True, "zeroline": False},
        yaxis={"gridcolor": "rgba(255,255,255,0.05)", "showgrid": True, "zeroline": False},
    )
    fig.add_trace(go.Scatter(
        y=[100, 105, 102, 112, 118, 115, 128, 136],
        name="My Portfolio",
        line={"color": "#2b8cee", "width": 3},
        fill="tozeroy",
        fillcolor="rgba(43,140,238,0.07)",
    ))
    fig.add_trace(go.Scatter(
        y=[100, 101, 103, 104, 106, 105, 108, 111],
        name="SPY Benchmark",
        line={"color": "#475569", "width": 2, "dash": "dot"},
    ))
    return rx.plotly(data=fig, height="300px", width="100%")


from reflex_app.state import State, RecentActivity


# ── Activity table ─────────────────────────────────────────────────────────────

def activity_row(item: RecentActivity) -> rx.Component:
    """Renderiza una fila de actividad reciente."""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.div(
                    rx.el.span(item["ticker"][0], class_name="text-slate-300 font-bold text-xs"),
                    class_name="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0",
                ),
                rx.el.span(item["ticker"], class_name="font-medium text-white text-sm"),
                class_name="flex items-center gap-2",
            ),
            class_name="px-6 py-3",
        ),
        rx.el.td(
            rx.el.span(
                item["action"],
                class_name=rx.cond(
                    item["action"] == "BUY",
                    "text-xs font-bold px-2 py-0.5 rounded bg-green-900/30 text-green-400",
                    "text-xs font-bold px-2 py-0.5 rounded bg-red-900/30 text-red-400",
                )
            ),
            class_name="px-6 py-3",
        ),
        rx.el.td(rx.el.span(item["qty"], class_name="text-slate-400 text-sm"), class_name="px-6 py-3"),
        rx.el.td(rx.el.span(item["price"], class_name="font-mono text-white text-sm"), class_name="px-6 py-3"),
        rx.el.td(rx.el.span(item["date"], class_name="text-slate-500 text-xs"), class_name="px-6 py-3 text-right"),
        class_name="hover:bg-slate-800/30 transition-colors border-b border-slate-800/50",
    )


def recent_activity() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3("Recent Activity", class_name="font-bold text-white"),
            rx.el.a("View All", href="/portfolio", class_name="text-xs text-blue-400 hover:text-blue-300 font-medium"),
            class_name="flex items-center justify-between px-6 py-4 border-b border-slate-800",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        *[rx.el.th(h, class_name="px-6 py-3 text-left text-xs font-medium text-slate-400 whitespace-nowrap")
                          for h in ["Ticker", "Action", "Quantity", "Price", "Date"]],
                    ),
                    class_name="bg-slate-800/50",
                ),
                rx.el.tbody(
                    rx.cond(
                        State.recent_activity.length() > 0,
                        rx.foreach(State.recent_activity, activity_row),
                        rx.el.tr(
                            rx.el.td(
                                rx.el.p("No transactions yet", class_name="text-slate-400 text-sm text-center py-8"),
                                colspan="5",
                            )
                        )
                    )
                ),
                class_name="w-full text-left text-sm",
            ),
            class_name="overflow-x-auto",
        ),
        class_name="bg-[#18222c] rounded-xl border border-slate-800 shadow-sm flex flex-col lg:col-span-2",
    )


# ── AI Summary ─────────────────────────────────────────────────────────────────

def ai_item(icon_tag: str, icon_color: str, title: str, body: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(tag=icon_tag, size=14, class_name=f"{icon_color} shrink-0 mt-0.5"),
            rx.el.p(
                rx.el.strong(title + ": ", class_name="text-white"),
                body,
                class_name="text-sm text-slate-300 leading-relaxed",
            ),
            class_name="flex items-start gap-3",
        ),
        class_name="p-3 bg-white/5 rounded-lg border border-white/10",
    )


def ai_summary() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(tag="bot", size=18, class_name="text-blue-400"),
            rx.el.h3("AI Market Summary", class_name="font-bold text-white"),
            class_name="flex items-center gap-2 mb-4",
        ),
        rx.el.div(
            ai_item("trending-up", "text-green-400", "Tech Rally",
                    "Market reacting positively to CPI data. Semiconductors leading."),
            ai_item("triangle-alert", "text-yellow-400", "Energy Volatility",
                    "Watch for volatility due to geopolitical tensions."),
            ai_item("info", "text-blue-400", "Upcoming Earnings",
                    "Key holdings (MSFT, GOOGL) reporting next week."),
            class_name="flex flex-col gap-3 flex-1",
        ),
        rx.el.div(
            rx.el.span("Updated 15m ago", class_name="text-xs text-slate-500"),
            rx.el.div(
                rx.el.span("Full Report", class_name="text-xs text-blue-400"),
                rx.icon(tag="arrow-right", size=12, class_name="text-blue-400"),
                class_name="flex items-center gap-1 cursor-pointer",
            ),
            class_name="flex items-center justify-between pt-4 border-t border-white/10 mt-4",
        ),
        class_name=(
            "bg-gradient-to-b from-slate-900 to-slate-800 rounded-xl "
            "border border-slate-700 p-6 shadow-sm flex flex-col lg:col-span-1"
        ),
    )


# ── Page ───────────────────────────────────────────────────────────────────────

def dashboard_page() -> rx.Component:
    return rx.box(
        # ── Left: Sidebar ───────────────────────────────────────────
        sidebar(active_page="dashboard"),

        # ── Right: Main area ────────────────────────────────────────
        rx.el.div(
            topbar(),
            # Scrollable content
            rx.el.div(
                rx.el.div(
                    # Page header
                    rx.el.div(
                        rx.el.div(
                            rx.el.h1("Dashboard Overview", class_name="text-2xl font-bold text-white"),
                            rx.el.p(
                                "Welcome back, Nico. Here's your portfolio performance today.",
                                class_name="text-slate-400 text-sm mt-1",
                            ),
                        ),
                        add_transaction_modal(),
                        class_name="flex items-end justify-between",
                    ),

                    # KPI cards
                    kpi_cards_grid(),

                    # Chart
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.h2("Portfolio Performance", class_name="text-lg font-bold text-white"),
                                rx.el.p("vs S&P 500 (SPY)", class_name="text-sm text-slate-400"),
                            ),
                            rx.el.div(
                                *[rx.el.button(
                                    lbl,
                                    class_name=(
                                        "px-3 py-1 text-xs font-medium rounded-md transition-colors "
                                        + ("bg-slate-700 text-white shadow-sm" if lbl == "1M"
                                           else "text-slate-400 hover:text-white")
                                    ),
                                ) for lbl in ["1D", "1W", "1M", "YTD", "ALL"]],
                                class_name="flex items-center gap-0.5 bg-slate-800/50 p-1 rounded-lg",
                            ),
                            class_name="flex items-center justify-between mb-4",
                        ),
                        portfolio_chart(),
                        class_name="bg-[#18222c] rounded-xl border border-slate-800 p-6 shadow-sm",
                    ),

                    # Bottom grid
                    rx.el.div(
                        recent_activity(),
                        ai_summary(),
                        class_name="grid grid-cols-1 lg:grid-cols-3 gap-6",
                    ),

                    # Footer
                    rx.el.p(
                        "© 2025 SmartFolio. All rights reserved.",
                        class_name="text-center text-xs text-slate-600 mt-8 mb-4",
                    ),

                    class_name="max-w-7xl mx-auto space-y-6",
                ),
                class_name="flex-1 overflow-y-auto p-8",
            ),
            class_name="flex-1 flex flex-col h-screen overflow-hidden min-w-0",
        ),

        on_mount=State.load_data,
        class_name="flex h-screen w-screen overflow-hidden bg-[#101922] text-white",
        style={"fontFamily": "Inter, system-ui, sans-serif"},
    )
