import streamlit as st
from PIL import Image
from services.gemini_service import GeminiService
from services.material_engine import MaterialEngine
from components.fusion_result_card import render_fusion_result_card

def render_fusion_page(material_engine: MaterialEngine, media_loader):
    """🔬 V2 3合1全模態綜合辨識主頁面 (全局 Session State 自動跨頁連動版)"""
    st.subheader("🔬 3合1全模態綜合辨識 (跨頁籤即時同步數據儀表板)")
    st.caption("支援在【照片辨識】、【聲響】與【燃燒】分頁分別完成測試，資料將自動即時跨頁同步，在此統一產出 3-in-1 全模態綜合鑑定報告。")

    # 全局數據同步狀態列 (Global Sync Status Bar)
    vis_ready = st.session_state.get("gemini_result") is not None or st.session_state.get("uploaded_image") is not None
    ac_ready = st.session_state.get("audio_analysis") is not None or st.session_state.get("sound_test") is not None
    th_ready = st.session_state.get("burn_test") is not None or st.session_state.get("flame_choice") is not None

    st.markdown("""
    <div style="background: #1e293b; padding: 12px 16px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #3b82f6;">
        <h4 style="margin: 0 0 8px 0; color: #f8fafc; font-size: 1rem;">⚡ 跨頁籤數據即時同步狀態</h4>
        <div style="display: flex; gap: 15px; flex-wrap: wrap; font-size: 0.9rem;">
            <span>📸 <b>照片視覺</b>: {}</span>
            <span>🎵 <b>敲擊聲響</b>: {}</span>
            <span>🎥 <b>燃燒氣味</b>: {}</span>
            <span>🌊 <b>水中浮沉</b>: {}</span>
        </div>
    </div>
    """.format(
        "<span style='color:#4ade80;'>✅ 已就緒</span>" if vis_ready else "<span style='color:#94a3b8;'>⏳ 待輸入</span>",
        "<span style='color:#4ade80;'>✅ 已就緒</span>" if ac_ready else "<span style='color:#94a3b8;'>⏳ 待輸入</span>",
        "<span style='color:#4ade80;'>✅ 已就緒</span>" if th_ready else "<span style='color:#94a3b8;'>⏳ 待輸入</span>",
        "<span style='color:#4ade80;'>✅ 浮於水 (<1.0)</span>" if st.session_state.get("float_test") == 1 else "<span style='color:#4ade80;'>✅ 沉於水 (>1.0)</span>"
    ), unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    # 模態 1: 視覺照片
    active_img = st.session_state.get("uploaded_image")
    g_res = st.session_state.get("gemini_result")

    with col1:
        st.markdown("#### 📸 模態 1：照片視覺 AI")
        uploaded_photo = st.file_uploader("選擇/拍攝照片 (或自動載入其他頁面)", type=["jpg", "jpeg", "png"], key="fusion_photo_uploader")
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
            st.image(active_img, caption="照片預覽", use_container_width=True)
            if g_res:
                st.success(f"AI識別: {g_res.get('object_name', '')}")
                st.caption(f"推測材質: {', '.join(g_res.get('estimated_materials', []))}")
        else:
            st.info("📷 尚未上傳照片")

    # 模態 2: 敲擊聲響
    audio_analysis = st.session_state.get("audio_analysis")
    with col2:
        st.markdown("#### 🎵 模態 2：敲擊聲響")
        audio_file = st.file_uploader("上傳敲擊音訊 (或自動載入聲響頁面)", type=["wav", "mp3", "m4a"], key="fusion_audio_uploader")
        if audio_file:
            audio_bytes = audio_file.read()
            st.session_state["audio_bytes"] = audio_bytes
            audio_analysis = material_engine.analyze_audio_bytes(audio_bytes)
            st.session_state["audio_analysis"] = audio_analysis

        if audio_analysis:
            st.metric("⚡ 峰值 Peak Freq", f"{audio_analysis.get('peak_freq', 0)} Hz")
            st.caption(f"剛性: {'高音硬質' if audio_analysis.get('is_high_pitch') else '低音延展'}")
        
        opts_sound = ["A. 硬質敲擊聲 (ABS, PS, PVC, 硬PP)", "B. 柔軟延展韌性 (PE, 軟PP)", "C. 打包帶/帶狀 (PP, PET)"]
        def_sound_idx = 0
        if st.session_state.get("sound_test"):
            for idx, o in enumerate(opts_sound):
                if o.startswith(st.session_state["sound_test"][0]):
                    def_sound_idx = idx

        selected_sound = st.selectbox("聲音選項確認", opts_sound, index=def_sound_idx)
        st.session_state["sound_test"] = selected_sound

    # 模態 3: 燃燒特徵與氣味
    with col3:
        st.markdown("#### 🎥 模態 3：燃燒與氣味")
        opts_smell = [
            "甲. 柴油/機油味 (PP)",
            "乙. 滴蠟/石蠟味 (PE)",
            "丙. 鹽酸酸臭味/綠焰 (PVC)",
            "丁. 燒焦輪胎味/濃黑煙 (ABS)",
            "戊. 化學甜味/碳黑 (PS)"
        ]
        def_smell_idx = 0
        if st.session_state.get("burn_test"):
            for idx, o in enumerate(opts_smell):
                if o.startswith(st.session_state["burn_test"][0]):
                    def_smell_idx = idx

        selected_smell = st.selectbox("1. 燃燒氣味觀察", opts_smell, index=def_smell_idx)
        st.session_state["burn_test"] = selected_smell

        opts_flame = ["黃色火焰/黃黃滴落 (PE/PP)", "綠色火焰/酸臭 (PVC)", "濃濃黑煙/輪胎 (ABS/PS)", "離火即熄/自熄 (PVC/ABS)"]
        def_flame_idx = 0
        if st.session_state.get("flame_choice"):
            for idx, o in enumerate(opts_flame):
                if o.startswith(st.session_state["flame_choice"][:2]):
                    def_flame_idx = idx

        selected_flame = st.selectbox("2. 火焰形態觀察", opts_flame, index=def_flame_idx)
        st.session_state["flame_choice"] = selected_flame

    st.markdown("---")

    # 物理約束: 水中浮沉
    st.markdown("#### 🌊 物理約束：水中浮沉測試")
    opts_float = ["1. 浮於水面 (ρ < 1.0 g/cm³, 候選: PP, PE)", "2. 沉於水底 (ρ > 1.0 g/cm³, 候選: ABS, PVC, PS, PET)"]
    def_float_idx = 0 if st.session_state.get("float_test") == 1 else 1
    float_input = st.radio("浮沉選項：", opts_float, index=def_float_idx, horizontal=True)
    st.session_state["float_test"] = 1 if "1." in float_input else 2

    # 自動即時計算與按鈕觸發
    fusion_res = material_engine.calculate_fusion_prediction(
        float_choice=st.session_state["float_test"],
        sound_choice=st.session_state.get("sound_test"),
        smell_choice=st.session_state.get("burn_test"),
        audio_analysis=st.session_state.get("audio_analysis"),
        gemini_analysis=st.session_state.get("gemini_result"),
        flame_choice=st.session_state.get("flame_choice")
    )
    st.session_state["fusion_final_result"] = fusion_res

    # 渲染結果
    render_fusion_result_card(st.session_state["fusion_final_result"])
