from datetime import datetime

import pandas as pd
import streamlit as st


def render_filters(filter_options: dict) -> dict[str, str]:
    st.sidebar.header("Filters")
    status = st.sidebar.selectbox("Status", ["All"] + filter_options.get("statuses", []))
    risk = st.sidebar.selectbox("Risk", ["All"] + filter_options.get("risks", []))
    department = st.sidebar.selectbox("Department", ["All"] + filter_options.get("departments", []))
    owner = st.sidebar.selectbox("Owner", ["All"] + filter_options.get("owners", []))
    return {
        "status": status,
        "risk": risk,
        "department": department,
        "owner": owner,
    }


def render_audit_table(audits: list[dict]) -> pd.DataFrame:
    st.subheader("Audit Records")
    dataframe = pd.DataFrame(audits)
    if dataframe.empty:
        st.info("No audits available.")
        return dataframe

    display_df = dataframe.copy()
    display_df["due_date"] = pd.to_datetime(display_df["due_date"]).dt.date
    display_df = display_df[
        ["id", "title", "department", "risk", "grade", "owner", "due_date", "status", "action"]
    ]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    return dataframe


def render_audit_form(form_key: str, filter_options: dict, defaults: dict | None = None) -> dict | None:
    defaults = defaults or {}
    with st.form(form_key):
        title = st.text_input("Title", value=defaults.get("title", ""))
        department = st.text_input("Department", value=defaults.get("department", ""))
        observation = st.text_area("Observation", value=defaults.get("observation", ""))
        risk = st.selectbox(
            "Risk",
            options=filter_options.get("risks", []),
            index=_select_index(filter_options.get("risks", []), defaults.get("risk")),
        )
        grade = st.selectbox(
            "Grade",
            options=filter_options.get("grades", []),
            index=_select_index(filter_options.get("grades", []), defaults.get("grade")),
        )
        action = st.text_area("Corrective Action", value=defaults.get("action", ""))
        owner = st.text_input("Owner", value=defaults.get("owner", ""))
        due_date_raw = defaults.get("due_date")
        due_date = st.date_input(
            "Due Date",
            value=_coerce_date(due_date_raw),
        )
        status = st.selectbox(
            "Status",
            options=filter_options.get("statuses", []),
            index=_select_index(filter_options.get("statuses", []), defaults.get("status")),
        )
        submitted = st.form_submit_button("Save Audit")

    if not submitted:
        return None

    return {
        "title": title.strip(),
        "department": department.strip(),
        "observation": observation.strip(),
        "risk": risk,
        "grade": grade,
        "action": action.strip(),
        "owner": owner.strip(),
        "due_date": due_date.isoformat(),
        "status": status,
    }


def _select_index(options: list[str], current_value: str | None) -> int:
    if current_value in options:
        return options.index(current_value)
    return 0


def _coerce_date(value):
    if hasattr(value, "year"):
        return value
    if isinstance(value, str) and value:
        return datetime.fromisoformat(value).date()
    return datetime.today().date()
