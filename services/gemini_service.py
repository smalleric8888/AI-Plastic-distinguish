import os
import requests
import json
import base64
from PIL import Image
import io
import streamlit as st

class GeminiService:
    def __init__(self, api_key=None):
        # 讀取 Streamlit Secrets、環境變數或 Session State 中的 GEMINI_API_KEY
        key_from_secrets = None
        try:
            if "GEMINI_API_KEY" in st.secrets:
                key_from_secrets = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass

        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or key_from_secrets or st.session_state.get("user_gemini_api_key")

    def analyze_image_structured(self, image_input):
        """
        1. 當傳入圖像時，壓縮尺寸為適合網路發送之 400px JPEG。
        2. 若有 GEMINI_API_KEY，呼叫 Google Gemini 3.5/3.6 Flash 多模態 Vision API 進行實時解析。
        3. 若未設定 API Key，執行動態圖像像素色度與形態分析。
        """
        if image_input is None:
            return None

        # 轉換與壓縮 PIL Image
        img = None
        if isinstance(image_input, Image.Image):
            img = image_input
        else:
            try:
                img = Image.open(image_input)
            except Exception:
                img = None

        if img:
            # 複製並縮放圖片提升發送速度
            img_copy = img.copy()
            img_copy.thumbnail((400, 400))
            buf = io.BytesIO()
            img_copy.convert("RGB").save(buf, format="JPEG", quality=85)
            img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

            # 嘗試呼叫 Gemini 多模態 API (若有金鑰)
            if self.api_key:
                for model_name in ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-flash-latest"]:
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                        prompt = """你是一位專業的塑膠廢料回收與材質鑑定專家。請分析這張照片中的物品：
1. 辨識照片中的主要物品（如：寶特瓶、瓶蓋、塑膠水管、工具握把、保鮮盒等）。
2. 描述外觀顏色與形態特徵。
3. 依據全球工業應用，推測其可能材質 (ABS, PVC, PS, PP, PE, PET)。
4. 給出簡短專業的推論說明。
請以繁體中文簡潔回答。"""

                        payload = {
                            "contents": [{
                                "parts": [
                                    {"text": prompt},
                                    {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
                                ]
                            }]
                        }
                        res = requests.post(url, json=payload, timeout=12)
                        if res.status_code == 200:
                            analysis_text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                            
                            estimated = ["PP", "PE", "ABS"]
                            upper_t = analysis_text.upper()
                            detected_mats = [m for m in ["PET", "PVC", "ABS", "PS", "PP", "PE"] if m in upper_t]
                            if detected_mats:
                                estimated = detected_mats

                            return {
                                "status": "success",
                                "object_name": f"Gemini 實時視覺 AI ({model_name})",
                                "color_appearance": "依照片色彩與圖像實時解析",
                                "estimated_materials": estimated,
                                "reasoning": analysis_text
                            }
                    except Exception:
                        continue

            # 動態影像像素備援分析 (當無 API Key 或連線異常時)
            w, h = img.size
            aspect = w / h if h > 0 else 1.0
            img_small = img.resize((50, 50)).convert('RGB')
            pixels = list(img_small.getdata())
            avg_r = sum(p[0] for p in pixels) / len(pixels)
            avg_g = sum(p[1] for p in pixels) / len(pixels)
            avg_b = sum(p[2] for p in pixels) / len(pixels)
            brightness = (avg_r + avg_g + avg_b) / 3.0

            if brightness < 70:
                color_desc = "深色/黑色 (黑色染色件或硬質外殼)"
                mat_candidates = ["ABS", "PS", "PVC"]
                reason = "深色或黑色硬質組件常用於家電外殼、汽車保桿、工具手把或排水管道 (ABS/PVC/PS)。"
            elif brightness > 190:
                color_desc = "白色/乳白色/半透明 (自然原色或吹瓶)"
                mat_candidates = ["PE", "PP", "PS"]
                reason = "白色或半透明容器常用於食品級包裝、鮮奶瓶、清潔劑桶或微波保鮮盒 (PE/PP)。"
            elif avg_b > avg_r and avg_b > avg_g:
                color_desc = "藍色/藍白相間 (容器瓶蓋或包裝膜)"
                mat_candidates = ["PET", "PP", "PE"]
                reason = "藍色螺紋瓶蓋極高比例為 PP，透明寶特瓶身為 PET，包裝膜為 PE。"
            else:
                color_desc = "多色染色件/雜料碎片"
                mat_candidates = ["PP", "ABS", "PE"]
                reason = "多色染色射出件常見於日用塑膠製品、收納盒或零件碎料。"

            form_desc = "長條狀/管材" if aspect > 2.2 else ("直立柱狀/瓶罐" if aspect < 0.65 else "塊狀/結構零件")

            return {
                "status": "success",
                "object_name": f"上傳照片動態視覺標的 ({form_desc})",
                "color_appearance": f"{color_desc} (分辨率: {w}x{h} px)",
                "estimated_materials": mat_candidates,
                "reasoning": reason
            }

        return {
            "status": "fallback",
            "object_name": "待測塑膠樣品",
            "color_appearance": "無法讀取影像特徵",
            "estimated_materials": ["PP", "PE", "ABS"],
            "reasoning": "請確認上傳有效的圖片檔。"
        }
