import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ----------------------------
# Load dataset
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv", parse_dates=["Date"])
    return df

df = load_data()

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("Filter Data")
region_filter = st.sidebar.multiselect(
    "Select Region:", 
    df["Region"].unique(), 
    default=df["Region"].unique()
)

product_filter = st.sidebar.multiselect(
    "Select Product:", 
    df["Product"].unique(), 
    default=df["Product"].unique()
)

date_filter = st.sidebar.date_input(
    "Select Date Range:", 
    [df["Date"].min(), df["Date"].max()]
)

# Apply filters safely
df_filtered = df[
    (df["Region"].isin(region_filter)) &
    (df["Product"].isin(product_filter)) &
    (df["Date"].between(pd.to_datetime(date_filter[0]), pd.to_datetime(date_filter[1])))
]

# ----------------------------
# KPIs
# ----------------------------
total_sales = df_filtered["Sales"].sum()
total_quantity = df_filtered["Quantity"].sum()
avg_order_value = total_sales / total_quantity if total_quantity > 0 else 0

st.title("📊 Interactive Sales Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Quantity", f"{total_quantity:,}")
col3.metric("Avg. Order Value", f"${avg_order_value:,.2f}")

# ----------------------------
# Charts
# ----------------------------

# Sales over time
sales_over_time = df_filtered.groupby("Date")["Sales"].sum().reset_index()
fig_time = px.line(sales_over_time, x="Date", y="Sales", title="Sales Over Time", markers=True)
st.plotly_chart(fig_time, use_container_width=True)

# Sales by region
fig_region = px.bar(
    df_filtered.groupby("Region")["Sales"].sum().reset_index(),
    x="Region", y="Sales", title="Sales by Region", text_auto=True
)
st.plotly_chart(fig_region, use_container_width=True)

# Sales by product
fig_product = px.pie(
    df_filtered, names="Product", values="Sales", title="Sales Distribution by Product"
)
st.plotly_chart(fig_product, use_container_width=True)

# ----------------------------
# Sankey Diagram (Region → Product → Sales)
# ----------------------------
st.subheader("🔗 Sales Flow (Region → Product)")

# Build Sankey data
regions = list(df_filtered["Region"].unique())
products = list(df_filtered["Product"].unique())

labels = regions + products
region_idx = {region: i for i, region in enumerate(regions)}
product_idx = {prod: len(regions) + i for i, prod in enumerate(products)}

sources, targets, values = [], [], []
for _, row in df_filtered.iterrows():
    sources.append(region_idx[row["Region"]])
    targets.append(product_idx[row["Product"]])
    values.append(row["Sales"])

fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values
    )
)])
fig_sankey.update_layout(title_text="Sales Flow: Region to Product", font_size=12)
st.plotly_chart(fig_sankey, use_container_width=True)

# ----------------------------
# Word Cloud (Top Products by Sales)
# ----------------------------
st.subheader("☁ Product Word Cloud")

word_freq = df_filtered.groupby("Product")["Sales"].sum().to_dict()
if word_freq:
    wc = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_freq)
    fig_wc, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig_wc)
else:
    st.info("No data available for Word Cloud.")

# ----------------------------
# Show filtered data
# ----------------------------
st.subheader("Filtered Sales Data")
st.dataframe(df_filtered)
