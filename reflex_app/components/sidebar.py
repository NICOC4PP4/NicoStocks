import reflex as rx


def nav_item(icon_tag: str, label: str, href: str, active: bool = False) -> rx.Component:
    cls = (
        "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-all duration-150 cursor-pointer "
        + ("bg-blue-500/10 text-blue-400 font-semibold" if active
           else "text-slate-400 hover:bg-slate-800 hover:text-white")
    )
    return rx.el.a(
        rx.icon(tag=icon_tag, size=17),
        rx.el.span(label),
        href=href,
        class_name=cls,
    )


def sidebar(active_page: str = "dashboard") -> rx.Component:
    return rx.el.aside(
        # ── Logo ────────────────────────────────────────────────────
        rx.el.div(
            rx.el.div(
                rx.el.span("S", class_name="text-white font-bold text-lg"),
                class_name=(
                    "w-8 h-8 rounded flex items-center justify-center shrink-0 "
                    "bg-gradient-to-br from-blue-500 to-blue-700"
                ),
            ),
            rx.el.span(
                rx.el.span("Smart", class_name="text-white"),
                rx.el.span("Folio", class_name="text-blue-400"),
                class_name="text-xl font-bold tracking-tight",
            ),
            class_name="flex items-center gap-2 h-16 px-6 border-b border-slate-800 shrink-0",
        ),

        # ── Menu ────────────────────────────────────────────────────
        rx.el.div(
            rx.el.p("MENU", class_name="px-4 text-[10px] font-bold text-slate-500 tracking-widest mb-2 mt-4"),
            nav_item("layout-dashboard", "Dashboard", "/", active=active_page == "dashboard"),
            nav_item("pie-chart", "Portfolio", "/portfolio", active=active_page == "portfolio"),
            nav_item("eye", "Watchlist", "/watchlist", active=active_page == "watchlist"),
            nav_item("candlestick-chart", "Analysis", "/research", active=active_page == "research"),
            class_name="flex flex-col gap-0.5 px-3",
        ),

        # ── System ──────────────────────────────────────────────────
        rx.el.div(
            rx.el.p("SYSTEM", class_name="px-4 text-[10px] font-bold text-slate-500 tracking-widest mb-2 mt-6"),
            nav_item("settings", "Settings", "#"),
            rx.el.a(
                rx.el.div(
                    rx.icon(tag="bell", size=17, class_name="text-slate-400 shrink-0"),
                    rx.el.span("Alerts", class_name="text-sm text-slate-400"),
                    rx.el.span(class_name="flex-1"),
                    rx.el.span(
                        "3",
                        class_name="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full leading-none",
                    ),
                    class_name="flex items-center gap-3 w-full",
                ),
                href="#",
                class_name="flex items-center px-4 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-colors",
            ),
            class_name="flex flex-col gap-0.5 px-3",
        ),

        # ── Spacer ──────────────────────────────────────────────────
        rx.el.div(class_name="flex-1"),

        # ── User Footer ─────────────────────────────────────────────
        rx.el.div(
            rx.el.button(
                rx.el.div(
                    rx.el.div(
                        rx.el.span("N", class_name="text-slate-300 font-bold text-sm"),
                        class_name="w-10 h-10 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center shrink-0",
                    ),
                    rx.el.div(
                        rx.el.p("Nico", class_name="text-sm font-medium text-white truncate text-left"),
                        rx.el.p("Pro Plan", class_name="text-xs text-slate-500 truncate text-left"),
                        class_name="flex-1 min-w-0",
                    ),
                    rx.icon(tag="log-out", size=16, class_name="text-slate-400"),
                    class_name="flex items-center gap-3 w-full",
                ),
                class_name="w-full p-2 rounded-lg hover:bg-slate-800 transition-colors text-left",
            ),
            class_name="p-4 border-t border-slate-800 shrink-0",
        ),

        class_name="w-64 h-screen bg-[#18222c] flex flex-col border-r border-slate-800 shrink-0 z-20",
    )
