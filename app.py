import os
import sys
import streamlit as st

# 載入專案子模組
sys.path.append(os.path.dirname(__file__))

from services.media_loader import MediaLoader
from services.material_engine import MaterialEngine
from components.navigation import render_navigation_bar
from pages.identify import render_identify_page
from pages.audio import render_audio_page
from pages.combustion import render_combustion_page
from pages.database import render_database_page

# 頁面配置
st.set_page_config(
    page_title="天辰 AI 塑膠材質辨識 App",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. 載入 CSS 主題樣式 (assets/styles.css)
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 2. 初始化 Session State 狀態
if "uploaded_image" not in st.session_state:
    st.session_state["uploaded_image"] = None
if "gemini_result" not in st.session_state:
    st.session_state["gemini_result"] = None
if "float_test" not in st.session_state:
    st.session_state["float_test"] = None
if "sound_test" not in st.session_state:
    st.session_state["sound_test"] = None
if "burn_test" not in st.session_state:
    st.session_state["burn_test"] = None
if "final_result" not in st.session_state:
    st.session_state["final_result"] = None

# 3. 實例化解耦服務模組
media_loader = MediaLoader()
material_engine = MaterialEngine(media_loader=media_loader)

# 4. 手機 Native App Header 標頭
st.markdown("""
<div class="app-header">
    <h2>♻️ 天辰 AI 塑膠辨識 App</h2>
    <p>Gemini 多模態大數據庫 ✕ 天辰廢料全循環履歷</p>
</div>
""", unsafe_allow_html=True)

# 5. 導覽選單列 (st.segmented_control 頁面路由)
active_tab = render_navigation_bar()

# 6. 頁面路由分發 (Page Router)
if active_tab == "🏠 辨識":
    render_identify_page(material_engine)
elif active_tab == "🎵 聲響":
    render_audio_page(material_engine)
elif active_tab == "🎥 燃燒":
    render_combustion_page(material_engine)
elif active_tab == "📁 資料庫":
    render_database_page(media_loader)
