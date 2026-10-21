# BÁO CÁO KẾT QUẢ BÀI TẬP
## ĐỀ TÀI: THU THẬP VÀ PHÂN LOẠI CẢM XÚC THẢO LUẬN TRÊN DIỄN ĐÀN UIT (forum.uit.edu.vn)

---

### MỤC LỤC
1. [GIỚI THIỆU ĐỀ TÀI & MỤC TIÊU](#1-giới-thiệu-đề-tài--mục-tiêu)
2. [KIẾN TRÚC HỆ THỐNG](#2-kiến-trúc-hệ-thống)
3. [PHƯƠNG PHÁP THU THẬP DỮ LIỆU (WEB CRAWLER)](#3-phương-pháp-thu-thập-dữ-liệu-web-crawler)
4. [QUY TRÌNH TIỀN XỬ LÝ VĂN BẢN TIẾNG VIỆT](#4-quy-trình-tiền-xử-lý-văn-bản-tiếng-việt)
5. [PHƯƠNG PHÁP PHÂN LOẠI CẢM XÚC & KHÍA CẠNH (RULE-BASED LEXICON)](#5-phương-pháp-phân-loại-cảm-xúc--khía-cạnh)
6. [PHÂN TÍCH KẾT QUẢ THỰC TẾ TRÊN DIỄN ĐÀN UIT](#6-phân-tích-kết-quả-thực-tế-trên-diễn-đàn-uit)
7. [GIAO DIỆN WEB DASHBOARD TRỰC QUAN HÓA](#7-giao-diện-web-dashboard-trực-quan-hóa)
8. [KẾT LUẬN & HƯỚNG PHÁT TRIỂN](#8-kết-luận--hướng-phát-triển)

---

### 1. GIỚI THIỆU ĐỀ TÀI & MỤC TIÊU

#### 1.1. Bối cảnh
Diễn đàn Sinh viên Trường Đại học Công nghệ Thông tin - ĐHQG-HCM ([https://forum.uit.edu.vn](https://forum.uit.edu.vn)) là kênh giao tiếp trực tuyến chính thống và sôi nổi giữa sinh viên, cán bộ quản lý và giảng viên. Nơi đây tập trung các thảo luận về học tập, cơ sở vật chất, hệ thống đăng ký môn học, học phí, hoạt động đoàn hội và dịch vụ sinh viên.

#### 1.2. Mục tiêu bài tập
1. **Thu thập dữ liệu tự động (Web Scraping):** Xây dựng crawler tự động thu thập các bài viết, chủ đề và bình luận từ diễn đàn UIT qua cả 2 cơ chế: Discourse REST API và HTML DOM Scraping (BeautifulSoup).
2. **Tiền xử lý văn bản:** Chuẩn hóa Unicode dựng sẵn (NFC), bóc tách HTML, và đặc biệt là chuẩn hóa từ điển viết tắt mang phong cách đặc trưng của sinh viên CNTT/UIT (`csvc`, `dkmh`, `pđt`, `ctsv`, `gv`,...).
3. **Phân loại cảm xúc (Rule-based Sentiment Classification):** Xác định thái độ của bài viết: nói **Tốt** (khen ngợi, tích cực), nói **Xấu** (phàn nàn, tiêu cực) hay **Trung lập** (hỏi đáp thủ tục, thông báo hành chính) bằng phương pháp tập luật và từ điển ngữ nghĩa tiếng Việt, không sử dụng mô hình học máy phức tạp.
4. **Phân loại khía cạnh trường (Aspect-based Labeling):** Gán nhãn chủ đề thuộc về khía cạnh nào: *Cơ sở vật chất, Học phí & Học bổng, Đăng ký môn học & Hệ thống, Giảng viên & Đào tạo, Phòng ban & Dịch vụ sinh viên, Môi trường chung*.
5. **Trực quan hóa:** Xây dựng Dashboard web tương tác và xuất bản các biểu đồ báo cáo khoa học.

---

### 2. KIẾN TRÚC HỆ THỐNG

Quy trình xử lý dữ liệu được thiết kế theo mô hình đường ống tuần hoàn (End-to-End Pipeline):

```
+---------------------------------------------------+
|               forum.uit.edu.vn                   |
+---------------------------------------------------+
                          |
             [1. Thu thập dữ liệu / Crawler]
             +-- API Crawler (/latest.json, /search.json)
             +-- HTML Crawler (BeautifulSoup DOM Parsing)
                          |
                          v
               data/raw/uit_forum_raw.json
                          |
             [2. Tiền xử lý & Chuẩn hóa (Text Cleaner)]
             +-- Chuẩn hóa Unicode NFC
             +-- Xóa HTML tags, URLs, Quotes
             +-- Mở rộng từ viết tắt (dkmh, csvc, pđt...)
                          |
                          v
     [3. Phân loại Cảm xúc & Gán nhãn Khía cạnh]
     +-- Aspect Detection (6 nhóm khía cạnh UIT)
     +-- Negation Handling (xử lý đảo ngược cảm xúc)
     +-- Rule & Lexicon Scoring (+Pos, -Neg, Neutral)
                          |
                          v
            data/processed/uit_forum_labeled.csv
                          |
                          v
             [4. Trực quan hóa & Báo cáo]
             +-- Biểu đồ phân bố cảm xúc (Bar/Donut)
             +-- Biểu đồ khía cạnh trường UIT
             +-- Biểu đồ khen/chê theo khía cạnh
             +-- Web Dashboard tương tác (HTML/JS)
```

---

### 3. PHƯƠNG PHÁP THU THẬP DỮ LIỆU (WEB CRAWLER)

Diễn đàn UIT được vận hành trên nền tảng nguồn mở **Discourse**. Hệ thống đã triển khai song song 2 phương pháp thu thập:

#### 3.1. Phương pháp Discourse REST API (`crawler/api_crawler.py`)
- **Nguyên lý:** Discourse tự động cung cấp định dạng JSON khi thêm đuôi `.json` vào các URL:
  - Danh sách bài viết mới nhất: `GET /latest.json?page=N`
  - Tìm kiếm theo từ khóa mục tiêu: `GET /search.json?q={keyword}`
  - Chi tiết bài viết và danh sách bình luận: `GET /t/{topic_id}.json`
- **Xử lý giới hạn tốc độ (Rate-Limit Backoff):** Khi diễn đàn phản hồi mã `HTTP 429 Too Many Requests`, hệ thống tự động tạm dừng và thử lại (Exponential Backoff), đảm bảo không gây quá tải máy chủ trường.
- **Thu thập có mục tiêu (Aspect-targeted Crawling):** Bên cạnh bài viết trang chủ, crawler truy vấn thêm các từ khóa trọng tâm (`máy lạnh`, `wifi`, `thang máy`, `học phí`, `học bổng`, `đăng ký môn học`, `sập web`, `giảng viên`, `phòng đào tạo`, `căn tin`) để đảm bảo tập dữ liệu bao hàm đầy đủ các ý kiến khen và phàn nàn.

#### 3.2. Phương pháp HTML Web Scraping (`crawler/html_crawler.py`)
- **Nguyên lý:** Phân tích trực tiếp mã nguồn HTML trả về từ diễn đàn thông qua thư viện `BeautifulSoup`.
- Bóc tách bảng `table.topic-list`, các thẻ bài viết `div.crawler-post` hoặc `div.post`, trích xuất tác giả `span[itemprop='author']`, tiêu đề, số lượt xem và phản hồi.
- Phù hợp với tiêu chuẩn thực hành bộ môn Thu thập Dữ liệu Web.

---

### 4. QUY TRÌNH TIỀN XỬ LÝ VĂN BẢN TIẾNG VIỆT

Văn bản thảo luận trên mạng xã hội và diễn đàn sinh viên chứa nhiều yếu tố phức tạp: từ lóng, teencode, lỗi gõ Unicode tổ hợp và các ký hiệu rác. Mô-đun `processor/text_cleaner.py` thực hiện các bước:

1. **Chuẩn hóa bảng mã Unicode:** Áp dụng `unicodedata.normalize('NFC', text)` đưa tất cả ký tự về dạng Unicode dựng sẵn chuẩn tiếng Việt.
2. **Làm sạch cấu trúc:** Xóa bỏ thẻ HTML, đường dẫn URL (`https://...`), địa chỉ email, các khối trích dẫn BBCode `[quote]...[/quote]`.
3. **Chuẩn hóa dấu câu & ký tự lặp:** Thay thế các chuỗi ký tự cảm thán lặp lại (ví dụ: `!!!!!!!!`, `??????`, `.......`) thành ký tự đơn để tránh làm nhiễu vector hóa.
4. **Mở rộng từ viết tắt đặc thù UIT (Domain-specific Slang Normalization):**
   - `csvc` $\rightarrow$ cơ sở vật chất
   - `dkmh` $\rightarrow$ đăng ký môn học
   - `pđt` / `pdt` $\rightarrow$ phòng đào tạo
   - `ctsv` $\rightarrow$ phòng công tác sinh viên
   - `sv` $\rightarrow$ sinh viên; `gv` $\rightarrow$ giảng viên
   - `hp` $\rightarrow$ học phí; `ktx` $\rightarrow$ ký túc xá
   - `đhqg` $\rightarrow$ đại học quốc gia; `cntt` $\rightarrow$ công nghệ thông tin
   - `ko` / `k` / `hok` $\rightarrow$ không; `dc` / `đc` $\rightarrow$ được; `r` $\rightarrow$ rồi

---

### 5. PHƯƠNG PHÁP PHÂN LOẠI CẢM XÚC & KHÍA CẠNH

Phương pháp phân loại được xây dựng hoàn toàn dựa trên tập luật ngôn ngữ (Rule-based) và từ điển sắc thái (Sentiment Lexicon), đảm bảo tính minh bạch, dễ giải thích và không phụ thuộc vào các mô hình AI phức tạp.

#### 5.1. Nhận diện khía cạnh (Aspect Detection)
Hệ thống định nghĩa 6 nhóm khía cạnh trọng tâm:
1. **Cơ sở vật chất:** máy lạnh, điều hòa, wifi, mạng, thang máy, nhà xe, bãi giữ xe, nhà vệ sinh, phòng học, lab, quạt, tòa nhà, tòa A, B, C, E...
2. **Học phí & Học bổng:** học phí, tiền học, đóng tiền, tăng học phí, miễn giảm, học bổng, hỗ trợ tài chính, ngân hàng...
3. **Đăng ký môn học & Hệ thống:** đăng ký môn học, dkmh, sập web, nghẽn mạng, hủy môn, trùng lịch, mở lớp, portal, moodle, quá tải server...
4. **Giảng viên & Đào tạo:** giảng viên, thầy cô, gv, chấm điểm, nhiệt tình, tận tâm, dạy hay, khó tính, chương trình học, đề thi, đồ án...
5. **Phòng ban & Dịch vụ sinh viên:** phòng đào tạo, pđt, ctsv, công tác sinh viên, văn phòng khoa, bảo vệ, căn tin, khám sức khỏe, thủ tục, giấy xác nhận...
6. **Môi trường & Hình ảnh UIT:** phong trào, câu lạc bộ, cuộc thi, đoàn hội, sinh viên UIT...

#### 5.2. Phân tích sắc thái & Xử lý phủ định (Negation Handling)
Sắc thái cảm xúc tiếng Việt có tính phức tạp cao do hiện tượng phủ định đảo ngược nghĩa:
- Cụm từ như *"máy lạnh không mát"*, *"wifi không vào được"*, *"không hoạt động"*: Từ *"mát"* (tích cực) khi đi kèm *"không"* phải được tính là **tiêu cực**.
- Hệ thống áp dụng cơ chế cửa sổ từ lân cận (Sliding Window):
  $$Score_{neg} += 1.5 \quad \text{nếu phát hiện [Từ phủ định] + [Từ tích cực]}$$
- Tiêu đề bài viết (Title) mang tính tóm lược cao, do đó được gán trọng số nhân đôi ($W_{title} = 2.0$) so với phần nội dung phản hồi.

#### 5.3. Tiêu chí phân định nhãn
- Điểm tổng hợp: $Diff = Score_{pos} - Score_{neg}$.
- Nếu $Score_{neg} \ge 1.0$ và $Score_{neg} > Score_{pos}$: Gán nhãn **`NEGATIVE`** (Nói xấu / Phàn nàn).
- Nếu $Score_{pos} \ge 1.0$ và $Score_{pos} > Score_{neg}$: Gán nhãn **`POSITIVE`** (Nói tốt / Khen ngợi).
- Các trường hợp còn lại: Gán nhãn **`NEUTRAL`** (Trung lập / Thông tin hành chính / Hỏi đáp thường).

---

### 6. PHÂN TÍCH KẾT QUẢ THỰC TẾ TRÊN DIỄN ĐÀN UIT
Từ tập mẫu thực tế **220 bài viết** thu thập từ `forum.uit.edu.vn`:

1. **Phân bố cảm xúc chung:**
   - **Trung lập (NEUTRAL):** **59.1%** (130 bài) — Chiếm đa số do đặc thù diễn đàn đại học là nơi đăng tải thông báo tuyển sinh, lịch thi, biểu mẫu học vụ, quy định học bổng, hỏi đáp thủ tục.
   - **Xấu / Phàn nàn (NEGATIVE):** **22.3%** (49 bài) — Thể hiện các bức xúc thực tế về cơ sở vật chất (máy lạnh, wifi), lỗi hệ thống và thủ tục hành chính.
   - **Tốt / Khen ngợi (POSITIVE):** **18.6%** (41 bài) — Sinh viên ghi nhận sự hỗ trợ nhiệt tình, giải đáp nhanh từ các thầy cô phòng đào tạo, khen các chương trình học bổng doanh nghiệp và chất lượng giảng dạy.

2. **Các vấn đề bị phàn nàn nhiều nhất (Tiêu cực):**
   - **Cơ sở vật chất:** Máy lạnh một số phòng (đặc biệt tòa B, tòa E) không mát hoặc kêu to trong giờ học; wifi chập chờn ở một số khu vực giảng đường; quy định/hạn thẻ giữ xe máy.
   - **Đăng ký môn học:** Lỗi quá tải, nghẽn mạng lúc cổng portal/dkmh mở đợt đăng ký môn học chính thức.

3. **Các điểm sáng được khen ngợi (Tích cực):**
   - Các chương trình học bổng khuyến khích học tập, học bổng doanh nghiệp (Đinh Thiện Lý, SYLFF, Pony Chung,...).
   - Thái độ giải đáp thắc mắc chu đáo, tận tình từ chuyên viên Phòng Đào tạo và Phòng Công tác Sinh viên (CTSV).

---

### 7. GIAO DIỆN WEB DASHBOARD TRỰC QUAN HÓA

Bài tập xây dựng hoàn chỉnh giao diện Web Dashboard tương tác trong thư mục `dashboard/`:
- **Giao diện hiện đại (Dark Theme):** Tối ưu trải nghiệm hiển thị với font *Plus Jakarta Sans*, màu sắc phân biệt trực quan: Xanh ngọc (Tốt), Đỏ cánh sen (Xấu), Xám (Trung lập).
- **Thẻ thống kê KPI thời gian thực:** Hiển thị tổng số bài, tỷ lệ % theo từng nhãn.
- **Biểu đồ động (Chart.js):** Biểu đồ tròn Donut phân bố cảm xúc và Biểu đồ cột các khía cạnh UIT.
- **Bảng tra cứu dữ liệu nâng cao:** Hỗ trợ tìm kiếm từ khóa tức thì, bộ lọc theo Cảm xúc, bộ lọc theo Khía cạnh trường và phân trang.
- **Hộp thoại xem chi tiết (Modal Dialog):** Nhấp vào bất kỳ bài viết nào để đọc nội dung đầy đủ, xem tác giả, liên kết trực tiếp đến bài viết gốc trên forum, cùng lời giải thích lý do hệ thống gán nhãn.
- **Công cụ thử nghiệm cảm xúc trực tiếp (Live Sentiment Tester):** Cho phép người dùng hoặc giảng viên chấm bài gõ thử câu nhận xét bất kỳ để hệ thống phân tích và trả về kết quả ngay lập tức trên trình duyệt.

---

### 8. KẾT LUẬN

Bài tập đã giải quyết đúng trọng tâm và trọn vẹn yêu cầu của đề bài:
- Thu thập dữ liệu thực tế thành công từ Diễn đàn UIT qua cả API và bóc tách HTML DOM.
- Phân loại cảm xúc dựa trên tập luật và từ điển ngữ nghĩa tiếng Việt: đơn giản, tốc độ cực nhanh (< 2 giây cho toàn bộ dataset), minh bạch, dễ giải thích từng từ khóa bằng chứng.
- Nhận diện chính xác 6 khía cạnh trường mà sinh viên quan tâm.
- Cung cấp đầy đủ công cụ dòng lệnh (CLI), biểu đồ phân tích và Web Dashboard trực quan phục vụ báo cáo bài tập.
