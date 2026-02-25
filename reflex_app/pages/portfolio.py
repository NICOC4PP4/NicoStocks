import reflex as rx
from reflex_app.components.sidebar import sidebar
from reflex_app.components.topbar import topbar
from reflex_app.components.add_transaction_modal import add_transaction_modal
from reflex_app.state import State, Holding

def portfolio_page() -> rx.Component:
    return rx.box(
        # Sidebar
        sidebar(active_page="portfolio"),
        
        # Main Content
        rx.el.div(
            topbar(),
            rx.el.div(
                rx.el.div(
            # Header & KPI Cards
            rx.flex(
                rx.box(
                    rx.heading("Portfolio Holdings", class_name="text-2xl font-bold text-slate-900 dark:text-white"),
                    rx.text("Manage your active positions and performance metrics.", class_name="text-sm text-slate-500 dark:text-slate-400 mt-1"),
                ),
                # Summary Stats
                rx.flex(
                    rx.box(
                        rx.text("TOTAL VALUE", class_name="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide font-medium"),
                        rx.text(State.total_value, class_name="text-xl font-bold text-slate-900 dark:text-white mt-1 tabular-nums"),
                        class_name="bg-surface-light dark:bg-surface-dark border border-slate-200 dark:border-slate-800 rounded-lg p-4 flex-1 min-w-[140px] shadow-sm"
                    ),
                    rx.box(
                        rx.text("TOTAL PnL %", class_name="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide font-medium"),
                        rx.flex(
                            rx.cond(
                                State.total_pnl >= 0,
                                rx.html('<span class="material-icons text-sm">trending_up</span>'),
                                rx.html('<span class="material-icons text-sm">trending_down</span>'),
                            ),
                            rx.text(
                                rx.cond(State.total_pnl >= 0, "+", ""),
                                State.total_pnl, "%",
                                class_name="text-xl font-bold tabular-nums"
                            ),
                            class_name=rx.cond(State.total_pnl >= 0, "flex items-center gap-1 mt-1 text-emerald-500", "flex items-center gap-1 mt-1 text-rose-500")
                        ),
                        class_name="bg-surface-light dark:bg-surface-dark border border-slate-200 dark:border-slate-800 rounded-lg p-4 flex-1 min-w-[140px] shadow-sm"
                    ),
                    rx.box(
                        rx.text("TWR (ANNUAL)", class_name="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide font-medium"),
                        rx.flex(
                            rx.text(State.twr_metric, "%", class_name="text-xl font-bold tabular-nums"),
                            class_name="flex items-center gap-1 mt-1 text-blue-500"
                        ),
                        class_name="bg-surface-light dark:bg-surface-dark border border-slate-200 dark:border-slate-800 rounded-lg p-4 flex-1 min-w-[140px] shadow-sm"
                    ),
                    class_name="flex flex-wrap gap-4 w-full lg:w-auto"
                ),
                class_name="flex flex-col lg:flex-row lg:items-end justify-between gap-6 mb-8"
            ),
            
            # Controls Toolbar
            rx.flex(
                # Search & Filters
                rx.flex(
                    rx.box(
                        rx.box(
                            rx.html('<span class="material-icons text-slate-400 text-lg">search</span>'),
                            class_name="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
                        ),
                        rx.el.input(
                            type="text",
                            placeholder="Filter by ticker...",
                            value=State.search_ticker,
                            on_change=State.set_search_ticker,
                            class_name="block w-full sm:w-64 pl-10 pr-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg leading-5 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm transition-colors"
                        ),
                        class_name="relative"
                    ),
                    rx.el.select(
                        rx.el.option("All Sectors"),
                        class_name="block w-full sm:w-40 pl-3 pr-10 py-2 text-base border-slate-300 dark:border-slate-700 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-lg bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200"
                    ),
                    class_name="flex flex-col sm:flex-row gap-3 w-full sm:w-auto"
                ),
                # Action Button
                rx.flex(
                    add_transaction_modal(),
                    class_name="flex items-center gap-3 w-full sm:w-auto sm:justify-end"
                ),
                class_name="flex flex-col sm:flex-row justify-between items-center gap-4 mb-6 bg-surface-light dark:bg-surface-dark p-4 rounded-lg border border-slate-200 dark:border-slate-800 shadow-sm"
            ),
            
            # Data Grid
            rx.box(
                rx.box(
                    create_portfolio_table(),
                    class_name="overflow-x-auto"
                ),
                # Table Footer / Pagination
                rx.box(
                    rx.box(
                        rx.box(
                            rx.text("Total Holdings: ", State.holdings.length(), class_name="text-sm text-slate-700 dark:text-slate-400"),
                        ),
                        class_name="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between"
                    ),
                    class_name="bg-surface-light dark:bg-surface-dark px-4 py-3 flex items-center justify-between border-t border-slate-200 dark:border-slate-800 sm:px-6"
                ),
                class_name="bg-surface-light dark:bg-surface-dark shadow ring-1 ring-black ring-opacity-5 rounded-lg overflow-hidden border border-slate-200 dark:border-slate-800"
            ),
            class_name="max-w-7xl mx-auto space-y-6"
        ),
        class_name="flex-1 overflow-y-auto p-8"
    ),
    class_name="flex-1 flex flex-col h-screen overflow-hidden min-w-0"
),
on_mount=State.load_data,
        class_name="flex h-screen w-screen overflow-hidden bg-[#101922] text-white",
        style={"fontFamily": "Inter, system-ui, sans-serif"}
    )


