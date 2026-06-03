import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Capacity Utilization Dashboard", layout="wide")


date_rng = pd.date_range("2025-01-01", periods=24*180, freq="h")

df = pd.DataFrame({
    "datetime": date_rng,
    "capacity_used": np.random.randint(20, 100, len(date_rng)),
    "capacity_total": 100
})

df["utilization"] = df["capacity_used"] / df["capacity_total"] * 100
df["date"] = df["datetime"].dt.date
df["hour"] = df["datetime"].dt.hour
df["month"] = df["datetime"].dt.month

season_map = {
    12:"Winter",1:"Winter",2:"Winter",
    3:"Spring",4:"Spring",5:"Spring",
    6:"Summer",7:"Summer",8:"Summer",
    9:"Fall",10:"Fall",11:"Fall"
}
df["season"] = df["month"].map(season_map)



# SIDEBAR CONTROLS


st.sidebar.title("Filters")

start_date = st.sidebar.date_input("Start Date", df["date"].min())
end_date = st.sidebar.date_input("End Date", df["date"].max())

season_filter = st.sidebar.multiselect(
    "Season",
    df["season"].unique(),
    default=df["season"].unique()
)

granularity = st.sidebar.selectbox(
    "Granularity",
    ["Hourly", "Daily"]
)

threshold = st.sidebar.slider("Alert Threshold (%)", 0, 100, 80)


# FILTER DATA


filtered = df[
    (df["date"] >= start_date) &
    (df["date"] <= end_date) &
    (df["season"].isin(season_filter))
]


# KPI CARDS


st.title("📊Ferry Capacity Utilization Dashboard")


col1, col2, col3 = st.columns(3)

col1.metric("Avg Utilization", f"{filtered['utilization'].mean():.1f}%")
col2.metric("Max Utilization", f"{filtered['utilization'].max():.1f}%")
col3.metric("Min Utilization", f"{filtered['utilization'].min():.1f}%")


# ALERTS


alerts = filtered[filtered["utilization"] > threshold]

if not alerts.empty:
    st.error(f"⚠ High utilization detected: {len(alerts)} records")
else:
    st.success("No critical overload detected")


# TIMELINE


st.subheader("📈 Ferry Capacity Utilization Timeline")

fig1 = px.line(filtered, x="datetime", y="utilization",color_discrete_sequence=["blue"])
st.plotly_chart(fig1, use_container_width=True)


# HEATMAP


st.subheader("🔥 Congestion & Idle Heatmap")

heatmap = filtered.pivot_table(
    index="date",
    columns="hour",
    values="utilization",
    aggfunc="mean"
)

fig2 = px.imshow(heatmap, aspect="RdYlGn_r")
st.plotly_chart(fig2, use_container_width=True)



# SEASONAL ANALYSIS


st.subheader("🌦 Seasonal Efficiency Comparison")

seasonal = filtered.groupby("season")["utilization"].mean().reset_index()

fig3 = px.bar(seasonal, x="season", y="utilization",color="season")
st.plotly_chart(fig3, use_container_width=True)