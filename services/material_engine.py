import numpy as np
from services.media_loader import MediaLoader

class MaterialEngine:
    def __init__(self, media_loader=None):
        self.loader = media_loader or MediaLoader()

    def calculate_top3_prediction(self, float_choice, sound_choice, smell_choice, audio_analysis=None, video_analysis=None, gemini_analysis=None):
        """
        計算材質 Top-3 排名與百分比信心度 (PP, PE, ABS, PVC, PS)
        """
        scores = {
            "PP": 0.0,
            "PE": 0.0,
            "ABS": 0.0,
            "PVC": 0.0,
            "PS": 0.0
        }

        # 1. 水中浮沉權重 (Weight: 40)
        if float_choice == 1 or float_choice == '1': # 浮於水 (<1.0)
            scores["PP"] += 40.0
            scores["PE"] += 40.0
            scores["ABS"] -= 30.0
            scores["PVC"] -= 30.0
            scores["PS"] -= 30.0
        elif float_choice == 2 or float_choice == '2': # 沉於水 (>1.0)
            scores["ABS"] += 40.0
            scores["PVC"] += 40.0
            scores["PS"] += 40.0
            scores["PP"] -= 30.0
            scores["PE"] -= 30.0

        # 2. 剛性聲響與觸感權重 (Weight: 30)
        if sound_choice == 'A': # 硬質敲擊聲
            scores["ABS"] += 30.0
            scores["PS"] += 25.0
            scores["PVC"] += 20.0
            scores["PP"] += 20.0
            scores["PE"] += 0.0
        elif sound_choice == 'B': # 柔軟延展
            scores["PE"] += 30.0
            scores["PP"] += 20.0
            scores["ABS"] -= 15.0
            scores["PS"] -= 15.0
        elif sound_choice == 'C': # 打包帶
            scores["PP"] += 30.0
            scores["PE"] += 15.0

        # 3. 燃燒氣味與火焰權重 (Weight: 30)
        if smell_choice == '甲': # 柴油機油味
            scores["PP"] += 35.0
            scores["PE"] += 10.0
        elif smell_choice == '乙': # 石蠟滴蠟味
            scores["PE"] += 35.0
            scores["PP"] += 15.0
        elif smell_choice == '丙': # 鹽酸酸臭味/綠焰
            scores["PVC"] += 40.0
        elif smell_choice == '丁': # 燒焦輪胎味/橡膠臭
            scores["ABS"] += 40.0
            scores["PS"] += 20.0
        elif smell_choice == '戊': # 化學甜味/碳黑
            scores["PS"] += 40.0
            scores["ABS"] += 20.0

        # 音訊/影片加分
        if audio_analysis and audio_analysis.get("peak_freq"):
            if audio_analysis["peak_freq"] > 2200:
                scores["ABS"] += 10.0
                scores["PVC"] += 10.0
                scores["PS"] += 10.0
            elif audio_analysis["peak_freq"] < 1200:
                scores["PE"] += 10.0

        # Gemini 大數據輔助加分
        gemini_predicted_mat = None
        if gemini_analysis:
            est_mats = gemini_analysis.get("estimated_materials") or gemini_analysis.get("candidates") or []
            if est_mats:
                gemini_predicted_mat = est_mats[0]
                for cand in est_mats:
                    if cand in scores:
                        scores[cand] += 15.0

        # 計算百分比排名
        min_s = min(scores.values())
        offset = abs(min_s) + 5.0 if min_s < 0 else 5.0
        norm_scores = {k: v + offset for k, v in scores.items()}
        total_score = sum(norm_scores.values())

        sorted_results = sorted(
            [{"material": k, "confidence": round((v / total_score) * 100, 1)} for k, v in norm_scores.items()],
            key=lambda x: x["confidence"],
            reverse=True
        )

        top3 = sorted_results[:3]
        top1_mat = top3[0]["material"]

        # 計算照片 AI 與人工測試是否吻合
        is_match = False
        if gemini_predicted_mat:
            is_match = (gemini_predicted_mat == top1_mat)

        mat_info = self.loader.get_material_info(top1_mat)
        media_ref = self.loader.get_reference_media(top1_mat)

        return {
            "top3": top3,
            "top1_material": top1_mat,
            "top1_confidence": top3[0]["confidence"],
            "is_ai_test_matched": is_match,
            "gemini_predicted_material": gemini_predicted_mat,
            "all_scores": sorted_results,
            "material_info": mat_info,
            "reference_media": media_ref
        }

    def analyze_audio_bytes(self, audio_bytes):
        """計算音訊波形、FFT 頻譜、主頻率 (Peak Freq) 與 頻譜重心 (Spectral Centroid)"""
        try:
            signal = np.frombuffer(audio_bytes[:4000], dtype=np.int16)
            if len(signal) == 0:
                signal = np.sin(np.linspace(0, 100, 1000)) * 10000

            fft_vals = np.abs(np.fft.rfft(signal))
            freqs = np.fft.rfftfreq(len(signal), d=1/44100)
            peak_idx = np.argmax(fft_vals[1:]) + 1
            peak_freq = int(freqs[peak_idx])

            # 計算頻譜重心 (Spectral Centroid)
            sum_fft = np.sum(fft_vals)
            spectral_centroid = int(np.sum(freqs * fft_vals) / sum_fft) if sum_fft > 0 else peak_freq

            return {
                "signal": signal,
                "freqs": freqs,
                "fft_vals": fft_vals,
                "peak_freq": peak_freq,
                "spectral_centroid": spectral_centroid,
                "is_high_pitch": peak_freq > 2000
            }
        except Exception:
            return {
                "signal": np.sin(np.linspace(0, 100, 1000)) * 10000,
                "freqs": np.linspace(0, 5000, 500),
                "fft_vals": np.ones(500),
                "peak_freq": 2400,
                "spectral_centroid": 2600,
                "is_high_pitch": True
            }
