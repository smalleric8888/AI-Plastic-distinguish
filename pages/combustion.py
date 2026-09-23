import streamlit as st
from services.material_engine import MaterialEngine

def render_combustion_page(material_engine: MaterialEngine):
    """🎥 燃燒觀察頁面 (V3.0 無障礙高對比 & 實用安全提醒版)"""
    st.subheader("🔥 燃燒氣味與觀察 (Combustion Observation)")

    # 通用實用安全提醒卡
    st.markdown("""
    <div class="warning-box">
        <b>⚠️ 燃燒觀察安全與通風提醒</b><br>
        塑膠微量燃燒測試可能產生高溫與化學氣味（如 PVC 燃燒產生 HCl 氣味）。<b>請務必於通風良好處操作，並注意火源安全！</b><br>
        首頁建議優先使用照片視覺、水中浮沉測試與資料庫查表進行初步判斷。
    </div>
    """, unsafe_allow_html=True)

    st.write("可上傳燃燒觀察影片 (.mp4)，或選擇火焰與氣味特徵：")

    video_file = st.file_uploader("上傳燃燒測試影片：", type=["mp4", "mov"], key="combustion_tab_uploader")
    if video_file:
        video_bytes = video_file.read()
        st.session_state["global_video_bytes"] = video_bytes
        st.video(video_bytes)
    elif st.session_state.get("global_video_bytes"):
        st.video(st.session_state["global_video_bytes"])

    st.markdown("---")
    st.subheader("🔥 特徵選配選項")

    col1, col2 = st.columns(2)
    with col1:
        opts_smell = [
            "(未測試 / 請選擇)",
            "甲. 柴油/機油味 (PP)",
            "乙. 滴蠟/石蠟味 (PE)",
            "丙. 鹽酸酸臭味/綠焰 (PVC)",
            "丁. 燒焦輪胎味/濃黑煙 (ABS)",
            "戊. 化學甜味/碳黑 (PS)"
        ]
        def_smell_idx = 0
        if st.session_state.get("burn_test"):
            for idx, o in enumerate(opts_smell):
                if idx > 0 and o.startswith(st.session_state["burn_test"][0]):
                    def_smell_idx = idx

        smell_sel = st.selectbox("1. 燃燒氣味：", opts_smell, index=def_smell_idx)
        st.session_state["burn_test"] = smell_sel if smell_sel != "(未測試 / 請選擇)" else None

    with col2:
        opts_flame = [
            "(未測試 / 請選擇)",
            "黃色火焰/黃黃滴落 (PE/PP)",
            "綠色火焰/酸臭 (PVC)",
            "濃濃黑煙/輪胎 (ABS/PS)",
            "離火即熄/自熄 (PVC/ABS)"
        ]
        def_flame_idx = 0
        if st.session_state.get("flame_choice"):
            for idx, o in enumerate(opts_flame):
                if idx > 0 and o.startswith(st.session_state["flame_choice"][:2]):
                    def_flame_idx = idx

        flame_sel = st.selectbox("2. 火焰與煙霧形態：", opts_flame, index=def_flame_idx)
        st.session_state["flame_choice"] = flame_sel if flame_sel != "(未測試 / 請選擇)" else None

    st.success("✅ 特徵已即時同步至【🔬 綜合辨識】。")
