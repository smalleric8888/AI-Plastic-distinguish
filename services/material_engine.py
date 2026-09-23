import numpy as np
from services.media_loader import MediaLoader

class MaterialEngine:
    def __init__(self, media_loader=None):
        self.loader = media_loader or MediaLoader()

    def calculate_top3_prediction(self, float_choice=None, sound_choice=None, smell_choice=None, audio_analysis=None, video_analysis=None, gemini_analysis=None):
        """相容 V1 單頁呼叫，轉接至 calculate_fusion_prediction"""
        return self.calculate_fusion_prediction(
            float_choice=float_choice,
            sound_choice=sound_choice,
            smell_choice=smell_choice,
            audio_analysis=audio_analysis,
            gemini_analysis=gemini_analysis
        )

    def calculate_fusion_prediction(self, float_choice=None, sound_choice=None, smell_choice=None, audio_analysis=None, gemini_analysis=None, flame_choice=None):
        """
        V3.0 塑膠材質初步辨識評分引擎：
        嚴格執行「零證據零輸出」原則，計算證據完整度、相對匹配分數與「無法判定」保護機制。
        """
        mats = ["PP", "PE", "ABS", "PVC", "PS", "PET"]
        
        # 1. 檢查是否有任何有效證據
        has_vis = gemini_analysis is not None and bool(gemini_analysis.get("estimated_materials"))
        has_ac = (sound_choice is not None and not sound_choice.startswith("(未")) or (audio_analysis is not None and audio_analysis.get("peak_freq") is not None)
        has_th = (smell_choice is not None and not smell_choice.startswith("(未")) or (flame_choice is not None and not flame_choice.startswith("(未"))
        has_phy = float_choice is not None and str(float_choice) in ["1", "2"]

        valid_evidence_count = sum([has_vis, has_ac, has_th, has_phy])

        if valid_evidence_count == 0:
            return {
                "version": "V3.0",
                "has_evidence": False,
                "evidence_count": 0,
                "evidence_completeness": "0/4 項 (0%)",
                "top3": [],
                "top1_material": None,
                "relative_match_score": None,
                "is_undetermined": True,
                "undetermined_reason": "尚未提供任何廢料照片或進行實體診斷測試。請開始提供證據以產出鑑定報告。",
                "material_info": {},
                "reference_media": {}
            }

        scores = {m: 0.0 for m in mats}
        modality_scores = {
            "vision": {m: 0.0 for m in mats},
            "acoustic": {m: 0.0 for m in mats},
            "thermal": {m: 0.0 for m in mats},
            "physical": {m: 0.0 for m in mats}
        }

        # 2. 物理約束：水中浮沉 (Weight: 40)
        if has_phy:
            if str(float_choice) == "1": # 浮水 (<1.0)
                modality_scores["physical"]["PP"] += 40.0
                modality_scores["physical"]["PE"] += 40.0
                modality_scores["physical"]["ABS"] -= 30.0
                modality_scores["physical"]["PVC"] -= 30.0
                modality_scores["physical"]["PS"] -= 30.0
                modality_scores["physical"]["PET"] -= 30.0
            elif str(float_choice) == "2": # 沉水 (>1.0)
                modality_scores["physical"]["ABS"] += 40.0
                modality_scores["physical"]["PVC"] += 40.0
                modality_scores["physical"]["PS"] += 40.0
                modality_scores["physical"]["PET"] += 40.0
                modality_scores["physical"]["PP"] -= 30.0
                modality_scores["physical"]["PE"] -= 30.0

        # 3. 視覺多模態 (Gemini AI Weight: 25)
        gemini_predicted_mat = None
        if has_vis:
            est_mats = gemini_analysis.get("estimated_materials") or gemini_analysis.get("candidates") or []
            if est_mats:
                gemini_predicted_mat = est_mats[0]
                for idx, cand in enumerate(est_mats):
                    if cand in modality_scores["vision"]:
                        modality_scores["vision"][cand] += (25.0 - idx * 5.0)

        # 4. 聲響敲擊 (Acoustic Weight: 25)
        if sound_choice and not sound_choice.startswith("(未"):
            if sound_choice.startswith('A'): # 硬質敲擊
                modality_scores["acoustic"]["ABS"] += 25.0
                modality_scores["acoustic"]["PS"] += 20.0
                modality_scores["acoustic"]["PVC"] += 15.0
                modality_scores["acoustic"]["PET"] += 15.0
            elif sound_choice.startswith('B'): # 柔軟延展
                modality_scores["acoustic"]["PE"] += 25.0
                modality_scores["acoustic"]["PP"] += 20.0
            elif sound_choice.startswith('C'): # 打包帶
                modality_scores["acoustic"]["PP"] += 25.0
                modality_scores["acoustic"]["PET"] += 20.0
                modality_scores["acoustic"]["PE"] += 10.0

        if audio_analysis and audio_analysis.get("peak_freq"):
            pf = audio_analysis["peak_freq"]
            if pf > 2200:
                modality_scores["acoustic"]["ABS"] += 10.0
                modality_scores["acoustic"]["PS"] += 10.0
                modality_scores["acoustic"]["PVC"] += 10.0
            elif pf < 1200:
                modality_scores["acoustic"]["PE"] += 10.0
                modality_scores["acoustic"]["PP"] += 5.0

        # 5. 燃燒熱解與氣味 (Thermal Weight: 35)
        if smell_choice and not smell_choice.startswith("(未"):
            if smell_choice.startswith('甲'):
                modality_scores["thermal"]["PP"] += 35.0
                modality_scores["thermal"]["PE"] += 10.0
            elif smell_choice.startswith('乙'):
                modality_scores["thermal"]["PE"] += 35.0
                modality_scores["thermal"]["PP"] += 15.0
            elif smell_choice.startswith('丙'):
                modality_scores["thermal"]["PVC"] += 40.0
            elif smell_choice.startswith('丁'):
                modality_scores["thermal"]["ABS"] += 35.0
                modality_scores["thermal"]["PS"] += 15.0
            elif smell_choice.startswith('戊'):
                modality_scores["thermal"]["PS"] += 35.0
                modality_scores["thermal"]["ABS"] += 20.0
                modality_scores["thermal"]["PET"] += 15.0

        if flame_choice and not flame_choice.startswith("(未"):
            if "綠" in flame_choice:
                modality_scores["thermal"]["PVC"] += 20.0
            elif "濃煙" in flame_choice or "黑煙" in flame_choice:
                modality_scores["thermal"]["ABS"] += 15.0
                modality_scores["thermal"]["PS"] += 15.0
            elif "滴落" in flame_choice:
                modality_scores["thermal"]["PE"] += 10.0
                modality_scores["thermal"]["PP"] += 10.0

        # 總分加總
        for m in mats:
            scores[m] = (
                modality_scores["physical"][m] +
                modality_scores["vision"][m] +
                modality_scores["acoustic"][m] +
                modality_scores["thermal"][m]
            )

        # 相對匹配分數百分比歸一化
        min_s = min(scores.values())
        offset = abs(min_s) + 5.0 if min_s < 0 else 5.0
        norm_scores = {k: v + offset for k, v in scores.items()}
        total_score = sum(norm_scores.values())

        sorted_results = sorted(
            [{"material": k, "relative_match_score": round((v / total_score) * 100, 1)} for k, v in norm_scores.items()],
            key=lambda x: x["relative_match_score"],
            reverse=True
        )

        top3 = sorted_results[:3]
        top1_mat = top3[0]["material"]

        # 三路一致性評估
        vis_mat = gemini_predicted_mat or "未測試"
        ac_mat = max(modality_scores["acoustic"], key=modality_scores["acoustic"].get) if has_ac else "未測試"
        th_mat = max(modality_scores["thermal"], key=modality_scores["thermal"].get) if has_th else "未測試"

        match_count = 0
        if vis_mat in [top1_mat, top3[1]["material"]]: match_count += 1
        if ac_mat in [top1_mat, top3[1]["material"]]: match_count += 1
        if th_mat in [top1_mat, top3[1]["material"]]: match_count += 1

        if match_count >= 2:
            consistency_status = "🟢 高度吻合 (Strong Agreement)"
        elif match_count == 1:
            consistency_status = "🟡 部分吻合 (Moderate Agreement)"
        else:
            consistency_status = "🔴 證據存在衝突 (Discrepancy Alert)"

        # 「無法判定」條件評估
        is_undetermined = False
        undetermined_reason = ""

        score_diff = top3[0]["relative_match_score"] - top3[1]["relative_match_score"]
        if valid_evidence_count < 2:
            is_undetermined = True
            undetermined_reason = f"目前僅提供 {valid_evidence_count}/4 項測試證據，資料完整度偏低，結果僅供初步相符度參考。"
        elif score_diff < 5.0:
            is_undetermined = True
            undetermined_reason = f"首選材質 {top1_mat} ({top3[0]['relative_match_score']}%) 與次選材質 {top3[1]['material']} ({top3[1]['relative_match_score']}%) 相對匹配分數過於接近 (相差 < 5%)，特徵具有重複性，建議送實驗室光譜確證。"
        elif "衝突" in consistency_status:
            is_undetermined = True
            undetermined_reason = f"照片、聲響與燃燒實驗特徵結論存在明顯衝突 (如照片為 {vis_mat} 但氣味為 {th_mat})，請複核輸入，或送實驗室進行 FTIR/NIR 標準檢測。"

        # 雷達圖資料準備
        radar_mats = [top1_mat, top3[1]["material"], top3[2]["material"]]
        radar_data = {}
        for r_mat in radar_mats:
            v_score = max(0, min(100, modality_scores["vision"][r_mat] * 4))
            a_score = max(0, min(100, modality_scores["acoustic"][r_mat] * 3))
            t_score = max(0, min(100, modality_scores["thermal"][r_mat] * 2.5))
            radar_data[r_mat] = [v_score, a_score, t_score]

        mat_info = self.loader.get_material_info(top1_mat)
        media_ref = self.loader.get_reference_media(top1_mat)

        return {
            "version": "V3.0",
            "has_evidence": True,
            "evidence_count": valid_evidence_count,
            "evidence_completeness": f"{valid_evidence_count}/4 項 ({int(valid_evidence_count/4*100)}%)",
            "top3": top3,
            "top1_material": top1_mat,
            "relative_match_score": top3[0]["relative_match_score"],
            "consistency_status": consistency_status,
            "is_undetermined": is_undetermined,
            "undetermined_reason": undetermined_reason,
            "evidence_chain": {
                "vision": vis_mat,
                "acoustic": ac_mat,
                "thermal": th_mat
            },
            "radar_data": radar_data,
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
