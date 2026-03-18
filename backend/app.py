import os
import random
import time
from datetime import datetime, timedelta, UTC
from functools import lru_cache

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
CORS(app, origins=[os.getenv("CORS_ORIGIN", "http://localhost:5173")])

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[
        f"{os.getenv('RATE_LIMIT_PER_HOUR')} per hour",
        f"{os.getenv('RATE_LIMIT_PER_MINUTE')} per minute",
    ],
    storage_uri="memory://",
)


CMC_API_KEY = os.getenv("CMC_API_KEY")
CMC_BASE = "https://pro-api.coinmarketcap.com/v1"


TRACKED_SYMBOLS = [
    "BTC", "ETH", "BNB", "SOL", "XRP",
    "DOGE", "ADA", "TRX", "AVAX", "DOT",
    "MATIC", "LTC",
]


_cache: dict = {}
CACHE_TTL = 300  # seconds


def _cache_get(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL:
        return entry["data"]
    return None


def _cache_set(key: str, data):
    _cache[key] = {"ts": time.time(), "data": data}



def _cmc_headers() -> dict:
    if not CMC_API_KEY:
        raise RuntimeError("CMC_API_KEY is not set in .env")
    return {
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
        "Accept": "application/json",
    }


def fetch_latest_quotes(symbols: list[str]) -> dict:
    """Fetch current prices for a list of symbols from CMC."""
    cache_key = "latest_" + ",".join(sorted(symbols))
    cached = _cache_get(cache_key)
    if cached:
        return cached

    url = f"{CMC_BASE}/cryptocurrency/quotes/latest"
    params = {"symbol": ",".join(symbols), "convert": "USD"}
    resp = requests.get(url, headers=_cmc_headers(), params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("data", {})
    _cache_set(cache_key, data)
    return data


def fetch_historical_price(symbol: str, days_ago: int = 30) -> float | None:
    """
    CMC's free tier doesn't expose OHLCV history, so we use the
    /v2/cryptocurrency/ohlcv/historical endpoint (available on Basic+).
    For free-tier users we fall back to the 30d percent_change supplied
    in the latest quotes endpoint (percent_change_30d).
    This function returns the historical price if available, else None.
    """
    # We rely on percent_change_30d embedded in the latest quote instead of
    # a separate historical call – keeps API usage minimal.
    return None


def build_coin_payload(symbols: list[str]) -> list[dict]:
    """Build the enriched coin list used by the frontend."""
    raw = fetch_latest_quotes(symbols)
    coins = []
    for symbol in symbols:
        entry = raw.get(symbol)
        if not entry:
            continue
        # CMC returns a list when a symbol maps to multiple coins; take first
        if isinstance(entry, list):
            entry = entry[0]

        quote = entry.get("quote", {}).get("USD", {})
        current_price = quote.get("price")
        change_30d = quote.get("percent_change_30d")  # built-in, no extra call

        if current_price is None or change_30d is None:
            continue

        # Derive approximate old price from the 30-day percent change
        old_price = current_price / (1 + change_30d / 100)

        coins.append({
            "id": entry.get("id"),
            "name": entry.get("name"),
            "symbol": symbol,
            "slug": entry.get("slug"),
            "current_price": current_price,
            "old_price": old_price,
            "change_30d": change_30d,
            "change_24h": quote.get("percent_change_24h"),
            "change_7d": quote.get("percent_change_7d"),
            "market_cap": quote.get("market_cap"),
            "volume_24h": quote.get("volume_24h"),
            "is_popping": change_30d > 0,
            "logo_url": f"https://s2.coinmarketcap.com/static/img/coins/64x64/{entry.get('id')}.png",
        })
    return coins


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(UTC).isoformat()})


@app.route("/api/coins")
@limiter.limit("30 per minute; 200 per hour")
def get_coins():
    """
    Returns a randomised selection of 6 coins from the 12 tracked.
    Query params:
      filter=all|increasing|decreasing   (default: all → random 6)
    """
    filter_param = request.args.get("filter", "all").lower()

    try:
        all_coins = build_coin_payload(TRACKED_SYMBOLS)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 500
        return jsonify({"error": "Upstream API error", "detail": str(e)}), status
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    if filter_param == "increasing":
        result = [c for c in all_coins if c["is_popping"]]
    elif filter_param == "decreasing":
        result = [c for c in all_coins if not c["is_popping"]]
    else:
        # Random 6 from all valid coins
        shuffled = all_coins.copy()
        random.shuffle(shuffled)
        result = shuffled[:6]

    return jsonify({
        "coins": result,
        "filter": filter_param,
        "cached_until": datetime.now(UTC).isoformat(),
        "total": len(result),
    })


@app.route("/api/coins/chart")
@limiter.limit("10 per minute; 60 per hour")
def get_chart_data():
    """
    Returns percentage change data for all tracked coins for bar chart.
    """
    try:
        all_coins = build_coin_payload(TRACKED_SYMBOLS)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 500
        return jsonify({"error": "Upstream API error", "detail": str(e)}), status
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    chart_data = [
        {
            "symbol": c["symbol"],
            "name": c["name"],
            "change_30d": round(c["change_30d"], 2),
            "change_7d": round(c["change_7d"], 2) if c["change_7d"] else None,
            "change_24h": round(c["change_24h"], 2) if c["change_24h"] else None,
            "is_popping": c["is_popping"],
        }
        for c in all_coins
    ]
    return jsonify({"chart": chart_data})


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Too many requests",
        "message": "You've hit the rate limit. Please slow down.",
        "retry_after": str(e.description),
    }), 429


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(debug=debug, host="0.0.0.0", port=5000)
