# Build prompts for a three-hour sprint, in order. Paste one into your coding agent, wait for green tests, commit, next.

The clock times assume a 10:00 start. Shift them to whenever you begin.

Rule for the sprint: if analytics are not on screen by 10:55, skip prompts 4 and 5 and polish what works.

## 0. 10:00. Orient (2 min)
```
Read README.md, .cursor/rules/project.mdc, src/ingestion.py and tests/test_analytics_spec.py. Do not change anything. Tell me in five lines what exists and what the spec asks for.
```

## 1. 10:05. Analytics (to 10:30)
```
Implement src/analytics.py so the four analytics tests in tests/test_analytics_spec.py pass. Do not edit the tests or src/ingestion.py. Pure pandas, no Streamlit. Run pytest -q and fix until those four are green.
```

## 2. 10:30. Imbalance (to 10:55)
```
Implement src/imbalance.py so the remaining tests in tests/test_analytics_spec.py pass. kind is "se vacía" when imbalance_ratio is below -0.10, "se llena" above 0.10, otherwise "equilibrada". recommendations() must quote the real departures and arrivals in its evidence text and must never mention current inventory. Run pytest -q until all 13 pass.
```

## 3. 10:55. Dashboard (to 11:25)
```
Fill the Panorama and Desequilibrio tabs in app.py using only functions from src. Panorama: four st.metric KPIs, a Plotly bar of hourly demand, a table of top stations. Desequilibrio: a Plotly horizontal bar of net flow for the 15 most imbalanced stations colored by kind, a station selector that shows imbalance_by_hour for that station, and the recommendations as cards with their evidence. Spanish labels. No calculations in app.py. Keep the historical-flow caption.
```

## 4. 11:25. Copilot (to 12:00)
```
Implement src/copilot.py answer(). Loop: call llm.chat(messages, TOOLS). If it returns tool_calls, run the matching function from src.analytics or src.imbalance, append the result as a tool message with the JSON, and call again, at most 3 rounds. If llm.chat returns None or raises, return the deterministic text built from imbalance.recommendations(). Return text, the list of tool results used as evidence, and the backend name. Then build the Copiloto tab: a text input, three sample question buttons, the answer, an expander "Evidencia" showing the tool results, and a small caption with the backend that answered. Add one test that answer() works with LLM_ORDER set to an empty string.
```

## 5. 12:00. Map, only if everything above is green (to 12:20)
```
Add a Plotly scatter map to the Desequilibrio tab: stations at lat and lon, size by total trips, color by kind. Skip stations without coordinates and say how many were skipped.
```

## 6. 12:30. Freeze
```
Run pytest -q and python scripts/preflight.py. Fix only failures. Update README.md with a "What it found" section containing three real findings copied from the app with the period they cover, and a "How it was built" section listing what was scaffolded before the event and what was built during it. Commit.
```
