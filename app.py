import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Burger Town | Business Analytics",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown("""
<style>
    .stApp { background: #f5f7fb; }
    [data-testid="stSidebar"] { background: #101827; }
    [data-testid="stSidebar"] * { color: #eef3fb !important; }
    .block-container { padding-top: 1.6rem; padding-bottom: 2rem; }
    .hero {
        background: linear-gradient(115deg, #14243b 0%, #254e68 60%, #287c78 100%);
        padding: 1.45rem 1.7rem; border-radius: 18px; color: white;
        margin-bottom: 1.1rem;
    }
    .hero h1 { color: white; margin: 0; font-size: 2rem; }
    .hero p { color: #d7e7ef; margin: .35rem 0 0 0; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #e8edf4; padding: 16px 18px;
        border-radius: 14px; box-shadow: 0 2px 8px rgba(20,36,59,.04);
    }
    div[data-testid="stMetricLabel"] { color: #65758b; }
    div[data-testid="stMetricValue"] { color: #14243b; }
    .section-label { color: #52647a; font-size: .82rem; font-weight: 700;
                     letter-spacing: .08em; text-transform: uppercase; margin: .6rem 0; }
    .footnote { color: #718096; font-size: .8rem; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = Path(__file__).parent / "data.csv.gz"

@st.cache_data(show_spinner="Loading and preparing 300,000 sales records…")
def load_data(file_path: str) -> pd.DataFrame:
    frame = pd.read_csv(file_path, compression="gzip", parse_dates=["Order_Datetime"])
    # Derive line revenue once during loading, not on every interaction.
    frame["Revenue"] = pd.to_numeric(frame["Price"], errors="coerce").fillna(0) * \
                       pd.to_numeric(frame["Quantity"], errors="coerce").fillna(0)
    return frame

df = load_data(str(DATA_FILE))

st.markdown("""
<div class="hero">
  <h1>🍔 Burger Town | Business Overview</h1>
  <p>Sales performance • Order trends • Product mix • Outlet comparison</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar filters ----------
st.sidebar.markdown("## Dashboard filters")
min_date = df["Order_Datetime"].min().date()
max_date = df["Order_Datetime"].max().date()
date_range = st.sidebar.date_input(
    "Order date range", value=(min_date, max_date),
    min_value=min_date, max_value=max_date,
)
outlets = sorted(df["Outlet_Name"].dropna().unique().tolist())
groups = sorted(df["Group"].dropna().unique().tolist())
order_types = sorted(df["Order_Type"].dropna().unique().tolist())
settlements = sorted(df["Settlement"].dropna().unique().tolist())

selected_outlets = st.sidebar.multiselect("Outlet", outlets, default=outlets)
selected_groups = st.sidebar.multiselect("Menu category", groups, default=groups)
selected_types = st.sidebar.multiselect("Order type", order_types, default=order_types)
selected_settlements = st.sidebar.multiselect("Payment / settlement", settlements, default=settlements)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Inclusive date filtering: end date includes the full day.
mask = (
    df["Order_Datetime"].dt.date.between(start_date, end_date)
    & df["Outlet_Name"].isin(selected_outlets)
    & df["Group"].isin(selected_groups)
    & df["Order_Type"].isin(selected_types)
    & df["Settlement"].isin(selected_settlements)
)
filtered = df.loc[mask]

# A BillNo can appear on multiple rows; count distinct bills as orders.
total_revenue = filtered["Revenue"].sum()
total_orders = filtered["BillNo"].nunique()
items_sold = filtered["Quantity"].sum()
aov = total_revenue / total_orders if total_orders else 0
line_items = len(filtered)

st.markdown('<div class="section-label">Performance snapshot</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total revenue", f"₹{total_revenue:,.0f}")
k2.metric("Orders", f"{total_orders:,}")
k3.metric("Items sold", f"{items_sold:,.0f}")
k4.metric("Average order value", f"₹{aov:,.0f}")
k5.metric("Line items", f"{line_items:,}")

st.caption(
    f"Showing {line_items:,} line items across {total_orders:,} unique bills. "
    "Revenue is calculated as unit price × quantity."
)

if filtered.empty:
    st.warning("No records match these filters. Try widening the date range or selecting more filter values.")
    st.stop()

# ---------- Charts ----------
st.markdown('<div class="section-label">Sales and order trends</div>', unsafe_allow_html=True)
left, right = st.columns(2)

with left:
    trend = filtered.assign(Order_Date=filtered["Order_Datetime"].dt.date).groupby(
        "Order_Date", as_index=False
    ).agg(Revenue=("Revenue", "sum"))
    fig = px.line(trend, x="Order_Date", y="Revenue", markers=True,
                  title="Revenue over time", labels={"Order_Date": "Date", "Revenue": "Revenue (₹)"})
    fig.update_traces(line=dict(width=3), marker=dict(size=5))
    fig.update_layout(template="plotly_white", margin=dict(l=15, r=15, t=55, b=15),
                      hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

with right:
    category = filtered.groupby("Group", as_index=False).agg(
        Revenue=("Revenue", "sum"), Items=("Quantity", "sum")
    ).sort_values("Revenue", ascending=False)
    fig = px.bar(category, x="Group", y="Revenue", color="Revenue",
                 title="Revenue by menu category",
                 labels={"Group": "Category", "Revenue": "Revenue (₹)"},
                 color_continuous_scale="Teal")
    fig.update_layout(template="plotly_white", showlegend=False,
                      margin=dict(l=15, r=15, t=55, b=15), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    order_mix = filtered.groupby("Order_Type", as_index=False).agg(
        Orders=("BillNo", "nunique")
    )
    fig = px.pie(order_mix, names="Order_Type", values="Orders", hole=.58,
                 title="Orders by order type",
                 color_discrete_sequence=["#287c78", "#e49b48", "#527da8"])
    fig.update_layout(template="plotly_white", margin=dict(l=15, r=15, t=55, b=15))
    st.plotly_chart(fig, use_container_width=True)

with right:
    outlet_perf = filtered.groupby("Outlet_Name", as_index=False).agg(
        Revenue=("Revenue", "sum")
    ).sort_values("Revenue", ascending=True)
    fig = px.bar(outlet_perf, x="Revenue", y="Outlet_Name", orientation="h",
                 title="Revenue by outlet",
                 labels={"Outlet_Name": "Outlet", "Revenue": "Revenue (₹)"},
                 color="Revenue", color_continuous_scale="Teal")
    fig.update_layout(template="plotly_white", showlegend=False,
                      margin=dict(l=15, r=15, t=55, b=15), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Detail tables ----------
st.markdown('<div class="section-label">Product performance</div>', unsafe_allow_html=True)
p1, p2 = st.columns(2)
with p1:
    top_items = filtered.groupby("Item", as_index=False).agg(
        Revenue=("Revenue", "sum"), Quantity=("Quantity", "sum")
    ).sort_values("Revenue", ascending=False).head(10)
    st.markdown("**Top 10 items by revenue**")
    st.dataframe(top_items.style.format({"Revenue": "₹{:,.0f}", "Quantity": "{:,.0f}"}),
                 use_container_width=True, hide_index=True)
with p2:
    payment = filtered.groupby("Settlement", as_index=False).agg(
        Revenue=("Revenue", "sum"), Orders=("BillNo", "nunique")
    ).sort_values("Revenue", ascending=False)
    st.markdown("**Payment / settlement summary**")
    st.dataframe(payment.style.format({"Revenue": "₹{:,.0f}", "Orders": "{:,.0f}"}),
                 use_container_width=True, hide_index=True)

# Download filtered records for further analysis.
st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download filtered data (CSV)", data=csv_bytes,
                   file_name="burger_town_filtered_sales.csv", mime="text/csv")

st.markdown(
    '<p class="footnote">Data source: supplied assessment workbook. '
    'Orders are counted as distinct BillNo values; revenue is Price × Quantity. '
    'Filters apply to line items before the metrics and charts are recalculated.</p>',
    unsafe_allow_html=True
)
