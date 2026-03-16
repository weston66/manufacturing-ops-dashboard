import streamlit as st
import pandas as pd
import plotly.express as px
from db import query
from alerts import check_and_alert

st.set_page_config(page_title="Manufacturing Ops Dashboard", layout="wide")
st.title("Manufacturing Ops Dashboard")

# ── Work Orders ──────────────────────────────────────────────────────────────
wo_rows = query("SELECT status, priority, qty_ordered, qty_completed, due_date FROM work_orders")
wo_df = pd.DataFrame(wo_rows)

overdue_count = 0
if not wo_df.empty:
    wo_df["due_date"] = pd.to_datetime(wo_df["due_date"])
    today = pd.Timestamp.today().normalize()
    overdue = wo_df[(wo_df["due_date"] < today) & (~wo_df["status"].str.lower().isin(["completed", "complete"]))]
    overdue_count = len(overdue)
    open_count = len(wo_df[wo_df["status"].str.lower().isin(["open", "in progress", "in_progress"])])
    total = len(wo_df)
    completed = len(wo_df[wo_df["status"].str.lower().isin(["completed", "complete"])])
    completion_rate = round(completed / total * 100, 1) if total else 0
else:
    open_count = completed = total = completion_rate = 0

# ── Inventory ────────────────────────────────────────────────────────────────
inv_rows = query("SELECT part_number, description, on_hand_qty, reorder_point, unit_cost FROM inventory")
inv_df = pd.DataFrame(inv_rows)

low_stock_parts = []
if not inv_df.empty:
    low_stock = inv_df[inv_df["on_hand_qty"] <= inv_df["reorder_point"]]
    low_stock_parts = low_stock["part_number"].tolist()
    low_stock_count = len(low_stock)
    total_inv_value = (inv_df["on_hand_qty"] * inv_df["unit_cost"]).sum()
else:
    low_stock_count = 0
    total_inv_value = 0

# ── Vendors ──────────────────────────────────────────────────────────────────
vendor_rows = query("SELECT vendor_name, on_time_rate, lead_time_days FROM vendors")
vendor_df = pd.DataFrame(vendor_rows)
avg_on_time = round(vendor_df["on_time_rate"].mean() * 100, 1) if not vendor_df.empty else 0

# ── KPI Tiles ────────────────────────────────────────────────────────────────
st.subheader("Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Open Work Orders", open_count)
col2.metric("Overdue Work Orders", overdue_count, delta=f"-{overdue_count}" if overdue_count else None, delta_color="inverse")
col3.metric("Completion Rate", f"{completion_rate}%")
col4.metric("Low Stock Parts", low_stock_count, delta=f"-{low_stock_count}" if low_stock_count else None, delta_color="inverse")
col5.metric("Avg Vendor On-Time", f"{avg_on_time}%")

st.divider()

# ── Charts ───────────────────────────────────────────────────────────────────
row1_left, row1_right = st.columns(2)

with row1_left:
    st.subheader("Work Orders by Status")
    if not wo_df.empty:
        status_counts = wo_df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.bar(status_counts, x="Status", y="Count", color="Status")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No work order data.")

with row1_right:
    st.subheader("Work Orders by Priority")
    if not wo_df.empty:
        pri_counts = wo_df["priority"].value_counts().reset_index()
        pri_counts.columns = ["Priority", "Count"]
        fig2 = px.pie(pri_counts, names="Priority", values="Count")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No work order data.")

row2_left, row2_right = st.columns(2)

with row2_left:
    st.subheader("Inventory: At-Risk Parts (On Hand vs Reorder Point)")
    if not inv_df.empty:
        inv_df["buffer"] = inv_df["on_hand_qty"] - inv_df["reorder_point"]
        at_risk = inv_df.nsmallest(15, "buffer")[["part_number", "on_hand_qty", "reorder_point"]]
        fig3 = px.bar(
            at_risk.melt(id_vars="part_number", value_vars=["on_hand_qty", "reorder_point"]),
            x="part_number", y="value", color="variable", barmode="group",
            labels={"value": "Qty", "variable": "Type", "part_number": "Part"},
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No inventory data.")

with row2_right:
    st.subheader("Vendor On-Time Rate")
    if not vendor_df.empty:
        vendor_df_sorted = vendor_df.sort_values("on_time_rate", ascending=True)
        fig4 = px.bar(
            vendor_df_sorted,
            x="on_time_rate", y="vendor_name", orientation="h",
            labels={"on_time_rate": "On-Time Rate", "vendor_name": "Vendor"},
        )
        fig4.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No vendor data.")

# ── Raw Tables ───────────────────────────────────────────────────────────────
with st.expander("Work Orders - Raw Data"):
    st.dataframe(wo_df)

with st.expander("Inventory - Raw Data"):
    st.dataframe(inv_df)

with st.expander("Vendors - Raw Data"):
    st.dataframe(vendor_df)

# ── Slack Alerts ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("Slack Alerts")
if st.button("Send Alerts Now"):
    check_and_alert(overdue_count, low_stock_parts)
    st.success("Alerts sent to Slack.")

st.caption("Alerts fire automatically when thresholds are breached on each page load.")
check_and_alert(overdue_count, low_stock_parts)
