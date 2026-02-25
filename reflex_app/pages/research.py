import reflex as rx
from reflex_app.components.sidebar import sidebar
from reflex_app.components.topbar import topbar
from reflex_app.state import State

def research_page() -> rx.Component:
    return rx.box(
        # Sidebar
        sidebar(active_page="research"),
        
        # Main Content
        rx.el.div(
            topbar(),
            rx.el.div(
                rx.el.div(
                    # Header for Selected Stock
                    rx.flex(
                        rx.box(
                            rx.flex(
                                rx.heading("Apple Inc. (AAPL)", class_name="text-3xl font-extrabold text-slate-900 dark:text-white"),
                                rx.html('<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-primary/10 text-primary border border-primary/20">Technology</span>'),
                                class_name="flex items-center gap-3 mb-1"
                            ),
                            rx.text("Real-time AI analysis & sentiment tracking based on global news sources.", class_name="text-slate-500 dark:text-slate-400 text-sm"),
                        ),
                        rx.flex(
                            rx.el.button(
                                rx.html('<span class="material-icons-round text-sm">show_chart</span>'),
                                " Technicals",
                                class_name="px-4 py-2 bg-slate-800 border border-slate-700 text-slate-300 rounded-lg text-sm font-semibold shadow-sm hover:bg-slate-700 transition-colors flex items-center gap-2"
                            ),
                            rx.el.button(
                                rx.html('<span class="material-icons-round text-sm">auto_awesome</span>'),
                                " AI Report",
                                class_name="px-4 py-2 bg-primary text-white rounded-lg text-sm font-bold shadow-lg shadow-primary/30 hover:bg-blue-600 transition-colors flex items-center gap-2"
                            ),
                            class_name="flex gap-2"
                        ),
                        class_name="flex flex-col md:flex-row md:items-center justify-between gap-4"
                    ),
                    
                    # Grid Layout
                    rx.box(
                        # Left Column: Sentiment Gauge & Stats
                        rx.box(
                            create_sentiment_card(),
                            create_quick_stats(),
                            class_name="lg:col-span-1 flex flex-col gap-6"
                        ),
                        
                        # Right Column: AI Summary
                        rx.box(
                            create_ai_summary(),
                            class_name="lg:col-span-2 flex flex-col"
                        ),
                        
                        class_name="grid grid-cols-1 lg:grid-cols-3 gap-6"
                    ),
                    
                    # Bottom Section: Headlines
                    create_headlines_section(),
                    
                    class_name="max-w-7xl mx-auto space-y-6"
                ),
                class_name="flex-1 overflow-y-auto p-8"
            ),
            class_name="flex-1 flex flex-col h-screen overflow-hidden min-w-0"
        ),
        
        class_name="flex h-screen w-screen overflow-hidden bg-[#101922] text-white",
        style={"fontFamily": "Inter, system-ui, sans-serif"}
    )


def create_sentiment_card() -> rx.Component:
    return rx.box(
        rx.html('<div class="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-emerald-500/10 to-transparent transition-colors"></div>'),
        rx.box(
            rx.heading("AI Sentiment Score", class_name="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6"),
            # Gauge Viz
            rx.html('''
                <div class="relative w-48 h-24 mx-auto mb-4 overflow-hidden">
                    <div class="absolute bottom-0 left-0 w-full h-full rounded-t-full bg-slate-700 border-[16px] border-b-0 border-slate-700/50 box-border"></div>
                    <div class="absolute bottom-0 left-0 w-full h-full rounded-t-full border-[16px] border-b-0 border-emerald-500 box-border origin-bottom transform" style="transform: rotate(15deg);"></div>
                    <div class="absolute bottom-0 left-1/2 w-1 h-24 bg-white origin-bottom transform -translate-x-1/2 rotate-12 transition-transform duration-1000 ease-out z-20"></div>
                    <div class="absolute bottom-0 left-1/2 w-4 h-4 bg-white rounded-full -translate-x-1/2 translate-y-1/2 z-30"></div>
                </div>
            '''),
            rx.box("0.65", class_name="text-4xl font-black text-white mb-1"),
            rx.box("Bullish", class_name="text-emerald-500 font-bold text-lg mb-4"),
            rx.box("Sentiment is strictly positive compared to the sector average of 0.42.", class_name="text-xs text-slate-400 leading-relaxed px-4"),
            class_name="relative z-10 text-center"
        ),
        class_name="bg-slate-800/50 rounded-2xl p-6 shadow-sm border border-slate-800 relative overflow-hidden group"
    )


def create_quick_stats() -> rx.Component:
    return rx.box(
        rx.box(
            rx.box("News Volume", class_name="text-xs text-slate-400 mb-1"),
            rx.html('<div class="text-xl font-bold text-white flex items-center gap-1">High <span class="material-icons-round text-primary text-base">bar_chart</span></div>'),
            class_name="bg-slate-800/50 rounded-xl p-4 shadow-sm border border-slate-800"
        ),
        rx.box(
            rx.box("Analyst Rating", class_name="text-xs text-slate-400 mb-1"),
            rx.html('<div class="text-xl font-bold text-white flex items-center gap-1">Buy <span class="material-icons-round text-emerald-500 text-base">check_circle</span></div>'),
            class_name="bg-slate-800/50 rounded-xl p-4 shadow-sm border border-slate-800"
        ),
        class_name="grid grid-cols-2 gap-4"
    )


