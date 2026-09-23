# ♻️ 天辰 AI 塑膠材質模擬辨識系統 V2.0 (Tianchen AI Plastic Identification System V2.0)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-plastic-distinguish-dbakjmlh2tvfaexwaynjip.streamlit.app)
![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

本系統是一套結合 **Gemini 3.5 Flash 多模態 AI** 與 **天辰廢料全循環履歷大數據庫** 的手機/Web 多模態塑膠材質鑑定系統。
V2.0 版本新增 **「3合1全模態綜合辨識 (3-in-1 Multi-Modal Fusion Analysis)」**，允許使用者在單一介面中同時融合 **照片視覺 AI**、**敲擊聲響頻譜 (FFT)** 與 **熱解燃燒氣味**，由融合診斷引擎動態算演 Top-3 最優估算結果、三路證據鏈契合度與 Plotly 雷達圖。

---

## 🌟 V2.0 核心功能與架構 (V2.0 Key Features)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 🔬 V2.0 3合1全模態綜合辨識 (Unified Fusion)             │
├────────────────────┬────────────────────┬───────────────────────────────┤
│ 📸 模態1: 視覺照片  │ 🎵 模態2: 敲擊聲響  │ 🎥 模態3: 燃燒與氣味          │
│ (Gemini 3.5 Flash) │ (FFT Peak/Centroid)│ (柴油/石蠟/鹽酸/輪胎/化學甜味) │
└────────────────────┴────────────────────┴───────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               🧠 多模態動態權重融合評分引擎 (MaterialEngine)            │
│  物理約束 (浮沉) + 視覺AI (+25) + 聲響FFT (+25) + 熱解氣味 (+35)         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 📊 V2.0 綜合診斷報告 ✕ 三路證據鏈對照                   │
│ 🥇 Top-3 歸一化信心度  │ 🕸️ Plotly 三路契合雷達圖 │ 🟢 證據鏈一致性檢測 │
└─────────────────────────────────────────────────────────────────────────┘
```

1. **🔬 V2.0 3合1全模態綜合辨識 (3-in-1 Fusion)**：
   - 整合照片、聲音波形與燃燒特徵三路數據，提供一站式綜合鑑定報告。
2. **🤖 Gemini 3.5 Flash 實時視覺 AI**：
   - 上傳廢料照片，實時分析物品輪廓、色彩特徵與全球工業應用。
3. **🎵 聲學波形與 FFT 頻譜分析**：
   - 支援敲擊聲音上傳/錄製，計算 Peak Freq (主頻) 與 Spectral Centroid (頻譜重心)，辨識硬質金屬響聲 ($>2200 \text{ Hz}$) 或柔軟低音。
4. **🎥 燃燒影片與熱解氣味觀察**：
   - 提供黃焰、濃煙、綠焰 (PVC) 與特定化學氣味（柴油味 PP / 石蠟味 PE / 輪胎味 ABS / 甜味 PS）對照。
5. **📁 天辰資料庫實體影音對照**：
   - 連接天辰廢料庫，包含標準參考照片與 8 組實體燃燒實驗影片。

---

## 📂 專案檔案結構 (Project Structure)

```text
├── app.py                         # V2.0 Streamlit Web 主程式與頁面路由
├── pages/                         # 模組化頁面分發
│   ├── fusion.py                  # [NEW V2.0] 3合1全模態綜合辨識頁面
│   ├── identify.py                # 漸進式照片與診斷問答頁面
│   ├── audio.py                   # 敲擊聲響波形與 FFT 頻譜頁面
│   ├── combustion.py             # 燃燒實驗影片觀察頁面
│   └── database.py                # 天辰 81 筆廢料大數據搜尋頁面
├── services/                      # 後端核心解耦服務
│   ├── material_engine.py         # [V2.0] 多模態動態融合評分引擎 (calculate_fusion_prediction)
│   ├── gemini_service.py          # Gemini 3.5 Flash 視覺 API 連線服務
│   └── media_loader.py            # 天辰廢料履歷資料庫載入與 Cloud 快取
├── components/                    # UI 元件庫
│   ├── fusion_result_card.py     # [NEW V2.0] 雷達圖與三路證據鏈結果卡片
│   ├── result_card.py             # 基礎排名結果卡片
│   └── navigation.py              # Sticky 手機導覽列
├── assets/styles.css              # 430px Mobile Shell 手機優化 CSS
├── requirements.txt               # 依賴套件清單
└── README.md                      # V2.0 專案說明文件
```

---

## 🛠️ 本地端快速啟動 (Local Quick Start)

### 1. 複製專案與安裝套件
```bash
git clone https://github.com/smalleric8888/AI-Plastic-distinguish.git
cd AI-Plastic-distinguish
pip install -r requirements.txt
```

### 2. 啟動 Streamlit V2.0 Web 服務
```bash
streamlit run app.py
```
瀏覽器打開 `http://localhost:8501` 或手機同 Wi-Fi 打開 `http://192.168.x.x:8501` 即可使用！

---

## 🌐 雲端一鍵部署 (Deploy to Streamlit Community Cloud)

1. 將本儲存庫 Fork 或 Push 至您的 GitHub。
2. 開啟 [Streamlit Community Cloud](https://share.streamlit.io)。
3. 點擊 **Create App**，填入：
   - **Repository**: `smalleric8888/AI-Plastic-distinguish`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. 在 **App Settings -> Secrets** 設定 Key：
   ```toml
   GEMINI_API_KEY = "Your_Gemini_API_Key"
   ```
5. 點擊 **Deploy!** 即可體驗最新 V2.0 手機網頁 App。

---

## 📄 授權條款 (License)

本專案採用 [MIT License](LICENSE) 授權。
