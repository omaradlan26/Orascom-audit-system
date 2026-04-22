import streamlit as st

from api_client import ApiClient
from components.audit_table import render_audit_form, render_audit_table, render_filters
from components.dashboard import render_dashboard
from session import clear_auth_state, initialize_session, is_authenticated, set_auth_state


st.set_page_config(page_title="Orascom Audit Management System", layout="wide")


def main() -> None:
    initialize_session()
    client = ApiClient()

    st.title("Orascom Audit Management System")
    st.caption("Role-based audit tracking for observations, actions, owners, and deadlines.")

    if not is_authenticated():
        render_login(client)
        return

    token = st.session_state.auth_token
    role = st.session_state.auth_role
    username = st.session_state.auth_user

    render_sidebar(client, token, role, username)

    try:
        filter_options = client.get_filter_options(token)
        filters = render_filters(filter_options)
        summary = client.get_summary(token)
        audits = client.list_audits(token, filters)
    except RuntimeError as exc:
        st.error(f"Unable to load data from the API: {exc}")
        return

    render_dashboard(summary, audits)
    dataframe = render_audit_table(audits)

    if role == "viewer":
        st.info("You are in read-only mode. Audit updates are disabled.")
        return

    st.divider()
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Add Audit")
        payload = render_audit_form("create_audit", filter_options)
        if payload:
            try:
                client.create_audit(token, payload)
                st.success("Audit created successfully.")
                st.rerun()
            except RuntimeError as exc:
                st.error(f"Unable to create audit: {exc}")

    with right_col:
        st.subheader("Edit Or Delete Audit")
        if dataframe.empty:
            st.caption("Create an audit first to enable edit and delete actions.")
            return

        audit_options = {
            f"#{row['id']} - {row['title']}": row.to_dict()
            for _, row in dataframe.iterrows()
        }
        selected_label = st.selectbox("Select Audit", list(audit_options.keys()))
        selected_audit = audit_options[selected_label]

        updated_payload = render_audit_form("edit_audit", filter_options, defaults=selected_audit)
        if updated_payload:
            try:
                client.update_audit(token, int(selected_audit["id"]), updated_payload)
                st.success("Audit updated successfully.")
                st.rerun()
            except RuntimeError as exc:
                st.error(f"Unable to update audit: {exc}")

        if st.button("Delete Selected Audit", type="secondary"):
            try:
                client.delete_audit(token, int(selected_audit["id"]))
                st.success("Audit deleted successfully.")
                st.rerun()
            except RuntimeError as exc:
                st.error(f"Unable to delete audit: {exc}")


def render_login(client: ApiClient) -> None:
    st.subheader("Login")
    login_mode = st.selectbox("Access Mode", ["Read Only", "Admin"])

    username = ""
    password = ""
    if login_mode == "Admin":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

    if st.button("Enter System", type="primary"):
        try:
            if login_mode == "Read Only":
                auth = client.guest_login()
            else:
                auth = client.admin_login(username=username, password=password)
            set_auth_state(auth["token"], auth["username"], auth["role"])
            st.rerun()
        except RuntimeError as exc:
            st.error(f"Login failed: {exc}")


def render_sidebar(client: ApiClient, token: str, role: str, username: str) -> None:
    st.sidebar.header("Session")
    st.sidebar.write(f"User: `{username}`")
    st.sidebar.write(f"Role: `{role}`")

    if st.sidebar.button("Logout"):
        try:
            client.logout(token)
        except RuntimeError:
            pass
        clear_auth_state()
        st.rerun()


if __name__ == "__main__":
    main()
