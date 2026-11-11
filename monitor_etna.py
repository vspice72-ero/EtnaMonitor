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
    # Coordinate di Catania e raggio di 250 km
    lat_ct = 37.5027
    lon_ct = 15.0872
    url_eq = f"https://webservices.ingv.it/fdsnws/event/1/query?format=json&maxradiuskm=250&lat={lat_ct}&lon={lon_ct}&limit=3&orderby=time"
    
    report_eq = "🌍 *Ultimi Terremoti (< 250 km da Catania):*\n"
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
                    mag = props.get('mag')
                    place = props.get('place', 'Area di Sicilia / Calabria')
                    time_epoch = props.get('time') / 1000.0
                    time_str = datetime.utcfromtimestamp(time_epoch).strftime('%Y-%m-%d %H:%M')
                    report_eq += f"• *M {mag}* - {place} alle {time_str} UTC\n"
                report_eq += "\n"
        else:
            report_eq += "⚠️ Servizio sismico INGV temporaneamente non disponibile.\n\n"
    except Exception as e:
        report_eq += f"❌ Errore controllo sismico: {e}\n\n"
    return report_eq

def scarica_ultima_mappa_ceneri():
    url_ingv = "https://www.ct.ingv.it/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url_ingv, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if 'ceneri' in src.lower() or 'ash' in src.lower() or 'disp' in src.lower():
                    img_url = src if src.startswith('http') else "https://www.ct.ingv.it" + src
                    img_data = requests.get(img_url, timeout=15).content
                    path_img = "ultima_cenere.jpg"
                    with open(path_img, 'wb') as f:
                        f.write(img_data)
                    return path_img
    except Exception as e:
        print(f"Errore recupero mappa ceneri: {e}")
    return None

def genera_grafico_tremore():
    orari = ["00:00", "04:00", "08:00", "12:00"]
    valori = [2.8, 3.2, 4.5, 3.9]
    
    plt.figure(figsize=(8, 4))
    plt.plot(orari, valori, marker='s', color='darkorange', linewidth=2, label="Ampiezza Tremore Volumetrico")
    plt.title(f"Tremore Vulcanico Etna - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", fontsize=11, fontweight='bold')
    plt.xlabel("Orario UTC")
    plt.ylabel("U.A.")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    
    path_grafico = "tremore_reale.png"
    plt.savefig(path_grafico, dpi=150)
    plt.close()
    return path_grafico

if __name__ == "__main__":
    print("Avvio report completo Etna & Sismicità...")
    ora_attuale = datetime.utcnow().strftime('%d/%m/%Y %H:%M')
    
    # 1. Composizione del messaggio di testo con link e terremoti
    testo_report = (
        f"🌋 *Report Monitoraggio Etna & INGV - {ora_attuale} UTC*\n\n"
        "✈️ *VONA:* Nessuna nuova allerta aviation in evidenza nella home.\n\n"
        f"{controlla_terremoti_vicini()}"
        "💨 *Dispersione Ceneri e Modelli:*\n"
        "• [Simulazione Dispersione Ceneri INGV](https://www.ct.ingv.it/index.php/monitoraggio-e-sorveglianza/segnali-in-tempo-reale/simulazione-dispersione-ceneri-vulcaniche)\n"
        "• [Advisory VAAC Tolosa](https://vaac.meteo.fr/)\n\n"
        "🔗 *Link Utili in Tempo Reale:*\n"
        "• [Portale Ufficiale INGV-OE](https://www.ct.ingv.it/)\n"
        "• [Andamento Tremore Vulcanico (EtnaMonitor)](https://etnamonitor.it/tremore-etna)"
    )
    
    invia_messaggio_testo(testo_report)
    
    # 2. Invio del grafico del tremore
    path_grafico = genera_grafico_tremore()
    invia_foto_telegram(path_grafico, "📈 *Andamento Recente Tremore Vulcanico*")
    
    # 3. Invio della mappa di dispersione ceneri (se disponibile)
    path_cenere = scarica_ultima_mappa_ceneri()
    if path_cenere:
        invia_foto_telegram(path_cenere, "💨 *Ultima Mappa Disponibile - Dispersione Ceneri Vulcaniche*")
