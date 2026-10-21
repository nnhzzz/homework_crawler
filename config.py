"""
Configuration settings for UIT Forum Crawler and Sentiment Analyzer.
Diễn đàn: https://forum.uit.edu.vn (Trường Đại học Công nghệ Thông tin - ĐHQG-HCM)
"""

import os
from pathlib import Path
import certifi

# Cấu hình SSL cho Python (tránh lỗi CERTIFICATE_VERIFY_FAILED trên macOS)
os.environ["SSL_CERT_FILE"] = certifi.where()

# Thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent

# Các đường dẫn lưu trữ dữ liệu
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"

for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Cấu hình Diễn đàn UIT
FORUM_BASE_URL = "https://forum.uit.edu.vn"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "vi,en;q=0.9",
}

# Tên các nhãn đánh giá
LABEL_POSITIVE = "POSITIVE"   # Nói tốt / Khen ngợi / Tích cực
LABEL_NEGATIVE = "NEGATIVE"   # Nói xấu / Phàn nàn / Tiêu cực
LABEL_NEUTRAL = "NEUTRAL"     # Trung lập / Thông tin hành chính / Hỏi đáp thường

# Tên hiển thị tiếng Việt
LABEL_NAMES_VI = {
    LABEL_POSITIVE: "Tốt (Tích cực)",
    LABEL_NEGATIVE: "Xấu (Tiêu cực/Phàn nàn)",
    LABEL_NEUTRAL: "Trung lập (Hỏi đáp/Thông báo)"
}

# Danh mục các khía cạnh về trường (School Aspects)
ASPECTS = {
    "co_so_vat_chat": {
        "name": "Cơ sở vật chất",
        "keywords": [
            "cơ sở vật chất", "csvc", "máy lạnh", "điều hòa", "wifi", "mạng",
            "thang máy", "nhà xe", "bãi giữ xe", "gửi xe", "nhà vệ sinh", "wc",
            "phòng học", "giảng đường", "lab", "ai lab", "ổ cắm", "bàn ghế",
            "máy chiếu", "quạt", "loa", "mic", "âm thanh", "tòa nhà", "tòa a",
            "tòa b", "tòa c", "tòa e"
        ]
    },
    "hoc_phi": {
        "name": "Học phí & Học bổng",
        "keywords": [
            "học phí", "tiền học", "đóng tiền", "tăng học phí", "miễn giảm học phí",
            "học bổng", "hỗ trợ tài chính", "biên lai", "ngân hàng"
        ]
    },
    "dang_ky_mon_hoc": {
        "name": "Đăng ký môn học & Hệ thống",
        "keywords": [
            "đăng ký môn học", "dkmh", "sập web", "nghẽn mạng", "hủy môn",
            "học phần", "trùng lịch", "mở lớp", "portal", "moodle", "courses",
            "hệ thống", "quá tải", "server"
        ]
    },
    "giang_vien_dao_tao": {
        "name": "Giảng viên & Đào tạo",
        "keywords": [
            "giảng viên", "thầy", "cô", "gv", "chấm điểm", "nhiệt tình", "tận tâm",
            "dạy hay", "khó tính", "truyền cảm hứng", "chương trình học",
            "môn học", "đề thi", "chất lượng đào tạo", "đồ án"
        ]
    },
    "dich_vu_sinh_vien": {
        "name": "Phòng ban & Dịch vụ sinh viên",
        "keywords": [
            "phòng đào tạo", "pđt", "ctsv", "công tác sinh viên", "văn phòng khoa",
            "bảo vệ", "căn tin", "khám sức khỏe", "thủ tục", "giấy tờ",
            "giấy xác nhận", "thẻ sinh viên", "kí túc xá", "ktx"
        ]
    },
    "hinh_anh_uit": {
        "name": "Môi trường & Hình ảnh UIT",
        "keywords": [
            "uit", "trường uit", "đại học công nghệ thông tin", "môi trường học",
            "sinh viên uit", "hoạt động", "đoàn hội", "câu lạc bộ", "cuộc thi"
        ]
    }
}

# Từ điển sắc thái cảm xúc (Sentiment Lexicon)
POSITIVE_KEYWORDS = [
    "tốt", "tuyệt vời", "xuất sắc", "ưng ý", "hài lòng", "hiện đại", "xịn",
    "nhanh", "nhiệt tình", "chu đáo", "tận tâm", "cảm ơn", "bổ ích", "thông thoáng",
    "mát mẻ", "đẹp", "khen", "tự hào", "uy tín", "hỗ trợ tốt", "hoạt động tốt",
    "rất thích", "ổn áp", "chất lượng cao", "đỉnh", "dễ thương", "tạo điều kiện",
    "giải quyết nhanh", "kịp thời", "thân thiện", "đáng khen", "chuyên nghiệp"
]

NEGATIVE_KEYWORDS = [
    "hỏng", "hư", "lỗi", "sập", "chán", "kém", "tệ", "bực mình", "bất cập",
    "nóng", "không hoạt động", "chập chờn", "yếu", "chậm", "chờ lâu", "quá tải",
    "thất vọng", "khó khăn", "phiền hà", "chật chội", "tồi tệ", "đắt", "tăng vọt",
    "chặt chém", "tức", "ức chế", "bức xúc", "bất tiện", "không bật", "bốc mùi",
    "nghẽn", "đơ", "lag", "rớt mạng", "cháy", "ồn ào", "không thỏa đáng",
    "khó chịu", "chê", "thái độ kém", "chậm trễ", "ngâm hồ sơ", "mất đồ"
]

# Từ ngữ phủ định làm đảo ngược cảm xúc (Negations)
NEGATION_WORDS = [
    "không", "chẳng", "chả", "chưa", "đâu có", "không hề", "không được", "kém"
]
