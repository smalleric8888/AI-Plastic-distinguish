import streamlit as st
from PIL import Image
from services.gemini_service import GeminiService
from services.material_engine import MaterialEngine
from components.fusion_result_card import render_fusion_result_card

def render_fusion_page(material_engine: MaterialEngine, media_loader):
    """🔬 V2 3合1全模態綜合辨識主頁面"""
    st.subheader("🔬 3合1全模態綜合辨識 (照片 ✕ 聲響 ✕ 燃燒)")
    st.caption("同時輸入照片視覺、敲擊聲響頻譜與燃燒氣味，由 V2 多模態 AI 融合評分引擎計算 Top-3 最優估算結果與證據鏈分析。")

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    # 模態 1: 視覺照片 (Gemini 3.5 Flash)
    active_img = None
    g_res = None
    with col1:
        st.markdown("#### 📸 模態 1：照片視覺 AI")
        uploaded_photo = st.file_uploader("上傳廢料照片", type=["jpg", "jpeg", "png"], key="fusion_photo")
        if uploaded_photo:
            active_img = Image.open(uploaded_photo)
            st.image(active_img, caption="照片預覽", use_container_width=True)
            
            img_key = f"fusion_{uploaded_photo.name}"
            if st.session_state.get("fusion_last_img") != img_key or "fusion_g_res" not in st.session_state:
                with st.spinner("🤖 Gemini 分析中..."):
                    gemini_svc = GeminiService()
                    st.session_state["fusion_g_res"] = gemini_svc.analyze_image_structured(active_img)
                    st.session_state["fusion_last_img"] = img_key
            
            g_res = st.session_state.get("fusion_g_res")
            if g_res:
                st.success(f"AI辨識: {g_res.get('object_name', '')}")
                st.caption(f"推測材質: {', '.join(g_res.get('estimated_materials', []))}")

    # 模態 2: 敲擊聲響 (FFT)
    audio_analysis = None
    sound_input = None
    with col2:
        st.markdown("#### 🎵 模態 2：敲擊聲響")
        audio_file = st.file_uploader("上傳敲擊音訊 (WAV/MP3)", type=["wav", "mp3"], key="fusion_audio")
        if audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/wav")
            audio_analysis = material_engine.analyze_audio_bytes(audio_bytes)
            st.info(f"主頻 Peak Freq: {audio_analysis['peak_freq']} Hz ({'高音硬質' if audio_analysis['is_high_pitch'] else '低音韌性'})")

        opts_sound = ["A. 硬質敲擊聲 (ABS, PS, PVC)", "B. 柔軟延展韌性 (PE, 軟PP)", "C. 打包帶/帶狀 (PP, PET)"]
        sound_input = st.selectbox("聲音與剛性輔助選擇", ["(未選擇)"] + opts_sound)
        if sound_input == "(未選擇)":
            sound_input = None

    # 模態 3: 燃燒特徵與氣味
    smell_input = None
    flame_input = None
    with col3:
        st.markdown("#### 🎥 模態 3：燃燒與氣味")
        opts_smell = [
            "甲. 柴油/機油味 (PP)",
            "乙. 滴蠟/石蠟味 (PE)",
            "丙. 鹽酸酸臭味/綠焰 (PVC)",
            "丁. 燒焦輪胎味/濃黑煙 (ABS)",
            "戊. 化學甜味/碳黑 (PS)"
        ]
        smell_input = st.selectbox("燃燒氣味觀察", ["(未選擇)"] + opts_smell)
        if smell_input == "(未選擇)":
            smell_input = None

        flame_input = st.selectbox("火焰與煙霧觀察", ["(未選擇)", "黃色火焰/黃黃滴落 (PE/PP)", "綠色火焰/酸臭 (PVC)", "濃濃黑煙/輪胎 (ABS/PS)"])
        if flame_input == "(未選擇)":
            flame_input = None

    st.markdown("---")

    # 物理約束: 水中浮沉
    st.markdown("#### 🌊 物理約束：水中浮沉測試")
    opts_float = ["1. 浮於水面 (ρ < 1.0 g/cm³, 候選: PP, PE)", "2. 沉於水底 (ρ > 1.0 g/cm³, 候選: ABS, PVC, PS, PET)"]
    float_input = st.radio("浮沉選項 (物理約束線)：", opts_float, horizontal=True)
    float_val = 1 if "1." in float_input else 2

    # 計算融合按鈕
    if st.button("🚀 執行 3-in-1 全模態 AI 綜合判定", type="primary", use_container_width=True):
        fusion_res = material_engine.calculate_fusion_prediction(
            float_choice=float_val,
            sound_choice=sound_input,
            smell_choice=smell_input,
            audio_analysis=audio_analysis,
            gemini_analysis=g_res,
            flame_choice=flame_input
        )
        st.session_state["fusion_final_result"] = fusion_res

    if st.session_state.get("fusion_final_result"):
        render_fusion_result_card(st.session_state["fusion_final_result"])
