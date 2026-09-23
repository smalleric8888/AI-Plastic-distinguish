import streamlit as st
from services.material_engine import MaterialEngine
from components.charts import plot_audio_waveform_and_fft

def render_audio_page(material_engine: MaterialEngine):
    """🎵 聲響儀表板頁面 (V3.0 無障礙高對比 & 錄音指引版)"""
    st.subheader("🎵 聲響儀表板 (Audio Spectrum Dashboard)")
    st.caption("上傳敲擊聲音檔 (.wav / .mp3 / .m4a)，AI 即時繪製波形與快速傅立葉 (FFT) 頻譜。")

    # 15秒標準敲擊錄音指引
    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #CBD5E1; padding: 14px; border-radius: 12px; margin-bottom: 16px; font-size: 0.85rem; color: #1E293B;">
        <h4 style="margin: 0 0 6px 0; color: #0F172A; font-size: 0.95rem;">🎙️ 15秒標準敲擊錄音指引</h4>
        <ol style="margin: 0; padding-left: 18px; line-height: 1.6; color: #334155;">
            <li><b>環境</b>：請於安靜室內進行錄製，減少周遭人聲與背景噪音。</li>
            <li><b>工具</b>：請使用金屬鑰匙或硬質金屬棒，輕敲塑膠樣品 3 ~ 5 次。</li>
            <li><b>距離</b>：保持手機麥克風距離廢料約 10 ~ 15 cm。</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    audio_file = st.file_uploader("上傳敲擊聲音檔：", type=["m4a", "mp3", "wav"], key="audio_tab_uploader")

    if audio_file:
        audio_bytes = audio_file.read()
        st.session_state["audio_bytes"] = audio_bytes
        st.audio(audio_bytes, format="audio/wav")

        res = material_engine.analyze_audio_bytes(audio_bytes)
        st.session_state["audio_analysis"] = res
        
        col1, col2, col3 = st.columns(3)
        col1.metric("⚡ 峰值頻率 (Peak)", f"{res['peak_freq']} Hz")
        col2.metric("🎼 頻譜重心", f"{res['spectral_centroid']} Hz")
        col3.metric("剛性質地", "高音硬質" if res['is_high_pitch'] else "低音延展")

        plot_audio_waveform_and_fft(res)

        if res['is_high_pitch']:
            st.session_state["sound_test"] = "A. 硬質敲擊聲 (ABS, PS, PVC, 硬PP)"
        else:
            st.session_state["sound_test"] = "B. 柔軟延展韌性 (PE, 軟PP)"

        st.success("✅ 敲擊聲頻譜分析結果已即時同步至【🔬 綜合辨識】。")

    elif st.session_state.get("audio_bytes"):
        audio_bytes = st.session_state["audio_bytes"]
        st.audio(audio_bytes, format="audio/wav")
        res = st.session_state.get("audio_analysis") or material_engine.analyze_audio_bytes(audio_bytes)
        plot_audio_waveform_and_fft(res)

    st.markdown("---")
    st.subheader("🔊 剛性與敲擊特徵選配")
    opts_sound = [
        "(未測試 / 請選擇)",
        "A. 硬質敲擊聲 (ABS, PS, PVC, 硬PP)",
        "B. 柔軟延展韌性 (PE, 軟PP)",
        "C. 打包帶/帶狀 (PP, PET)"
    ]
    def_sound_idx = 0
    if st.session_state.get("sound_test"):
        for idx, o in enumerate(opts_sound):
            if idx > 0 and o.startswith(st.session_state["sound_test"][0]):
                def_sound_idx = idx

    selected_sound = st.selectbox("請選擇聲音特徵：", opts_sound, index=def_sound_idx)
    st.session_state["sound_test"] = selected_sound if selected_sound != "(未測試 / 請選擇)" else None
