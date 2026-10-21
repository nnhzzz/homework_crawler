"""
Module trực quan hóa dữ liệu và báo cáo phân tích cảm xúc Diễn đàn UIT:
- Biểu đồ phân bố cảm xúc (Tốt, Xấu, Trung lập) dạng Cột & Donut
- Biểu đồ phân tích khía cạnh (Aspect Breakdown) của UIT
- Biểu đồ sắc thái cảm xúc theo từng khía cạnh trường (Cơ sở vật chất, Học phí, ĐKMH...)
- Biểu đồ ma trận nhầm lẫn (Confusion Matrix) của mô hình Machine Learning
- Xuất file hình ảnh độ phân giải cao (DPI 300) vào thư mục data/reports/
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from config import (
    REPORTS_DIR,
    LABEL_POSITIVE,
    LABEL_NEGATIVE,
    LABEL_NEUTRAL,
    LABEL_NAMES_VI
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Visualizer")

# Cấu hình font và style cho biểu đồ
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


COLOR_PALETTE = {
    LABEL_POSITIVE: "#10b981",  # Emerald Green (Tích cực)
    LABEL_NEGATIVE: "#ef4444",  # Crimson Red (Tiêu cực)
    LABEL_NEUTRAL: "#64748b"    # Slate Grey (Trung lập)
}


class SentimentVisualizer:
    def __init__(self, output_dir: Path = REPORTS_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_sentiment_distribution(self, df: pd.DataFrame, filename: str = "sentiment_distribution.png") -> str:
        """Vẽ biểu đồ kết hợp (Bar chart & Donut chart) phân bố cảm xúc chung."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        counts = df["label"].value_counts()
        labels_present = [l for l in [LABEL_POSITIVE, LABEL_NEGATIVE, LABEL_NEUTRAL] if l in counts.index]
        values = [counts[l] for l in labels_present]
        colors = [COLOR_PALETTE[l] for l in labels_present]
        display_names = [LABEL_NAMES_VI.get(l, l) for l in labels_present]

        # 1. Bar Chart
        bars = axes[0].bar(display_names, values, color=colors, width=0.55, edgecolor="#ffffff", linewidth=1.5)
        axes[0].set_title("Số lượng bài viết theo nhãn cảm xúc", fontsize=14, fontweight="bold", pad=15)
        axes[0].set_ylabel("Số lượng bài viết", fontsize=12)
        axes[0].grid(axis="y", linestyle="--", alpha=0.6)

        # Ghi số lượng và phần trăm trên từng cột
        total = sum(values) if sum(values) > 0 else 1
        for bar in bars:
            h = bar.get_height()
            pct = (h / total) * 100
            axes[0].annotate(f"{h}\n({pct:.1f}%)",
                             xy=(bar.get_x() + bar.get_width() / 2, h),
                             xytext=(0, 4), textcoords="offset points",
                             ha="center", va="bottom", fontsize=11, fontweight="bold")

        # 2. Donut Chart
        wedges, texts, autotexts = axes[1].pie(
            values,
            labels=display_names,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            pctdistance=0.75,
            wedgeprops=dict(width=0.45, edgecolor="w", linewidth=2)
        )
        for t in texts:
            t.set_fontsize(11)
        for at in autotexts:
            at.set_fontsize(11)
            at.set_fontweight("bold")
            at.set_color("white")

        axes[1].set_title("Tỷ lệ phần trăm cảm xúc thảo luận", fontsize=14, fontweight="bold", pad=15)

        plt.suptitle("PHÂN TÍCH ĐÁNH GIÁ VỀ TRƯỜNG TRÊN DIỄN ĐÀN UIT (forum.uit.edu.vn)",
                     fontsize=16, fontweight="bold", y=1.02)
        plt.tight_layout()

        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Đã lưu biểu đồ phân bố cảm xúc tại: {out_path}")
        return str(out_path)

    def plot_aspect_breakdown(self, df: pd.DataFrame, filename: str = "aspect_breakdown.png") -> str:
        """Vẽ biểu đồ các khía cạnh về trường được sinh viên quan tâm nhất."""
        fig, ax = plt.subplots(figsize=(12, 6))

        aspect_counts = df["primary_aspect"].value_counts()
        # Bỏ hoặc để lại 'Chung / Khác'
        colors = sns.color_palette("mako", len(aspect_counts))

        bars = ax.barh(aspect_counts.index[::-1], aspect_counts.values[::-1], color=colors, height=0.6)
        ax.set_title("CÁC KHÍA CẠNH VỀ TRƯỜNG ĐƯỢC THẢO LUẬN NHIỀU NHẤT TRÊN FORUM UIT",
                     fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Số lượng bài viết / chủ đề", fontsize=12)
        ax.grid(axis="x", linestyle="--", alpha=0.6)

        for bar in bars:
            w = bar.get_width()
            ax.annotate(f" {w}",
                        xy=(w, bar.get_y() + bar.get_height() / 2),
                        xytext=(5, 0), textcoords="offset points",
                        ha="left", va="center", fontsize=11, fontweight="bold")

        plt.tight_layout()
        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Đã lưu biểu đồ khía cạnh tại: {out_path}")
        return str(out_path)

    def plot_sentiment_by_aspect(self, df: pd.DataFrame, filename: str = "sentiment_by_aspect.png") -> str:
        """Biểu đồ phân tích chéo: Khía cạnh nào được khen và khía cạnh nào bị phàn nàn nhiều nhất."""
        crosstab = pd.crosstab(df["primary_aspect"], df["label"], normalize="index") * 100

        # Đảm bảo có đủ 3 cột
        for col in [LABEL_POSITIVE, LABEL_NEGATIVE, LABEL_NEUTRAL]:
            if col not in crosstab.columns:
                crosstab[col] = 0.0

        crosstab = crosstab[[LABEL_POSITIVE, LABEL_NEGATIVE, LABEL_NEUTRAL]]
        
        # Sắp xếp theo tỷ lệ tiêu cực giảm dần để làm nổi bật vấn đề
        crosstab = crosstab.sort_values(by=LABEL_NEGATIVE, ascending=True)

        fig, ax = plt.subplots(figsize=(13, 7))
        crosstab.plot(
            kind="barh",
            stacked=True,
            color=[COLOR_PALETTE[c] for c in crosstab.columns],
            ax=ax,
            width=0.6,
            edgecolor="#ffffff"
        )

        ax.set_title("TỶ LỆ ĐÁNH GIÁ (TỐT / XẤU / TRUNG LẬP) THEO TỪNG KHÍA CẠNH CỦA UIT",
                     fontsize=15, fontweight="bold", pad=15)
        ax.set_xlabel("Tỷ lệ phần trăm (%)", fontsize=12)
        ax.set_ylabel("Khía cạnh trường UIT", fontsize=12)
        ax.set_xlim(0, 100)
        ax.legend(
            labels=[LABEL_NAMES_VI[c] for c in crosstab.columns],
            loc="lower center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=3,
            frameon=True,
            fontsize=11
        )
        ax.grid(axis="x", linestyle="--", alpha=0.6)

        plt.tight_layout()
        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Đã lưu biểu đồ sắc thái theo khía cạnh tại: {out_path}")
        return str(out_path)

    def plot_confusion_matrix(self, cm_data: List[List[int]], labels: List[str], model_name: str, filename: str = "confusion_matrix.png") -> str:
        """Vẽ ma trận nhầm lẫn của mô hình Machine Learning."""
        fig, ax = plt.subplots(figsize=(8, 6))

        display_labels = [LABEL_NAMES_VI.get(l, l).split()[0] for l in labels]
        sns.heatmap(
            cm_data,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=display_labels,
            yticklabels=display_labels,
            cbar=False,
            ax=ax,
            annot_kws={"size": 14, "weight": "bold"}
        )

        ax.set_title(f"MA TRẬN NHẦM LẪN (CONFUSION MATRIX) - {model_name.upper()}",
                     fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Nhãn dự đoán (Predicted Label)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Nhãn thực tế (True Label)", fontsize=11, fontweight="bold")

        plt.tight_layout()
        out_path = self.output_dir / filename
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()
        logger.info(f"Đã lưu ma trận nhầm lẫn tại: {out_path}")
        return str(out_path)

    def generate_all_reports(self, df: pd.DataFrame) -> Dict[str, str]:
        """Tạo trọn bộ biểu đồ báo cáo hoàn chỉnh (Phân loại tập luật & sắc thái)."""
        charts = {}
        charts["distribution"] = self.plot_sentiment_distribution(df)
        charts["aspects"] = self.plot_aspect_breakdown(df)
        charts["sentiment_by_aspect"] = self.plot_sentiment_by_aspect(df)
        return charts

