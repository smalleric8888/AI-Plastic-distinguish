import streamlit as st
from PIL import Image
from services.gemini_service import GeminiService
from services.material_engine import MaterialEngine
from components.fusion_result_card import render_fusion_result_card

def render_fusion_page(material_engine: MaterialEngine, media_loader):
    """🔬 V3.0 塑膠材質初步辨識主頁面 (無預設解答與零證據保護版)"""
    st.subheader("🔬 塑膠材質初步辨識系統")
    st.caption("結合照片視覺、敲擊聲響、物理浮沉與燃燒氣味多模態特徵；結果非實驗室確證。")

    # 4 步流程提示
    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 14px; border-radius: 10px; margin-bottom: 16px; font-size: 0.85rem; color: #475569;">
        <b>📌 建議四步鑑定流程</b>：1. 上傳廢料照片 ➔ 2. 進行水中浮沉 ➔ 3. 選配敲擊/氣味 ➔ 4. 查看初步診斷
    </div>
    """, unsafe_allow_html=True)

    # 跨頁籤數據即時同步狀態
    vis_ready = st.session_state.get("gemini_result") is not None or st.session_state.get("uploaded_image") is not None
    ac_ready = st.session_state.get("audio_analysis") is not None or (st.session_state.get("sound_test") and not st.session_state["sound_test"].startswith("(未"))
    th_ready = (st.session_state.get("burn_test") and not st.session_state["burn_test"].startswith("(未")) or (st.session_state.get("flame_choice") and not st.session_state["flame_choice"].startswith("(未"))
    phy_ready = st.session_state.get("float_test") is not None and str(st.session_state.get("float_test")) != "None"

    st.markdown("""
    <div style="background: #0F172A; padding: 12px 16px; border-radius: 12px; margin-bottom: 16px; color: #FFFFFF;">
        <div style="display: flex; gap: 14px; flex-wrap: wrap; font-size: 0.85rem;">
            <span>📸 照片: {}</span>
            <span>🌊 浮沉: {}</span>
            <span>🎵 聲響: {}</span>
            <span>🔥 氣味: {}</span>
        </div>
    </div>
    """.format(
        "<span style='color:#4ADE80;'>已上傳</span>" if vis_ready else "<span style='color:#94A3B8;'>未提供</span>",
        "<span style='color:#4ADE80;'>已選擇</span>" if phy_ready else "<span style='color:#94A3B8;'>未選擇</span>",
        "<span style='color:#4ADE80;'>已提供</span>" if ac_ready else "<span style='color:#94A3B8;'>未提供</span>",
        "<span style='color:#4ADE80;'>已提供</span>" if th_ready else "<span style='color:#94A3B8;'>未提供</span>"
    ), unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    # 模態 1: 視覺照片
    active_img = st.session_state.get("uploaded_image")
    g_res = st.session_state.get("gemini_result")

    with col1:
        st.markdown("#### 📸 照片視覺 AI")
        uploaded_photo = st.file_uploader("上傳廢料照片：", type=["jpg", "jpeg", "png"], key="fusion_photo_uploader")
        if uploaded_photo:
            active_img = Image.open(uploaded_photo)
            st.session_state["uploaded_image"] = active_img
            img_key = getattr(uploaded_photo, "name", str(id(active_img)))
            if st.session_state.get("last_uploaded_name") != img_key or not g_res:
                with st.spinner("🤖 Gemini 視覺分析中..."):
                    gemini_svc = GeminiService()
                    g_res = gemini_svc.analyze_image_structured(active_img)
                    st.session_state["gemini_result"] = g_res
                    st.session_state["last_uploaded_name"] = img_key

        if active_img:
            st.image(active_img, caption="待測照片預覽", use_container_width=True)
            if g_res:
                st.success(f"AI辨識: {g_res.get('object_name', '')}")
                st.caption(f"推測材質: {', '.join(g_res.get('estimated_materials', []))}")
        else:
            st.info("尚未上傳照片")

    # 模態 2: 敲擊聲響
    audio_analysis = st.session_state.get("audio_analysis")
    with col2:
        st.markdown("#### 🎵 敲擊聲響與剛性")
        audio_file = st.file_uploader("上傳敲擊聲音檔：", type=["wav", "mp3", "m4a"], key="fusion_audio_uploader")
        if audio_file:
            audio_bytes = audio_file.read()
            st.session_state["audio_bytes"] = audio_bytes
            audio_analysis = material_engine.analyze_audio_bytes(audio_bytes)
            st.session_state["audio_analysis"] = audio_analysis

        if audio_analysis:
            st.metric("⚡ Peak Freq", f"{audio_analysis.get('peak_freq', 0)} Hz")
        
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

        selected_sound = st.selectbox("聲音選項：", opts_sound, index=def_sound_idx)
        st.session_state["sound_test"] = selected_sound if selected_sound != "(未測試 / 請選擇)" else None

    # 模態 3: 燃燒觀察
    with col3:
        st.markdown("#### 🔥 燃燒與氣味 (輔助)")
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

        selected_smell = st.selectbox("1. 燃燒氣味：", opts_smell, index=def_smell_idx)
        st.session_state["burn_test"] = selected_smell if selected_smell != "(未測試 / 請選擇)" else None

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

        selected_flame = st.selectbox("2. 火焰形態：", opts_flame, index=def_flame_idx)
        st.session_state["flame_choice"] = selected_flame if selected_flame != "(未測試 / 請選擇)" else None

    st.markdown("---")

    # 物理約束: 水中浮沉
    st.markdown("#### 🌊 物理測試：水中浮沉")
    opts_float = [
        "(未測試 / 請選擇)",
        "1. 浮於水面 (ρ < 1.0 g/cm³, 候選: PP, PE)",
        "2. 沉於水底 (ρ > 1.0 g/cm³, 候選: ABS, PVC, PS, PET)"
    ]
    def_float_idx = 0
    if st.session_state.get("float_test") == 1:
        def_float_idx = 1
    elif st.session_state.get("float_test") == 2:
        def_float_idx = 2

    float_input = st.selectbox("請選擇水中浮沉測試結果：", opts_float, index=def_float_idx)
    if float_input.startswith("1."):
        st.session_state["float_test"] = 1
    elif float_input.startswith("2."):
        st.session_state["float_test"] = 2
    else:
        st.session_state["float_test"] = None

    # 計算融合結果
    fusion_res = material_engine.calculate_fusion_prediction(
        float_choice=st.session_state.get("float_test"),
        sound_choice=st.session_state.get("sound_test"),
        smell_choice=st.session_state.get("burn_test"),
        audio_analysis=st.session_state.get("audio_analysis"),
        gemini_analysis=st.session_state.get("gemini_result"),
        flame_choice=st.session_state.get("flame_choice")
    )
    st.session_state["fusion_final_result"] = fusion_res

    # 渲染診斷結果卡片
    render_fusion_result_card(st.session_state["fusion_final_result"])
