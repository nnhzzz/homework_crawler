# UIT Forum Crawler & Rule-based Sentiment Classifier 🎓
### Hệ thống Thu thập Dữ liệu & Phân loại Đánh giá Diễn đàn Trường Đại học Công nghệ Thông tin (ĐHQG-HCM)

> **Mục tiêu đề bài:** Thu thập các bài viết, thảo luận từ Diễn đàn sinh viên UIT ([https://forum.uit.edu.vn](https://forum.uit.edu.vn)), làm sạch dữ liệu và **phân loại chay (rule-based / lexicon)** xem diễn đàn nói **Tốt** hay **Xấu** về trường rồi dán nhãn theo các khía cạnh cụ thể (*Cơ sở vật chất, Giảng viên, Học phí, Đăng ký môn học, Dịch vụ sinh viên*).

---

## 🌟 Điểm Nổi Bật Của Hệ Thống

1. **Thu thập dữ liệu thực tế (Web Scraping):**
   - **Discourse REST API (`/latest.json`, `/search.json`, `/t/{id}.json`)**: Cào nhanh, có cấu trúc, tự động xử lý phân trang và rate-limit (HTTP 429).
   - **HTML Web Scraping (`BeautifulSoup`)**: Phân tích trực tiếp cây DOM HTML của diễn đàn (crawler mode), bóc tách thẻ bài viết, lượt xem, phản hồi đúng chuẩn môn học Thu thập Dữ liệu Web.
2. **Tiền xử lý văn bản tiếng Việt chuyên sâu:**
   - Chuẩn hóa mã Unicode tiếng Việt dựng sẵn (`NFC`).
   - Xóa bỏ HTML tags, URL, Email, ký tự thừa và trích dẫn quote.
   - **Mở rộng từ điển viết tắt đặc thù sinh viên UIT**: `csvc` $\rightarrow$ cơ sở vật chất, `dkmh` $\rightarrow$ đăng ký môn học, `pđt` $\rightarrow$ phòng đào tạo, `ctsv` $\rightarrow$ phòng công tác sinh viên, `sv` $\rightarrow$ sinh viên, `gv` $\rightarrow$ giảng viên, `ktx` $\rightarrow$ ký túc xá, `đhqg` $\rightarrow$ đại học quốc gia,...
3. **Phân loại cảm xúc chay (Rule-based & Aspect Lexicon):**
   - Sử dụng tập luật ngữ nghĩa tiếng Việt kết hợp từ điển sắc thái (Lexicon) chuyên biệt cho môi trường đại học.
   - **Xử lý hiện tượng phủ định đảo ngược nghĩa**: Ví dụ `không mát`, `không hỏng`, `chờ quá lâu`, `sập web`.
   - **Tự động gán nhãn 3 mức**: **TỐT** (Khen ngợi/Tích cực), **XẤU** (Phàn nàn/Tiêu cực), **TRUNG LẬP** (Hỏi đáp/Thông báo hành chính).
   - **Gán nhãn khía cạnh trường**: Tự động phát hiện bài viết nói về *Cơ sở vật chất, Học phí & Học bổng, ĐKMH & Hệ thống, Giảng viên & Đào tạo, Phòng ban & Dịch vụ SV*.
   - Trích xuất từ khóa bằng chứng và lý giải minh bạch lý do gán nhãn.
4. **Trực quan hóa & Xuất bản biểu đồ (DPI 300):**
   - Tự động vẽ và lưu biểu đồ: Phân bố cảm xúc (Bar & Donut), Thống kê khía cạnh trường, Tỷ lệ khen/chê theo từng khía cạnh.
5. **Giao diện Web Dashboard Tương tác (Interactive Dashboard):**
   - Thẻ thống kê KPI thời gian thực, biểu đồ Chart.js, bảng tra cứu lọc đa chiều (theo cảm xúc, theo khía cạnh, tìm kiếm từ khóa), và **công cụ thử nghiệm phân loại cảm xúc trực tiếp trên trình duyệt**.

---

## 📁 Cấu Trúc Mã Nguồn

```text
BT_crawler/
├── config.py                     # Cấu hình chung, URL, đường dẫn, từ điển cảm xúc & khía cạnh UIT
├── requirements.txt              # Danh sách thư viện Python cần thiết (requests, bs4, pandas, matplotlib)
├── main.py                       # CLI điều phối toàn bộ quy trình (Master Pipeline)
├── run_dashboard.py              # Script khởi chạy nhanh giao diện Web Dashboard
│
├── crawler/                      # Package thu thập dữ liệu
│   ├── __init__.py
│   ├── api_crawler.py            # Cào dữ liệu qua Discourse REST API
│   └── html_crawler.py           # Cào dữ liệu qua bóc tách HTML DOM (BeautifulSoup)
│
├── processor/                    # Package xử lý và phân loại cảm xúc chay
│   ├── __init__.py
│   ├── text_cleaner.py           # Làm sạch văn bản, chuẩn hóa từ viết tắt UIT
│   ├── sentiment_analyzer.py     # Phân loại cảm xúc chay theo tập luật & khía cạnh (Rule/Lexicon)
│   └── visualizer.py             # Trực quan hóa dữ liệu và xuất biểu đồ (Matplotlib/Seaborn)
│
├── data/
│   ├── raw/                      # Dữ liệu cào thô (JSON, CSV)
│   │   ├── uit_forum_raw.json
│   │   └── uit_forum_raw.csv
│   ├── processed/                # Dữ liệu đã làm sạch & dán nhãn
│   │   ├── uit_forum_labeled.json
│   │   └── uit_forum_labeled.csv
│   └── reports/                  # Biểu đồ phân tích trực quan xuất ra
│       ├── sentiment_distribution.png
│       ├── aspect_breakdown.png
│       └── sentiment_by_aspect.png
│
├── dashboard/                    # Giao diện Web Dashboard tương tác
│   ├── index.html                # Trang giao diện chính
│   ├── style.css                 # Giao diện hiện đại Dark Theme
│   ├── app.js                    # Logic tương tác, lọc dữ liệu, live tester
│   └── data.js                   # Dữ liệu xuất tự động cho Dashboard
│
└── REPORT.md                     # Báo cáo học thuật chi tiết kết quả bài tập
```

---

## 🚀 Hướng Dẫn Cài Đặt & Vận Hành

### 1. Cài đặt thư viện

Yêu cầu môi trường Python 3.9 trở lên:
```bash
pip install -r requirements.txt
```

### 2. Thực thi toàn bộ quy trình (End-to-End Pipeline)

Lệnh thực thi tuần tự: Cào bài viết từ forum UIT $\rightarrow$ Tiền xử lý $\rightarrow$ Phân loại cảm xúc chay & Dán nhãn $\rightarrow$ Xuất biểu đồ phân tích:
```bash
python3 main.py --all --max-topics 220
```

### 3. Thực thi từng giai đoạn độc lập (Modular Execution)

- **Thu thập dữ liệu qua API:**
  ```bash
  python3 main.py --crawl --method api --pages 5 --max-topics 220
  ```
- **Hoặc thu thập bằng HTML Scraping (BeautifulSoup):**
  ```bash
  python3 main.py --crawl --method html --pages 3 --max-topics 100
  ```
- **Làm sạch văn bản và phân loại chay:**
  ```bash
  python3 main.py --analyze
  ```
- **Xuất biểu đồ phân tích trực quan:**
  ```bash
  python3 main.py --visualize
  ```

---

## 🔍 Phân Loại Trực Tiếp Câu Bình Luận (CLI Live Predict)

Hệ thống hỗ trợ phân tích tức thì từng đoạn ý kiến hoặc phản ánh đơn lẻ thông qua tham số `--predict`:

```bash
# Phản ánh phàn nàn (Tiêu cực):
python3 main.py --predict "Máy lạnh phòng B1.14 bị hỏng kêu to và không mát chút nào"

# Khen ngợi (Tích cực):
python3 main.py --predict "Các thầy cô và phòng đào tạo hỗ trợ rất nhiệt tình, giải quyết thắc mắc nhanh chóng và chu đáo"

# Đăng ký môn học bị sập web:
python3 main.py --predict "Đến giờ đăng ký môn học là server dkmh lại sập web nghẽn mạng"

# Thông báo hành chính (Trung lập):
python3 main.py --predict "Thông báo lịch nộp học phí học kỳ 2 qua ngân hàng Vietcombank"
```

---

## 🖥️ Trực Quan Hóa Với Web Dashboard Tương Tác

Giao diện trực quan hỗ trợ lọc dữ liệu đa chiều, biểu đồ thống kê động và công cụ thử nghiệm phân loại trực tiếp:

```bash
# Khởi chạy qua main.py
python3 main.py --dashboard

# Hoặc khởi chạy qua script launcher
python3 run_dashboard.py
```
Địa chỉ truy cập: **`http://localhost:8080`**

*(Có thể mở trực tiếp file `dashboard/index.html` trên trình duyệt web bất kỳ).*

---

## 📊 Kết Quả Thực Tế Trên Diễn Đàn UIT (220 Bài Viết)

- **Trung lập (Hỏi đáp / Thông báo):** `59.1%` (130 bài)
- **Xấu (Tiêu cực / Phàn nàn):** `22.3%` (49 bài)
- **Tốt (Tích cực / Khen ngợi):** `18.6%` (41 bài)

**Các vấn đề sinh viên phản ánh nhiều nhất:**
- **Cơ sở vật chất:** Máy lạnh không mát, chập chờn, wifi tầng cao, thẻ xe.
- **Đăng ký môn học & Hệ thống:** Tình trạng nghẽn mạng lúc mở cổng ĐKMH.
- **Giảng viên & Đào tạo:** Rất nhiều đánh giá tích cực khen ngợi sự tận tâm, nhiệt tình của thầy cô UIT.
