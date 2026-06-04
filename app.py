from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from shiny import App, reactive, render, ui


APP_DIR = Path(__file__).parent

SECTOR_COLORS = {
    "AI / ML": "#2563EB",
    "Fintech": "#14B8A6",
    "Healthcare": "#7C3AED",
    "Developer Tools": "#F59E0B",
    "Climate": "#16A34A",
    "Consumer": "#DC2626",
}

REGION_POINTS = {
    "United States": (-98, 39),
    "Europe": (12, 50),
    "India": (78, 22),
    "Canada": (-106, 56),
    "Latin America": (-60, -15),
    "Southeast Asia": (105, 12),
}


def weighted_pick(items: list[str], weights: list[int], index: int) -> str:
    total = sum(weights)
    seed = ((index * 9301 + 49297) % 233280) / 233280
    cursor = seed * total
    for item, weight in zip(items, weights):
        cursor -= weight
        if cursor <= 0:
            return item
    return items[-1]


def make_sample_data() -> pd.DataFrame:
    sectors = ["AI / ML", "Fintech", "Healthcare", "Developer Tools", "Climate", "Consumer"]
    regions = ["United States", "Europe", "India", "Canada", "Latin America", "Southeast Asia"]
    schools = ["Stanford", "MIT", "UC Berkeley", "Harvard", "CMU", "Oxford", "Waterloo", "IIT Bombay"]
    companies = ["Google", "Meta", "Amazon", "Microsoft", "Stripe", "Goldman Sachs", "Apple", "McKinsey"]
    statuses = ["Active", "Acquired", "IPO", "Closed"]
    batches = ["W20", "S20", "W21", "S21", "W22", "S22", "W23", "S23", "W24", "S24"]
    founder_names = [
        "Alex Chen",
        "Priya Shah",
        "David Kim",
        "Sara Liu",
        "Miguel Santos",
        "Nina Patel",
        "John Smith",
        "Minh Nguyen",
        "Elena Rossi",
        "Arjun Mehta",
        "Maya Johnson",
        "Hannah Lee",
        "Tom Becker",
        "Aisha Khan",
        "Kenji Tanaka",
        "Linh Tran",
        "Ravi Menon",
        "Julia Evans",
    ]
    startup_prefixes = ["Apex", "Fin", "Infra", "Medi", "Clima", "Lumen", "Rev", "Nexa", "Trust", "Flow"]
    startup_suffixes = ["AI", "lytics", "Base", "Bridge", "Grid", "Stack", "Ops", "Loop", "Cloud", "Labs"]

    rows = []
    for i in range(180):
        sector = weighted_pick(sectors, [28, 20, 17, 18, 10, 12], i + 4)
        region = weighted_pick(regions, [48, 18, 12, 9, 6, 7], i + 9)
        status = weighted_pick(statuses, [70, 17, 5, 8], i + 15)
        school = weighted_pick(schools, [23, 18, 17, 12, 10, 8, 6, 6], i + 22)
        prior_company = weighted_pick(companies, [22, 16, 14, 14, 10, 9, 8, 7], i + 31)
        rows.append(
            {
                "Startup": f"{startup_prefixes[i % len(startup_prefixes)]}{startup_suffixes[(i * 3) % len(startup_suffixes)]}",
                "Founder": founder_names[i % len(founder_names)],
                "Sector": sector,
                "Region": region,
                "Batch": batches[i % len(batches)],
                "School": school,
                "Prior Company": prior_company,
                "Outcome": status,
                "Founder Count": 1 + ((i * 7) % 4),
            }
        )
    return pd.DataFrame(rows)


DATA = make_sample_data()


def fig_html(fig: go.Figure) -> ui.HTML:
    fig.update_layout(
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#172033"),
        height=290,
    )
    return ui.HTML(fig.to_html(include_plotlyjs="cdn", full_html=False, config={"displayModeBar": False}))


