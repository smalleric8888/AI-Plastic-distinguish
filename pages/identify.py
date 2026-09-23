import os
import streamlit as st
from PIL import Image
from services.gemini_service import GeminiService
from services.material_engine import MaterialEngine
from components.fusion_result_card import render_fusion_result_card

def render_identify_page(material_engine: MaterialEngine):
    """📷 照片辨識與實體診斷頁面 (V3.0 無預設選中版)"""
    st.subheader("📷 步驟一：選擇或拍攝廢料照片")
    
    col1, col2 = st.columns([1, 1])
    uploaded_photo = None
    active_img = None

    with col1:
        uploaded_photo = st.file_uploader("拍攝或選擇塑膠廢料照片：", type=["jpg", "png", "jpeg"], key="identify_photo_uploader")

    with col2:
        if uploaded_photo:
            active_img = Image.open(uploaded_photo)
            st.image(active_img, caption="待測照片預覽", use_container_width=True)
            st.session_state["uploaded_image"] = active_img
        elif st.session_state.get("uploaded_image"):
            active_img = st.session_state["uploaded_image"]
            st.image(active_img, caption="待測照片預覽 (已跨頁連動)", use_container_width=True)
        else:
            st.info("📷 請拍攝或上傳塑膠廢料照片")

    # Gemini 結構化分析
    if active_img:
        current_img_key = getattr(uploaded_photo, "name", str(id(active_img)))
        if st.session_state.get("last_uploaded_name") != current_img_key or "gemini_result" not in st.session_state:
            with st.spinner("🤖 Gemini 視覺 AI 分析照片中..."):
                gemini_svc = GeminiService()
                st.session_state["gemini_result"] = gemini_svc.analyze_image_structured(active_img)
                st.session_state["last_uploaded_name"] = current_img_key

        g_res = st.session_state.get("gemini_result")
        if g_res:
            st.markdown(f"""
            <div class="gemini-card">
                <h4>🤖 第一關：Gemini 視覺 AI 解析摘要</h4>
                <p><b>🔍 AI 識別物品</b>：{g_res['object_name']}</p>
                <p><b>🎨 外觀與特徵</b>：{g_res['color_appearance']}</p>
                <p><b>💡 候選推測材質</b>：{', '.join(g_res['estimated_materials'])}</p>
                <p><b>📝 工業應用推論</b>：{g_res['reasoning']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔍 步驟二：實體觸控診斷測試 (選配)")
    st.caption("請點選下列物理特徵，選擇完成後即可即時計算相對匹配分數。")

    # 1. 水中浮沉
    opts_float = [
        "(未測試 / 請選擇)",
        "1. 浮於水面 (ρ < 1.0 g/cm³, 候選: PP, PE)",
        "2. 沉於水底 (ρ > 1.0 g/cm³, 候選: ABS, PVC, PS, PET)"
    ]
    def_float_idx = 0
    if st.session_state.get("float_test") == 1: def_float_idx = 1
    elif st.session_state.get("float_test") == 2: def_float_idx = 2

    float_input = st.selectbox("1. 水中浮沉測試：", opts_float, index=def_float_idx)
    if float_input.startswith("1."): st.session_state["float_test"] = 1
    elif float_input.startswith("2."): st.session_state["float_test"] = 2
    else: st.session_state["float_test"] = None

    # 2. 觸感聲音
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

    sound_input = st.selectbox("2. 觸感與剛性聲音特徵：", opts_sound, index=def_sound_idx)
    st.session_state["sound_test"] = sound_input if sound_input != "(未測試 / 請選擇)" else None

    # 3. 燃燒氣味
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

    smell_input = st.selectbox("3. 燃燒氣味觀察：", opts_smell, index=def_smell_idx)
    st.session_state["burn_test"] = smell_input if smell_input != "(未測試 / 請選擇)" else None

    st.markdown("---")

    # 執行與渲染結果
    res = material_engine.calculate_fusion_prediction(
        float_choice=st.session_state.get("float_test"),
        sound_choice=st.session_state.get("sound_test"),
        smell_choice=st.session_state.get("burn_test"),
        audio_analysis=st.session_state.get("audio_analysis"),
        gemini_analysis=st.session_state.get("gemini_result"),
        flame_choice=st.session_state.get("flame_choice")
    )
    st.session_state["fusion_final_result"] = res

    render_fusion_result_card(res)
