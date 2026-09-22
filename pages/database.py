import os
import streamlit as st
import pandas as pd
from services.media_loader import MediaLoader, EXCEL_PATH

def render_database_page(media_loader: MediaLoader):
    """📁 天辰資料庫頁面渲染邏輯 (關鍵字搜尋/篩選/Excel下載)"""
    st.subheader("📁 天辰廢料履歷資料庫 (Database Search & Download)")

    # Excel 下載功能
    col_search, col_dl = st.columns([3, 1])

    with col_dl:
        if os.path.exists(EXCEL_PATH):
            with open(EXCEL_PATH, "rb") as f:
                st.download_button(
                    label="📥 下載 Excel 報表",
                    data=f.read(),
                    file_name="天辰廢料全循環履歷系統品項.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    with col_search:
        search_kw = st.text_input("🔍 搜尋關鍵字（例如：水管、保鮮盒、鹽酸、石蠟...）：", "")

    mat_filter = st.selectbox("篩選材質分類：", ["全部 (All)", "ABS", "PVC", "PS", "PP", "PE"])

    st.markdown("---")

    materials_data = media_loader.materials_data

    # 進行搜尋與過濾
    filtered_items = {}
    for mat_code, info in materials_data.items():
        if mat_filter != "全部 (All)" and mat_code != mat_filter:
            continue
        
        # 關鍵字比對
        info_str = " ".join([str(v) for v in info.values()])
        if search_kw and search_kw.lower() not in info_str.lower():
            continue

        filtered_items[mat_code] = info

    st.caption(f"已找到 {len(filtered_items)} 筆符合條件的材質條目")

    for mat_code, info in filtered_items.items():
        with st.expander(f"📦 【{mat_code}】{info.get('材質', mat_code)} - 常用名：{info.get('市場常用名稱', 'NA')}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**產源產業別**：{info.get('產源產業別', 'NA')}")
                st.markdown(f"**原始用途**：{info.get('原始用途', 'NA')}")
                st.markdown(f"**水中浮沉**：{info.get('水中浮沉', 'NA')}")
            with col2:
                st.markdown(f"**燃燒特徵**：\n{info.get('燃燒特徵', 'NA')}")
                st.markdown(f"**AI 關鍵字領域**：\n{info.get('關鍵字', 'NA')}")

            # 媒體檔對照
            media_ref = media_loader.get_reference_media(mat_code)
            sounds = media_ref.get("sounds", [])
            videos = media_ref.get("videos", [])

            m1, m2 = st.columns(2)
            with m1:
                if sounds:
                    st.caption("🎵 敲擊聲音檔：")
                    for s in sounds:
                        if os.path.exists(s['path']):
                            st.audio(s['path'])
                        else:
                            st.caption(f"• {s['filename']}")
            with m2:
                if videos:
                    st.caption("🎥 燃燒影片檔：")
                    for v in videos:
                        if os.path.exists(v['path']):
                            st.video(v['path'])
                        else:
                            st.caption(f"• {v['filename']}")
