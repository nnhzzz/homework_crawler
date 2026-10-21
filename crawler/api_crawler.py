"""
Module thu thập dữ liệu Diễn đàn UIT qua Discourse REST API.
API Endpoints:
- /latest.json?page=N : Danh sách chủ đề mới nhất
- /search.json?q=KEYWORD : Tìm kiếm chủ đề theo từ khóa
- /t/{topic_id}.json : Chi tiết chủ đề và các bài viết (posts)
"""

import time
import json
import logging
from typing import List, Dict, Any, Optional
import requests
import pandas as pd
from bs4 import BeautifulSoup

from config import FORUM_BASE_URL, DEFAULT_HEADERS, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("APICrawler")


class UITApiCrawler:
    def __init__(self, base_url: str = FORUM_BASE_URL, headers: Optional[Dict[str, str]] = None, delay: float = 0.5):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or DEFAULT_HEADERS
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Gửi GET request với xử lý lỗi và rate-limit."""
        url = f"{self.base_url}{endpoint}" if endpoint.startswith("/") else f"{self.base_url}/{endpoint}"
        try:
            time.sleep(self.delay)
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Bị giới hạn tốc độ (Rate limited 429). Tạm dừng 5 giây...")
                time.sleep(5)
                return self._get(endpoint, params)
            else:
                logger.error(f"Lỗi HTTP {response.status_code} khi tải {url}")
                return None
        except Exception as e:
            logger.error(f"Ngoại lệ khi gọi {url}: {e}")
            return None

    def crawl_latest_topics(self, max_pages: int = 3) -> List[Dict[str, Any]]:
        """Thu thập danh sách chủ đề mới nhất qua /latest.json."""
        all_topics = []
        seen_ids = set()

        for page in range(max_pages):
            logger.info(f"[API] Đang cào trang mới nhất page={page}...")
            data = self._get(f"/latest.json", params={"page": page})
            if not data or "topic_list" not in data or "topics" not in data["topic_list"]:
                logger.warning(f"Không lấy được dữ liệu trang {page}. Dừng.")
                break

            topics = data["topic_list"]["topics"]
            if not topics:
                break

            for t in topics:
                t_id = t.get("id")
                if t_id and t_id not in seen_ids:
                    seen_ids.add(t_id)
                    all_topics.append({
                        "id": t_id,
                        "title": t.get("title", ""),
                        "slug": t.get("slug", ""),
                        "views": t.get("views", 0),
                        "posts_count": t.get("posts_count", 0),
                        "like_count": t.get("like_count", 0),
                        "created_at": t.get("created_at", ""),
                        "category_id": t.get("category_id", None),
                        "url": f"{self.base_url}/t/{t.get('slug', 'topic')}/{t_id}"
                    })

        logger.info(f"[API] Thu thập được {len(all_topics)} chủ đề từ latest feed.")
        return all_topics

    def crawl_topics_by_keywords(self, keywords: List[str], max_per_kw: int = 30) -> List[Dict[str, Any]]:
        """Thu thập chủ đề liên quan qua tìm kiếm từ khóa (để gom bài về CSVC, học phí, giảng viên...)."""
        collected_topics = []
        seen_ids = set()

        for kw in keywords:
            logger.info(f"[API] Đang tìm kiếm chủ đề với từ khóa: '{kw}'...")
            data = self._get("/search.json", params={"q": kw})
            if not data or "topics" not in data:
                continue

            topics = data.get("topics", [])
            count = 0
            for t in topics:
                t_id = t.get("id")
                if t_id and t_id not in seen_ids:
                    seen_ids.add(t_id)
                    collected_topics.append({
                        "id": t_id,
                        "title": t.get("title", ""),
                        "slug": t.get("slug", ""),
                        "views": t.get("views", 0),
                        "posts_count": t.get("posts_count", 0),
                        "like_count": t.get("like_count", 0),
                        "created_at": t.get("created_at", ""),
                        "category_id": t.get("category_id", None),
                        "url": f"{self.base_url}/t/{t.get('slug', 'topic')}/{t_id}",
                        "matched_keyword": kw
                    })
                    count += 1
                    if count >= max_per_kw:
                        break

        logger.info(f"[API] Thu thập được {len(collected_topics)} chủ đề từ tìm kiếm từ khóa.")
        return collected_topics

    def fetch_topic_content(self, topic_id: int, max_posts: int = 5) -> Dict[str, Any]:
        """Tải nội dung chi tiết bài viết gốc và các bình luận phản hồi trong một chủ đề."""
        data = self._get(f"/t/{topic_id}.json")
        if not data:
            return {"first_post": "", "replies": [], "author": "", "full_text": ""}

        post_stream = data.get("post_stream", {}).get("posts", [])
        if not post_stream:
            return {"first_post": "", "replies": [], "author": "", "full_text": ""}

        # Bài viết mở đầu (original post)
        first_post_obj = post_stream[0]
        first_post_cooked = first_post_obj.get("cooked", "")
        author = first_post_obj.get("username", "")

        # Chuyển HTML cooked sang text thuần
        first_post_text = BeautifulSoup(first_post_cooked, "html.parser").get_text(separator=" ", strip=True)

        # Các bình luận phản hồi
        replies_text = []
        for post in post_stream[1:max_posts]:
            cooked = post.get("cooked", "")
            text = BeautifulSoup(cooked, "html.parser").get_text(separator=" ", strip=True)
            if text:
                replies_text.append({
                    "username": post.get("username", ""),
                    "content": text
                })

        all_text_list = [first_post_text] + [r["content"] for r in replies_text]
        full_text = " | ".join(all_text_list)

        return {
            "first_post": first_post_text,
            "replies": replies_text,
            "author": author,
            "full_text": full_text
        }

    def crawl_full_dataset(self, latest_pages: int = 3, search_keywords: Optional[List[str]] = None, max_topics: int = 150) -> List[Dict[str, Any]]:
        """Quy trình cào hoàn chỉnh: Gom danh sách topics -> Tải chi tiết nội dung từng bài."""
        topics = self.crawl_latest_topics(max_pages=latest_pages)

        if search_keywords:
            kw_topics = self.crawl_topics_by_keywords(search_keywords)
            # Hợp nhất tránh trùng lặp
            existing_ids = {t["id"] for t in topics}
            for kt in kw_topics:
                if kt["id"] not in existing_ids:
                    existing_ids.add(kt["id"])
                    topics.append(kt)

        topics = topics[:max_topics]
        logger.info(f"[API] Bắt đầu lấy nội dung chi tiết cho {len(topics)} chủ đề...")

        full_dataset = []
        for idx, t in enumerate(topics, 1):
            if idx % 10 == 0 or idx == len(topics):
                logger.info(f"Đang xử lý {idx}/{len(topics)}: {t['title'][:40]}...")

            details = self.fetch_topic_content(t["id"])
            item = {
                **t,
                "author": details["author"],
                "first_post": details["first_post"],
                "replies_count": len(details["replies"]),
                "content": details["first_post"],
                "full_text": f"{t['title']}. {details['full_text']}"
            }
            full_dataset.append(item)

        return full_dataset

    def save_dataset(self, dataset: List[Dict[str, Any]], filename_prefix: str = "uit_forum_api") -> Dict[str, str]:
        """Lưu dữ liệu ra định dạng JSON và CSV trong data/raw/."""
        json_path = RAW_DATA_DIR / f"{filename_prefix}.json"
        csv_path = RAW_DATA_DIR / f"{filename_prefix}.csv"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        df = pd.DataFrame(dataset)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

        logger.info(f"Đã lưu {len(dataset)} bản ghi vào:")
        logger.info(f" - JSON: {json_path}")
        logger.info(f" - CSV:  {csv_path}")

        return {"json": str(json_path), "csv": str(csv_path)}
