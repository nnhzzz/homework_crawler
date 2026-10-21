"""
Script khởi chạy Dashboard trực quan hóa Diễn đàn UIT:
python3 run_dashboard.py
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent / "dashboard"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)


def main():
    os.chdir(Path(__file__).parent)
    print("=" * 60)
    print(" KHỞI CHẠY UIT FORUM SENTIMENT DASHBOARD")
    print("=" * 60)
    print(f"Địa chỉ truy cập: http://localhost:{PORT}")
    print(f"Thư mục phục vụ:  {DIRECTORY}")
    print("Nhấn Ctrl + C để dừng máy chủ.")
    print("=" * 60)

    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nĐã tắt máy chủ Dashboard.")


if __name__ == "__main__":
    main()
