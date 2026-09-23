import os
import streamlit as st
import pandas as pd
from services.media_loader import MediaLoader, EXCEL_PATH

def render_database_page(media_loader: MediaLoader):
    """📚 材質資料庫頁面 (V3.0 卡片預設收合 & 高對比搜尋版)"""
    st.subheader("📚 廢料履歷資料庫 (Material Database)")
    st.caption("收錄天辰廢料大數據，提供材質特性、水中浮沉、燃燒特徵與標準影音樣本比對。")

    # Excel 下載與搜尋列
    col_search, col_dl = st.columns([3, 1])

    with col_dl:
        if os.path.exists(EXCEL_PATH):
            with open(EXCEL_PATH, "rb") as f:
                st.download_button(
                    label="📥 下載 Excel",
                    data=f.read(),
                    file_name="天辰廢料全循環履歷系統品項.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    with col_search:
        search_kw = st.text_input("🔍 關鍵字搜尋（如：寶特瓶、水管、鹽酸、石蠟...）：", "")

    mat_filter = st.selectbox("材質分類篩選：", ["全部 (All)", "ABS", "PVC", "PS", "PP", "PE", "PET"])

    st.markdown("---")

    materials_data = media_loader.materials_data

    # 進行搜尋與過濾
    filtered_items = {}
    for mat_code, info in materials_data.items():
        if mat_filter != "全部 (All)" and mat_code != mat_filter:
            continue
        
        info_str = " ".join([str(v) for v in info.values()])
        if search_kw and search_kw.lower() not in info_str.lower():
            continue

        filtered_items[mat_code] = info

    st.caption(f"共找到 {len(filtered_items)} 筆符合條件的材質條目（預設收合卡片，點擊展開查看影音）")

    for mat_code, info in filtered_items.items():
        title = f"📦 【{mat_code}】{info.get('材質', mat_code)} | 浮沉: {info.get('水中浮沉', 'NA')} | 常見物: {info.get('市場常用名稱', 'NA')}"
        with st.expander(title, expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**產源產業別**：{info.get('產源產業別', 'NA')}")
                st.markdown(f"**原始用途**：{info.get('原始用途', 'NA')}")
                st.markdown(f"**水中浮沉**：{info.get('水中浮沉', 'NA')}")
            with col2:
                st.markdown(f"**燃燒特徵**：\n{info.get('燃燒特徵', 'NA')}")
                st.markdown(f"**關鍵字標籤**：\n{info.get('關鍵字', 'NA')}")

            # 媒體檔對照
            media_ref = media_loader.get_reference_media(mat_code)
            sounds = media_ref.get("sounds", [])
            videos = media_ref.get("videos", [])

            m1, m2 = st.columns(2)
            with m1:
                if sounds:
                    st.caption("🎵 標準敲擊聲音檔：")
                    for s in sounds:
                        if os.path.exists(s['path']):
                            st.audio(s['path'])
                        else:
                            st.caption(f"• {s['filename']}")
            with m2:
                if videos:
                    st.caption("🎥 標準燃燒影片檔：")
                    for v in videos:
                        if os.path.exists(v['path']):
                            st.video(v['path'])
                        else:
                            st.caption(f"• {v['filename']}")
