import reflex as rx
from reflex_app.state import State, WatchlistItem
from reflex_app.components.sidebar import sidebar
from reflex_app.components.topbar import topbar


def watchlist_page() -> rx.Component:
    return rx.box(
        # Sidebar
        sidebar(active_page="watchlist"),
        
        # Main Content
        rx.el.div(
            topbar(),
            rx.el.div(
                rx.el.div(
            # Header
            rx.flex(
                rx.box(
                    rx.heading("Watchlist", class_name="text-2xl font-bold text-slate-900 dark:text-white"),
                    rx.text("Track potential investments and market metrics.", class_name="text-sm text-slate-500 dark:text-slate-400 mt-1"),
                ),
                class_name="mb-8"
            ),
            
            # Watchlist Table
            rx.box(
                rx.box(
                    create_watchlist_table(),
                    class_name="overflow-x-auto"
                ),
                class_name="bg-surface-light dark:bg-surface-dark shadow ring-1 ring-black ring-opacity-5 rounded-lg overflow-hidden border border-slate-200 dark:border-slate-800"
            ),
            
                    class_name="max-w-7xl mx-auto space-y-6"
                ),
                class_name="flex-1 overflow-y-auto p-8"
            ),
            class_name="flex-1 flex flex-col h-screen overflow-hidden min-w-0"
        ),
        on_mount=State.fetch_watchlist,
        class_name="flex h-screen w-screen overflow-hidden bg-[#101922] text-white",
        style={"fontFamily": "Inter, system-ui, sans-serif"}
    )


def create_watchlist_table() -> rx.Component:
    return rx.el.table(
        rx.el.thead(
            rx.el.tr(
                rx.el.th("Ticker", scope="col", class_name="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th("Price", scope="col", class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th("Day Change", scope="col", class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th("Market Cap", scope="col", class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th("NTM P/E", scope="col", class_name="px-6 py-3 text-center text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th(rx.html('<span class="sr-only">Actions</span>'), scope="col", class_name="relative px-6 py-3"),
                class_name="bg-slate-50 dark:bg-slate-900/50"
            )
        ),
        rx.el.tbody(
            rx.foreach(State.watchlist, create_watchlist_row),
            class_name="bg-surface-light dark:bg-surface-dark divide-y divide-slate-200 dark:divide-slate-800"
        ),
        class_name="min-w-full divide-y divide-slate-200 dark:divide-slate-800"
    )


def create_watchlist_row(item: WatchlistItem) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.flex(
                rx.box(item.ticker, class_name="h-8 w-8 rounded bg-white dark:bg-slate-700 flex items-center justify-center text-xs font-bold mr-3 border border-slate-200 dark:border-slate-600"),
                rx.box(
                    rx.box(item.ticker, class_name="text-sm font-medium text-primary hover:underline cursor-pointer"),
                    rx.box("Equity", class_name="text-xs text-slate-500"),
                ),
                class_name="flex items-center"
            ),
            class_name="px-6 py-4 whitespace-nowrap"
        ),
        rx.el.td(item.price, class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-slate-300 text-right tabular-nums"),
        rx.el.td(
            rx.text(
                rx.cond(item.change_pct >= 0, "+", ""),
                item.change_pct, "%",
                class_name=rx.cond(item.change_pct >= 0, "text-emerald-600 dark:text-emerald-400 tabular-nums", "text-rose-600 dark:text-rose-400 tabular-nums")
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
        ),
        rx.el.td(item.market_cap, class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400 text-right tabular-nums"),
        rx.el.td(
            rx.box(
                item.pe_ntm,
                class_name="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300 tabular-nums"
            ),
            class_name="px-6 py-4 whitespace-nowrap text-center"
        ),
        rx.el.td(
            rx.el.button(
                rx.html('<span class="material-icons text-base text-rose-500">delete</span>'),
                on_click=lambda: State.toggle_watchlist(item.ticker),
                class_name="p-2 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-lg transition-colors"
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
        ),
        class_name="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
    )
