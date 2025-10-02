from flask import Flask, request, jsonify
from urllib.parse import urlparse, parse_qs, unquote
import logging

# --- Config ---
app = Flask(__name__)

# Danh sách Key hợp lệ (Ví dụ)
# Key: Status (True = Hoạt động, False = Ngừng hoạt động)
# Lưu ý: Trong môi trường production, bạn nên lưu trữ key an toàn hơn (ví dụ: database hoặc biến môi trường)
DANH_SACH_KEY = {
    "hentaiz": True,  # Key mẫu, True là còn hoạt động
    "key_khac": False, # Key mẫu, False là ngừng hoạt động
    "xxxxxxxx": True, # Key mẫu
}

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
@app.route("/extract", methods=["GET"])
def parse():
    # 1. KIỂM TRA API KEY
    api_key = request.args.get("key")

    if not api_key:
        return jsonify({"status": "error", "error": "API Key bị thiếu. Vui lòng cung cấp key."}), 401 # 401: Unauthorized

    if api_key not in DANH_SACH_KEY or DANH_SACH_KEY[api_key] is not True:
        return jsonify({"status": "error", "error": "API Key không hợp lệ hoặc đã hết hạn."}), 403 # 403: Forbidden

    # 2. XỬ LÝ URL SAU KHI KEY HỢP LỆ
    raw_query = request.query_string.decode()
    # Tách thủ công url= (cần phải xử lý key=... trước nếu nó nằm ở đầu)
    
    # Cách an toàn hơn để lấy 'url' khi đã lấy 'key' bằng request.args.get()
    inner_url = request.args.get("url", "")

    try:
        data = extract_garena_info(inner_url)
        return jsonify({
            "status": "success",
            "message": "Garena access info extracted successfully",
            "data": data
        }), 200
    except ValueError as ve:
        return jsonify({"status": "error", "error": str(ve)}), 400
        
# --- Chức năng /health hiển thị Hướng dẫn API (bao gồm cách lấy token) ---
@app.route("/health", methods=["GET"])
def health_guide():
    # Tạo hyperlink cho help.garena.com
    garena_link = '<a href="https://help.garena.com/">help.garena.com</a>'
    
    api_link = '<a href="https://fantastic-palm-tree.vercel.app">https://fantastic-palm-tree.vercel.app</a>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Hướng dẫn sử dụng API Garena Info Extractor</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            code {{ background-color: #eee; padding: 2px 4px; border-radius: 3px; }}
            pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            h2 {{ color: #333; }}
            ol {{ padding-left: 20px; }}
        </style>
    </head>
    <body>
        <h1>Hướng dẫn sử dụng API Garena Info Extractor</h1>
        <p>API này được tạo bởi <strong>@henntaiiz</strong>, dùng để trích xuất Access Token, UID và Nickname từ liên kết hỗ trợ Garena (<code>{garena_link}</code>).</p>

        <h2>Hướng dẫn lấy liên kết Garena Access Token</h2>
        <p>Để nhận được liên kết</p>
        <p>{garena_link}</p>
        <p>có chứa Access Token, bạn thường phải thực hiện theo các bước sau trong quá trình đăng nhập hoặc truy cập hỗ trợ của Garena:</p>
        <ol>
            <li>Đăng nhập tài khoản Garena/Free Fire trên trình duyệt (thông thường là đăng nhập vào trang Hỗ trợ Garena).</li>
            <li>Tìm kiếm và truy cập vào một liên kết hỗ trợ nội bộ hoặc liên kết kiểm tra thông tin tài khoản.</li>
            <li>Sau khi Garena xác thực bạn và chuyển hướng đến trang hỗ trợ/trang khác, trình duyệt sẽ hiển thị URL dạng 
            <li><code>https://help.garena.com/?access_token=...</code>.</li>
            <li><strong>Sao chép toàn bộ liên kết này</strong> để gửi đến bot Telegram hoặc sử dụng với API <code>/extract</code>.</li>
            <li><em>Lưu ý: Quá trình này có thể thay đổi tùy theo chính sách của Garena.</em></li>
        </ol>

        <h2>Endpoint chính</h2>
        <p><code>GET /extract</code></p>

        <h2>Tham số bắt buộc</h2>
        <ul>
            <li>
                <strong>API KEY:</strong> <code>key</code>
                <p>Mã khóa API được cung cấp để xác thực. (Ví dụ: <code>key=xxxxxxxx</code>)</p>
            </li>
            <li>
                <strong>URL:</strong> <code>url</code>
                <p>Liên kết {garena_link} đã sao chép ở trên. Liên kết này cần được mã hóa (URL-encode) nếu gửi qua trình duyệt hoặc công cụ API.</p>
            </li>
        </ul>

        <h2>Ví dụ sử dụng</h2>
        <p>Giả sử BASE_URL là</p>
        <p><code>{api_link}</code>:</p>
        <pre><code>[BASE_URL]/extract?key=xxxxxxxx&amp;url=https://help.garena.com/?access_token=...&amp;nickname=...</code></pre>

        <h2>Phản hồi (Response) thành công (HTTP 200)</h2>
        <pre><code>{{
    "status": "success",
    "message": "Garena access info extracted successfully",
    "data": {{
        "game": "FF",
        "access_token": "0b4f6044be4ef51d41d7346b9a03a124f5cdad...",
        "uid": "xxxxxxxx",
        "nickname": "HenTaiz",
        "region": "TH",
        "lang": "en",
        "telegram": "@henntaiiz"
    }}
}}</code></pre>

        <h2>Phản hồi (Response) lỗi (HTTP 401/403 - Lỗi Key)</h2>
        <pre><code>{{
    "status": "error",
    "error": "API Key bị thiếu. Vui lòng cung cấp key."
}}</code></pre>

        <h2>Phản hồi (Response) lỗi (HTTP 400 - Lỗi URL)</h2>
        <pre><code>{{
    "status": "error",
    "error": "Missing access_token in link."
}}</code></pre>
    </body>
    </html>
    """
    return html_content

# --- Entry ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
