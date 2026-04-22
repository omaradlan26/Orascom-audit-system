import pandas as pd
import streamlit as st


def render_dashboard(summary: dict, audits: list[dict]) -> None:
    st.subheader("Audit Dashboard")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Total Audits", summary.get("total", 0))
    metric_cols[1].metric("Open", summary.get("open", 0))
    metric_cols[2].metric("Closed", summary.get("closed", 0))
    metric_cols[3].metric("Overdue", summary.get("overdue", 0))

    if not audits:
        st.info("No audit records match the current filters.")
        return

    dataframe = pd.DataFrame(audits)
    risk_counts = dataframe["risk"].value_counts().rename_axis("risk").reset_index(name="count")
    status_counts = dataframe["status"].value_counts().rename_axis("status").reset_index(name="count")

    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.caption("Risk Distribution")
        st.bar_chart(risk_counts.set_index("risk"))
    with chart_cols[1]:
        st.caption("Status Distribution")
        st.bar_chart(status_counts.set_index("status"))
