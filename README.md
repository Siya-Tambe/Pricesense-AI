# PriceSense 🎯
### *Know when to buy. Let AI decide.*

PriceSense is a full-stack AI-powered price tracking web app for Indian e-commerce platforms. Paste any product URL, and PriceSense automatically tracks the price every 8 hours, builds a price history, and uses AI to tell you whether to **Buy now**, **Wait**, or keep **Watching** — in plain English.

---

## 📸 Screenshots

| Landing Page | Dashboard |
|---|---|
| ![Landing]("D:\Projects\PriceSense\frontend\Landing_page.png") | ![Dashboard]("D:\Projects\PriceSense\frontend\Dashboard_page.png") 

---

## ✨ Features

- 🔗 **URL-based tracking** — paste any product link, no CSV or manual data entry
- 🤖 **AI Buy/Wait verdict** — powered by time-series forecasting with confidence levels (High / Medium / Low)
- 📊 **Interactive price chart** — actual prices + 7-day forecast with a dashed line
- 🏷️ **Sale event markers** — 12 Indian shopping events annotated on the chart (Big Billion Days, Great Indian Festival, Diwali Sale, etc.)
- ⚡ **Auto price fetching** — prices fetched every 8 hours automatically in the background
- 🔔 **Price alerts** — set a target price and get notified when it drops below it
- 🟢 **Scraping health indicator** — shows when data was last fetched and warns if a URL is stale
- 🌙 **Premium dark UI** — built with Tailwind CSS + Stitch design system

---

## 🛒 Supported Platforms

| Platform | Type |
|---|---|
| Amazon India | E-commerce |
| Flipkart | E-commerce |
| Myntra | Fashion |
| Croma | Electronics |
| Reliance Digital | Electronics |
| Meesho | Fashion / General |
| Tata CLiQ | Multi-category |
| Snapdeal | Multi-category |

---

## 🗂️ Project Structure

```
PriceSense/
├── start.bat                  ← One-click launcher (Windows)
├── backend/
│   ├── main.py                ← FastAPI server + all API routes
│   ├── models.py              ← SQLite database models
│   ├── scraper.py             ← Price scraping for all 8 platforms
│   ├── predictor.py           ← Buy/Wait verdict + forecasting engine
│   ├── scheduler.py           ← Background price fetch every 8 hours
│   ├── requirements.txt       ← Python dependencies
│   └── .env                   ← Environment variables (not committed)
└── frontend/
    ├── index.html             ← Landing page
    ├── dashboard.html         ← Watchlist + market control panel
    ├── product.html           ← Product detail + chart + verdict
    ├── css/
    │   └── style.css          ← Custom styles
    └── js/
        ├── api.js             ← All backend API calls + helpers
        ├── chart.js           ← Chart.js price history + sale events
        ├── dashboard.js       ← Watchlist rendering logic
        └── product.js         ← Product page logic
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### 1. Clone the repository
```bash
git clone https://github.com/your-username/pricesense.git
cd pricesense
```

### 2. Set up the backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Configure environment variables
Create a `.env` file inside the `backend/` folder:
```env
DATABASE_URL=sqlite:///./pricesense.db
ANTHROPIC_API_KEY=your_key_here
SECRET_KEY=your_random_secret_key
```

### 4. Start the backend server
```bash
python -m uvicorn main:app --reload
```

The API will be running at `http://127.0.0.1:8000`

### 5. Open the frontend
Open `frontend/index.html` in your browser — that's it!

---

## 🖥️ One-Click Launch (Windows)

Double-click `start.bat` in the root folder. It will:
- Activate the virtual environment automatically
- Start the backend server minimized in the background
- Open the app in your default browser
- Auto-restart the server if it crashes

---

## 🔌 API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/track` | Add a new product URL |
| `GET` | `/products` | Get all tracked products |
| `GET` | `/products/{id}` | Get product with full history + verdict |
| `POST` | `/products/{id}/refresh` | Manually re-fetch price now |
| `POST` | `/alerts` | Set a price drop alert |
| `DELETE` | `/products/{id}` | Stop tracking a product |

Interactive API docs available at `http://127.0.0.1:8000/docs`

---

## 🧠 How the Prediction Engine Works

1. **Data collection** — prices are fetched every 8 hours and stored in SQLite
2. **Smoothing** — a moving average filters out random noise
3. **Trend** — linear regression identifies whether the price is rising or falling
4. **Volatility** — measures how much the price swings historically
5. **Forecast** — projects day 3 and day 7 prices based on the trend
6. **Verdict** — combines forecast direction, volatility, and proximity to all-time low:
   - **Buy** — price near all-time low, or predicted to rise
   - **Wait** — price predicted to drop 3%+ with medium/high confidence
   - **Watching** — not enough data or unclear trend

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | SQLite |
| Scraping | BeautifulSoup, Playwright, requests |
| Prediction | pandas, scikit-learn |
| Scheduling | APScheduler |
| Frontend | HTML, Tailwind CSS (CDN), Vanilla JS |
| Charts | Chart.js + chartjs-plugin-annotation |
| Fonts | Manrope + Inter (Google Fonts) |

---

## 📋 Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | SQLite DB path — `sqlite:///./pricesense.db` |
| `ANTHROPIC_API_KEY` | Optional — for AI explanation features |
| `SECRET_KEY` | Random string for security |

---

## ⚠️ Important Notes

- **Scraping** — price scraping from third-party platforms is subject to each platform's terms of service. This project is for educational purposes.
- **Anti-bot** — the scraper uses random user agents and request delays to be respectful of platform servers.
- **Data freshness** — prices are fetched every 8 hours. The UI shows a stale warning if a fetch fails 3+ times.
- **Prediction accuracy** — the model needs at least 7 data points for a reliable verdict. Earlier verdicts show "Low confidence".

---

## 🗺️ Roadmap

- [ ] Telegram / push notifications for price alerts
- [ ] Multi-platform price comparison (same product, different retailers)
- [ ] Browser extension for one-click tracking
- [ ] Deploy online (Railway / Render)
- [ ] Mobile app (Phase 3)
- [ ] Login system for multiple users
- [ ] Sale event calendar with upcoming events

---

## 📄 License

This project is for educational and personal use. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) — backend framework
- [Chart.js](https://www.chartjs.org/) — price history charts
- [Tailwind CSS](https://tailwindcss.com/) — styling
- [Google Stitch](https://stitch.withgoogle.com/) — UI design generation

---

*Built with ❤️ — PriceSense Intelligence*
