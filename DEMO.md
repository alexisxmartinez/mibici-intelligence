# Demo, 3 minutes, in Spanish

Open with the app already running on real October 2026 data, Panorama tab.

**0:00 El problema.** "MiBici publica cada viaje que se hace en Guadalajara. Son cientos de miles al mes. Pero un archivo de viajes no le dice a nadie qué estación se queda sin bicicletas a las 8 de la mañana."

**0:30 Los datos.** Panorama: total de viajes, hora pico, estaciones más activas. Say the real period out loud. Point at the cleaning report: "No escondo lo que descarté, aquí está cuántos viajes y por qué."

**1:10 El hallazgo.** Desequilibrio: pick the most extreme station. "Esta estación tuvo X salidas y Y llegadas. Se vacía." Show its hours.

**1:40 El copiloto.** Ask: "¿Cuáles son las tres estaciones con mayor desequilibrio y qué revisarías primero?" Open Evidencia. "El modelo no calcula nada. Llama funciones de Python y cita lo que devuelven. Si le quito el modelo, la respuesta sigue saliendo."

**2:20 El detalle que nadie más trae.** Point at the backend caption. "Este copiloto corre en una laptop de 4 GB en mi casa, sin pagar una API. Si se cae, pasa a Gemini. Si se cae Gemini, responde sin modelo."

**2:40 Cierre.** "Son flujos históricos, no inventario en tiempo real, y lo dice la pantalla. Es código abierto, con pruebas, y está en mi GitHub. MiBici Intelligence: de los datos a decisiones de movilidad."

## If something breaks on stage
| Breaks | Do |
|---|---|
| Koatl unreachable | Nothing. The app falls to Gemini by itself. Say so, it is a feature |
| No internet at all | Nothing. Deterministic answers still appear |
| Real data file missing | Sidebar upload, or the sample, and say out loud it is synthetic |
| App will not start | Show the passing tests and the README findings |

## Three questions to have ready
1. ¿Cuáles son las tres estaciones con mayor desequilibrio y qué revisarías primero?
2. ¿A qué hora se vacía la estación más desequilibrada y hacia dónde van los viajes?
3. ¿Cuál es la hora pico de toda la red y cuántos viajes hay por día?
