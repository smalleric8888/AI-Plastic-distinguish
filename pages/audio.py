import streamlit as st
from services.material_engine import MaterialEngine
from components.charts import plot_audio_waveform_and_fft

def render_audio_page(material_engine: MaterialEngine):
    """🎵 聲響儀表板頁面 (全局 Session State 連動版)"""
    st.subheader("🎵 聲響儀表板 (Audio Spectrum Dashboard)")
    st.caption("請上傳敲擊聲或揉搓聲音訊 (.m4a / .mp3 / .wav)，分析結果將自動與 V2.0 3合1 綜合分析同步。")

    audio_file = st.file_uploader("上傳敲擊聲音檔：", type=["m4a", "mp3", "wav"], key="audio_tab_uploader")

    if audio_file:
        audio_bytes = audio_file.read()
        st.session_state["audio_bytes"] = audio_bytes
        st.audio(audio_bytes, format="audio/wav")

        res = material_engine.analyze_audio_bytes(audio_bytes)
        st.session_state["audio_analysis"] = res
        
        # 顯示指標卡片
        col1, col2, col3 = st.columns(3)
        col1.metric("⚡ 峰值頻率 (Peak Freq)", f"{res['peak_freq']} Hz")
        col2.metric("🎼 頻譜重心 (Centroid)", f"{res['spectral_centroid']} Hz")
        col3.metric("剛性脆度 (Brightness)", "高音硬質 (High)" if res['is_high_pitch'] else "低音韌性 (Soft)")

        # 繪製 Plotly 圖表
        plot_audio_waveform_and_fft(res)

        # 自動將頻譜特徵連動至聲音選項
        if res['is_high_pitch']:
            st.session_state["sound_test"] = "A. 硬質敲擊聲 (ABS, PS, PVC)"
        else:
            st.session_state["sound_test"] = "B. 柔軟延展韌性 (PE, 軟PP)"

        st.success("✅ 敲擊聲頻譜分析結果已自動即時同步至【🔬 3合1綜合】大數據儀表板！")

    elif st.session_state.get("audio_bytes"):
        audio_bytes = st.session_state["audio_bytes"]
        st.audio(audio_bytes, format="audio/wav")
        res = st.session_state.get("audio_analysis") or material_engine.analyze_audio_bytes(audio_bytes)
        plot_audio_waveform_and_fft(res)
        st.info("ℹ️ 正在讀取先前已上傳之聲音檔案。")

    # 手動聲音與剛性輔助選擇
    st.markdown("---")
    st.subheader("🔊 剛性與敲擊聲音特徵選項")
    opts_sound = ["A. 硬質敲擊聲 (ABS, PS, PVC, 硬PP)", "B. 柔軟延展韌性 (PE, 軟PP)", "C. 打包帶/帶狀 (PP, PET)"]
    def_sound = None
    if st.session_state.get("sound_test"):
        for o in opts_sound:
            if o.startswith(st.session_state["sound_test"][0]):
                def_sound = o

    selected_sound = st.radio("請確認聲音特徵選項：", opts_sound, index=opts_sound.index(def_sound) if def_sound in opts_sound else 0)
    st.session_state["sound_test"] = selected_sound
