import reflex as rx
from reflex_app.state import State

def topbar() -> rx.Component:
    return rx.el.header(
        # ── Search ──────────────────────────────────────────────────
        rx.el.div(
            rx.el.div(
                rx.icon(tag="search", size=15, class_name="text-slate-400"),
                class_name="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none flex items-center",
            ),
            rx.el.input(
                placeholder="Search tickers (e.g., AAPL, TSLA)...",
                value=State.search_ticker,
                on_change=State.set_search_ticker,
                class_name=(
                    "w-full pl-10 pr-14 py-2 text-sm rounded-lg "
                    "bg-slate-800 text-slate-100 placeholder-slate-500 "
                    "border border-slate-700 outline-none "
                    "focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                ),
            ),
            rx.el.div(
                rx.el.span(
                    "⌘K",
                    class_name="text-slate-500 text-xs border border-slate-600 rounded px-1.5 py-0.5",
                ),
                class_name="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none",
            ),
            class_name="relative w-80",
        ),

        # ── Actions ─────────────────────────────────────────────────
        rx.el.div(
            rx.el.div(
                rx.el.span(class_name="w-2 h-2 rounded-full bg-green-400 animate-pulse inline-block"),
                rx.el.span("Market Open", class_name="text-sm text-slate-400"),
                class_name="flex items-center gap-2",
            ),
            rx.el.button(
                rx.icon(tag="moon", size=18, class_name="text-slate-400"),
                class_name="p-2 hover:text-blue-400 transition-colors rounded-lg hover:bg-slate-800",
            ),
            class_name="flex items-center gap-4",
        ),

        class_name=(
            "h-16 flex items-center justify-between px-8 shrink-0 "
            "bg-[#101922]/80 backdrop-blur-sm border-b border-slate-800"
        ),
    )
