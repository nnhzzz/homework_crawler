"""
Module thu thập dữ liệu Diễn đàn UIT qua HTML Scraping sử dụng BeautifulSoup.
Phương pháp này phân tích trực tiếp cây DOM HTML của diễn đàn (chế độ crawler của Discourse),
phục vụ đặc thù yêu cầu môn học Kỹ thuật Thu thập dữ liệu Web (Web Scraping).
"""

import time
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd

from config import FORUM_BASE_URL, DEFAULT_HEADERS, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HTMLCrawler")


class UITHtmlCrawler:
    def __init__(self, base_url: str = FORUM_BASE_URL, headers: Optional[Dict[str, str]] = None, delay: float = 0.8):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or DEFAULT_HEADERS
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _fetch_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Tải trang web và parse thành BeautifulSoup object."""
        try:
            time.sleep(self.delay)
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                return BeautifulSoup(resp.text, "html.parser")
            else:
                logger.error(f"Lỗi HTTP {resp.status_code} khi tải {url}")
                return None
        except Exception as e:
            logger.error(f"Ngoại lệ tải {url}: {e}")
            return None

    def crawl_topic_list(self, pages: int = 2) -> List[Dict[str, Any]]:
        """
        Cào danh sách các chủ đề từ trang /latest qua HTML.
        Phân tích bảng topic-list: thẻ <tr>, tiêu đề trong <a> class 'title', số lượt trả lời, lượt xem...
        """
        topics = []
        seen_urls = set()

        for page in range(pages):
            url = f"{self.base_url}/latest?no_definitions=true&page={page}"
            logger.info(f"[HTML] Đang cào danh sách chủ đề: {url}")
            soup = self._fetch_soup(url)
            if not soup:
                continue

            # Discourse crawler mode render bảng topic-list
            rows = soup.select("table.topic-list tr")
            if not rows:
                # Thử tìm thẻ item khác
                rows = soup.select("tr.topic-list-item")

            logger.info(f"[HTML] Tìm thấy {len(rows)} dòng trên trang {page}")

            for row in rows:
                link_tag = row.select_one("a.title") or row.select_one("td.main-link a")
                if not link_tag:
                    continue

                title = link_tag.get_text(strip=True)
                relative_url = link_tag.get("href", "")
                full_url = urljoin(self.base_url, relative_url)

                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)

                # Lấy id từ URL (dạng /t/slug/id)
                topic_id = None
                parts = full_url.strip("/").split("/")
                if parts and parts[-1].isdigit():
                    topic_id = int(parts[-1])

                # Số lượt trả lời / bài viết
                posts_col = row.select_one("td.posts") or row.select_one("span.posts")
                posts_count = posts_col.get_text(strip=True) if posts_col else "0"

                # Số lượt xem
                views_col = row.select_one("td.views") or row.select_one("span.views")
                views = views_col.get_text(strip=True) if views_col else "0"

                topics.append({
                    "id": topic_id,
                    "title": title,
                    "url": full_url,
                    "posts_count": posts_count,
                    "views": views
                })

        logger.info(f"[HTML] Tổng số chủ đề cào được từ HTML: {len(topics)}")
        return topics

    def crawl_topic_details(self, topic_url: str) -> Dict[str, Any]:
        """
        Tải và bóc tách nội dung chi tiết bài viết từ trang HTML chủ đề.
        Cấu trúc DOM Discourse crawler:
        - div.topic-body crawler-post
        - div.post (nội dung)
        - div.crawler-post-meta (tác giả, ngày đăng)
        """
        soup = self._fetch_soup(topic_url)
        if not soup:
            return {"author": "", "first_post": "", "replies": [], "full_text": ""}

        # Tiêu đề từ thẻ <h1>
        h1_tag = soup.find("h1")
        title = h1_tag.get_text(strip=True) if h1_tag else ""

        # Các bài viết (post) trong chủ đề
        post_elements = soup.select("div.crawler-post")
        if not post_elements:
            post_elements = soup.select("div.topic-body")

        first_post_text = ""
        author = ""
        replies = []

        for idx, post_elem in enumerate(post_elements):
            # Tác giả
            creator_tag = post_elem.select_one("span[itemprop='author'] span[itemprop='name']") or post_elem.select_one(".creator")
            post_author = creator_tag.get_text(strip=True) if creator_tag else "Ẩn danh"

            # Nội dung post
            content_tag = post_elem.select_one("div.post") or post_elem.select_one("div[itemprop='articleBody']")
            post_text = content_tag.get_text(separator=" ", strip=True) if content_tag else ""

            if idx == 0:
                first_post_text = post_text
                author = post_author
            else:
                if post_text:
                    replies.append({
                        "author": post_author,
                        "text": post_text
                    })

        all_text_list = [first_post_text] + [r["text"] for r in replies]
        full_text = " | ".join(all_text_list)

        return {
            "title": title,
            "author": author,
            "first_post": first_post_text,
            "replies": replies,
            "replies_count": len(replies),
            "full_text": f"{title}. {full_text}" if title else full_text
        }

    def crawl_dataset(self, pages: int = 2, max_topics: int = 50) -> List[Dict[str, Any]]:
        """Quy trình cào hoàn chỉnh bằng BeautifulSoup."""
        topics = self.crawl_topic_list(pages=pages)
        topics = topics[:max_topics]

        dataset = []
        for idx, t in enumerate(topics, 1):
            logger.info(f"[HTML] Đang bóc tách chi tiết ({idx}/{len(topics)}): {t['title'][:40]}...")
            details = self.crawl_topic_details(t["url"])
            item = {
                "id": t["id"],
                "title": t["title"] or details["title"],
                "url": t["url"],
                "author": details["author"],
                "content": details["first_post"],
                "first_post": details["first_post"],
                "replies_count": details["replies_count"],
                "full_text": details["full_text"],
                "views": t["views"]
            }
            dataset.append(item)

        return dataset

    def save_dataset(self, dataset: List[Dict[str, Any]], filename_prefix: str = "uit_forum_html") -> Dict[str, str]:
        """Lưu kết quả ra file."""
        json_path = RAW_DATA_DIR / f"{filename_prefix}.json"
        csv_path = RAW_DATA_DIR / f"{filename_prefix}.csv"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        df = pd.DataFrame(dataset)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

        logger.info(f"Đã lưu {len(dataset)} bản ghi HTML vào:")
        logger.info(f" - JSON: {json_path}")
        logger.info(f" - CSV:  {csv_path}")

        return {"json": str(json_path), "csv": str(csv_path)}