def create_ai_summary() -> rx.Component:
    return rx.box(
        rx.html('<div class="absolute -right-10 -top-10 w-40 h-40 bg-primary/10 rounded-full blur-3xl"></div>'),
        rx.flex(
            rx.html('<div class="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-500/30"><span class="material-icons-round text-white">psychology</span></div>'),
            rx.box(
                rx.html('<h3 class="text-lg font-bold text-white flex items-center gap-2">SmartFolio AI Summary <span class="px-2 py-0.5 rounded text-[10px] bg-indigo-900/30 text-indigo-400 font-bold uppercase">Updated 10m ago</span></h3>'),
            ),
            class_name="flex items-start gap-4 relative z-10 mb-4"
        ),
        rx.box(
            rx.html('<p><span class="font-semibold text-white">Bottom Line:</span> SmartFolio AI detects a strong <span class="text-emerald-500 font-bold">bullish trend</span> for AAPL, primarily driven by leaked specifications of the upcoming Vision Pro headset and stronger-than-expected services revenue projections from major institutional analysts.</p>'),
            rx.html('<p>Market sentiment has shifted positively over the last 24 hours despite broader sector volatility. Key risk factors mentioned in minority reports include potential supply chain constraints in East Asia, though impact is currently assessed as low.</p>'),
            class_name="space-y-4 text-slate-300 leading-relaxed text-sm md:text-base pl-14"
        ),
        rx.flex(
            rx.html('<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-slate-700/50 text-slate-400 text-xs font-medium">#VisionPro</span>'),
            rx.html('<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-slate-700/50 text-slate-400 text-xs font-medium">#EarningsPreview</span>'),
            rx.html('<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-slate-700/50 text-slate-400 text-xs font-medium">#TechRally</span>'),
            class_name="mt-6 pl-14 flex flex-wrap gap-2"
        ),
        class_name="bg-slate-800/50 rounded-2xl p-6 shadow-sm border border-slate-800 h-full relative overflow-hidden"
    )


def create_headlines_section() -> rx.Component:
    news_items = [
        {"source": "Bloomberg", "impact": "High Impact", "impact_class": "bg-rose-100 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-200 dark:border-rose-500/20", "dot_color": "bg-rose-500", "title": "Apple announces revised release schedule for upcoming AR wearables", "excerpt": "Sources close to the matter indicate a slight delay in the Q4 shipment targets, potentially affecting holiday revenue guidance...", "time": "2 hours ago", "sentiment": "-0.4", "sentiment_class": "text-rose-500", "icon": "thumb_down"},
        {"source": "Reuters", "impact": "Med Impact", "impact_class": "bg-orange-100 dark:bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-200 dark:border-orange-500/20", "dot_color": "bg-orange-500", "title": "Analyst Upgrades: Morgan Stanley raises price target to $210", "excerpt": "Citigroup and Morgan Stanley have both issued notes to investors highlighting the robust services growth in the last quarter...", "time": "4 hours ago", "sentiment": "+0.8", "sentiment_class": "text-emerald-500", "icon": "thumb_up"},
        {"source": "TechCrunch", "impact": "Low Impact", "impact_class": "bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-600", "dot_color": "bg-slate-400", "title": "Apple TV+ secures rights to new major league sports package", "excerpt": "Expansion into live sports continues as the streaming service adds more exclusive content to bolster subscription numbers...", "time": "6 hours ago", "sentiment": "0.1", "sentiment_class": "text-slate-500", "icon": "remove"},
    ]
    
    return rx.box(
        rx.flex(
            rx.heading("Recent Analysis & Headlines", class_name="text-lg font-bold text-white"),
            rx.flex(
                rx.el.button("View All News", class_name="text-xs font-semibold text-primary hover:text-primary/80 transition-colors"),
                class_name="flex gap-2"
            ),
            class_name="flex items-center justify-between"
        ),
        rx.box(
            *[create_news_card(item) for item in news_items],
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        ),
        class_name="space-y-4"
    )


def create_news_card(item: dict) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.html(f'<span class="w-1.5 h-1.5 rounded-full {item["dot_color"]}"></span>'),
                rx.text(item["source"], class_name="text-xs font-semibold text-slate-400 uppercase"),
                class_name="flex items-center gap-2"
            ),
            rx.html(f'<span class="px-2 py-0.5 rounded text-[10px] font-bold {item["impact_class"]} border">{item["impact"]}</span>'),
            class_name="flex items-start justify-between mb-3"
        ),
        rx.heading(item["title"], class_name="font-bold text-slate-100 mb-2 group-hover:text-primary transition-colors"),
        rx.text(item["excerpt"], class_name="text-xs text-slate-400 line-clamp-3 mb-4 flex-1"),
        rx.flex(
            rx.text(item["time"], class_name="text-[10px] text-slate-400"),
            rx.html(f'<div class="flex gap-1"><span class="material-icons-round text-slate-300 text-sm">{item["icon"]}</span><span class="text-[10px] font-bold {item["sentiment_class"]}">{item["sentiment"]}</span></div>'),
            class_name="flex items-center justify-between mt-auto pt-3 border-t border-slate-700/50"
        ),
        class_name="bg-slate-800/50 rounded-xl p-5 shadow-sm border border-slate-800 hover:border-primary/50 transition-colors cursor-pointer flex flex-col h-full group"
    )
