#!/usr/bin/env python3
"""Write a small SYNTHETIC sample in the MiBici file layout, for tests and for working offline.
It is not real data. Never present numbers from it as findings. Standard library only.

  python3 scripts/make_sample.py            # writes data/sample/*.csv
"""
import csv, random, datetime, pathlib

random.seed(14)
out = pathlib.Path(__file__).resolve().parent.parent / "data" / "sample"
out.mkdir(parents=True, exist_ok=True)

names = ["Av. Juárez / Federalismo", "López Cotilla / Chapultepec", "Av. Vallarta / Américas", "Parque Revolución",
         "Catedral", "Expiatorio", "Glorieta Minerva", "Av. México / Chapultepec", "Mercado San Juan de Dios",
         "Estación Juárez", "Av. La Paz / Enrique Díaz de León", "Parque Agua Azul"]
stations = [{"id": i + 2, "name": "(GDL-%03d) %s" % (i + 1, n), "obcn": "GDL-%03d" % (i + 1), "location": "POLÍGONO CENTRAL",
             "latitude": round(20.674 + random.uniform(-0.02, 0.02), 6), "longitude": round(-103.36 + random.uniform(-0.03, 0.03), 6),
             "status": "IN_SERVICE"} for i, n in enumerate(names)]
with open(out / "nomenclatura_sample.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(stations[0])); w.writeheader(); w.writerows(stations)

ids = [s["id"] for s in stations]
homes, works = ids[:6], ids[6:]          # mornings flow homes -> works, evenings the reverse
hour_weights = [1, 1, 1, 1, 1, 2, 6, 14, 16, 9, 6, 6, 8, 9, 7, 6, 7, 10, 15, 12, 7, 4, 3, 2]
rows, day0 = [], datetime.datetime(2026, 10, 5)
for n in range(6000):
    start = day0 + datetime.timedelta(days=random.randrange(14), hours=random.choices(range(24), hour_weights)[0], minutes=random.randrange(60), seconds=random.randrange(60))
    if 6 <= start.hour <= 10 and random.random() < 0.75:
        o, d = random.choice(homes), random.choice(works)
    elif 17 <= start.hour <= 20 and random.random() < 0.6:
        o, d = random.choice(works), random.choice(homes)
    else:
        o, d = random.choice(ids), random.choice(ids)
    end = start + datetime.timedelta(minutes=max(0.2, random.gauss(13, 7)))
    rows.append([900000 + n, random.randrange(1000, 4000), random.choice(["M", "F", "M", ""]), random.randrange(1960, 2006),
                 start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), o, d])
rows[10][4] = "no-es-fecha"; rows[11][6] = ""; rows[12][5] = rows[12][4]     # three dirty rows on purpose
with open(out / "datos_abiertos_sample.csv", "w", newline="", encoding="latin-1") as f:
    w = csv.writer(f)
    w.writerow(["Viaje_Id", "Usuario_Id", "Genero", "Año_de_nacimiento", "Inicio_del_viaje", "Fin_del_viaje", "Origen_Id", "Destino_Id"])
    w.writerows(rows)
print("Wrote", len(rows), "synthetic trips and", len(stations), "stations to", out)
