import streamlit as st

def render_navigation_bar():
    """渲染單一狀態 App 導覽頁籤 (Position Sticky)"""
    options = ["🏠 辨識", "🎵 聲響", "🎥 燃燒", "📁 資料庫"]
    
    # 初始化 active_page
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "🏠 辨識"

    # 使用 segmented_control (Streamlit 1.40+) 或 radio
    try:
        selected_tab = st.segmented_control(
            "功能導覽",
            options,
            default=st.session_state["active_page"],
            label_visibility="collapsed"
        )
    except AttributeError:
        selected_tab = st.radio(
            "功能導覽",
            options,
            index=options.index(st.session_state["active_page"]),
            horizontal=True,
            label_visibility="collapsed"
        )

    if selected_tab:
        st.session_state["active_page"] = selected_tab

    return st.session_state["active_page"]
