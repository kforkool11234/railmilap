# 🚂 RailMilap

**RailMilap** is an intelligent Indian Railways connection finder. Given a source and destination station, it searches for the best **two-train interchanges** — sorting results by total journey duration so you always see the fastest option first.

> Built with Django + PostgreSQL on the backend and React + TailwindCSS on the frontend. Features a light/dark mode, live scraping of train running days, and a clean paginated results UI.

---

## ✨ Features

- 🔍 **Smart Route Search** — finds all possible single-interchange connections between two stations
- ⏱️ **Accurate Time Math** — total journey time = Train 1 travel + wait at interchange + Train 2 travel, with full 7-day weekly wrap-around handling
- 📅 **Day-aware Filtering** — only shows connections where trains actually run on your selected day of travel
- ⏳ **Adjustable Min Wait Time** — slider to control the minimum wait at the interchange (1–20 hrs, default 4 hrs)
- 📋 **Paginated Results** — 15 results per page, sorted by shortest total journey time
- 🌙 **Light / Dark Mode** — theme persists across sessions via `localStorage`
- ⚡ **On-demand Scraping** — running day data is scraped from `etrain.info` once and cached in PostgreSQL forever

---

## 🗂️ Project Structure

```
railmilap/
├── backend/                    # Django REST API
│   ├── railmilap_api/          # Django project settings & URLs
│   └── railways/
│       ├── models.py           # Station, Train, TrainSchedule, TrainRunningDay
│       ├── views.py            # find_routes — main search logic
│       ├── scraper.py          # etrain.info scraper + DB caching
│       └── management/
│           └── commands/
│               └── load_new_schedule.py   # Bulk CSV data loader
│
├── front/                      # React frontend
│   └── src/
│       └── component/
│           ├── App.jsx         # Router setup
│           ├── header.jsx      # Navbar + theme toggle
│           ├── home.jsx        # Hero page layout
│           ├── search.jsx      # Search form card
│           ├── routes.jsx      # Paginated results table
│           └── footer.jsx      # Footer
│
└── Trains schedule.csv         # Source data (~417k rows)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5, Django REST Framework |
| Database | PostgreSQL (SQLite for dev) |
| Scraping | `requests` + `BeautifulSoup4` |
| Concurrency | `concurrent.futures.ThreadPoolExecutor` |
| Frontend | React 18, React Router v6 |
| Styling | TailwindCSS v3 (dark mode via `class` strategy) |
| Fonts | Inter, Outfit (Google Fonts) |
| HTTP Client | Axios |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or use the default SQLite for local dev)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/railmilap.git
cd railmilap
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Configure your database in `railmilap_api/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railmilap',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Run migrations and load the schedule data:

```bash
python manage.py migrate
python manage.py load_new_schedule
```

Start the development server:

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`.

### 3. Frontend Setup

```bash
cd ../front
npm install
npm start
```

The app will be available at `http://localhost:3000`.

---

## 🔌 API Reference

### `POST /routes`

Find connecting train routes between two stations.

**Request Body**

```json
{
  "fromStation": "NDLS",
  "toStation": "HWH",
  "day": "Mon",
  "minWaitTime": 4
}
```

| Field | Type | Description |
|-------|------|-------------|
| `fromStation` | `string` | Station code of origin |
| `toStation` | `string` | Station code of destination |
| `day` | `string` | Day of travel (Mon, Tue, Wed, Thu, Fri, Sat, Sun) |
| `minWaitTime` | `integer` | Minimum interchange wait in hours (default: 4) |

**Response**

```json
[
  {
    "station": "MUGHAL SARAI JN (MGS)",
    "train1": "Poorvanchal Express",
    "train2": "Howrah Rajdhani",
    "interval": "5:30 hrs",
    "total": "14:20 hrs",
    "wait_seconds": 19800,
    "total_seconds": 51600
  }
]
```

Results are **sorted by `total_seconds`** (shortest journey first).

---

## 🗃️ Database Models

```
Station          → station_code (PK), station_name
Train            → train_no (PK), train_name, source_station, destination_station
TrainSchedule    → train, station, stop_sequence, arrival_time, departure_time, day_count
TrainRunningDay  → train, day_of_week  ← populated by scraper
```

---

## 🕷️ Scraping & Caching

Train running days (Mon/Tue/...) are **not in the CSV** and must be fetched from the web.

- On every search, trains with **no cached running days** are scraped from `etrain.info` using a `ThreadPoolExecutor` (up to 10 concurrent threads).
- Once scraped, data is stored in `TrainRunningDay` and never scraped again for that train.
- If scraping fails (network error, site down), the train defaults to running **daily** so the app doesn't break.

---

## 📜 License

MIT License — feel free to use and adapt.
