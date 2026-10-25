# Personalized Travel Itinerary Planner
**Skill Wallet Capstone Project 4** — Streamlit + Python

## Features
- Secure-in-session API key entry for Google Gemini or Groq, plus no-key demo mode.
- Destination recommendations based on trip vibe, budget, season heuristics, party and interests.
- Day-wise itinerary with chronological time slots, estimated itemized costs, running cumulative spend and INR/USD estimate.
- Approximate geographic clustering using a nearest-neighbour heuristic and bundled coordinates.
- Activity swap and single-day refresh without replacing the rest of the itinerary.
- JSON-based local trip history and one-click PDF export with an emergency checklist.
- Modern travel-inspired styling, defensive input parsing and exception handling.

## Run locally
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and this README to a GitHub repository.
2. In Streamlit Community Cloud, choose the repository and `app.py` as the entry point.
3. Deploy. Demo mode works without secrets.
4. For AI use, choose Gemini or Groq in the sidebar and enter your key in the password field. Do not commit API keys.

## AI provider notes
- Gemini uses the `generateContent` REST endpoint.
- Groq uses the OpenAI-compatible chat completions endpoint.
- API keys stay in Streamlit session state and are not included in saved trip snapshots. Requests can still fail because of quota, provider outages, model availability or network conditions; the app falls back to demo itinerary generation.

## Important production limitations
This is a self-contained capstone application, not a verified live booking or navigation product:
- Demo attractions, coordinates, season windows, prices and exchange-rate estimates are illustrative and must be checked before travel.
- Geographic grouping uses straight-line distances and a nearest-neighbour heuristic, not live road travel times, transit schedules or a global optimizer.
- The built-in city catalog contains Jaipur, Goa, Udaipur, Manali, Mumbai and Bengaluru; unknown destinations are not supported in demo mode.
- JSON persistence is local filesystem storage. Streamlit Community Cloud may reset or not guarantee persistence across restarts/redeploys. Multiple workers do not share this file safely. Use a managed database/object store for durable multi-user production.
- There is no authentication, account isolation, booking, live weather, live exchange-rate feed, live POI search or emergency-service lookup. Do not treat the app as a substitute for official travel or safety information.
- USD conversion is an approximate fallback for demo display; it is not a live financial quote.

## Project layout
```text
personalized_travel_itinerary_planner/
├── app.py
├── requirements.txt
└── README.md
```
