import os
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def invia_messaggio_testo(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": testo,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Errore invio testo: {e}")

def invia_foto_telegram(foto_path, didascalia):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(foto_path, 'rb') as photo_file:
        files = {'photo': photo_file}
        data = {
            'chat_id': CHAT_ID,
            'caption': didascalia,
            'parse_mode': 'Markdown'
        }
        try:
            requests.post(url, data=data, files=files, timeout=20)
        except Exception as e:
            print(f"Errore invio foto: {e}")

def controlla_terremoti_vicini():
    lat_ct = 37.5027
    lon_ct = 15.0872
    url_eq = f"https://webservices.ingv.it/fdsnws/event/1/query?format=json&maxradiuskm=250&lat={lat_ct}&lon={lon_ct}&limit=5&orderby=time"
    
    report_eq = "🌍 *Ultimi Terremoti (< 250 km da Catania):*\n"
    evento_significativo = False
    
    try:
        res = requests.get(url_eq, timeout=10)
        if res.status_code == 200:
            data = res.json()
            features = data.get('features', [])
            if not features:
                report_eq += "• Nessun evento sismico rilevante registrato nel raggio di 250 km.\n\n"
            else:
                for f in features:
                    props = f['properties']
                    mag = props.get('mag', 0.0)
                    place = props.get('place', 'Area di Sicilia / Calabria')
                    time_epoch = props.get('time') / 1000.0
                    time_str = datetime.utcfromtimestamp(time_epoch).strftime('%Y-%m-%d %H:%M')
                    
                    if mag and mag >= 3.0:
                        evento_significativo = True
                        report_eq += f"• 🚨 *M {mag} (RILIEVO)* - {place} alle {time_str} UTC\n"
                    else:
                        report_eq += f"• *M {mag}* - {place} alle {time_str} UTC\n"
                report_eq += "\n"
        else:
            report_eq += "⚠️ Servizio sismico INGV temporaneamente non disponibile.\n\n"
    except Exception as e:
        report_eq += f"❌ Errore controllo sismico: {e}\n\n"
        
    return report_eq, evento_significativo

def scarica_immagine_
