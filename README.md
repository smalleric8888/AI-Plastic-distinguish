# ♻️ 塑膠材質初步辨識系統 V3.0 (Tianchen Plastic Material Identification System V3.0)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-plastic-distinguish-dbakjmlh2tvfaexwaynjip.streamlit.app)
![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

本系統是一套結合 **Gemini 3.5 Flash 多模態 AI** 與 **天辰廢料全循環履歷大數據庫** 的手機/Web 多模態塑膠材質初步鑑定系統。

V3.0 版本完成重大的 **UX/UI、WCAG 2.1 AA 高對比度與「零證據零輸出」可信度重構**，嚴格確保未提供測試數據前絕對不輸出假材質排名，並引入「相對匹配分數」、「資料完整度 Badge」與「無法判定/光譜複核保護卡」。

---

## 🌟 V3.0 核心亮點與體驗重構 (V3.0 Key Features)

```
┌─────────────────────────────────────────────────────────────────────────┐
│              🔬 V3.0 塑膠材質初步辨識系統 (零證據保護機制)              │
├────────────────────┬────────────────────┬───────────────────────────────┤
│ 📸 模態1: 視覺照片  │ 🌊 模態2: 水中浮沉  │ 🎵 模態3: 敲擊聲響 & 熱解氣味 │
│ (Gemini 3.5 Flash) │ (ρ < 1.0 / > 1.0)  │ (15秒錄音指引 / 實用通風提醒) │
└────────────────────┴────────────────────┴───────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               🧠 多模態特徵評分與「無法判定」保護引擎                  │
│  無預設解答 + 證據完整度 (X/4) + 相對匹配分數 + 衝突檢測保護機制       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 📊 V3.0 初步診斷報告 ✕ 收合式雷達圖與資料庫             │
│ 🥇 相對匹配分數排名 │ 🔴 無法判定/光譜複核卡 │ 📚 81筆預設收合廢料庫 │
└─────────────────────────────────────────────────────────────────────────┘
```

1. **🛡️ 零證據零輸出原則**：
   - 移除所有問答選單的預設勾選（全數預設 `(未測試 / 請選擇)`）。
   - 未上傳照片或完成任何實體測試前，**不顯示**任何材質名稱與百分比，僅呈現引導提示卡。
2. **♿ WCAG 2.1 AA 無障礙高對比度**：
   - 重構全站 CSS 色彩 Token，內文全面採用 Dark Slate (`#1e293b`) 與高對比背景，戶外與手機螢幕清晰可讀。
3. **📊 相對匹配分數與「無法判定」保護**：
   - 信心度名詞調整為 **「相對匹配分數 (Relative Match Score)」**，並註明「非實驗室光譜確證檢驗」。
   - 標示「已完成 X/4 項測試，資料完整度 Y%」。
   - 當數據低於 2 項、同分（< 5%）或特徵衝突時，主動觸發 **「🔴 無法可靠判定 / 建議送 FTIR/NIR 光譜檢驗」**。
4. **🔥 實用通風與高溫安全提醒**：
   - 燃燒頁面提供實用的通風與火源安全提示卡，開放直接選擇，無需阻礙操作。
5. **📚 預設收合材質資料庫**：
   - 天辰 81 筆廢料項目採預設收合 (`st.expander(..., expanded=False)`)，大幅降低手機掃讀成本。

---

## 📂 專案檔案結構 (Project Structure)

```text
├── app.py                         # V3.0 Streamlit Web 主程式與全頁面路由
├── pages/                         # 模組化頁面分發
│   ├── fusion.py                  # V3.0 綜合辨識主頁面 (4步引導 & 零證據保護)
│   ├── identify.py                # 漸進式照片辨識與診斷問答頁面
│   ├── audio.py                   # 敲擊聲響波形與 15 秒錄音指引頁面
│   ├── combustion.py             # 燃燒觀察與通風安全提醒頁面
│   └── database.py                # [V3.0] 預設收合廢料庫搜尋頁面
├── services/                      # 後端核心服務
│   ├── material_engine.py         # [V3.0] 零證據保護、相對匹配分數與無法判定評分引擎
│   ├── gemini_service.py          # Gemini 3.5 Flash 視覺 API 連線服務
│   └── media_loader.py            # 天辰廢料履歷資料庫載入與 Cloud 快取
├── components/                    # UI 元件庫
│   ├── fusion_result_card.py     # [V3.0] 匹配分數、無法判定警告框與收合雷達圖卡片
│   └── navigation.py              # 筆直簡潔高對比手機導覽列
├── assets/styles.css              # [V3.0] WCAG AA 高對比 CSS 樣式表
├── requirements.txt               # 依賴套件清單
└── README.md                      # V3.0 專案說明文件
```

---

## 🛠️ 本地端快速啟動 (Local Quick Start)

```bash
# 1. 複製專案與安裝套件
git clone https://github.com/smalleric8888/AI-Plastic-distinguish.git
cd AI-Plastic-distinguish
pip install -r requirements.txt

# 2. 啟動 Streamlit V3.0 Web 服務
streamlit run app.py
```
瀏覽器打開 `http://localhost:8501` 或手機同 Wi-Fi 打開 `http://192.168.x.x:8501` 即可使用！

---

## 📄 授權條款 (License)

本專案採用 [MIT License](LICENSE) 授權。
