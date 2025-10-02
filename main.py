from flask import Flask, request, jsonify
from urllib.parse import urlparse, parse_qs, unquote
import logging

# --- Config ---
app = Flask(__name__)

@app.route('/')
def home():
    return "PEOPLE CREATE API: @henntaiiz"
    
# Cấu hình logging cho debug production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# --- Helper ---
def extract_garena_info(url: str) -> dict:
    """
    Extract Garena access info from help.garena.com URL
    """
    if not url:
        raise ValueError("Missing url parameter.")

    # Parse lớp ngoài
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Nếu query ngoài có param "url" -> parse tiếp lớp trong
    if "url" in query:
        inner_url = query.get("url", [None])[0]
        if not inner_url or "help.garena.com" not in inner_url:
            raise ValueError("Invalid Garena help link.")
        parsed_inner = urlparse(inner_url)
        inner_query = parse_qs(parsed_inner.query)
    else:
        # Không có lớp ngoài, parse trực tiếp
        if "help.garena.com" not in url:
            raise ValueError("Invalid Garena help link.")
        inner_query = query

    # Lấy các giá trị từ lớp trong
    access_token = inner_query.get("access_token", [None])[0]
    if not access_token:
        raise ValueError("Missing access_token in link.")

    account_id = inner_query.get("account_id", ["N/A"])[0]
    nickname = unquote(inner_query.get("nickname", ["N/A"])[0])
    region = inner_query.get("region", ["N/A"])[0]
    lang = inner_query.get("lang", ["N/A"])[0]
    game = inner_query.get("game", ["N/A"])[0]

    return {
        "game": game,
        "access_token": access_token,
        "uid": account_id,
        "nickname": nickname,
        "region": region,
        "lang": lang,
        "telegram": "@henntaiiz",
    }

# --- API Routes ---
# ĐÃ SỬA: Đổi từ "/parse" thành "/extract" để khớp với cấu hình bot telegram
@app.route("/extract", methods=["GET"])
def parse():
    raw_query = request.query_string.decode()  # lấy query gốc chưa bị Flask xử lý
    # Tách thủ công url=
    if raw_query.startswith("url="):
        inner_url = unquote(raw_query[4:])
    else:
        inner_url = request.args.get("url", "")

    try:
        data = extract_garena_info(inner_url)
        return jsonify({
            "status": "success", # Đã sửa: Thay "success": True bằng "status": "success" để khớp với code kiểm tra trong bot
            "message": "Garena access info extracted successfully",
            "data": data
        }), 200
    except ValueError as ve:
        # Đã sửa: Thay "success": False bằng "status": "error"
        return jsonify({"status": "error", "error": str(ve)}), 400
        
# --- Health check ---
# --- ĐÃ SỬA: Chức năng mới cho /health (Hướng dẫn API) ---
@app.route("/health", methods=["GET"])
def health_guide():
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Hướng dẫn sử dụng API Garena Info Extractor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            code { background-color: #eee; padding: 2px 4px; border-radius: 3px; }
            pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            h2 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Hướng dẫn sử dụng API Garena Info Extractor</h1>
        <p>API này được tạo bởi <strong>@henntaiiz</strong>, dùng để trích xuất Access Token, UID và Nickname từ liên kết hỗ trợ Garena (<code>help.garena.com</code>).</p>

        <h2>Endpoint chính</h2>
        <p><code>GET /extract</code></p>

        <h2>Tham số bắt buộc</h2>
        <ul>
            <li>
                <strong>Tên tham số:</strong> <code>url</code>
            </li>
            <li>
                <strong>Mô tả:</strong> Liên kết <code>help.garena.com</code> (ví dụ: <code>https://help.garena.com/?access_token=...</code>). Liên kết này cần được mã hóa (URL-encode) nếu gửi qua trình duyệt hoặc công cụ API.
            </li>
        </ul>

        <h2>Ví dụ sử dụng</h2>
        <p>Giả sử BASE_URL là <code>https://fantastic-palm-tree.vercel.app</code>:</p>
        <pre><code>[BASE_URL]/extract?url=https://help.garena.com/?access_token=...&amp;nickname=...</code></pre>

        <h2>Phản hồi (Response) thành công (HTTP 200)</h2>
        <pre><code>{
    "status": "success",
    "message": "Garena access info extracted successfully",
    "data": {
        "game": "FF",
        "access_token": "0b4f6044be4ef51d41d7346b9a03a124f5cdad...",
        "uid": "12345678",
        "nickname": "HenTaiz",
        "region": "TH",
        "lang": "en",
        "telegram": "@henntaiiz"
    }
}</code></pre>

        <h2>Phản hồi (Response) lỗi (HTTP 400)</h2>
        <pre><code>{
    "status": "error",
    "error": "Missing access_token in link."
}</code></pre>
    </body>
    </html>
    """
    return html_content

# --- Entry ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
