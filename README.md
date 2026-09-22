# ♻️ 天辰 AI 塑膠材質模擬辨識系統 (Tianchen AI Plastic Identification System)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

本系統是一套結合 **Gemini 多模態 AI 大數據庫** 與 **天辰廢料全循環履歷資料庫** 的手機 Web (PWA) 塑膠材質辨識系統。系統支援 **照片拍攝/上傳**、**敲擊聲音頻波形與 FFT 頻譜分析**、**燃燒實驗影片分析**，並結合 **三步引導式診斷問答**，快速推估廢料材質（PP、PE、ABS、PVC、PS、PET 等）與信心度比分，並提供天辰實體影音對比。

---

## 🌟 核心功能與亮點 (Key Features)

```
┌─────────────────────────────────────────────────────────────────────────┐
│              🤖 第一關：Gemini 多模態 AI 大數據庫初步分析               │
│  🔍 物品輪廓與顏色辨識  │ 💡 提示全球工業常用材質  │ 📝 建議測試選項與用途分析   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     🎙️ / 🎥 多模態媒體輔助分析                          │
│  🎵 音訊上傳 (.m4a/.mp3)：即時繪製時域波形與 FFT 頻譜主頻率 (Hz)        │
│  🎥 影片上傳 (.mp4)：火焰顏色 (如 PVC 綠焰) 與煙霧濃度採樣               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    🔍 實體驗證：三步引導式診斷問答                       │
│  Step 1: 水中浮沉測試 (ρ < 1.0 g/cm³ 浮水 vs ρ > 1.0 g/cm³ 沉水)        │
│  Step 2: 觸感與剛性聲音特徵 (硬質敲擊聲 / 柔軟延展 / 打包帶)            │
│  Step 3: 燃燒特徵與氣味 (柴油味 / 石蠟味 / 鹽酸酸臭與綠焰 / 燒焦輪胎味)  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 📊 最終推估報告 ✕ 天辰資料庫實體影音對照                 │
│  🥇 材質信心度百分比儀表板  │ 🎵 播放標準敲擊聲  │ 🎥 播放燃燒實驗影片  │
└─────────────────────────────────────────────────────────────────────────┘
```

1. **🤖 Gemini 多模態 AI 大數據庫初步分析**：
   - 載入照片後，自動進行物品形態、顏色、工業用途解析與材質候選預測。
2. **🎵 聲學波形與 FFT 頻譜分析**：
   - 支援上傳 `.m4a` / `.wav` / `.mp3` 敲擊聲音檔。
   - 即時繪製**時域波形圖**與**快速傅立葉 (FFT) 頻譜圖**，判定高頻金屬響聲 ($>2200 \text{ Hz}$) 或低頻沉悶聲。
3. **🎥 燃燒影片視覺分析**：
   - 支援上傳 `.mp4` 燃燒實錄影片，進行綠底火焰（PVC 標誌）、藍底火焰與煙霧濃度檢測。
4. **📁 天辰履歷庫實體影音對照**：
   - 對照天辰獨立 `聲音檔/` (13 個 .m4a 檔) 與 `影片檔/` (8 個 .mp4 燃燒影片)，結果頁可直接播放標準影音進行實體驗證。

---

## 📂 專案檔案結構 (Project Structure)

```text
├── app.py                         # Streamlit Web 手機 App 主程式與多模態介面
├── plastic_data_loader.py         # 天辰廢料履歷資料庫 (Excel/音訊/影片) 載入模組
├── plastic_identifier_engine.py   # 雙層 AI 推估算法、聲學 FFT 與影像分析引擎
├── requirements.txt               # 雲端部署環境依賴套件清單
└── README.md                      # 專案說明文件
```

---

## 🛠️ 本地端快速啟動 (Local Quick Start)

### 1. 複製專案與安裝套件
```bash
git clone https://github.com/smalleric8888/AI-Plastic-distinguish.git
cd AI-Plastic-distinguish
pip install -r requirements.txt
```

### 2. 啟動 Streamlit Web 服務
```bash
streamlit run app.py
```
啟動後瀏覽器打開 `http://localhost:8501` 即可進行測試！

---

## 🌐 雲端一鍵部署 (Deploy to Streamlit Community Cloud)

1. 將本儲存庫 Fork 或 Push 至您的 GitHub。
2. 開啟 [Streamlit Community Cloud](https://share.streamlit.io)。
3. 點擊 **Create App**，填入：
   - **Repository**: `smalleric8888/AI-Plastic-distinguish`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. 點擊 **Deploy!** 即可獲得永久免費的手機 App 網址。

---

## 📱 手機 App 桌面圖示設定 (PWA)

在手機瀏覽器開啟部署完成的網址後：
- **iOS (Safari)**：點擊「分享」圖示 ➔ 選擇 **「新增至主畫面」**。
- **Android (Chrome)**：點擊右上角「⋮」選單 ➔ 選擇 **「新增至主畫面」**。

---

## 📄 授權條款 (License)

本專案採用 [MIT License](LICENSE) 授權。
