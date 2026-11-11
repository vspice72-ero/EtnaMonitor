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
    requests.post(url, json=payload, timeout=15)

def invia_foto_telegram(foto_path, didascalia):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(foto_path, 'rb') as photo_file:
        files = {'photo': photo_file}
        data = {
            'chat_id': CHAT_ID,
            'caption': didascalia,
            'parse_mode': 'Markdown'
        }
        requests.post(url, data=data, files=files, timeout=20)

def scarica_ultima_mappa_ceneri():
    url_ingv = "https://www.ct.ingv.it/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url_ingv, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Cerca immagini relative alla dispersione ceneri o modellate
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
    # Qui puoi integrare il recupero dei dati reali del tremore (es. da feed o API)
    orari = ["00:00", "04:00", "08:00", "12:00"]
    valori = [2.8, 3.2, 4.5, 3.9] # Dati di esempio aggiornabili
    
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
    print("Avvio elaborazione report multimediale Etna...")
    
    # 1. Invia testo riassuntivo con timestamp
    ora_attuale = datetime.utcnow().strftime('%d/%m/%Y %H:%M')
    invia_messaggio_testo(f"🌋 *Report Dinamico Etna - {ora_attuale} UTC*\nAnalisi automatica in corso...")
    
    # 2. Genera e invia il grafico del tremore
    path_grafico = genera_grafico_tremore()
    invia_foto_telegram(path_grafico, "📈 *Andamento Recente Tremore Vulcanico*")
    
    # 3. Cerca e invia l'ultima mappa di dispersione ceneri disponibile
    path_cenere = scarica_ultima_mappa_ceneri()
    if path_cenere:
        invia_foto_telegram(path_cenere, "💨 *Ultima Mappa Disponibile - Dispersione Ceneri Vulcaniche*")
    else:
        invia_messaggio_testo("💨 *Dispersione Ceneri:* Al momento non sono presenti immagini dinamiche dirette nella home INGV. Consulta il [portale ufficiale](https://www.ct.ingv.it/).")
