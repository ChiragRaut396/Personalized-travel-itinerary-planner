"""
Personalized Travel Itinerary Planner — Skill Wallet Capstone Project 4
Run locally: streamlit run app.py
"""
from __future__ import annotations

import json
import math
import os
import re
import tempfile
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import requests
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether
)

APP_NAME = "Personalized Travel Itinerary Planner"
DATA_DIR = Path(os.getenv("TRAVEL_PLANNER_DATA_DIR", ".travel_planner_data"))
TRIPS_FILE = DATA_DIR / "saved_trips.json"

# Coordinates, approximate activity prices, and demo attractions are illustrative.
# Confirm opening hours, prices, transport, and safety information before travel.
CITY_DATA: dict[str, dict[str, Any]] = {
    "Jaipur, India": {
        "country": "India", "currency": "INR", "usd_rate": 0.012, "lat": 26.9124, "lon": 75.7873,
        "tags": ["Culture", "Architecture", "Food"], "best_vibes": ["Cultural", "Urban"],
        "budget": "Budget", "season": "Oct–Mar", "weather_note": "Usually more comfortable in the cooler months.",
        "activities": [
            ("Amber Fort", "Morning Sightseeing", 550, 26.9855, 75.8513, "History"),
            ("City Palace", "Morning Sightseeing", 400, 26.9258, 75.8237, "History"),
            ("Jantar Mantar", "Afternoon Leisure", 200, 26.9248, 75.8246, "History"),
            ("Hawa Mahal area walk", "Afternoon Leisure", 0, 26.9239, 75.8267, "Culture"),
            ("Johari Bazaar food walk", "Lunch Recommendation", 450, 26.9205, 75.8267, "Food"),
            ("Local thali restaurant", "Lunch Recommendation", 350, 26.9188, 75.8172, "Food"),
            ("Chokhi Dhani-style cultural dinner", "Evening Dining & Entertainment", 1200, 26.7680, 75.8550, "Food"),
            ("Bapu Bazaar browsing", "Evening Dining & Entertainment", 0, 26.9170, 75.8190, "Shopping"),
            ("Nahargarh sunset viewpoint", "Evening Dining & Entertainment", 150, 26.9370, 75.8150, "Adventure"),
        ],
    },
    "Goa, India": {
        "country": "India", "currency": "INR", "usd_rate": 0.012, "lat": 15.2993, "lon": 74.1240,
        "tags": ["Beach", "Seafood", "Nightlife"], "best_vibes": ["Beach", "Urban"],
        "budget": "Moderate", "season": "Nov–Mar", "weather_note": "Dry-season beach weather is generally best around Nov–Mar.",
        "activities": [
            ("Baga Beach", "Morning Sightseeing", 0, 15.5553, 73.7517, "Adventure"),
            ("Fort Aguada", "Morning Sightseeing", 100, 15.4920, 73.7730, "History"),
            ("Anjuna Flea Market area", "Afternoon Leisure", 0, 15.5730, 73.7410, "Shopping"),
            ("Beach shack lunch", "Lunch Recommendation", 650, 15.5580, 73.7510, "Food"),
            ("Fontainhas Latin Quarter walk", "Afternoon Leisure", 0, 15.4980, 73.8310, "Culture"),
            ("Vegetarian Goan café", "Lunch Recommendation", 450, 15.4960, 73.8280, "Food"),
            ("Sunset beach café", "Evening Dining & Entertainment", 900, 15.5500, 73.7600, "Food"),
            ("Live-music venue", "Evening Dining & Entertainment", 700, 15.5650, 73.7580, "Nightlife"),
            ("Dona Paula viewpoint", "Morning Sightseeing", 0, 15.4589, 73.8036, "Adventure"),
        ],
    },
    "Udaipur, India": {
        "country": "India", "currency": "INR", "usd_rate": 0.012, "lat": 24.5854, "lon": 73.7125,
        "tags": ["Lakes", "Romance", "Heritage"], "best_vibes": ["Cultural", "Mountains"],
        "budget": "Moderate", "season": "Sep–Mar", "weather_note": "Pleasant sightseeing is more likely in the cooler months.",
        "activities": [
            ("City Palace", "Morning Sightseeing", 400, 24.5764, 73.6835, "History"),
            ("Jagdish Temple", "Morning Sightseeing", 0, 24.5785, 73.6830, "History"),
            ("Lake Pichola boat ride", "Afternoon Leisure", 500, 24.5750, 73.6790, "Adventure"),
            ("Old-city vegetarian thali", "Lunch Recommendation", 300, 24.5780, 73.6840, "Food"),
            ("Saheliyon-ki-Bari", "Afternoon Leisure", 100, 24.5930, 73.6850, "Culture"),
            ("Fateh Sagar lakeside café", "Lunch Recommendation", 450, 24.6020, 73.6780, "Food"),
            ("Rooftop dinner with lake view", "Evening Dining & Entertainment", 1000, 24.5780, 73.6820, "Food"),
            ("Bagore Ki Haveli cultural show", "Evening Dining & Entertainment", 250, 24.5790, 73.6830, "Culture"),
        ],
    },
    "Manali, India": {
        "country": "India", "currency": "INR", "usd_rate": 0.012, "lat": 32.2396, "lon": 77.1887,
        "tags": ["Mountains", "Adventure", "Cafés"], "best_vibes": ["Mountains", "Adventure"],
        "budget": "Moderate", "season": "Mar–Jun / Oct–Nov", "weather_note": "Check road and weather advisories, especially in winter and monsoon.",
        "activities": [
            ("Hadimba Devi Temple", "Morning Sightseeing", 30, 32.2480, 77.1850, "History"),
            ("Old Manali riverside walk", "Morning Sightseeing", 0, 32.2570, 77.1870, "Adventure"),
            ("Local café lunch", "Lunch Recommendation", 500, 32.2560, 77.1880, "Food"),
            ("Manu Temple and village lanes", "Afternoon Leisure", 0, 32.2600, 77.1900, "Culture"),
            ("Solang Valley day visit", "Afternoon Leisure", 800, 32.3160, 77.1550, "Adventure"),
            ("Himachali meal", "Lunch Recommendation", 350, 32.2430, 77.1900, "Food"),
            ("Mall Road dinner and stroll", "Evening Dining & Entertainment", 650, 32.2430, 77.1890, "Food"),
            ("Live music café", "Evening Dining & Entertainment", 500, 32.2560, 77.1880, "Nightlife"),
        ],
    },
    "Mumbai, India": {
        "country": "India", "currency": "INR", "usd_rate": 0.012, "lat": 19.0760, "lon": 72.8777,
        "tags": ["Urban", "Food", "Nightlife"], "best_vibes": ["Urban", "Cultural"],
        "budget": "Moderate", "season": "Nov–Feb", "weather_note": "Cooler months are generally more comfortable for walking.",
        "activities": [
            ("Gateway of India", "Morning Sightseeing", 0, 18.9220, 72.8347, "History"),
            ("Chhatrapati Shivaji Maharaj Vastu Sangrahalaya", "Morning Sightseeing", 500, 18.9269, 72.8325, "History"),
            ("Colaba café lunch", "Lunch Recommendation", 550, 18.9150, 72.8310, "Food"),
            ("Kala Ghoda art district", "Afternoon Leisure", 0, 18.9280, 72.8310, "Culture"),
            ("Marine Drive promenade", "Afternoon Leisure", 0, 18.9430, 72.8238, "Adventure"),
            ("Vegetarian thali restaurant", "Lunch Recommendation", 400, 18.9320, 72.8330, "Food"),
            ("Local dinner spot", "Evening Dining & Entertainment", 850, 18.9350, 72.8250, "Food"),
            ("Live-music venue", "Evening Dining & Entertainment", 900, 18.9400, 72.8270, "Nightlife"),
        ],
    },
    "Bengaluru, India": {
        "country": "India", "currency": "INR", "usd_rate": 0.012, "lat": 12.9716, "lon": 77.5946,
        "tags": ["Urban", "Gardens", "Cafés"], "best_vibes": ["Urban", "Cultural"],
        "budget": "Moderate", "season": "Oct–Feb", "weather_note": "Most months are workable; check local rain forecasts.",
        "activities": [
            ("Cubbon Park", "Morning Sightseeing", 0, 12.9763, 77.5929, "Adventure"),
            ("Bengaluru Palace", "Morning Sightseeing", 300, 12.9987, 77.5920, "History"),
            ("South Indian breakfast/lunch", "Lunch Recommendation", 250, 12.9750, 77.6050, "Food"),
            ("National Gallery of Modern Art", "Afternoon Leisure", 20, 12.9890, 77.5880, "Culture"),
            ("Commercial Street browse", "Afternoon Leisure", 0, 12.9830, 77.6080, "Shopping"),
            ("Vegetarian dosa café", "Lunch Recommendation", 200, 12.9750, 77.6040, "Food"),
            ("Indiranagar dinner", "Evening Dining & Entertainment", 800, 12.9780, 77.6400, "Food"),
            ("Craft cocktail-free live music venue", "Evening Dining & Entertainment", 600, 12.9700, 77.6400, "Nightlife"),
        ],
    },
}

