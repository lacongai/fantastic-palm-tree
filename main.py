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
@app.route("/parse", methods=["GET"])
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
            "success": True,
            "message": "Garena access info extracted successfully",
            "data": data
        }), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
        
# --- Health check ---
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# --- Entry ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)