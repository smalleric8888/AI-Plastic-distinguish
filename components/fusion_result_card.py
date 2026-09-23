import streamlit as st
import plotly.graph_objects as go

def render_fusion_result_card(res: dict):
    """
    V3.0 多模態綜合鑑定結果渲染卡片
    具備：零證據保護、相對匹配分數標示、資料完整度Badge、無法判定警告框、收合式雷達圖
    """
    if not res or not res.get("has_evidence"):
        st.markdown("""
        <div class="empty-state-box">
            <h4>📷 尚未提供測試數據</h4>
            <p>請於上方上傳廢料照片或進行物理診斷測試。系統將即時為您生成多模態相對匹配分數與判定報告。</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("---")
    st.subheader("🔬 塑膠材質初步辨識報告 (V3.0)")

    top1 = res["top1_material"]
    match_score = res["relative_match_score"]
    status = res["consistency_status"]
    completeness = res["evidence_completeness"]
    is_undetermined = res.get("is_undetermined", False)

    # 1. 主結果卡片 (高對比色系)
    st.markdown(f"""
    <div style="background: #0F172A; padding: 18px; border-radius: 14px; color: #FFFFFF; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="background: #2563EB; color: #FFFFFF; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.85rem;">完整度: {completeness}</span>
            <span style="color: #E2E8F0; font-size: 0.85rem;">{status}</span>
        </div>
        <h2 style="margin: 8px 0 4px 0; color: #38BDF8; font-size: 24px;">🏆 最優估算材質：{top1} <span style="font-size: 1.1rem; color: #4ADE80;">(相對匹配分數: {match_score}%)</span></h2>
        <p style="margin: 0; color: #94A3B8; font-size: 0.85rem;">{res['material_info'].get('full_name', '')} | 密度: {res['material_info'].get('density', '')} | 典型應用: {res['material_info'].get('applications', '')}</p>
        <p style="margin-top: 6px; color: #CBD5E1; font-size: 0.75rem;">※ 此分數為多模態特徵相符度，非實驗室光譜確證對比。結果僅供初步分選參考。</p>
    </div>
    """, unsafe_allow_html=True)

    # 2. 無法判定警告框 (當同分、衝突或證據少於 2 項時)
    if is_undetermined:
        st.markdown(f"""
        <div class="warning-box">
            <b>🔴 系統警示：無法可靠確定單一材質</b><br>
            {res.get('undetermined_reason', '')}<br>
            <b>建議下一步</b>：請嘗試補全敲擊聲音或燃燒觀察；若為高價值塑料，請送實驗室進行 <b>FTIR / NIR 光譜標準檢測</b>。
        </div>
        """, unsafe_allow_html=True)

    # 3. Top-3 排名與相對匹配分數
    st.markdown("#### 📊 材質相對匹配分數排名")
    for idx, item in enumerate(res["top3"]):
        mat = item["material"]
        score = item["relative_match_score"]
        badge = "🥇 首選候選" if idx == 0 else ("🥈 次選候選" if idx == 1 else "🥉 備選候選")
        st.write(f"**{badge} {mat}** — 相對匹配分數: `{score}%`")
        st.progress(min(1.0, score / 100.0))

    # 4. 可收合多模態雷達圖與證據鏈細節
    with st.expander("🔍 查看多模態契合度雷達圖與三路證據鏈對比", expanded=False):
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("**🧬 三路證據對比細節**")
            ev = res.get("evidence_chain", {})
            st.markdown(f"""
            - 📸 **照片視覺 (Gemini)**：`{ev.get('vision', '未測試')}`
            - 🎵 **敲擊聲響 (FFT)**：`{ev.get('acoustic', '未測試')}`
            - 🎥 **熱解燃燒氣味**：`{ev.get('thermal', '未測試')}`
            """)

        with col_right:
            st.markdown("**🕸️ 三路特徵契合度雷達圖**")
            categories = ['視覺外觀', '敲擊剛性', '熱解氣味']
            fig = go.Figure()
            colors = ['#38BDF8', '#818CF8', '#F472B6']
            
            for idx, (r_mat, scores_list) in enumerate(res.get("radar_data", {}).items()):
                fig.add_trace(go.Scatterpolar(
                    r=scores_list + [scores_list[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    name=f"{r_mat}",
                    line_color=colors[idx % len(colors)]
                ))

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                margin=dict(l=20, r=20, t=20, b=20),
                height=240
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 5. 天辰實體影音對照庫
    st.subheader("📚 天辰廢料實體影音比對")
    col_ref1, col_ref2 = st.columns([1, 1])
    ref_media = res.get("reference_media", {})

    with col_ref1:
        st.markdown("**📷 天辰標準廢料參考圖**")
        if ref_media.get("image_path"):
            st.image(ref_media["image_path"], caption=f"天辰 {top1} 標準廢料參考樣品", use_container_width=True)
        else:
            st.info("尚無實體參考照片")

    with col_ref2:
        st.markdown("**🎥 燃燒對照影片與處置建議**")
        if ref_media.get("video_path"):
            st.video(ref_media["video_path"])
        else:
            st.info("尚無標準燃燒影片")
        
        st.markdown(f"**回收處置說明**：{res['material_info'].get('recycle_note', '進行分類打包與造粒再生')}")
