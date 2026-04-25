import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
import requests

st.set_page_config(page_title="PhonePe Dashboard", layout="wide")

st.title("📊 PhonePe Transaction Insights Dashboard")

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234567890",
    database="Phonepay_pulse"
)

# Load tables
agg_trans = pd.read_sql("SELECT * FROM aggregated_transaction", conn)
map_trans = pd.read_sql("SELECT * FROM map_transaction", conn)
agg_user = pd.read_sql("SELECT * FROM aggregated_user", conn)
map_user = pd.read_sql("SELECT * FROM map_user", conn)
agg_ins = pd.read_sql("SELECT * FROM aggregated_insurance", conn)
map_ins = pd.read_sql("SELECT * FROM map_insurance", conn)

# Sidebar filters
st.sidebar.header("🔍 Filters")

year = st.sidebar.selectbox("Select Year", sorted(agg_trans["year"].unique()))
state = st.sidebar.selectbox("Select State", sorted(agg_trans["state"].unique()))

filtered_trans = agg_trans[
    (agg_trans["year"] == year) &
    (agg_trans["state"] == state)
]

# KPI
total_amount = filtered_trans["transaction_amount"].sum()
total_count = filtered_trans["transaction_count"].sum()
avg_value = total_amount / total_count if total_count != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Transaction Amount", round(total_amount, 2))
col2.metric("Total Transaction Count", int(total_count))
col3.metric("Average Transaction Value", round(avg_value, 2))

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Customer Segmentation",
    "Payment Performance",
    "Geographical Insights",
    "User Engagement",
    "Insurance Insights"
])

# 1. Customer Segmentation
with tab1:
    st.header("👥 Customer Segmentation")

    customer_df = agg_trans.groupby("state")["transaction_amount"].sum().reset_index()
    customer_df = customer_df.sort_values("transaction_amount", ascending=False).head(10)

    fig1 = px.bar(
        customer_df,
        x="transaction_amount",
        y="state",
        orientation="h",
        title="Top 10 States by Customer Spending"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.info("High transaction states represent strong customer segments for marketing and business growth.")

# 2. Payment Performance
with tab2:
    st.header("💳 Payment Performance")

    category_df = filtered_trans.groupby("transaction_type")["transaction_amount"].sum().reset_index()

    fig2 = px.bar(
        category_df,
        x="transaction_type",
        y="transaction_amount",
        title=f"Payment Category Performance - {state} {year}"
    )

    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.pie(
        category_df,
        names="transaction_type",
        values="transaction_amount",
        title="Transaction Category Share"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.info("This helps identify which payment categories are most used by customers.")

# 3. Geographical Insights
with tab3:
    st.header("🌍 Geographical Insights")

    st.subheader("🗺️ India Choropleth Map - State-wise Transaction Amount")

    map_df = agg_trans.groupby("state")[["transaction_amount", "transaction_count"]].sum().reset_index()

    map_df["state"] = (
        map_df["state"]
        .str.replace("-", " ")
        .str.title()
    )

    geojson_url = "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"

    response = requests.get(geojson_url)

    if response.status_code != 200:
        st.error("Could not load India map GeoJSON.")
    else:
        india_geojson = response.json()

        fig_map = go.Figure(
            go.Choroplethmapbox(
                geojson=india_geojson,
                locations=map_df["state"],
                z=map_df["transaction_amount"],
                featureidkey="properties.NAME_1",
                colorscale="Reds",
                marker_opacity=0.75,
                marker_line_width=0.5,
                text=map_df["state"],
                customdata=map_df[["transaction_count"]],
                hovertemplate=
                    "<b>%{text}</b><br>" +
                    "Transaction Amount: ₹%{z:,.2f}<br>" +
                    "Transaction Count: %{customdata[0]:,}<br>" +
                    "<extra></extra>"
            )
        )

        fig_map.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=3.5,
            mapbox_center={"lat": 22.9734, "lon": 78.6569},
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            height=650
        )

    st.plotly_chart(fig_map, use_container_width=True)

    st.info("Darker states show higher transaction amounts. This helps identify strong and weak digital payment regions.")

# 4. User Engagement
with tab4:
    st.header("📱 User Engagement")

    brand_df = agg_user.groupby("brand")["transaction_count"].sum().reset_index()
    brand_df = brand_df.sort_values("transaction_count", ascending=False).head(10)

    fig5 = px.bar(
        brand_df,
        x="transaction_count",
        y="brand",
        orientation="h",
        title="Top 10 Mobile Brands by Users"
    )

    st.plotly_chart(fig5, use_container_width=True)

    app_df = map_user.groupby("district")["app_opens"].sum().reset_index()
    app_df = app_df.sort_values("app_opens", ascending=False).head(10)

    fig6 = px.bar(
        app_df,
        x="app_opens",
        y="district",
        orientation="h",
        title="Top 10 Districts by App Opens"
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.info("App opens show how actively users are engaging with the PhonePe platform.")

# 5. Insurance Insights
with tab5:
    st.header("🛡️ Insurance Insights")

    ins_state = agg_ins.groupby("state")["insurance_amount"].sum().reset_index()
    ins_state = ins_state.sort_values("insurance_amount", ascending=False).head(10)

    fig7 = px.bar(
        ins_state,
        x="insurance_amount",
        y="state",
        orientation="h",
        title="Top 10 States by Insurance Amount"
    )

    st.plotly_chart(fig7, use_container_width=True)

    ins_year = agg_ins.groupby("year")["insurance_amount"].sum().reset_index()

    fig8 = px.line(
        ins_year,
        x="year",
        y="insurance_amount",
        markers=True,
        title="Year-wise Insurance Growth"
    )

    st.plotly_chart(fig8, use_container_width=True)

    ins_district = map_ins.groupby("district")["insurance_amount"].sum().reset_index()
    ins_district = ins_district.sort_values("insurance_amount", ascending=False).head(10)

    fig9 = px.bar(
        ins_district,
        x="insurance_amount",
        y="district",
        orientation="h",
        title="Top 10 Districts by Insurance Amount"
    )

    st.plotly_chart(fig9, use_container_width=True)

    st.info("Insurance analysis helps identify regions with higher insurance adoption.")

conn.close()