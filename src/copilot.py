"""The operations copilot: an LLM that can only answer by calling the analytics functions.

TO BUILD (step 4 in PROMPTS.md). Rules:
- Every number in an answer comes from a tool result. The model never computes or estimates.
- If src.llm.chat returns None, answer with imbalance.recommendations() as plain text. The demo must not depend on a model.
- Answers in Spanish, with the evidence shown under the answer.
"""
from __future__ import annotations

SYSTEM = (
    "Eres un analista de operaciones de MiBici en Guadalajara. Respondes en español, breve y concreto. "
    "Solo usas cifras devueltas por las herramientas. Si no tienes el dato, llamas a una herramienta o dices que no lo tienes. "
    "Los flujos son históricos: nunca afirmes cuántas bicicletas hay ahora en una estación."
)

TOOLS = [
    {"type": "function", "function": {"name": "get_kpis", "description": "Indicadores generales del periodo cargado", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_imbalance", "description": "Estaciones con mayor desequilibrio entre salidas y llegadas", "parameters": {"type": "object", "properties": {"n": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "get_station", "description": "Estadísticas de una estación por su id", "parameters": {"type": "object", "properties": {"station_id": {"type": "integer"}}, "required": ["station_id"]}}},
    {"type": "function", "function": {"name": "get_peak_hours", "description": "Demanda por hora, de toda la red o de una estación", "parameters": {"type": "object", "properties": {"station_id": {"type": "integer"}}}}},
]


def answer(question: str, trips, stations) -> dict:
    """Return {"text": str, "evidence": list[dict], "backend": str}."""
    raise NotImplementedError
