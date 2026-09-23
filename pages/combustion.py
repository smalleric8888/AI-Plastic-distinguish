import streamlit as st
from services.material_engine import MaterialEngine

def render_combustion_page(material_engine: MaterialEngine):
    """🎥 燃燒實驗室頁面 (全局 Session State 連動版)"""
    st.subheader("🎥 燃燒實驗室 (Combustion Test Lab)")

    # ⚠️ 專屬安全警示面板 (Safety Notice)
    st.markdown("""
    <div class="warning-box">
        <b>⚠️ 嚴正安全警示 (Safety Notice)</b><br>
        塑膠廢料微量燃燒測試涉及高溫火源及可能的化學有害氣體（如 PVC 燃燒產生之氯化氫 HCl 氣體）。<b>本試驗僅供受控實驗室環境、配戴防護裝備與專業人員操作！</b>
    </div>
    """, unsafe_allow_html=True)

    st.write("上傳燃燒實錄影片 (.mp4)，或選擇**火焰顏色 (Green/Blue Base)**、**煙霧濃度**與**離火自熄性**氣味特徵：")

    video_file = st.file_uploader("上傳燃燒測試影片：", type=["mp4", "mov"], key="combustion_tab_uploader")
    if video_file:
        video_bytes = video_file.read()
        st.session_state["global_video_bytes"] = video_bytes
        st.video(video_bytes)

    elif st.session_state.get("global_video_bytes"):
        st.video(st.session_state["global_video_bytes"])

    st.markdown("---")
    st.subheader("🔥 燃燒氣味與火焰觀察選擇")

    col1, col2 = st.columns(2)
    with col1:
        opts_smell = [
            "甲. 柴油/機油味 (PP)",
            "乙. 滴蠟/石蠟味 (PE)",
            "丙. 鹽酸酸臭味/綠焰 (PVC)",
            "丁. 燒焦輪胎味/濃黑煙 (ABS)",
            "戊. 化學甜味/碳黑 (PS)"
        ]
        def_smell = None
        if st.session_state.get("burn_test"):
            for o in opts_smell:
                if o.startswith(st.session_state["burn_test"][0]):
                    def_smell = o

        smell_sel = st.selectbox("1. 燃燒氣味歸類：", opts_smell, index=opts_smell.index(def_smell) if def_smell in opts_smell else 0)
        st.session_state["burn_test"] = smell_sel

    with col2:
        opts_flame = [
            "黃色火焰/黃黃滴落 (PE/PP)",
            "綠色火焰/酸臭 (PVC)",
            "濃濃黑煙/輪胎 (ABS/PS)",
            "離火即熄/自熄 (PVC/ABS)"
        ]
        def_flame = st.session_state.get("flame_choice")
        flame_sel = st.selectbox("2. 火焰與煙霧形態：", opts_flame, index=opts_flame.index(def_flame) if def_flame in opts_flame else 0)
        st.session_state["flame_choice"] = flame_sel

    st.success("✅ 燃燒與氣味特徵已自動即時同步至【🔬 3合1綜合】大數據儀表板！")
