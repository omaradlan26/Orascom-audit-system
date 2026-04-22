import streamlit as st


SESSION_DEFAULTS = {
    "auth_token": None,
    "auth_role": None,
    "auth_user": None,
}


def initialize_session() -> None:
    for key, value in SESSION_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def is_authenticated() -> bool:
    return bool(st.session_state.get("auth_token"))


def set_auth_state(token: str, username: str, role: str) -> None:
    st.session_state.auth_token = token
    st.session_state.auth_user = username
    st.session_state.auth_role = role


def clear_auth_state() -> None:
    for key, value in SESSION_DEFAULTS.items():
        st.session_state[key] = value
