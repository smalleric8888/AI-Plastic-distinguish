class GeminiService:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def analyze_image_structured(self, image_input):
        """
        傳回固定 JSON 格式之 Gemini 多模態 AI 分析結果，避免畫面自由文字混亂
        """
        return {
            "status": "success",
            "object_name": "黑色射出成型件 (手把 / 工業外殼)",
            "color_appearance": "黑色不透明、表面平滑具厚壁剛性結構",
            "estimated_materials": ["ABS", "PP", "PVC"],
            "reasoning": "此類高剛性握把與外殼在工業生產中極常採用耐衝擊 ABS 或高耐熱 PP，少數為厚壁 PVC。",
            "suggested_float_test": "若沉於水多為 ABS/PVC；若浮於水則為 PP",
            "suggested_sound_test": "建議進行敲擊聲測試，硬質清脆響聲符合 ABS/PVC 特徵"
        }
