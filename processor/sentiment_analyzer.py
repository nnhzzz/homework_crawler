"""
Module phân tích cảm xúc và dán nhãn bài viết trên Diễn đàn UIT:
- Phân loại: Tốt (POSITIVE), Xấu (NEGATIVE), Trung lập (NEUTRAL).
- Xác định khía cạnh liên quan đến trường: Cơ sở vật chất, Giảng viên, Học phí, ĐKMH, Dịch vụ SV...
- Xử lý phủ định tiếng Việt (ví dụ: 'không tốt' -> negative, 'không hỏng' -> neutral/positive).
- Trích xuất từ khóa bằng chứng (evidence keywords) và điểm độ tin cậy (confidence score).
"""

import re
from typing import Dict, Any, List, Tuple
from config import (
    ASPECTS,
    POSITIVE_KEYWORDS,
    NEGATIVE_KEYWORDS,
    NEGATION_WORDS,
    LABEL_POSITIVE,
    LABEL_NEGATIVE,
    LABEL_NEUTRAL,
    LABEL_NAMES_VI,
)
from processor.text_cleaner import clean_text


class UITSentimentAnalyzer:
    def __init__(self):
        self.aspects = ASPECTS
        self.positive_words = set(POSITIVE_KEYWORDS)
        self.negative_words = set(NEGATIVE_KEYWORDS)
        self.negation_words = set(NEGATION_WORDS)

    def detect_aspects(self, text: str) -> List[Dict[str, Any]]:
        """Phát hiện các khía cạnh về trường được đề cập trong bài viết."""
        detected = []
        text_lower = text.lower()

        for key, info in self.aspects.items():
            matched_kw = []
            for kw in info["keywords"]:
                # Tìm từ khóa nguyên từ hoặc cụm từ
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, text_lower):
                    matched_kw.append(kw)

            if matched_kw:
                detected.append({
                    "aspect_key": key,
                    "aspect_name": info["name"],
                    "matched_keywords": matched_kw,
                    "count": len(matched_kw)
                })

        # Sắp xếp theo số lượng từ khóa xuất hiện nhiều nhất
        detected.sort(key=lambda x: x["count"], reverse=True)
        return detected

    def analyze_sentence_polarity(self, sentence: str) -> Tuple[float, float, List[str], List[str]]:
        """
        Tính điểm tích cực và tiêu cực cho một câu cụ thể, có xử lý từ phủ định.
        Ví dụ: 'máy lạnh không hoạt động' -> negative.
        'thầy cô rất nhiệt tình' -> positive.
        """
        words = sentence.lower().split()
        pos_score = 0.0
        neg_score = 0.0
        pos_evidences = []
        neg_evidences = []

        # Kiểm tra cụm từ đặc thù (nguyên cụm)
        phrase_rules_neg = [
            "không hoạt động", "không chạy", "không bật", "không mát", "không vào được",
            "mất mạng", "rớt mạng", "chập chờn", "sập web", "bị lỗi", "hư rồi", "hỏng rồi",
            "chờ quá lâu", "thái độ kém", "tăng học phí", "quá nóng", "quá tải"
        ]
        phrase_rules_pos = [
            "rất tốt", "rất nhiệt tình", "rất xịn", "quá xịn", "cảm ơn thầy cô",
            "cảm ơn trường", "hỗ trợ rất nhanh", "giải quyết nhanh", "rất hài lòng",
            "được khen", "chất lượng tốt", "hoạt động ổn định"
        ]

        for p in phrase_rules_neg:
            if p in sentence.lower():
                neg_score += 2.5
                neg_evidences.append(p)

        for p in phrase_rules_pos:
            if p in sentence.lower():
                pos_score += 2.5
                pos_evidences.append(p)

        # Phân tích từng từ và ngữ cảnh lân cận (window 3 từ trước)
        for i, word in enumerate(words):
            # Kiểm tra xem có từ phủ định trước đó không (cửa sổ 2 từ trước)
            has_negation = False
            if i > 0 and words[i - 1] in self.negation_words:
                has_negation = True
            elif i > 1 and words[i - 2] in self.negation_words:
                has_negation = True

            if word in self.positive_words:
                if has_negation:
                    # 'không tốt' -> tính thành tiêu cực
                    neg_score += 1.5
                    neg_evidences.append(f"{words[i-1]} {word}")
                else:
                    pos_score += 1.0
                    pos_evidences.append(word)

            elif word in self.negative_words:
                if has_negation:
                    # 'không hỏng', 'không đắt' -> trung hòa
                    pos_score += 0.5
                else:
                    neg_score += 1.2
                    neg_evidences.append(word)

        return pos_score, neg_score, pos_evidences, neg_evidences

    def classify(self, title: str, content: str = "") -> Dict[str, Any]:
        """
        Phân loại toàn diện bài viết diễn đàn UIT:
        - Input: Tiêu đề và Nội dung
        - Output: Nhãn (POSITIVE, NEGATIVE, NEUTRAL), Điểm số, Khía cạnh, Bằng chứng
        """
        clean_title = clean_text(title)
        clean_content = clean_text(content)
        full_text = f"{clean_title}. {clean_content}"

        # 1. Phát hiện các khía cạnh của trường
        detected_aspects = self.detect_aspects(full_text)
        primary_aspect = detected_aspects[0]["aspect_name"] if detected_aspects else "Chung / Khác"
        aspect_key = detected_aspects[0]["aspect_key"] if detected_aspects else "chung"

        # 2. Phân tích sắc thái của Tiêu đề (Tiêu đề mang trọng số cao x 2.0)
        t_pos, t_neg, t_pos_ev, t_neg_ev = self.analyze_sentence_polarity(clean_title)

        # 3. Phân tích sắc thái của Nội dung
        c_pos, c_neg, c_pos_ev, c_neg_ev = self.analyze_sentence_polarity(clean_content)

        total_pos = (t_pos * 2.0) + c_pos
        total_neg = (t_neg * 2.0) + c_neg

        all_pos_ev = list(dict.fromkeys(t_pos_ev + c_pos_ev))
        all_neg_ev = list(dict.fromkeys(t_neg_ev + c_neg_ev))

        # 4. Logic phân định nhãn
        # Nếu không có bất kỳ từ khóa cảm xúc nào hoặc điểm số ngang nhau -> NEUTRAL
        diff = total_pos - total_neg
        
        # Ngưỡng tối thiểu để gán nhãn Tốt hoặc Xấu
        threshold = 1.0

        if total_neg >= threshold and total_neg > total_pos:
            label = LABEL_NEGATIVE
            confidence = min(0.98, 0.65 + (total_neg / (total_pos + total_neg + 1.0)) * 0.3)
            reason = f"Phản ánh/phàn nàn tiêu cực về {primary_aspect}: phát hiện các từ/cụm từ '{', '.join(all_neg_ev[:4])}'"

        elif total_pos >= threshold and total_pos > total_neg:
            label = LABEL_POSITIVE
            confidence = min(0.98, 0.65 + (total_pos / (total_pos + total_neg + 1.0)) * 0.3)
            reason = f"Đánh giá tích cực/khen ngợi về {primary_aspect}: phát hiện các từ/cụm từ '{', '.join(all_pos_ev[:4])}'"

        else:
            label = LABEL_NEUTRAL
            confidence = 0.85 if not detected_aspects else 0.75
            if detected_aspects:
                reason = f"Bài viết trao đổi, thông báo hoặc hỏi đáp liên quan đến {primary_aspect} (sắc thái trung tính)"
            else:
                reason = "Chủ đề học thuật, công nghệ, tuyển dụng hoặc trao đổi thông tin không có ý kiến đánh giá trường"

        return {
            "label": label,
            "label_name_vi": LABEL_NAMES_VI[label],
            "confidence": round(confidence, 2),
            "pos_score": round(total_pos, 2),
            "neg_score": round(total_neg, 2),
            "primary_aspect": primary_aspect,
            "aspect_key": aspect_key,
            "positive_evidences": all_pos_ev,
            "negative_evidences": all_neg_ev,
            "reason": reason
        }

    def process_dataset(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Dán nhãn tự động cho toàn bộ tập dữ liệu đã cào."""
        labeled_dataset = []
        for item in dataset:
            title = item.get("title", "")
            content = item.get("content", "") or item.get("first_post", "")
            res = self.classify(title, content)

            processed_item = {
                **item,
                "label": res["label"],
                "label_vi": res["label_name_vi"],
                "confidence": res["confidence"],
                "sentiment_score": round(res["pos_score"] - res["neg_score"], 2),
                "primary_aspect": res["primary_aspect"],
                "aspect_key": res["aspect_key"],
                "positive_evidences": ", ".join(res["positive_evidences"]),
                "negative_evidences": ", ".join(res["negative_evidences"]),
                "reason": res["reason"]
            }
            labeled_dataset.append(processed_item)

        return labeled_dataset