SLOTS = [
    ("Morning Sightseeing", "08:30–11:30"),
    ("Lunch Recommendation", "12:00–13:00"),
    ("Afternoon Leisure", "14:00–17:00"),
    ("Evening Dining & Entertainment", "18:30–21:00"),
]
INTERESTS = ["Food", "Adventure", "History", "Nightlife"]
VIBES = ["Beach", "Mountains", "Cultural", "Urban"]
USD_PER_INR = 1 / 83.5  # illustrative fallback conversion; label as estimate

st.set_page_config(page_title=APP_NAME, page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root { --ink:#172a3a; --muted:#5d6b75; --sea:#0f766e; --sand:#f4eee4; --coral:#ef8354; }
.stApp { background: linear-gradient(135deg,#f8f6f0 0%,#edf5f2 55%,#fffaf2 100%); color:var(--ink); font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Playfair Display',serif !important; color:#173b3a; }
.hero { padding:2rem 2.2rem; border-radius:24px; color:white; background:linear-gradient(120deg,#143d3a,#187c75 60%,#e69b6a); box-shadow:0 14px 36px #183c3a1f; margin-bottom:1.2rem; }
.hero h1 { color:white !important; font-size:2.35rem; margin:0 0 .4rem 0; }
.hero p { margin:0; opacity:.92; font-size:1.05rem; }
.pill { display:inline-block; padding:.3rem .65rem; margin:.15rem; border-radius:999px; background:#dceee9; color:#17534d; font-size:.82rem; font-weight:700; }
div[data-testid="stMetric"] { background:#ffffffb8; padding:1rem; border:1px solid #dce7e2; border-radius:16px; }
div.stButton > button { border-radius:12px; font-weight:700; }
section[data-testid="stSidebar"] { background:#f1f3ec; }
.small-note { color:#5d6b75; font-size:.88rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance between latitude/longitude pairs."""
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    x = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(x))

def cluster_activities(activities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Greedy nearest-neighbour ordering to reduce backtracking; not live routing."""
    if len(activities) < 2:
        return activities[:]
    remaining = activities[:]
    ordered = [remaining.pop(0)]
    while remaining:
        last = ordered[-1]
        nearest_i = min(
            range(len(remaining)),
            key=lambda i: haversine_km(
                (last["lat"], last["lon"]), (remaining[i]["lat"], remaining[i]["lon"])
            ),
        )
        ordered.append(remaining.pop(nearest_i))
    return ordered

def safe_money(amount: float, currency: str) -> str:
    return f"{currency} {amount:,.0f}"

def load_trips() -> list[dict[str, Any]]:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if TRIPS_FILE.exists():
            value = json.loads(TRIPS_FILE.read_text(encoding="utf-8"))
            return value if isinstance(value, list) else []
    except (OSError, json.JSONDecodeError) as exc:
        st.warning(f"Saved trip history could not be loaded: {exc}")
    return []

def persist_trips(trips: list[dict[str, Any]]) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = TRIPS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(trips, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(TRIPS_FILE)
    except OSError as exc:
        st.error(f"Could not persist trips to local storage: {exc}")

def api_generate(prompt: str, provider: str, api_key: str, model: str) -> str:
    """Call Gemini or Groq using their HTTPS REST APIs; never persist API keys."""
    if provider == "Gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.7}}
        response = requests.post(url, json=body, timeout=45)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    url = "https://api.groq.com/openai/v1/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a careful travel planner. Return valid JSON only, with no markdown fences. Never invent real-time opening hours, availability, or current prices; label estimates clearly."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }
    response = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=body, timeout=45)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

def ai_json(prompt: str) -> dict[str, Any] | None:
    provider = st.session_state.get("provider", "Demo mode")
    key = st.session_state.get("api_key", "")
    if provider == "Demo mode" or not key.strip():
        return None
    model = st.session_state.get("model", "")
    try:
        raw = api_generate(prompt, provider, key.strip(), model)
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else None
    except (requests.RequestException, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        st.warning(f"AI service could not complete this request. Showing the local demo plan instead. Details: {exc}")
        return None

def get_city_activities(city: str, interests: list[str], vegetarian: bool = False) -> list[dict[str, Any]]:
    data = CITY_DATA[city]
    acts = []
    for name, slot, cost, lat, lon, category in data["activities"]:
        if interests and category not in interests and category not in ("Culture", "Shopping"):
            continue
        if vegetarian and slot == "Lunch Recommendation" and not any(x in name.lower() for x in ["vegetarian", "thali", "south indian", "dosa", "café", "cafe"]):
            continue
        acts.append({"name": name, "slot": slot, "cost": cost, "lat": lat, "lon": lon, "category": category})
    if len(acts) < 4:
        for name, slot, cost, lat, lon, category in data["activities"]:
            item = {"name": name, "slot": slot, "cost": cost, "lat": lat, "lon": lon, "category": category}
            if item not in acts:
                acts.append(item)
    return acts

def build_demo_itinerary(city: str, days: int, interests: list[str], pace: str, vegetarian: bool = False) -> list[dict[str, Any]]:
    data = CITY_DATA[city]
    activities = get_city_activities(city, interests, vegetarian)
    if pace == "Relaxed":
        per_day = 3
    elif pace == "Fast-Paced":
        per_day = 5
    else:
        per_day = 4
    plans = []
    cursor = 0
    for day_num in range(1, days + 1):
        # Rotate activity pools across days; fill four named slots in chronological order.
        daily_pool = activities[cursor:cursor + max(per_day, 4)]
        if len(daily_pool) < 4:
            daily_pool += activities[:4 - len(daily_pool)]
        cursor = (cursor + max(per_day, 4)) % max(len(activities), 1)
        daily_pool = cluster_activities(daily_pool)
        by_slot: dict[str, dict[str, Any]] = {}
        for slot_name, _time in SLOTS:
            candidates = [a for a in daily_pool if a["slot"] == slot_name]
            if not candidates:
                candidates = [a for a in activities if a["slot"] == slot_name]
            by_slot[slot_name] = candidates[0] if candidates else {
                "name": "Flexible free time / neighbourhood exploration", "slot": slot_name,
                "cost": 0, "lat": data["lat"], "lon": data["lon"], "category": "Leisure"
            }
        # Keep itinerary chronology, while the activity pool has been spatially clustered.
        items = []
        for slot_name, time_label in SLOTS:
            activity = by_slot[slot_name].copy()
            activity["time"] = time_label
            activity["estimated_cost"] = int(activity.get("cost", 0))
            items.append(activity)
        plans.append({"day": day_num, "title": f"Day {day_num} · {city.split(',')[0]}", "activities": items})
    return plans

def generate_itinerary(city: str, days: int, interests: list[str], pace: str, start_date: date, vegetarian: bool) -> list[dict[str, Any]]:
    prompt = f"""
Create a {days}-day itinerary for {city}. Travel start date: {start_date.isoformat()}. Interests: {interests}.
Pace: {pace}. Vegetarian meal preference: {vegetarian}. Use this four-slot structure per day, in chronological order:
Morning Sightseeing (08:30–11:30), Lunch Recommendation (12:00–13:00), Afternoon Leisure (14:00–17:00), Evening Dining & Entertainment (18:30–21:00).
Minimize travel by clustering nearby attractions and avoid backtracking. Use plausible estimates, not claims of live availability. Include 4 activities per day.
Return JSON: {{"days":[{{"day":1,"title":"...","activities":[{{"name":"...","slot":"Morning Sightseeing","time":"08:30–11:30","estimated_cost":500,"currency":"INR","why":"...","area":"...","category":"History"}}]}}]}}.
"""
    response = ai_json(prompt)
    if response and isinstance(response.get("days"), list) and response["days"]:
        valid = []
        for i, day in enumerate(response["days"][:days], 1):
            acts = day.get("activities", []) if isinstance(day, dict) else []
            normalized = []
            for j, act in enumerate(acts[:8]):
                if not isinstance(act, dict) or not act.get("name"):
                    continue
                slot = act.get("slot", SLOTS[min(j, 3)][0])
                if slot not in [x[0] for x in SLOTS]:
                    slot = SLOTS[min(j, 3)][0]
                try:
                    cost = max(0, int(float(act.get("estimated_cost", act.get("cost", 0)))))
                except (ValueError, TypeError):
                    cost = 0
                normalized.append({
                    "name": str(act["name"])[:160], "slot": slot,
                    "time": str(act.get("time", dict(SLOTS).get(slot, "Flexible"))),
                    "estimated_cost": cost, "category": str(act.get("category", "Leisure")),
                    "why": str(act.get("why", "Suggested based on your trip preferences.")),
                    "area": str(act.get("area", city)),
                    "lat": CITY_DATA[city]["lat"], "lon": CITY_DATA[city]["lon"],
                })
            if normalized:
                # Keep chronological order by the requested slot sequence.
                normalized.sort(key=lambda x: [s[0] for s in SLOTS].index(x["slot"]))
                valid.append({"day": i, "title": str(day.get("title", f"Day {i}"))[:100], "activities": normalized})
        if valid:
            while len(valid) < days:
                valid.extend(build_demo_itinerary(city, 1, interests, pace, vegetarian))
                valid[-1]["day"] = len(valid)
            return valid[:days]
    return build_demo_itinerary(city, days, interests, pace, vegetarian)

def recommend_cities(vibe: str, budget: str, travel_date: date, party: str, interests: list[str]) -> list[tuple[str, int, list[str]]]:
    month = travel_date.month
    results = []
    for city, d in CITY_DATA.items():
        score = 0
        tags = []
        if vibe in d["best_vibes"]:
            score += 4
            tags.append(f"{vibe} match")
        elif vibe == "Open to anything":
            score += 2
            tags.append("Flexible vibe")
        if budget == d["budget"]:
            score += 2
            tags.append(f"{budget} fit")
        elif budget == "Budget" and d["budget"] == "Moderate":
            score += 1
        season_text = d["season"].lower()
        if (month in [10, 11, 12, 1, 2, 3] and any(x in season_text for x in ["oct", "nov", "sep"])) or (month in [4, 5, 6] and ("mar" in season_text or "jun" in season_text)):
            score += 2
            tags.append("Seasonal pick")
        cats = set(interests)
        city_tags = set(d["tags"])
        if cats & city_tags:
            score += 2
            tags.append("Interest match")
        if party == "Couple" and any(x in d["tags"] for x in ["Romance", "Lakes"]):
            score += 1
            tags.append("Couple-friendly")
        if party == "Family":
            score += 1
            tags.append("Family options")
        results.append((city, score, tags or ["Worth exploring"]))
    return sorted(results, key=lambda x: x[1], reverse=True)[:3]

def calculate_totals(itinerary: list[dict[str, Any]]) -> tuple[int, list[dict[str, Any]]]:
    running = 0
    rows = []
    for day in itinerary:
        for act in day.get("activities", []):
            cost = int(act.get("estimated_cost", act.get("cost", 0)) or 0)
            running += max(0, cost)
            rows.append({"day": day.get("day", 1), "slot": act.get("slot", ""), "name": act.get("name", ""),
                         "cost": cost, "running": running})
    return running, rows

def build_pdf(trip: dict[str, Any]) -> bytes:
    output = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    output.close()
    try:
        doc = SimpleDocTemplate(output.name, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=17*mm, bottomMargin=17*mm)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=28, textColor=colors.HexColor("#155e59"), alignment=TA_CENTER, spaceAfter=8))
        styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#53656b"), alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="DayTitle", parent=styles["Heading2"], textColor=colors.HexColor("#155e59"), spaceBefore=12, spaceAfter=6))
        styles.add(ParagraphStyle(name="Activity", parent=styles["Normal"], fontSize=9, leading=12))
        story = [
            Spacer(1, 16*mm),
            Paragraph("Your Journey, Thoughtfully Planned", styles["CoverTitle"]),
            Paragraph(trip.get("name", "Personalized Travel Itinerary"), styles["Heading1"]),
            Paragraph(f"{trip.get('destination','Destination')} · {trip.get('start_date','')} · {trip.get('days',0)} days", styles["Sub"]),
            Spacer(1, 8*mm),
            Paragraph(f"<b>Travel style:</b> {trip.get('budget','Moderate')} budget · {trip.get('party','Solo')} · {trip.get('pace','Moderate')} pace", styles["Normal"]),
            Paragraph(f"<b>Estimated listed activity spend:</b> {trip.get('currency','INR')} {trip.get('total_cost',0):,} (excludes transport, accommodation and incidental expenses unless listed)", styles["Normal"]),
            Spacer(1, 5*mm),
        ]
        for day in trip.get("itinerary", []):
            story.append(Paragraph(f"Day {day.get('day', '')}: {day.get('title', '')}", styles["DayTitle"]))
            data = [["Time", "Plan", "Estimated cost"]]
            for act in day.get("activities", []):
                name = str(act.get("name", "")).replace("&", "&amp;")
                slot = str(act.get("slot", "")).replace("&", "&amp;")
                time_label = str(act.get("time", "Flexible"))
                cost = int(act.get("estimated_cost", act.get("cost", 0)) or 0)
                data.append([Paragraph(f"{time_label}<br/><font color='#667777'>{slot}</font>", styles["Activity"]),
                             Paragraph(f"<b>{name}</b><br/>{str(act.get('why','')).replace('&','&amp;')[:180]}", styles["Activity"]),
                             f"{trip.get('currency','INR')} {cost:,}"])
            table = Table(data, colWidths=[37*mm, 98*mm, 35*mm], repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#155e59")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#d8e4df")),
                ("BACKGROUND", (0,1), (-1,-1), colors.white),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
                ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            story.extend([table, Spacer(1, 3*mm)])
        story.extend([
            PageBreak(),
            Paragraph("Before You Go", styles["DayTitle"]),
            Paragraph("Emergency & essentials checklist", styles["Heading3"]),
        ])
        checklist = [
            "[ ] Save local emergency number and accommodation address offline.",
            "[ ] Share your itinerary and check-in plan with a trusted contact.",
            "[ ] Carry ID, travel insurance details, required prescriptions and copies of documents.",
            "[ ] Confirm attraction opening hours, tickets, weather, transport and local advisories.",
            "[ ] Keep a charged phone, power bank, water and a small first-aid kit.",
            "[ ] Note the nearest hospital, local police contact and your country's consular contact if abroad.",
            "[ ] Keep payment backup and emergency cash separate from your wallet.",
        ]
        for item in checklist:
            story.append(Paragraph(item, styles["Normal"]))
            story.append(Spacer(1, 2*mm))
        story.extend([Spacer(1, 6*mm), Paragraph("Planning note", styles["Heading3"]),
                      Paragraph("Prices, routes and suggestions are estimates for planning purposes, not live quotes. Check current conditions and official sources before booking. The itinerary is not a substitute for local safety advice.", styles["Normal"])])
        doc.build(story)
        return Path(output.name).read_bytes()
    finally:
        try:
            os.unlink(output.name)
        except OSError:
            pass

def init_state() -> None:
    defaults = {
        "provider": "Demo mode", "api_key": "", "model": "llama-3.3-70b-versatile",
        "itinerary": None, "current_trip": None, "saved_trips": load_trips(),
        "selected_city": "Jaipur, India", "swap_day": 1, "swap_slot": SLOTS[1][0],
        "trip_name": "My Travel Plan", "last_recommendations": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()
st.markdown(f"""
<div class="hero">
  <h1>🧭 {APP_NAME}</h1>
  <p>Less planning stress. More meaningful moments. Build a trip that feels like you.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ AI & Trip Setup")
    provider = st.selectbox("AI provider", ["Demo mode", "Gemini", "Groq"], key="provider")
    if provider != "Demo mode":
        key_label = "Gemini API key" if provider == "Gemini" else "Groq API key"
        st.text_input(key_label, type="password", key="api_key", help="Used only for requests in this session; never saved in trip history.")
        if provider == "Gemini":
            st.selectbox("Gemini model", ["gemini-2.5-flash", "gemini-2.0-flash"], key="model")
            st.caption("Get a key from Google AI Studio.")
        else:
            st.selectbox("Groq model", ["llama-3.3-70b-versatile", "openai/gpt-oss-20b"], key="model")
            st.caption("Get a key from Groq Console.")
    else:
        st.info("Demo mode is ready to use without an API key.")
    st.divider()
    st.markdown("### 🌍 Your travel preferences")
    destination_mode = st.radio("Do you have a destination?", ["I have a destination", "Recommend somewhere"], horizontal=False)
    city_options = list(CITY_DATA.keys())
    if destination_mode == "I have a destination":
        destination = st.selectbox("Destination", city_options, key="destination_select")
        vibe = st.selectbox("Trip vibe", ["Beach", "Mountains", "Cultural", "Urban", "Open to anything"], index=2)
    else:
        destination = None
        vibe = st.selectbox("What sounds good?", ["Open to anything", "Beach", "Mountains", "Cultural", "Urban"])
    days = st.slider("Trip duration (days)", min_value=1, max_value=14, value=4)
    travel_date = st.date_input("Start date", value=date.today() + timedelta(days=30), min_value=date.today())
    budget = st.selectbox("Budget level", ["Budget", "Moderate", "Luxury"], index=1)
    party = st.selectbox("Travel party", ["Solo", "Couple", "Family", "Friends"])
    pace = st.selectbox("Pace", ["Relaxed", "Moderate", "Fast-Paced"], index=1)
    interests = st.multiselect("Interests", INTERESTS, default=["Food", "History"])
    vegetarian = st.checkbox("Prefer vegetarian food", value=False)
    trip_name = st.text_input("Trip name", value="My Travel Plan", key="trip_name")
    generate_btn = st.button("✨ Create / Refresh itinerary", type="primary", use_container_width=True)
    st.caption("Demo city data is illustrative. Confirm current prices, opening hours and travel advisories.")

tabs = st.tabs(["✨ Destination Recommender", "🗺️ Day-by-Day Itinerary", "🎨 Customize & Swap", "📚 Trip Management & PDF"])

with tabs[0]:
    st.subheader("Find a destination that matches your mood")
    st.write("Recommendations combine your selected vibe, budget fit, season heuristics, travel party and interests. Weather notes are seasonal guidance, not a live forecast.")
    recs = recommend_cities(vibe, budget, travel_date, party, interests)
    cols = st.columns(3)
    for idx, (city, score, tags) in enumerate(recs):
        d = CITY_DATA[city]
        with cols[idx]:
            st.markdown(f"#### {city.split(',')[0]}")
            st.markdown(" ".join(f'<span class="pill">{tag}</span>' for tag in tags[:3]), unsafe_allow_html=True)
            st.write(f"**Best season:** {d['season']}")
            st.write(f"**Why it fits:** {d['weather_note']}")
            st.write(f"**Mood:** {', '.join(d['tags'])}")
            if st.button(f"Plan this trip", key=f"rec_{idx}", use_container_width=True):
                st.session_state.selected_city = city
                st.session_state["destination_select"] = city
                st.session_state["itinerary"] = None
                st.success(f"{city} selected. Click **Create / Refresh itinerary** in the sidebar.")
    st.caption("Recommendations are based on built-in demo metadata and do not represent live weather or verified current costs.")

with tabs[1]:
    st.subheader("Your itinerary, one day at a time")
    if generate_btn:
        chosen_city = destination or st.session_state.get("selected_city", city_options[0])
        with st.spinner("Building your trip plan…"):
            plan = generate_itinerary(chosen_city, days, interests, pace, travel_date, vegetarian)
            st.session_state.itinerary = plan
            st.session_state.selected_city = chosen_city
            total, _ = calculate_totals(plan)
            st.session_state.current_trip = {
                "id": f"trip-{date.today().isoformat()}-{len(st.session_state.saved_trips)+1}",
                "name": trip_name.strip() or "My Travel Plan", "destination": chosen_city,
                "start_date": travel_date.isoformat(), "days": days, "budget": budget,
                "party": party, "pace": pace, "interests": interests, "vibe": vibe,
                "currency": CITY_DATA[chosen_city]["currency"], "itinerary": plan, "total_cost": total,
                "created_at": date.today().isoformat(),
            }
        st.success("Itinerary generated. Review estimates and customize any slot in the next tab.")
    itinerary = st.session_state.get("itinerary")
    trip = st.session_state.get("current_trip")
    if itinerary and trip:
        total, rows = calculate_totals(itinerary)
        rate = CITY_DATA.get(trip["destination"], {}).get("usd_rate", USD_PER_INR)
        c1, c2, c3 = st.columns(3)
        c1.metric("Days planned", trip["days"])
        c2.metric("Listed activity spend", safe_money(total, trip["currency"]))
        c3.metric("Approx. USD", f"${total * rate:,.2f}")
        st.caption("Costs are indicative activity/meal estimates. Flights, accommodation, transfers, shopping and incidentals may not be included.")
        for day in itinerary:
            with st.expander(f"Day {day['day']} · {day.get('title', '')}", expanded=day["day"] == 1):
                for act in sorted(day.get("activities", []), key=lambda x: [s[0] for s in SLOTS].index(x.get("slot", SLOTS[0][0])) if x.get("slot") in [s[0] for s in SLOTS] else 0):
                    a, b = st.columns([4, 1])
                    with a:
                        st.markdown(f"**{act.get('time','')} · {act.get('slot','')}**")
                        st.write(act.get("name", "Flexible activity"))
                        if act.get("why"):
                            st.caption(act["why"])
                    with b:
                        st.markdown(f"**{trip['currency']} {int(act.get('estimated_cost',act.get('cost',0))):,}**")
                    st.divider()
        st.markdown("#### Running cumulative activity budget")
        budget_rows = []
        running = 0
        for row in rows:
            running += row["cost"]
            budget_rows.append({"Day": row["day"], "Activity": row["name"], "Cost": f"{trip['currency']} {row['cost']:,}", "Cumulative": f"{trip['currency']} {running:,}"})
        st.dataframe(budget_rows, use_container_width=True, hide_index=True)
        st.info("Geographic clustering uses approximate straight-line distances from bundled demo coordinates; it is not a live road-route optimizer.")
    else:
        st.info("Choose your preferences in the sidebar and click **Create / Refresh itinerary** to generate a plan.")

with tabs[2]:
    st.subheader("Tune the vibe without rebuilding the whole trip")
    itinerary = st.session_state.get("itinerary")
    trip = st.session_state.get("current_trip")
    if not itinerary or not trip:
        st.info("Create an itinerary first. Then you can swap a single slot or regenerate one day.")
    else:
        day_options = [int(x["day"]) for x in itinerary]
        selected_day = st.selectbox("Select day", day_options, key="swap_day")
        slot_names = [s[0] for s in SLOTS]
        selected_slot = st.selectbox("Select slot to change", slot_names, key="swap_slot")
        current_day = next(d for d in itinerary if int(d["day"]) == int(selected_day))
        current_act = next((a for a in current_day["activities"] if a.get("slot") == selected_slot), None)
        st.write("**Current activity:**", current_act.get("name", "Not set") if current_act else "Not set")
        swap_request = st.text_input("What would you prefer instead?", placeholder="e.g. outdoor market, vegetarian lunch, quiet garden")
        if st.button("🔁 Swap selected activity", type="primary"):
            city = trip["destination"]
            candidates = CITY_DATA.get(city, {}).get("activities", [])
            request_lower = swap_request.lower()
            keywords = []
            for word in ["market", "vegetarian", "museum", "outdoor", "garden", "beach", "adventure", "history", "food", "cafe", "café", "quiet"]:
                if word in request_lower:
                    keywords.append(word)
            candidate_items = []
            for name, slot, cost, lat, lon, category in candidates:
                if slot != selected_slot:
                    continue
                haystack = f"{name} {category}".lower()
                if not keywords or any(k in haystack for k in keywords) or (("vegetarian" in keywords) and category == "Food"):
                    candidate_items.append({"name": name, "slot": slot, "cost": cost, "estimated_cost": cost, "lat": lat, "lon": lon, "category": category, "time": dict(SLOTS)[slot], "why": "Selected as a local demo alternative matching your requested vibe."})
            if not candidate_items and selected_slot == "Lunch Recommendation" and "vegetarian" in request_lower:
                candidate_items = [{"name": "Vegetarian local thali / café (verify venue)", "slot": selected_slot, "cost": 350, "estimated_cost": 350, "lat": CITY_DATA[city]["lat"], "lon": CITY_DATA[city]["lon"], "category": "Food", "time": dict(SLOTS)[selected_slot], "why": "Vegetarian-friendly placeholder; verify menu and opening hours."}]
            if candidate_items:
                replacement = next((x for x in candidate_items if not current_act or x["name"] != current_act.get("name")), candidate_items[0])
                if current_act:
                    idx = current_day["activities"].index(current_act)
                    current_day["activities"][idx] = replacement
                else:
                    current_day["activities"].append(replacement)
                trip["itinerary"] = itinerary
                trip["total_cost"], _ = calculate_totals(itinerary)
                st.session_state.current_trip = trip
                st.session_state.itinerary = itinerary
                st.success(f"Updated Day {selected_day} only. Other days are unchanged.")
                st.rerun()
            else:
                st.warning("No local demo match for that exact request. Try a broader preference such as food, history, garden, market or outdoor.")
        st.divider()
        st.markdown("#### Regenerate a single day")
        day_prompt = st.text_input("Direction for this day", placeholder="e.g. slower pace, more history, more outdoor time")
        if st.button("✨ Refresh this day only"):
            city = trip["destination"]
            prompt = f"""Return valid JSON only with an activities array of four activities for day {selected_day} in {city}. Focus: {day_prompt or 'match existing interests'}. Preferences: {trip.get('interests', [])}, pace {trip.get('pace')}. Slots: Morning Sightseeing, Lunch Recommendation, Afternoon Leisure, Evening Dining & Entertainment. Include time, name, estimated_cost, category, area. Estimates only, no live claims."""
            ai_result = ai_json(prompt)
            if ai_result and isinstance(ai_result.get("activities"), list):
                fresh = []
                for i, act in enumerate(ai_result["activities"][:8]):
                    if isinstance(act, dict) and act.get("name"):
                        slot = act.get("slot", SLOTS[min(i, 3)][0])
                        if slot not in slot_names:
                            slot = SLOTS[min(i, 3)][0]
                        fresh.append({"name": str(act["name"]), "slot": slot, "time": str(act.get("time", dict(SLOTS)[slot])), "estimated_cost": max(0, int(float(act.get("estimated_cost", 0) or 0))), "category": str(act.get("category", "Leisure")), "why": str(act.get("why", "")), "lat": CITY_DATA[city]["lat"], "lon": CITY_DATA[city]["lon"]})
                if fresh:
                    fresh.sort(key=lambda x: slot_names.index(x["slot"]))
                    current_day["activities"] = fresh
                else:
                    st.warning("AI response had no valid activities. The day was left unchanged.")
            else:
                # Demo refresh: change only the selected day's activity ordering/picks.
                old_names = {a.get("name") for a in current_day["activities"]}
                pool = get_city_activities(city, trip.get("interests", []), vegetarian)
                pool = [a for a in pool if a["name"] not in old_names] or pool
                pool = cluster_activities(pool)
                fresh = []
                for i, (slot, time_label) in enumerate(SLOTS):
                    candidates = [a for a in pool if a["slot"] == slot]
                    if not candidates:
                        candidates = [a for a in get_city_activities(city, [], vegetarian) if a["slot"] == slot]
                    a = (candidates[0] if candidates else {"name": "Flexible free time", "cost": 0, "category": "Leisure", "lat": CITY_DATA[city]["lat"], "lon": CITY_DATA[city]["lon"]}).copy()
                    a.update({"slot": slot, "time": time_label, "estimated_cost": int(a.get("cost", 0)), "why": f"Refreshed for: {day_prompt or 'your original preferences'}"})
                    fresh.append(a)
                current_day["activities"] = fresh
            trip["itinerary"] = itinerary
            trip["total_cost"], _ = calculate_totals(itinerary)
            st.session_state.current_trip = trip
            st.session_state.itinerary = itinerary
            st.success(f"Day {selected_day} refreshed; the rest of your trip is preserved.")
            st.rerun()

with tabs[3]:
    st.subheader("Save, revisit and take your plan offline")
    trip = st.session_state.get("current_trip")
    if trip:
        st.markdown(f"**Current plan:** {trip['name']} · {trip['destination']} · {trip['days']} days")
        left, right = st.columns(2)
        with left:
            if st.button("💾 Save trip to history", type="primary", use_container_width=True):
                trips = st.session_state.saved_trips[:]
                existing = next((i for i, x in enumerate(trips) if x.get("id") == trip.get("id")), None)
                snapshot = json.loads(json.dumps(trip))
                if existing is None:
                    trips.insert(0, snapshot)
                else:
                    trips[existing] = snapshot
                st.session_state.saved_trips = trips
                persist_trips(trips)
                st.success("Trip saved to local JSON history.")
        with right:
            try:
                pdf_bytes = build_pdf(trip)
                filename = re.sub(r"[^A-Za-z0-9_-]+", "-", trip["name"]).strip("-") or "travel-itinerary"
                st.download_button("📄 Download offline PDF guide", data=pdf_bytes, file_name=f"{filename}.pdf", mime="application/pdf", use_container_width=True)
            except Exception as exc:
                st.error(f"PDF generation failed: {exc}")
    else:
        st.info("Generate an itinerary before saving or exporting it.")
    st.divider()
    st.markdown("#### Saved trip history")
    trips = st.session_state.saved_trips
    if not trips:
        st.caption("No saved trips yet. Saving stores a local JSON snapshot; Streamlit Community Cloud's filesystem may reset or be ephemeral.")
    else:
        for idx, saved in enumerate(trips):
            with st.expander(f"{saved.get('name','Untitled')} · {saved.get('destination','')} · {saved.get('start_date','')}"):
                st.write(f"{saved.get('days',0)} days · {saved.get('budget','')} · {saved.get('party','')}")
                st.write(f"Listed activity spend: {saved.get('currency','INR')} {saved.get('total_cost',0):,}")
                c1, c2 = st.columns(2)
                if c1.button("Load this trip", key=f"load_{idx}"):
                    st.session_state.current_trip = saved
                    st.session_state.itinerary = saved.get("itinerary", [])
                    st.session_state.selected_city = saved.get("destination", city_options[0])
                    st.success("Trip loaded.")
                    st.rerun()
                try:
                    pdf = build_pdf(saved)
                    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", saved.get("name","trip")).strip("-") or "trip"
                    c2.download_button("Download saved PDF", data=pdf, file_name=f"{safe_name}.pdf", mime="application/pdf", key=f"pdf_{idx}")
                except Exception as exc:
                    st.caption(f"PDF unavailable: {exc}")
        if st.button("🗑️ Clear saved history"):
            st.session_state.saved_trips = []
            persist_trips([])
            st.success("Local saved history cleared.")
            st.rerun()

st.divider()
st.markdown('<p class="small-note">Built as a capstone-ready demo. API keys are not written to disk. For real production persistence, add an external database; local JSON storage is intentionally used here to keep deployment dependency-light.</p>', unsafe_allow_html=True)
