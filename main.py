"""
Script điều phối toàn bộ quy trình (Master Pipeline) cho Dự án Thu thập và Phân loại Cảm xúc Diễn đàn UIT:
1. Thu thập dữ liệu (Crawler): API REST / HTML BeautifulSoup
2. Tiền xử lý & Làm sạch (Text Cleaning & Normalization)
3. Phân loại cảm xúc chay & Dán nhãn khía cạnh trường (Rule-based Sentiment & Aspect Labeling)
4. Trực quan hóa & Xuất báo cáo biểu đồ (Visualizer)
5. Web Dashboard tương tác
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    ASPECTS,
    LABEL_POSITIVE,
    LABEL_NEGATIVE,
    LABEL_NEUTRAL,
    LABEL_NAMES_VI
)
from crawler.api_crawler import UITApiCrawler
from crawler.html_crawler import UITHtmlCrawler
from processor.sentiment_analyzer import UITSentimentAnalyzer
from processor.visualizer import SentimentVisualizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("UITForumPipeline")


# Danh sách từ khóa tìm kiếm đại diện cho các khía cạnh khác nhau của trường UIT
SEARCH_KEYWORDS = [
    "máy lạnh", "wifi", "nhà xe", "thang máy", "nhà vệ sinh",
    "học phí", "học bổng",
    "đăng ký môn học", "sập web", "dkmh",
    "giảng viên", "thầy cô", "nhiệt tình",
    "phòng đào tạo", "công tác sinh viên", "căn tin"
]


def step_crawl(method: str = "api", pages: int = 3, max_topics: int = 150) -> Path:
    """Bước 1: Thu thập dữ liệu từ diễn đàn UIT."""
    logger.info("=" * 60)
    logger.info(f"BẮT ĐẦU BƯỚC 1: THU THẬP DỮ LIỆU TỪ FORUM UIT (Phương pháp: {method.upper()})")
    logger.info("=" * 60)

    if method == "api":
        crawler = UITApiCrawler(delay=0.4)
        dataset = crawler.crawl_full_dataset(
            latest_pages=pages,
            search_keywords=SEARCH_KEYWORDS,
            max_topics=max_topics
        )
        saved = crawler.save_dataset(dataset, filename_prefix="uit_forum_raw")
    else:
        crawler = UITHtmlCrawler(delay=0.6)
        dataset = crawler.crawl_dataset(pages=pages, max_topics=max_topics)
        saved = crawler.save_dataset(dataset, filename_prefix="uit_forum_raw")

    raw_json_path = Path(saved["json"])
    logger.info(f"Hoàn thành thu thập! Tổng cộng {len(dataset)} bài viết đã được lưu.")
    return raw_json_path


def step_analyze(raw_file: Optional[Path] = None) -> Tuple[pd.DataFrame, Path]:
    """Bước 2: Tiền xử lý, phân loại cảm xúc chay (Tốt/Xấu/Trung lập) và gán nhãn khía cạnh trường."""
    logger.info("=" * 60)
    logger.info("BẮT ĐẦU BƯỚC 2: TIỀN XỬ LÝ & PHÂN LOẠI CẢM XÚC (RULE-BASED) - GÁN NHÃN KHÍA CẠNH")
    logger.info("=" * 60)

    if not raw_file or not raw_file.exists():
        raw_file = RAW_DATA_DIR / "uit_forum_raw.json"
        if not raw_file.exists():
            candidates = list(RAW_DATA_DIR.glob("*.json"))
            if not candidates:
                raise FileNotFoundError(f"Không tìm thấy file dữ liệu thô trong {RAW_DATA_DIR}. Hãy chạy crawl trước (--crawl).")
            raw_file = candidates[0]

    logger.info(f"Đang đọc dữ liệu từ: {raw_file}")
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    analyzer = UITSentimentAnalyzer()
    labeled_data = analyzer.process_dataset(raw_data)

    df = pd.DataFrame(labeled_data)

    # Lưu kết quả đã dán nhãn
    json_out = PROCESSED_DATA_DIR / "uit_forum_labeled.json"
    csv_out = PROCESSED_DATA_DIR / "uit_forum_labeled.csv"

    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(labeled_data, f, ensure_ascii=False, indent=2)

    df.to_csv(csv_out, index=False, encoding="utf-8-sig")

    logger.info(f"Đã dán nhãn xong {len(labeled_data)} bài viết:")
    sentiment_counts = df["label"].value_counts()
    for lbl, count in sentiment_counts.items():
        pct = (count / len(df)) * 100
        logger.info(f" - {LABEL_NAMES_VI.get(lbl, lbl)}: {count} ({pct:.1f}%)")

    # Xuất data.js cho Dashboard
    dashboard_dir = Path(__file__).parent / "dashboard"
    if dashboard_dir.exists():
        with open(dashboard_dir / "data.js", "w", encoding="utf-8") as f:
            f.write("// Auto-generated data for UIT Forum Dashboard\n")
            f.write("window.UIT_DATA = " + json.dumps(labeled_data, ensure_ascii=False) + ";\n")

    logger.info(f"Dữ liệu dán nhãn đã lưu tại:\n - {json_out}\n - {csv_out}")
    return df, json_out


def step_visualize(labeled_file: Optional[Path] = None) -> Dict[str, str]:
    """Bước 3: Tạo biểu đồ phân tích và xuất báo cáo trực quan."""
    logger.info("=" * 60)
    logger.info("BẮT ĐẦU BƯỚC 3: TRỰC QUAN HÓA DỮ LIỆU & XUẤT BIỂU ĐỒ BÁO CÁO")
    logger.info("=" * 60)

    if not labeled_file or not labeled_file.exists():
        labeled_file = PROCESSED_DATA_DIR / "uit_forum_labeled.csv"

    df = pd.read_csv(labeled_file)
    visualizer = SentimentVisualizer()
    charts = visualizer.generate_all_reports(df)

    logger.info("Đã tạo thành công các biểu đồ trực quan hóa:")
    for name, path in charts.items():
        logger.info(f" - {name}: {path}")

    return charts


def predict_single(text: str):
    """Phân loại cảm xúc chay của 1 đoạn văn bản trực tiếp qua dòng lệnh."""
    print("\n" + "=" * 60)
    print("PHÂN LOẠI CẢM XÚC CHAY (RULE-BASED LEXICON) CHO VĂN BẢN ĐẦU VÀO")
    print("=" * 60)
    print(f"Văn bản: '{text}'\n")

    analyzer = UITSentimentAnalyzer()
    res = analyzer.classify(text)

    print(f"Nhãn đánh giá: {res['label']} -> {res['label_name_vi']}")
    print(f"Độ tin cậy:    {res['confidence'] * 100:.1f}%")
    print(f"Điểm sắc thái: {res['pos_score'] - res['neg_score']} (Tích cực: +{res['pos_score']}, Tiêu cực: -{res['neg_score']})")
    print(f"Khía cạnh UIT: {res['primary_aspect']}")
    print(f"Lý giải:       {res['reason']}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="UIT Forum Sentiment Crawler & Rule-based Classifier Pipeline")
    parser.add_argument("--crawl", action="store_true", help="Chạy crawler thu thập dữ liệu từ forum.uit.edu.vn")
    parser.add_argument("--method", choices=["api", "html"], default="api", help="Phương pháp cào (api: Discourse API, html: BeautifulSoup)")
    parser.add_argument("--pages", type=int, default=3, help="Số trang cần cào (mặc định: 3)")
    parser.add_argument("--max-topics", type=int, default=150, help="Số lượng bài tối đa cần lấy (mặc định: 150)")

    parser.add_argument("--analyze", action="store_true", help="Làm sạch và phân loại cảm xúc chay / khía cạnh cho dữ liệu đã cào")
    parser.add_argument("--visualize", action="store_true", help="Xuất các biểu đồ phân tích trực quan hóa vào data/reports/")
    parser.add_argument("--all", action="store_true", help="Chạy toàn bộ pipeline từ cào dữ liệu đến trực quan hóa")

    parser.add_argument("--predict", type=str, default="", help="Nhập câu bình luận để phân loại cảm xúc trực tiếp")
    parser.add_argument("--dashboard", action="store_true", help="Khởi chạy giao diện Web Dashboard tương tác")

    args = parser.parse_args()

    if args.dashboard:
        import subprocess
        subprocess.run([sys.executable, str(Path(__file__).parent / "run_dashboard.py")])
        return

    if args.predict:
        predict_single(args.predict)
        return

    # Nếu không có cờ nào được truyền hoặc chọn --all, chạy toàn bộ quy trình
    if args.all or (not args.crawl and not args.analyze and not args.visualize):
        logger.info("Khởi động toàn bộ quy trình End-to-End (Phân loại chay)...")
        raw_file = step_crawl(method=args.method, pages=args.pages, max_topics=args.max_topics)
        df, labeled_file = step_analyze(raw_file)
        step_visualize(PROCESSED_DATA_DIR / "uit_forum_labeled.csv")
        logger.info("QUY TRÌNH HOÀN TẤT XUẤT SẮC!")
        return

    raw_file = None
    if args.crawl:
        raw_file = step_crawl(method=args.method, pages=args.pages, max_topics=args.max_topics)

    labeled_file = None
    if args.analyze or (args.crawl and args.visualize):
        df, labeled_file = step_analyze(raw_file)

    if args.visualize:
        step_visualize(PROCESSED_DATA_DIR / "uit_forum_labeled.csv")


if __name__ == "__main__":
    main()
