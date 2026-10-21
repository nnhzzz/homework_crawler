"""
Module tiền xử lý và làm sạch văn bản thảo luận diễn đàn UIT.
- Chuẩn hóa Unicode tiếng Việt (NFC)
- Loại bỏ HTML tags, URL, email, ký tự rác
- Mở rộng các từ viết tắt phổ biến của sinh viên UIT (csvc, dkmh, pđt, ctsv, gv,...)
- Chuẩn hóa khoảng trắng và dấu câu
"""

import re
import unicodedata
from bs4 import BeautifulSoup

# Từ điển viết tắt phổ biến trong môi trường ĐH CNTT - UIT
ABBREVIATIONS = {
    r"\bcsvc\b": "cơ sở vật chất",
    r"\bdkmh\b": "đăng ký môn học",
    r"\bpđt\b": "phòng đào tạo",
    r"\bpdt\b": "phòng đào tạo",
    r"\bctsv\b": "phòng công tác sinh viên",
    r"\bsv\b": "sinh viên",
    r"\bgv\b": "giảng viên",
    r"\bkt\b": "kiểm tra",
    r"\btail\b": "tài liệu",
    r"\bhp\b": "học phí",
    r"\bktx\b": "ký túc xá",
    r"\bđhqg\b": "đại học quốc gia",
    r"\bcntt\b": "công nghệ thông tin",
    r"\bkhmt\b": "khoa học máy tính",
    r"\bktmt\b": "kỹ thuật máy tính",
    r"\bhttt\b": "hệ thống thông tin",
    r"\bmmt\b": "mạng máy tính",
    r"\bktdl\b": "khoa học và kỹ thuật dữ liệu",
    r"\battt\b": "an toàn thông tin",
    r"\bok\b": "ổn",
    r"\bko\b": "không",
    r"\bk\b": "không",
    r"\bhok\b": "không",
    r"\bdc\b": "được",
    r"\bđc\b": "được",
    r"\br\b": "rồi",
    r"\bbqdcs\b": "ban quản lý cơ sở"
}


def normalize_unicode(text: str) -> str:
    """Chuẩn hóa bảng mã ký tự tiếng Việt về dạng Unicode dựng sẵn (NFC)."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", text)


def remove_html_and_urls(text: str) -> str:
    """Làm sạch thẻ HTML và đường dẫn URL."""
    if not text:
        return ""
    # Nếu còn thẻ HTML, bóc tách bằng BeautifulSoup
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text(separator=" ")

    # Xóa URL (http, https, ftp, www)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Xóa địa chỉ email
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", " ", text)
    return text


def expand_abbreviations(text: str) -> str:
    """Mở rộng các từ viết tắt chuyên dùng trong diễn đàn sinh viên."""
    if not text:
        return ""
    text_lower = text.lower()
    for pattern, replacement in ABBREVIATIONS.items():
        text_lower = re.sub(pattern, replacement, text_lower)
    return text_lower


def clean_text(text: str, lowercase: bool = True) -> str:
    """
    Hàm tổng hợp làm sạch văn bản hoàn chỉnh cho dữ liệu diễn đàn.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    text = normalize_unicode(text)
    text = remove_html_and_urls(text)
    
    # Xóa các ký tự đặc biệt lặp lại (ví dụ: !!!!!!!!, ???????, ........)
    text = re.sub(r"([!?.,])\1+", r"\1", text)
    # Xóa trích dẫn quote hoặc metadata diễn đàn
    text = re.sub(r"\[quote.*?\](.*?)\[/quote\]", " ", text, flags=re.DOTALL)

    if lowercase:
        text = expand_abbreviations(text)

    # Chuẩn hóa khoảng trắng
    text = re.sub(r"\s+", " ", text).strip()
    return text
