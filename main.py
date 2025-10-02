from flask import Flask, request, jsonify
import urllib.parse
import re
import logging

# --- Config ---
app = Flask(__name__)

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

    # Regex cho các tham số quan trọng
    token_match = re.search(r"access_token=([a-fA-F0-9]{64})", url)
    uid_match = re.search(r"account_id=(\d+)", url)
    nick_match = re.search(r"nickname=([^&]+)", url)
    region_match = re.search(r"region=([A-Z]+)", url)
    lang_match = re.search(r"lang=([a-zA-Z-]+)", url)

    if not token_match:
        raise ValueError("Missing access_token in link.")

    return {
        "access_token": token_match.group(1),
        "uid": uid_match.group(1) if uid_match else "N/A",
        "nickname": urllib.parse.unquote(nick_match.group(1)) if nick_match else "N/A",
        "region": region_match.group(1) if region_match else "N/A",
        "lang": lang_match.group(1) if lang_match else "N/A",
        "telegram": "@henntaiiz",
    }

# --- API Routes ---
@app.route("/api/parse", methods=["GET"])
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
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# --- Entry ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)