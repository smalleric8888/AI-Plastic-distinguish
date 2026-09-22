import os
import streamlit as st
from components.charts import plot_confidence_top3_chart

def render_prediction_result_card(prediction_res):
    """渲染綜合判定結果卡片 (含 Top 3 排名與吻合度標籤)"""
    top3 = prediction_res["top3"]
    top1 = top3[0]
    top1_mat = top1["material"]
    top1_conf = top1["confidence"]
    info = prediction_res["material_info"]
    media = prediction_res["reference_media"]
    is_matched = prediction_res["is_ai_test_matched"]
    gemini_mat = prediction_res["gemini_predicted_material"]

    # 主 Banner
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 18px; border-radius: 16px; text-align: center; margin-top: 10px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);">
        <h2 style="margin:0; font-size: 24px;">🥇 最高機率材質：{top1_mat} ({info.get('材質', top1_mat)})</h2>
        <h3 style="margin:6px 0 0 0; font-size: 20px;">AI 綜合信心度：{top1_conf}%</h3>
    </div>
    """, unsafe_allow_html=True)

    # 照片 AI 與 人工測試 吻合度標籤
    if gemini_mat:
        if is_matched:
            st.success(f"✅ 驗證結果：照片模型初辨 ({gemini_mat}) 與人工三步測試 ({top1_mat}) 【完全吻合】！")
        else:
            st.warning(f"⚠️ 驗證提醒：照片模型初辨可能為 {gemini_mat}，但人工實測特徵更符合 {top1_mat}。建議依實測結果判定。")

    # 繪製 Top-3 排名圖
    plot_confidence_top3_chart(top3)

    # 詳細特徵對比
    st.subheader("🔬 診斷依據與天辰履歷數據比對")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**市場常用名稱**：{info.get('市場常用名稱', 'NA')}")
        st.markdown(f"**產源產業別**：{info.get('產源產業別', 'NA')}")
        st.markdown(f"**原始用途**：{info.get('原始用途', 'NA')}")
        st.markdown(f"**水中浮沉**：{info.get('水中浮沉', 'NA')}")
    with col2:
        st.markdown(f"**燃燒特徵說明**：\n{info.get('燃燒特徵', 'NA')}")
        st.markdown(f"**AI 辨識領域**：\n{info.get('關鍵字', 'NA')}")

    st.markdown("---")

    # 媒體對照
    st.subheader(f"📁 天辰資料庫對照媒體 ({top1_mat} 專屬影音)")
    m_col1, m_col2, m_col3 = st.columns(3)

    with m_col1:
        st.markdown("#### 🎵 標準敲擊聲")
        sounds = media.get("sounds", [])
        if sounds:
            for s in sounds:
                st.caption(f"檔名：{s['filename']}")
                if os.path.exists(s['path']):
                    st.audio(s['path'])
        else:
            st.info("尚無實體聲音檔")

    with m_col2:
        st.markdown("#### 🎥 燃燒實驗影片")
        videos = media.get("videos", [])
        if videos:
            for v in videos:
                st.caption(f"檔名：{v['filename']}")
                if os.path.exists(v['path']):
                    st.video(v['path'])
        else:
            st.info("尚無實體燃燒影片")

    with m_col3:
        st.markdown("#### 📷 樣品參考照")
        samples = media.get("samples", [])
        if samples and samples[0]["images"]:
            for img_p in samples[0]["images"][:1]:
                if os.path.exists(img_p):
                    st.image(img_p, caption=os.path.basename(img_p), use_container_width=True)
        else:
            st.info("尚無對照照片")
