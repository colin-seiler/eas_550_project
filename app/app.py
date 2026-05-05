import streamlit as st
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide")
@st.cache_resource
def get_connection():
    load_dotenv()
    return psycopg2.connect(os.getenv("DATABASE_URL"))

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
        st.session_state.top_x = 5000
    else:
        st.session_state.top_x = 1000

col1, col2 = st.columns([5,2])
with col1:
    if "tab" not in st.session_state:
        st.session_state.tab = "Customers"
    if "top_x" not in st.session_state:
        st.session_state.top_x = 1000

    df = load_customer_summary().rename(columns={"customer_zip": "zip"}) if st.session_state.tab == "Customers" else load_seller_summary().rename(columns={"seller_zip": "zip"})
    base_count = df['zip'].count()
    df = df.nlargest(st.session_state.top_x, "total_orders")
    st.title("Brazilian E-Commerce Dashboard")

    #Map work
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

    view_state = pdk.ViewState(
        latitude=df["latitude"].mean(),
        longitude=df["longitude"].mean(),
        zoom=4
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Zip: {zip}\nOrders: {total_orders}\nAverage Price: {avg_order_price}\nAverage Shipping Price: {avg_order_freight}\nAverage Days to Ship: {avg_ship_days}\nAverage Delivery Days: {avg_delivery_days}\nAverage Late Days: {avg_late_days}"}
    ))

    sub1, sub2 = st.columns([2, 5])
    #view picker
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
    st.metric("Total Orders", df["total_orders"].sum())
    st.metric("Avg Order Price", f"${df['avg_order_price'].mean():.2f}")
    st.metric("Avg Delivery Days", f"{df['avg_delivery_days'].mean():.1f} days")