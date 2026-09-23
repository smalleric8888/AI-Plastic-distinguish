import os
import sys
import streamlit as st

# 載入專案子模組
sys.path.append(os.path.dirname(__file__))

from services.media_loader import MediaLoader
from services.material_engine import MaterialEngine
from components.navigation import render_navigation_bar
from pages.fusion import render_fusion_page
from pages.identify import render_identify_page
from pages.audio import render_audio_page
from pages.combustion import render_combustion_page
from pages.database import render_database_page

# 頁面配置
st.set_page_config(
    page_title="天辰 AI 塑膠材質辨識 App V2.0",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. 載入 CSS 主題樣式 (assets/styles.css)
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 2. 初始化全局 Session State 狀態 (跨頁籤持久化)
global_keys = {
    "uploaded_image": None,
    "gemini_result": None,
    "float_test": 1,
    "sound_test": None,
    "burn_test": None,
    "flame_choice": None,
    "audio_bytes": None,
    "audio_analysis": None,
    "fusion_final_result": None,
    "last_uploaded_name": None
}
for key, val in global_keys.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 3. 實例化解耦服務模組
media_loader = MediaLoader()
material_engine = MaterialEngine(media_loader=media_loader)

# 4. 手機 Native App Header 標頭 (V2.0 雙發行版)
st.markdown("""
<div class="app-header">
    <h2>♻️ 天辰 AI 塑膠辨識 App <span style="font-size:0.9rem; background:#2563eb; color:white; padding:2px 8px; border-radius:12px;">V2.0 全模態</span></h2>
    <p>Gemini 3.5 Flash ✕ 聲響頻譜 ✕ 熱解燃燒 3合1綜合分析</p>
</div>
""", unsafe_allow_html=True)

# 5. 導覽選單列 (st.segmented_control 頁面路由)
active_tab = render_navigation_bar()

# 6. 頁面路由分發 (Page Router)
if active_tab == "🔬 3合1綜合":
    render_fusion_page(material_engine, media_loader)
elif active_tab in ["🏠 照片辨識", "🏠 辨識"]:
    render_identify_page(material_engine)
elif active_tab == "🎵 聲響":
    render_audio_page(material_engine)
elif active_tab == "🎥 燃燒":
    render_combustion_page(material_engine)
elif active_tab == "📁 資料庫":
    render_database_page(media_loader)
