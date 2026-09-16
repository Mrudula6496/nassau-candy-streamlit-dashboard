
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Nassau Candy Sales & Profit Dashboard",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Theme / CSS
# -----------------------------
NAVY = "#151F78"
ORANGE = "#F28C28"
BLUE = "#2196F3"
WHITE = "#FFFFFF"
LIGHT_BG = "#F5F7FA"
TEXT = "#1F2937"

st.markdown(
    f"""
    <style>
        .stApp {{
            background: {NAVY};
        }}

        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 1.2rem;
            max-width: 1450px;
        }}

        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
            color: {WHITE};
        }}

        [data-testid="stSidebar"] {{
            background: #10185F;
        }}

        [data-testid="stSidebar"] * {{
            color: {WHITE};
        }}

        .dashboard-title {{
            background: {WHITE};
            border-left: 6px solid {ORANGE};
            border-radius: 12px;
            padding: 14px 20px;
            margin-bottom: 12px;
        }}

        .dashboard-title h1 {{
            color: {TEXT};
            margin: 0;
            font-size: 28px;
        }}

        .dashboard-title p {{
            color: #667085;
            margin: 4px 0 0 0;
            font-size: 14px;
        }}

        .kpi-card {{
            background: {WHITE};
            border-left: 6px solid {ORANGE};
            border-radius: 12px;
            padding: 13px 15px;
            min-height: 105px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        }}

        .kpi-label {{
            color: #667085;
            font-size: 13px;
            margin-top: 4px;
        }}

        .kpi-value {{
            color: {TEXT};
            font-size: 28px;
            font-weight: 700;
            line-height: 1.1;
        }}

        .section-note {{
            color: #D6D9EA;
            font-size: 12px;
            margin-top: 5px;
        }}

        .stDataFrame {{
            background: white;
            border-radius: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Load data
# -----------------------------
DATA_FILE = "nassau_candy.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0)
    df["Gross_Profit"] = pd.to_numeric(df["Gross_Profit"], errors="coerce").fillna(0)
    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0)
    df["Units"] = pd.to_numeric(df["Units"], errors="coerce").fillna(0)
    df["Order Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%B")
    return df

df = load_data()

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.title("Dashboard Filters")

years = sorted(df["Order Year"].dropna().unique().tolist())
selected_years = st.sidebar.multiselect(
    "Order Year",
    years,
    default=years,
)

regions = sorted(df["Region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions,
)

ship_modes = sorted(df["Ship Mode"].dropna().unique().tolist())
selected_ship_modes = st.sidebar.multiselect(
    "Ship Mode",
    ship_modes,
    default=ship_modes,
)

divisions = sorted(df["Division"].dropna().unique().tolist())
selected_divisions = st.sidebar.multiselect(
    "Division",
    divisions,
    default=divisions,
)

filtered = df[
    df["Order Year"].isin(selected_years)
    & df["Region"].isin(selected_regions)
    & df["Ship Mode"].isin(selected_ship_modes)
    & df["Division"].isin(selected_divisions)
].copy()

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="dashboard-title">
        <h1>🍫 Nassau Candy — Sales & Profit Analysis</h1>
        <p>Interactive dashboard based on Order Date and reliable business metrics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# KPI calculations
# -----------------------------
total_cost = filtered["Cost"].sum()
total_profit = filtered["Gross_Profit"].sum()
total_sales = filtered["Sales"].sum()
total_units = filtered["Units"].sum()
total_orders = filtered["Order ID"].nunique()

def money(value):
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value/1_000:.0f}K"
    return f"${value:,.0f}"

def number(value):
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value/1_000:.0f}K"
    return f"{value:,.0f}"

kpis = [
    ("Total Cost", money(total_cost)),
    ("Total Gross Profit", money(total_profit)),
    ("Total Sales", money(total_sales)),
    ("Total Units Sold", number(total_units)),
    ("Total Orders", number(total_orders)),
]

cols = st.columns(5)
for col, (label, value) in zip(cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# -----------------------------
# Plotly theme helper
# -----------------------------
def style_fig(fig, height=320):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(color=TEXT),
        title_font=dict(size=17, color=TEXT),
        legend=dict(font=dict(color=TEXT)),
    )
    return fig

# -----------------------------
# Row 1: Monthly Sales + Ship Mode + Orders by Ship Mode
# -----------------------------
left, center, right = st.columns([1.65, 0.9, 1.0])

month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

monthly_sales = (
    filtered.groupby("Month Name", as_index=False)["Sales"]
    .sum()
)
monthly_sales["Month Name"] = pd.Categorical(
    monthly_sales["Month Name"], categories=month_order, ordered=True
)
monthly_sales = monthly_sales.sort_values("Month Name")

with left:
    fig = px.line(
        monthly_sales,
        x="Month Name",
        y="Sales",
        markers=True,
        title="Monthly Sales Trend",
    )
    fig.update_traces(line=dict(color=BLUE, width=3), marker=dict(color=BLUE, size=7))
    fig.update_yaxes(title=None, tickformat=".2s")
    fig.update_xaxes(title=None)
    st.plotly_chart(style_fig(fig, 310), use_container_width=True)

with center:
    ship_sales = (
        filtered.groupby("Ship Mode", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=True)
    )
    fig = px.bar(
        ship_sales,
        x="Sales",
        y="Ship Mode",
        orientation="h",
        title="Sales by Ship Mode",
    )
    fig.update_traces(marker_color=BLUE)
    fig.update_xaxes(title=None, tickformat=".2s")
    fig.update_yaxes(title=None)
    st.plotly_chart(style_fig(fig, 310), use_container_width=True)

with right:
    ship_orders = (
        filtered.groupby("Ship Mode", as_index=False)["Order ID"]
        .nunique()
        .rename(columns={"Order ID": "Orders"})
    )
    fig = px.pie(
        ship_orders,
        names="Ship Mode",
        values="Orders",
        hole=0.55,
        title="Orders by Ship Mode",
    )
    fig.update_traces(textposition="outside", textinfo="value+percent")
    st.plotly_chart(style_fig(fig, 310), use_container_width=True)

# -----------------------------
# Row 2: Table + Map + Monthly Gross Profit
# -----------------------------
left, middle, right = st.columns([1.45, 1.0, 1.15])

with left:
    table_df = (
        filtered[
            ["Product_Name", "Product ID", "City", "Order Date", "Sales", "Gross_Profit"]
        ]
        .sort_values("Order Date", ascending=False)
        .head(15)
        .copy()
    )
    table_df["Order Date"] = table_df["Order Date"].dt.strftime("%b %d, %Y")
    table_df["Sales"] = table_df["Sales"].round(2)
    table_df["Gross_Profit"] = table_df["Gross_Profit"].round(2)
    table_df.columns = [
        "Product Name", "Product ID", "City", "Order Date", "Sales", "Gross Profit"
    ]
    st.markdown("### Order Details")
    st.dataframe(table_df, use_container_width=True, hide_index=True, height=300)

with middle:
    st.markdown("### Gross Profit by State")
    state_profit = (
        filtered.groupby("State_Province", as_index=False)["Gross_Profit"]
        .sum()
    )
    state_profit = state_profit.sort_values("Gross_Profit", ascending=False)

    # The dataset includes mostly US states plus a small number of Canadian provinces.
    # Plotly's USA-state choropleth supports US states, so Canadian provinces are excluded here.
    state_map = state_profit[
        ~state_profit["State_Province"].isin(["Ontario", "Alberta"])
    ].copy()

    fig = px.choropleth(
        state_map,
        locations="State_Province",
        locationmode="USA-states",
        color="Gross_Profit",
        scope="usa",
        color_continuous_scale="Blues",
        hover_name="State_Province",
        title=None,
    )
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=WHITE,
        geo=dict(bgcolor=WHITE),
        coloraxis_colorbar=dict(title="Gross Profit"),
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    monthly_profit = (
        filtered.groupby("Month Name", as_index=False)["Gross_Profit"]
        .sum()
    )
    monthly_profit["Month Name"] = pd.Categorical(
        monthly_profit["Month Name"], categories=month_order, ordered=True
    )
    monthly_profit = monthly_profit.sort_values("Month Name")

    fig = px.bar(
        monthly_profit,
        x="Month Name",
        y="Gross_Profit",
        title="Monthly Gross Profit",
    )
    fig.update_traces(marker_color=BLUE)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None, tickformat=".2s")
    st.plotly_chart(style_fig(fig, 300), use_container_width=True)

# -----------------------------
# Row 3: Sales vs Profit + Top 5 Profit + Product Treemap
# -----------------------------
left, middle, right = st.columns([1.0, 1.15, 1.0])

with left:
    scatter_df = (
        filtered.groupby("Product_Name", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Gross_Profit=("Gross_Profit", "sum"),
            Units=("Units", "sum"),
            Division=("Division", "first"),
        )
    )
    fig = px.scatter(
        scatter_df,
        x="Sales",
        y="Gross_Profit",
        size="Units",
        color="Division",
        hover_name="Product_Name",
        title="Sales vs Gross Profit",
    )
    fig.update_xaxes(title="Sales", tickformat=".2s")
    fig.update_yaxes(title="Gross Profit", tickformat=".2s")
    st.plotly_chart(style_fig(fig, 320), use_container_width=True)

with middle:
    top5 = (
        filtered.groupby("Product_Name", as_index=False)["Gross_Profit"]
        .sum()
        .sort_values("Gross_Profit", ascending=False)
        .head(5)
        .sort_values("Gross_Profit", ascending=True)
    )
    fig = px.bar(
        top5,
        x="Gross_Profit",
        y="Product_Name",
        orientation="h",
        title="Top 5 Products by Gross Profit",
    )
    fig.update_traces(marker_color=BLUE)
    fig.update_xaxes(title=None, tickformat=".2s")
    fig.update_yaxes(title=None)
    st.plotly_chart(style_fig(fig, 320), use_container_width=True)

with right:
    product_sales = (
        filtered.groupby("Product_Name", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )
    fig = px.treemap(
        product_sales,
        path=["Product_Name"],
        values="Sales",
        title="Sales by Product",
        color="Sales",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=55, b=0),
        paper_bgcolor=WHITE,
        font=dict(color=TEXT),
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Footer / data note
# -----------------------------
st.markdown(
    """
    <div class="section-note">
        Note: Ship Date is intentionally not used for delivery-time KPIs because the source data contains unrealistic
        multi-year gaps between Order Date and Ship Date. All time-based analysis in this dashboard uses Order Date.
    </div>
    """,
    unsafe_allow_html=True,
)
