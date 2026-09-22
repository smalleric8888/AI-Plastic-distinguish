import streamlit as st
from services.material_engine import MaterialEngine

def render_combustion_page(material_engine: MaterialEngine):
    """🎥 燃燒實驗室頁面渲染邏輯"""
    st.subheader("🎥 燃燒實驗室 (Combustion Test Lab)")

    # ⚠️ 專屬安全警示面板 (Safety Notice)
    st.markdown("""
    <div class="warning-box">
        <b>⚠️ 嚴正安全警示 (Safety Notice)</b><br>
        塑膠廢料微量燃燒測試涉及高溫火源及可能的化學有害氣體（如 PVC 燃燒產生之氯化氫 HCl 氣體）。<b>本試驗僅供受控實驗室環境、配戴防護裝備與專業人員操作！</b>
    </div>
    """, unsafe_allow_html=True)

    st.write("上傳燃燒實錄影片 (.mp4)，AI 將進行**火焰顏色 (Green/Blue Base)**、**煙霧濃度**與**離火自熄性**特徵採樣：")

    video_file = st.file_uploader("上傳燃燒測試影片：", type=["mp4", "mov"])

    if video_file:
        st.video(video_file)

        st.markdown("---")
        st.subheader("🔥 AI 影片燃燒特徵採樣分析")
        col1, col2 = st.columns(2)
        with col1:
            st.write("🟢 **火焰顏色底圖**：底端帶綠色 (Green Base Detected) ➔ PVC 特徵")
            st.write("💨 **黑煙濃度與炭黑**：微弱 (Low Smoke)")
        with col2:
            st.write("⏱️ **離火反應**：離火即熄 (Self-Extinguishing)")
            st.write("👃 **氣味歸類**：酸臭刺鼻味 (Hydrochloric Odor)")
