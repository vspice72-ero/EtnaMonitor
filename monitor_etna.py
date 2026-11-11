from datetime import datetime, timedelta
import math
import os
import requests

# --- CONFIGURAZIONE TELEGRAM (dalle Variabili d'Ambiente / Secrets) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# --- COORDINATE DI CATANIA ---
CATANIA_LAT = 37.5078
CATANIA_LON = 15.0830
MAX_RADIUS_KM = 250.0  # Raggio massimo di controllo in km


def invia_messaggio_telegram(testo):
  """Invia un messaggio di testo formattato tramite il Bot Telegram."""
  if not TELEGRAM_TOKEN or not CHAT_ID:
    print(
        "Errore: TELEGRAM_TOKEN o CHAT_ID non impostati tra i Secrets di"
        " GitHub."
    )
    return

  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}
  try:
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    print("Alert inviato con successo su Telegram.")
  except Exception as e:
    print(f"Errore nell'invio del messaggio Telegram: {e}")


def calcola_distanza(lat1, lon1, lat2, lon2):
  """Calcola la distanza in km tra due punti geografici (Formula di Haversine)."""
  R = 6371.0  # Raggio medio della terra in km
  dlat = math.radians(lat2 - lat1)
  dlon = math.radians(lon2 - lon1)
  a = (
      math.sin(dlat / 2) ** 2
      + math.cos(math.radians(lat1))
      * math.cos(math.radians(lat2))
      * math.sin(dlon / 2) ** 2
  )
  c = 2 * math.asin(math.sqrt(a))
  return R * c


def controlla_terremoti_ingv():
  """Interroga il servizio FDSN dell'INGV per cercare terremoti recenti."""
  print("Controllo terremoti recenti nel database INGV...")

  # Finestra temporale di controllo: ultimi 20 minuti
  endtime = datetime.utcnow()
  starttime = endtime - timedelta(minutes=20)

  url = "https://webservices.ingv.it/fdsnws/event/1/query"
  params = {
      "format": "geojson",
      "starttime": starttime.strftime("%Y-%m-%dT%H:%M:%S"),
      "endtime": endtime.strftime("%Y-%m-%dT%H:%M:%S"),
      "minmagnitude": 2.0,  # Filtro magnitudo minima
  }

  try:
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 204:
      print("Nessun terremoto rilevato nella finestra temporale.")
      return

    data = response.json()
    features = data.get("features", [])

    for feature in features:
      props = feature["properties"]
      coords = feature["geometry"]["coordinates"]  # [longitudine, latitudine, profondità]
      eq_lon, eq_lat = coords[0], coords[1]

      distanza = calcola_distanza(CATANIA_LAT, CATANIA_LON, eq_lat, eq_lon)

      if distanza <= MAX_RADIUS_KM:
        magnitudo = props.get("mag")
        luogo = props.get("place")
        tempo_ms = props.get("time")
        profondita = coords[2]

        tempo = datetime.utcfromtimestamp(tempo_ms / 1000.0).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        alert_text = (
            f"🚨 *ALERT SISMICO RILEVATO*\n\n"
            f"• *Magnitudo:* M {magnitudo}\n"
            f"• *Zona:* {luogo}\n"
            f"• *Profondità:* {profondita} km\n"
            f"• *Distanza da Catania:* {distanza:.1f} km\n"
            f"• *Orario (UTC):* {tempo}"
        )
        invia_messaggio_telegram(alert_text)

  except Exception as e:
    print(f"Errore durante la richiesta dei dati sismici: {e}")


def controlla_tremore_e_vona():
  """Logica di verifica per il tremore vulcanico dell'Etna e i bollettini VONA."""
  print("Verifica stato tremore vulcanico Etna e bollettini VONA...")

  # Qui puoi inserire la logica di scraping o parsing specifica per le pagine INGV-OE
  tremore_in_salita = False
  nuovo_vona_emesso = False

  if tremore_in_salita:
    invia_messaggio_telegram(
        "🌋 *ALERT ETNA: Trend Tremore Vulcanico in Salita!*\nRegistrato"
        " un incremento significativo dell'ampiezza del tremore."
    )

  if nuovo_vona_emesso:
    invia_messaggio_telegram(
        "✈️ *ALERT VONA (Aviazione Civile):*\nÈ stato emesso un nuovo bollettino"
        " VONA per l'Etna."
    )


if __name__ == "__main__":
  controlla_terremoti_ingv()
  controlla_tremore_e_vona()