def create_portfolio_table() -> rx.Component:
    return rx.el.table(
        rx.el.thead(
            rx.el.tr(
                rx.el.th(
                    rx.box(
                        "Ticker",
                        class_name="flex items-center gap-1"
                    ),
                    scope="col",
                    class_name="sticky left-0 z-10 bg-slate-50 dark:bg-[#15202b] px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider cursor-pointer hover:text-primary transition-colors group"
                ),
                rx.el.th("Shares", scope="col", class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th("Avg Cost", scope="col", class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th("Price", scope="col", class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th(
                    rx.box(
                        "Market Value",
                        class_name="flex items-center justify-end gap-1"
                    ),
                    scope="col",
                    class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"
                ),
                rx.el.th("NTM P/E", scope="col", class_name="px-6 py-3 text-center text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th("FCF/Share", scope="col", class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th("Gain/Loss %", scope="col", class_name="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider"),
                rx.el.th(rx.html('<span class="sr-only">Actions</span>'), scope="col", class_name="relative px-6 py-3"),
                class_name="bg-slate-50 dark:bg-slate-900/50"
            )
        ),
        rx.el.tbody(
            rx.foreach(State.filtered_holdings, create_portfolio_row),
            class_name="bg-surface-light dark:bg-surface-dark divide-y divide-slate-200 dark:divide-slate-800"
        ),
        class_name="min-w-full divide-y divide-slate-200 dark:divide-slate-800"
    )


def create_portfolio_row(holding: Holding) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.flex(
                rx.box(holding.ticker, class_name="h-8 w-8 rounded bg-white dark:bg-slate-700 flex items-center justify-center text-xs font-bold mr-3 border border-slate-200 dark:border-slate-600"),
                rx.box(
                    rx.box(holding.ticker, class_name="text-sm font-medium text-primary hover:underline cursor-pointer"),
                    rx.box("Equity Position", class_name="text-xs text-slate-500"),
                ),
                class_name="flex items-center"
            ),
            class_name="sticky left-0 z-10 bg-surface-light dark:bg-surface-dark px-6 py-4 whitespace-nowrap"
        ),
        rx.el.td(holding.shares, class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-slate-300 text-right tabular-nums"),
        rx.el.td(holding.avg_buy, class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400 text-right tabular-nums"),
        rx.el.td(holding.price, class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-slate-300 text-right tabular-nums font-medium"),
        rx.el.td(holding.value, class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-white text-right font-bold tabular-nums"),
        rx.el.td(
            rx.box(
                holding.pe_ntm,
                class_name=rx.cond(
                    holding.pe_ntm < 15,
                    "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300 tabular-nums",
                    rx.cond(
                        holding.pe_ntm > 25,
                        "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300 tabular-nums",
                        "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300 tabular-nums"
                    )
                )
            ),
            class_name="px-6 py-4 whitespace-nowrap text-center"
        ),
        rx.el.td(holding.fcf_share, class_name="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400 text-right tabular-nums"),
        rx.el.td(
            rx.text(
                rx.cond(holding.pnl_pct >= 0, "+", ""),
                holding.pnl_pct, "%",
                class_name=rx.cond(holding.pnl_pct >= 0, "text-emerald-600 dark:text-emerald-400 tabular-nums", "text-rose-600 dark:text-rose-400 tabular-nums")
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
        ),
        rx.el.td(
            rx.el.button(
                rx.html('<span class="material-icons text-base">more_vert</span>'),
                class_name="text-slate-400 hover:text-primary transition-colors"
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
        ),
        class_name="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
    )
