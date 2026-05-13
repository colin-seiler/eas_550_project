import streamlit as st
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
import pydeck as pdk
import json


st.set_page_config(layout="wide")
@st.cache_resource
def get_connection():
    load_dotenv()
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@st.cache_data
def load_geojson():
    with open("brazil-states.geojson") as f:
        return json.load(f)

@st.cache_data(ttl=3600)
def load_customer_summary():
    conn = get_connection()
    return pd.read_sql("SELECT * FROM analytics.sum_customers_zip", conn)

@st.cache_data(ttl=3600)
def load_seller_summary():
    conn = get_connection()
    return pd.read_sql("SELECT * FROM analytics.sum_sellers_zip", conn)

def reset_top_x():
    if st.session_state.tab == "Customers":
        st.session_state.top_x = 10000
    else:
        st.session_state.top_x = 1000

@st.fragment
def render_map(df, all_features, selected_features):
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_radius="total_orders",
        radius_scale=500,
        radius_min_pixels=2,
        radius_max_pixels=30,
        get_fill_color=[255, 0, 0, 80] if st.session_state.tab == "Sellers" else [0, 0, 255, 80],
        pickable=True
    )

    all_features = geojson_data["features"]
    selected_features = [f for f in all_features if f["properties"]["sigla"] in selected_states] if selected_states else all_features

    base_layer = pdk.Layer(
        "GeoJsonLayer",
        data=all_features,
        stroked=True,
        filled=True,
        get_fill_color=[255, 255, 255, 10],
        get_line_color=[255, 255, 255, 100],
        line_width_min_pixels=1
    )

    highlight_layer = pdk.Layer(
        "GeoJsonLayer",
        data=selected_features,
        stroked=False,
        filled=True,
        get_fill_color=[255, 255, 255, 60],
    )

    st.pydeck_chart(pdk.Deck(
        layers=[base_layer, highlight_layer, layer],
        initial_view_state=view_state,
        tooltip={"text": "Zip: {zip}\nOrders: {total_orders}\nAverage Price: {avg_order_price}\nAverage Shipping Price: {avg_order_freight}\nAverage Days to Ship: {avg_ship_days}\nAverage Delivery Days: {avg_delivery_days}\nAverage Late Days: {avg_late_days}"}
    ))

@st.fragment
def render_cust_chart():
    state_cust_chart = cust.groupby("state")[st.session_state.get("cust_metric", "total_orders")].agg(
        "sum" if st.session_state.get("cust_metric", "total_orders") == "total_orders" else "mean"
    ).reset_index().sort_values(st.session_state.get("cust_metric", "total_orders"), ascending=False).round(2)
    st.header('Customer Charts')
    st.bar_chart(
        state_cust_chart,
        x="state",
        y=st.session_state.get("cust_metric", "total_orders"),
        use_container_width=True,
        color="#0000FF"
    )
    metric = st.selectbox(
        "Metric",
        options=["total_orders", "avg_order_price", "avg_order_freight", "avg_delivery_days", "avg_late_days"],
        key="cust_metric"
    )

@st.fragment
def render_sell_chart():
    state_sell_chart = sell.groupby("state")[st.session_state.get("sell_metric", "total_orders")].agg(
        "sum" if st.session_state.get("sell_metric", "total_orders") == "total_orders" else "mean"
    ).reset_index().sort_values(st.session_state.get("sell_metric", "total_orders"), ascending=False).round(2)
    st.header('Seller Charts')
    st.bar_chart(
        state_sell_chart,
        x="state",
        y=st.session_state.get("sell_metric", "total_orders"),
        use_container_width=True,
        color="#FF0000"
    )
    metric = st.selectbox(
        "Metric",
        options=["total_orders", "avg_order_price", "avg_order_freight", "avg_delivery_days", "avg_late_days"],
        key="sell_metric"
    )

geojson_data = load_geojson()


if "view_state" not in st.session_state:
    st.session_state.view_state = pdk.ViewState(
        latitude=-15.0,
        longitude=-50.0,
        zoom=3
    )

view_state = st.session_state.view_state

st.title("Brazilian E-Commerce Dashboard")
if "tab" not in st.session_state:
    st.session_state.tab = "Customers"
if "top_x" not in st.session_state:
    st.session_state.top_x = 1000


df = load_customer_summary().rename(columns={"customer_zip": "zip"}) if st.session_state.tab == "Customers" else load_seller_summary().rename(columns={"seller_zip": "zip"})
cust = load_customer_summary().rename(columns={"customer_zip": "zip"})
sell = load_seller_summary().rename(columns={"seller_zip": "zip"})
base_count = df['zip'].count()
states = sorted(df["state"].dropna().unique().tolist())
df = df.nlargest(st.session_state.top_x, "total_orders")

col1, col2 = st.columns([5,3])
with col1:
    selected_states = st.pills(
        "Filter by State",
        options=states,
        selection_mode="multi",
        key="states"
    )
    if not selected_states:
        selected_states=states
    df = df[df["state"].isin(selected_states)]

    render_map(df, states, selected_states)

    sub1, sub2 = st.columns([2, 5])
    with sub1:
        st.radio("View", ["Customers", "Sellers"], key='tab', on_change=reset_top_x)

    with sub2:
        if st.session_state.tab == "Customers":
            if st.session_state.get("prev_tab") != "Customers":
                st.session_state.top_x = 5000
                st.session_state.prev_tab = "Customers"
            st.slider("Top Market Zips", min_value=5, max_value=base_count, value=5000, key='top_x')
        else:
            if st.session_state.get("prev_tab") != "Sellers":
                st.session_state.top_x = 1000
                st.session_state.prev_tab = "Sellers"
            st.slider("Top Seller Zips", min_value=5, max_value=base_count, value=1000, key='top_x')

    df = df.nlargest(st.session_state.top_x, "total_orders")

with col2:
    filtered = df[df["state"].isin(selected_states)] if selected_states else df
    state_summary = filtered.groupby("state").agg(
        total_orders=("total_orders", "sum"),
        avg_order_price=("avg_order_price", "mean"),
        avg_order_freight=("avg_order_freight", "mean"),
        avg_delivery_days=("avg_delivery_days", "mean"),
        avg_late_days=("avg_late_days", "mean")
    ).round(2).sort_values("total_orders", ascending=False).reset_index().set_index('state')
    st.dataframe(state_summary, height=650, use_container_width=True)

state_orders = df.groupby("state")["total_orders"].sum().sort_values(ascending=False).reset_index()

col3, col4 = st.columns([1,1])
with col3:
    render_cust_chart()
with col4:
    render_sell_chart()

col5, col6 = st.columns([1,1])

with col5:
    st.header("Avg Delivery Days by State")
    delivery = cust.groupby("state")["avg_delivery_days"].mean().reset_index().sort_values("avg_delivery_days", ascending=False).round(2)
    st.bar_chart(delivery, x="state", y="avg_delivery_days", use_container_width=True, color="#00AAFF")

with col6:
    st.header("Avg Freight vs Avg Order Price")
    freight = cust.groupby("state").agg(avg_order_freight=("avg_order_freight","mean"), avg_order_price=("avg_order_price","mean")).reset_index().round(2)
    st.scatter_chart(freight, x="avg_order_freight", y="avg_order_price", use_container_width=True)