def kpi_card(label: str, output_id: str, caption: str, icon: str) -> ui.Tag:
    return ui.tags.article(
        {"class": "kpi-card"},
        ui.tags.div(icon, class_="kpi-symbol"),
        ui.tags.div(
            ui.tags.span(label),
            ui.tags.strong(ui.output_text(output_id)),
            ui.tags.small(caption),
        ),
    )


def panel(title: str, subtitle: str, output_id: str, wide: bool = False, compact: bool = False) -> ui.Tag:
    classes = "panel"
    if wide:
        classes += " wide-panel"
    if compact:
        classes += " compact-panel"
    return ui.tags.article(
        {"class": classes},
        ui.tags.div(
            ui.tags.div(ui.tags.h2(title), ui.tags.p(subtitle)),
            class_="panel-header",
        ),
        ui.output_ui(output_id),
    )


app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.title("FounderRadar Shiny Dashboard"),
        ui.tags.link(rel="preconnect", href="https://cdn.plot.ly"),
        ui.tags.link(rel="stylesheet", href="styles.css"),
    ),
    ui.tags.div(
        {"class": "app-shell"},
        ui.tags.aside(
            {"class": "sidebar"},
            ui.tags.div(
                ui.tags.div("FounderRadar", class_="brand"),
                ui.tags.div("VC intelligence dashboard", class_="brand-subtitle"),
                class_="brand-block",
            ),
            ui.tags.nav(
                ui.tags.button("Overview", class_="nav-item active"),
                ui.tags.button("Founders", class_="nav-item"),
                ui.tags.button("Pipeline", class_="nav-item"),
                ui.tags.button("Compare", class_="nav-item"),
                class_="nav-list",
            ),
            ui.tags.section(
                ui.tags.div("Filters", class_="filter-title"),
                ui.input_select("batch", "Batch", ["All"] + sorted(DATA["Batch"].unique().tolist())),
                ui.input_select("sector", "Sector", ["All"] + list(SECTOR_COLORS.keys())),
                ui.input_select("region", "Region", ["All"] + sorted(DATA["Region"].unique().tolist())),
                ui.input_select("outcome", "Outcome", ["All"] + sorted(DATA["Outcome"].unique().tolist())),
                ui.input_text("search", "Search", placeholder="Founder, startup, school..."),
                ui.input_action_button("reset", "Reset filters", class_="primary-button"),
                class_="filter-block",
            ),
        ),
        ui.tags.main(
            {"class": "main"},
            ui.tags.header(
                ui.tags.div(
                    ui.tags.h1("Startup Ecosystem Overview"),
                    ui.tags.p("Explore founder, startup, and ecosystem patterns in YC-backed companies."),
                ),
                class_="topbar",
            ),
            ui.tags.section(
                kpi_card("Total startups", "kpi_startups", "Filtered companies", "▦"),
                kpi_card("Total founders", "kpi_founders", "Estimated people", "◎"),
                kpi_card("Schools", "kpi_schools", "Contributing schools", "◈"),
                kpi_card("Prior companies", "kpi_companies", "Previous employers", "▣"),
                kpi_card("Regions", "kpi_regions", "Startup locations", "◌"),
                class_="kpi-grid",
            ),
            ui.tags.section(
                panel("Global Founder / Startup Concentration", "Bubble size shows filtered startup density by region.", "map_chart", wide=True),
                panel("Top Founder Schools", "Ranked by founder count.", "school_chart"),
                panel("Sector Trends Across Batches", "Share of startups by YC batch.", "trend_chart"),
                panel("Prior Company Experience", "Previous employers feeding into YC startups.", "company_chart"),
                panel("Founder Pipeline", "School -> prior company -> sector -> outcome.", "pipeline_chart", wide=True),
                ui.tags.article(
                    {"class": "panel compact-panel"},
                    ui.tags.div(ui.tags.div(ui.tags.h2("Ecosystem Insights"), ui.tags.p("Auto-updated summary.")), class_="panel-header"),
                    ui.output_ui("insights"),
                ),
                class_="dashboard-grid",
            ),
            ui.tags.section(
                ui.tags.div(
                    ui.tags.div(ui.tags.h2("Startup / Founder Explorer"), ui.tags.p(ui.output_text("result_count"))),
                    ui.download_button("download_csv", "Export CSV", class_="secondary-button"),
                    class_="explorer-header",
                ),
                ui.output_data_frame("records_table"),
                class_="explorer-panel",
            ),
        ),
    ),
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.reset)
    def _reset_filters():
        ui.update_select("batch", selected="All")
        ui.update_select("sector", selected="All")
        ui.update_select("region", selected="All")
        ui.update_select("outcome", selected="All")
        ui.update_text("search", value="")

    @reactive.calc
    def filtered_data() -> pd.DataFrame:
        df = DATA.copy()
        if input.batch() != "All":
            df = df[df["Batch"] == input.batch()]
        if input.sector() != "All":
            df = df[df["Sector"] == input.sector()]
        if input.region() != "All":
            df = df[df["Region"] == input.region()]
        if input.outcome() != "All":
            df = df[df["Outcome"] == input.outcome()]
        query = input.search().strip().lower()
        if query:
            haystack = df[["Startup", "Founder", "School", "Prior Company", "Sector", "Region"]].astype(str).agg(" ".join, axis=1).str.lower()
            df = df[haystack.str.contains(query, regex=False)]
        return df

    @output
    @render.text
    def kpi_startups():
        return f"{filtered_data()['Startup'].nunique():,}"

    @output
    @render.text
    def kpi_founders():
        return f"{int(filtered_data()['Founder Count'].sum()):,}"

    @output
    @render.text
    def kpi_schools():
        return f"{filtered_data()['School'].nunique():,}"

    @output
    @render.text
    def kpi_companies():
        return f"{filtered_data()['Prior Company'].nunique():,}"

    @output
    @render.text
    def kpi_regions():
        return f"{filtered_data()['Region'].nunique():,}"

    @output
    @render.text
    def result_count():
        return f"Showing {len(filtered_data()):,} filtered records"

    @output
    @render.ui
    def school_chart():
        counts = filtered_data()["School"].value_counts().head(8).sort_values()
        fig = go.Figure(go.Bar(x=counts.values, y=counts.index, orientation="h", marker_color="#2563EB"))
        fig.update_xaxes(showgrid=True, gridcolor="#E6EAF2", title="")
        fig.update_yaxes(title="")
        return fig_html(fig)

    @output
    @render.ui
    def company_chart():
        counts = filtered_data()["Prior Company"].value_counts().head(8).sort_values()
        fig = go.Figure(go.Bar(x=counts.values, y=counts.index, orientation="h", marker_color="#14B8A6"))
        fig.update_xaxes(showgrid=True, gridcolor="#E6EAF2", title="")
        fig.update_yaxes(title="")
        return fig_html(fig)

    @output
    @render.ui
    def trend_chart():
        df = filtered_data()
        grouped = df.groupby(["Batch", "Sector"]).size().reset_index(name="Count")
        totals = df.groupby("Batch").size().reset_index(name="Total")
        chart = grouped.merge(totals, on="Batch", how="left")
        chart["Share"] = chart["Count"] / chart["Total"]
        fig = go.Figure()
        for sector, color in SECTOR_COLORS.items():
            sector_df = chart[chart["Sector"] == sector]
            fig.add_trace(
                go.Scatter(
                    x=sector_df["Batch"],
                    y=sector_df["Share"],
                    mode="lines",
                    stackgroup="one",
                    name=sector,
                    line=dict(width=0.5, color=color),
                    hovertemplate="%{x}<br>%{y:.0%}<extra>" + sector + "</extra>",
                )
            )
        fig.update_yaxes(tickformat=".0%", range=[0, 1], showgrid=True, gridcolor="#E6EAF2")
        fig.update_xaxes(categoryorder="array", categoryarray=sorted(DATA["Batch"].unique()))
        return fig_html(fig)

    @output
    @render.ui
    def map_chart():
        counts = filtered_data()["Region"].value_counts().reset_index()
        counts.columns = ["Region", "Count"]
        counts["lon"] = counts["Region"].map(lambda r: REGION_POINTS[r][0])
        counts["lat"] = counts["Region"].map(lambda r: REGION_POINTS[r][1])
        fig = go.Figure(
            go.Scattergeo(
                lon=counts["lon"],
                lat=counts["lat"],
                text=counts["Region"] + ": " + counts["Count"].astype(str),
                mode="markers+text",
                textposition="top center",
                marker=dict(
                    size=(counts["Count"] / counts["Count"].max() * 34 + 8) if len(counts) else [],
                    color="#2563EB",
                    opacity=0.72,
                    line=dict(color="#FFFFFF", width=1),
                ),
            )
        )
        fig.update_geos(
            projection_type="natural earth",
            showcountries=True,
            countrycolor="#D9DEE8",
            showland=True,
            landcolor="#E6EAF2",
            showocean=True,
            oceancolor="#F5F7FB",
            bgcolor="rgba(0,0,0,0)",
        )
        return fig_html(fig)

    @output
    @render.ui
    def pipeline_chart():
        df = filtered_data()
        top_schools = df["School"].value_counts().head(4).index.tolist()
        top_companies = df["Prior Company"].value_counts().head(4).index.tolist()
        top_sectors = df["Sector"].value_counts().head(4).index.tolist()
        top_outcomes = df["Outcome"].value_counts().head(3).index.tolist()
        reduced = df.assign(
            School=lambda x: x["School"].where(x["School"].isin(top_schools), "Other schools"),
            **{"Prior Company": lambda x: x["Prior Company"].where(x["Prior Company"].isin(top_companies), "Other companies")},
            Sector=lambda x: x["Sector"].where(x["Sector"].isin(top_sectors), "Other sectors"),
            Outcome=lambda x: x["Outcome"].where(x["Outcome"].isin(top_outcomes), "Other outcomes"),
        )
        stages = ["School", "Prior Company", "Sector", "Outcome"]
        labels = []
        for stage in stages:
            labels.extend(reduced[stage].drop_duplicates().tolist())
        label_index = {label: i for i, label in enumerate(labels)}
        sources, targets, values = [], [], []
        for left, right in zip(stages, stages[1:]):
            flows = reduced.groupby([left, right]).size().reset_index(name="Count")
            for _, row in flows.iterrows():
                sources.append(label_index[row[left]])
                targets.append(label_index[row[right]])
                values.append(int(row["Count"]))
        fig = go.Figure(
            go.Sankey(
                node=dict(label=labels, pad=14, thickness=14, color="#EAF2FF", line=dict(color="#D9DEE8", width=1)),
                link=dict(source=sources, target=targets, value=values, color="rgba(37,99,235,0.18)"),
            )
        )
        return fig_html(fig)

    @output
    @render.ui
    def insights():
        df = filtered_data()
        if df.empty:
            return ui.tags.ul(ui.tags.li("No records match the current filters."), class_="insight-list")
        top_sector = df["Sector"].value_counts().idxmax()
        top_school = df["School"].value_counts().idxmax()
        top_region = df["Region"].value_counts().idxmax()
        exit_rate = round((df["Outcome"].isin(["Acquired", "IPO"]).mean()) * 100)
        return ui.tags.ul(
            ui.tags.li(ui.tags.strong(top_sector), ui.tags.span(" is the largest filtered sector.")),
            ui.tags.li(ui.tags.strong(top_school), ui.tags.span(" is the most common school signal.")),
            ui.tags.li(ui.tags.strong(top_region), ui.tags.span(" has the highest concentration.")),
            ui.tags.li(ui.tags.strong(f"{exit_rate}% exit signal"), ui.tags.span(" from acquired or IPO outcomes.")),
            class_="insight-list",
        )

    @output
    @render.data_frame
    def records_table():
        return render.DataGrid(filtered_data().drop(columns=["Founder Count"]), filters=True, height=360)

    @render.download(filename="founderradar_filtered_records.csv")
    def download_csv():
        yield filtered_data().to_csv(index=False)


app = App(app_ui, server, static_assets=APP_DIR)
