# 🪙 Crypto Point

Real-time cryptocurrency tracker — Flask backend + React frontend, powered by CoinMarketCap API.

---

## Project Structure

```
crypto-point/
├── backend/
│   ├── app.py              ← Flask API
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── CoinCard.jsx
│   │   │   └── CryptoBarChart.jsx
│   │   ├── hooks/
│   │   │   └── useCoins.js
│   │   └── utils/
│   │       └── api.js
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── .env
└── README.md
```

---

## Setup

### 1. Get a CoinMarketCap API key
- Sign up free at https://coinmarketcap.com/api/
- Copy your API key

### 2. Backend

```bash
cd backend
# Edit .env — paste your CMC_API_KEY

# Create virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Run
python app.py
# → Flask running on http://localhost:5000
```

### 3. Frontend

```bash
cd frontend

# Install deps
npm install

# Run dev server
npm run dev
# → Vite running on http://localhost:5173
```

Open **http://localhost:5173** in your browser.

---

## Environment Variables

### `backend/.env`
| Variable | Description | Default |
|---|---|---|
| `CMC_API_KEY` | **Required.** Your CoinMarketCap API key | — |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions | `dev-secret-key` |
| `FLASK_ENV` | `development` or `production` | `production` |
| `RATE_LIMIT_PER_MINUTE` | Max requests per IP per minute | `10` |
| `RATE_LIMIT_PER_HOUR` | Max requests per IP per hour | `100` |
| `CORS_ORIGIN` | Allowed frontend origin | `http://localhost:5173` |

### `frontend/.env`
| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Backend URL (leave empty if using Vite proxy) | `` |

---

## API Endpoints

| Endpoint | Method | Rate Limit | Description |
|---|---|---|---|
| `/api/health` | GET | default | Health check |
| `/api/coins?filter=all\|increasing\|decreasing` | GET | 30/min, 200/hr | Fetch coins |
| `/api/coins/chart` | GET | 10/min, 60/hr | Chart data |

---

## Features
- ✅ 12 tracked coins — 6 shown at a time (randomised)
- ✅ Filter by increasing / decreasing 30-day change
- ✅ Bar chart with percentage change visualisation
- ✅ Server-side 5-minute cache (reduces CoinMarketCap quota usage)
- ✅ Per-IP rate limiting (flask-limiter) — prevents API abuse
- ✅ Client-side refresh cooldown (8s)
- ✅ Auto-refresh every 5 minutes
- ✅ All credentials in `.env` — nothing hardcoded
- ✅ Fully responsive (mobile → desktop)

---

## Production Notes

For production deployment:

1. Set `FLASK_ENV=production` in backend `.env`
2. Change `FLASK_SECRET_KEY` to a long random string
3. Set `CORS_ORIGIN` to your actual frontend domain
4. Use a proper WSGI server: `gunicorn app:app`
5. Build the frontend: `npm run build` → serve the `dist/` folder via nginx
