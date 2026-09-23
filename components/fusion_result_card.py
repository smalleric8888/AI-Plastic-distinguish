import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_fusion_result_card(res: dict):
    """
    V2.0 全模態 3-in-1 綜合結果渲染卡片
    包含：Top-3 信心度、三路一致性狀態、Plotly 雷達圖、三路證據對比、天辰廢料庫對照
    """
    st.markdown("---")
    st.subheader("🔬 V2.0 全模態 3-in-1 綜合判定報告")

    # 一致性與 Top1 標題
    top1 = res["top1_material"]
    top1_conf = res["top1_confidence"]
    status = res["consistency_status"]

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 18px; border-radius: 12px; color: white; margin-bottom: 20px; border: 1px solid #334155;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="background: #3b82f6; color: white; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.85rem;">V2.0 全模態引擎</span>
            <span style="font-weight: bold; font-size: 0.9rem;">{status}</span>
        </div>
        <h2 style="margin: 10px 0 5px 0; color: #38bdf8;">🏆 最佳估算材質：{top1} <span style="font-size: 1.2rem; color: #4ade80;">({top1_conf}%)</span></h2>
        <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">{res['material_info'].get('full_name', '')} | 密度: {res['material_info'].get('density', '')} | 典型應用: {res['material_info'].get('applications', '')}</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### 📊 Top-3 綜合排名與信心度")
        for idx, item in enumerate(res["top3"]):
            mat = item["material"]
            conf = item["confidence"]
            badge = "🥇 首選" if idx == 0 else ("🥈 次選" if idx == 1 else "🥉 備選")
            st.write(f"**{badge} {mat}** - {conf}%")
            st.progress(min(1.0, conf / 100.0))

        st.markdown("#### 🧬 三路證據鏈一致性比對")
        ev = res.get("evidence_chain", {})
        st.markdown(f"""
        - 📸 **照片視覺 (Gemini)**：`{ev.get('vision', '無')}`
        - 🎵 **敲擊聲響 (FFT)**：`{ev.get('acoustic', '無')}`
        - 🎥 **熱解燃燒氣味**：`{ev.get('thermal', '無')}`
        """)

    with col_right:
        st.markdown("#### 🕸️ 三路特徵契合度雷達圖")
        categories = ['視覺外觀', '敲擊剛性', '熱解氣味']
        fig = go.Figure()

        colors = ['#38bdf8', '#818cf8', '#f472b6']
        for idx, (r_mat, scores) in enumerate(res.get("radar_data", {}).items()):
            fig.add_trace(go.Scatterpolar(
                r=scores + [scores[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name=f"{r_mat}",
                line_color=colors[idx % len(colors)]
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True,
            margin=dict(l=30, r=30, t=20, b=20),
            height=260
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 天辰廢料對照庫
    st.subheader("📚 天辰廢料實體媒體對照")
    col_ref1, col_ref2 = st.columns([1, 1])
    ref_media = res.get("reference_media", {})

    with col_ref1:
        st.markdown("**📷 標準廢料照片**")
        if ref_media.get("image_path"):
            st.image(ref_media["image_path"], caption=f"天辰 {top1} 標準參考樣品", use_container_width=True)
        else:
            st.info("尚無實體參考照片")

    with col_ref2:
        st.markdown("**🎥 燃燒影片與處置建議**")
        if ref_media.get("video_path"):
            st.video(ref_media["video_path"])
        else:
            st.info("尚無標準燃燒影片")
        
        st.markdown(f"**回收建議**：{res['material_info'].get('recycle_note', '進行分類與造粒再生')}")
