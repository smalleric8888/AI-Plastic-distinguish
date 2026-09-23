import os
import streamlit as st
from PIL import Image
from services.gemini_service import GeminiService
from services.material_engine import MaterialEngine
from components.result_card import render_prediction_result_card

def render_identify_page(material_engine: MaterialEngine):
    """🏠 辨識主頁渲染邏輯"""
    st.subheader("📷 步驟一：選擇或拍攝廢料照片")
    
    col1, col2 = st.columns([1, 1])
    selected_image_path = None
    uploaded_photo = None
    active_img = None

    with col1:
        uploaded_photo = st.file_uploader("請拍攝或選擇塑膠廢料照片：", type=["jpg", "png", "jpeg"])

    with col2:
        if uploaded_photo:
            active_img = Image.open(uploaded_photo)
            st.image(active_img, caption="待測照片預覽", use_container_width=True)
            st.session_state["uploaded_image"] = active_img
        else:
            st.info("📷 請拍攝或上傳塑膠廢料照片")

    # Gemini 結構化 JSON 分析摘要 (使用 session_state 快取避免每次切換重複呼叫)
    if active_img:
        current_img_key = getattr(uploaded_photo, "name", str(id(active_img)))
        if st.session_state.get("last_uploaded_name") != current_img_key or "gemini_result" not in st.session_state:
            with st.spinner("🤖 Gemini 視覺 AI 正在分析照片與推測材質..."):
                gemini_svc = GeminiService()
                st.session_state["gemini_result"] = gemini_svc.analyze_image_structured(active_img)
                st.session_state["last_uploaded_name"] = current_img_key
                st.session_state["final_result"] = None  # 上傳新照片時重置舊預測

        g_res = st.session_state.get("gemini_result")
        if g_res:
            st.markdown(f"""
            <div class="gemini-card">
                <h4>🤖 第一關：Gemini 多模態大數據庫初步分析摘要</h4>
                <p><b>🔍 AI 識別物品</b>：{g_res['object_name']}</p>
                <p><b>🎨 外觀與特徵</b>：{g_res['color_appearance']}</p>
                <p><b>💡 大數據庫材質推測</b>：{', '.join(g_res['estimated_materials'])}</p>
                <p><b>📝 全球工業應用</b>：{g_res['reasoning']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.session_state["gemini_result"] = None
        st.session_state["last_uploaded_name"] = None

    st.markdown("---")

    # 漸進式三步問答 (Progressive Disclosure)
    st.subheader("🔍 步驟二：漸進式實體觸控診斷問答")
    st.caption("請依序完成各關卡測試，全數勾選後即可啟用分析按鈕。")

    # 關卡 1: 水中浮沉
    st.markdown("#### 1. 水中浮沉測試")
    opts_float = ["1. 浮於水面 (ρ < 1.0 g/cm³, 候選: PP, PE)", "2. 沉於水底 (ρ > 1.0 g/cm³, 候選: ABS, PVC, PS, PET)"]
    def_float = opts_float[0] if st.session_state.get("float_test") == 1 else (opts_float[1] if st.session_state.get("float_test") == 2 else None)
    
    float_input = st.segmented_control("浮沉選項", opts_float, default=def_float) if hasattr(st, "segmented_control") else st.radio("1. 水中浮沉測試：", opts_float, index=0)
    
    if float_input:
        st.session_state["float_test"] = 1 if "1." in float_input else 2

    # 關卡 2: 觸感聲音 (第一關完成後展開)
    sound_input = None
    if st.session_state.get("float_test"):
        st.markdown("#### 2. 觸感與剛性聲音特徵")
        opts_sound = ["A. 硬質敲擊聲 (ABS, PS, PVC, 硬PP)", "B. 柔軟延展韌性 (PE, 軟PP)", "C. 打包帶/帶狀 (PP, PET)"]
        def_sound = None
        if st.session_state.get("sound_test"):
            for o in opts_sound:
                if o.startswith(st.session_state["sound_test"]):
                    def_sound = o

        sound_input = st.segmented_control("聲音選項", opts_sound, default=def_sound) if hasattr(st, "segmented_control") else st.radio("2. 觸感與聲音特徵：", opts_sound, index=0)
        if sound_input:
            st.session_state["sound_test"] = sound_input[0]

    # 關卡 3: 燃燒氣味 (前兩關完成後展開)
    smell_input = None
    if st.session_state.get("sound_test"):
        st.markdown("#### 3. 微量燃燒特徵與氣味")
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
                if o.startswith(st.session_state["burn_test"]):
                    def_smell = o

        smell_input = st.segmented_control("氣味選項", opts_smell, default=def_smell) if hasattr(st, "segmented_control") else st.radio("3. 燃燒特徵與氣味：", opts_smell, index=0)
        if smell_input:
            st.session_state["burn_test"] = smell_input[0]

    st.markdown("---")

    # 按鈕啟用條件：三項全完成
    can_submit = (
        st.session_state.get("float_test") is not None and
        st.session_state.get("sound_test") is not None and
        st.session_state.get("burn_test") is not None
    )

    if st.button("🚀 執行 AI 綜合材質推估與排名", disabled=not can_submit, type="primary", use_container_width=True):
        res = material_engine.calculate_top3_prediction(
            float_choice=st.session_state["float_test"],
            sound_choice=st.session_state["sound_test"],
            smell_choice=st.session_state["burn_test"],
            gemini_analysis=st.session_state.get("gemini_result")
        )
        st.session_state["final_result"] = res

    # 渲染結果
    if st.session_state.get("final_result"):
        render_prediction_result_card(st.session_state["final_result"])
