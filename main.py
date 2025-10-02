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
    if not url or "help.garena.com" not in url:
        raise ValueError("Invalid Garena help link.")

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    access_token = query.get("access_token", [None])[0]
    if not access_token:
        raise ValueError("Missing access_token in link.")

    return {
        "access_token": access_token,
        "uid": query.get("account_id", ["N/A"])[0],
        "nickname": unquote(query.get("nickname", ["N/A"])[0]),
        "region": query.get("region", ["N/A"])[0],
        "lang": query.get("lang", ["N/A"])[0],
        "telegram": "@henntaiiz",
    }

# --- API Routes ---
@app.route("/parse", methods=["GET"])
def parse():
    """
    Parse Garena support link to extract access info
    Example: /api/parse?url=https://help.garena.com/?access_token=...
    """
    url = request.args.get("url", "").strip()
    try:
        data = extract_garena_info(url)
        response = {
            "success": True,
            "message": "Garena access info extracted successfully",
            "data": data
        }
        return jsonify(response), 200
    except ValueError as ve:
        logging.warning(f"Validation error: {ve}")
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Internal Server Error"}), 500

# --- Health check ---
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# --- Entry ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)