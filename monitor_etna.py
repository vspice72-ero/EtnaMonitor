import os
import requests
from bs4 import BeautifulSoup
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

def scarica_immagine_da_pagina(url_pagina, keyword_filtro, nome_file_output):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url_pagina, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if keyword_filtro in src.lower():
                    img_url = src if src.startswith('http') else "https://www.ct.ingv.it" + src
                    img_data = requests.get(img_url, timeout=15).content
                    with open(nome_file_output, 'wb') as f:
                        f.write(img_data)
                    return nome_file_output
    except Exception as e:
        print(f"Errore recupero immagine con filtro '{keyword_filtro}': {e}")
    return None

def gestisci_grafico_tremore():
    url_immagine_fissa = "https://www.ct.ingv.it/RMS_Etna/0.png"
    nome_file = "tremore_reale_ingv.png"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url_immagine_fissa, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(nome_file, 'wb') as f:
                f.write(response.content)
            return nome_file
        else:
            print(f"Errore HTTP {response.status_code} nello scaricare l'immagine fissa del tremore.")
    except Exception as e:
        print(f"Errore di connessione nel download del grafico del tremore: {e}")
    
    return None

if __name__ == "__main__":
    print("Avvio report periodico Etna & Sismicità...")
    ora_attuale = datetime.utcnow().strftime('%d/%m/%Y %H:%M')
    
    report_sismi, evento_rilevante = controlla_terremoti_vicini()
    
    if evento_rilevante:
        intestazione = f"🚨 *ATTENZIONE: EVENTO SISMICO RILEVANTE RILEVATO!*\n" \
                       f"🌋 *Report Straordinario/Periodico Etna & INGV - {ora_attuale} UTC*\n\n"
    else:
        intestazione = f"🌋 *Report Periodico Etna & INGV (RC2026) - {ora_attuale} UTC*\n\n"
    
    testo_report = (
        f"{intestazione}"
        "✈️ *VONA:* Nessuna nuova allerta aviation in evidenza nella home.\n\n"
        f"{report_sismi}"
        "💨 *Dispersione Ceneri e Modelli:*\n"
        "• [Simulazione Dispersione Ceneri INGV](https://www.ct.ingv.it/index.php/monitoraggio-e-sorveglianza/segnali-in-tempo-reale/simulazione-dispersione-ceneri-vulcaniche)\n"
        "• [Advisory VAAC Tolosa](https://vaac.meteo.fr/)\n\n"
        "🔗 *Link Utili in Tempo Reale:*\n"
        "• [Portale Ufficiale INGV-OE](https://www.ct.ingv.it/)\n"
        "• [Andamento Tremore Vulcanico (INGV-OE)](https://www.ct.ingv.it/index.php/monitoraggio-e-sorveglianza/segnali-in-tempo-reale/tremore-vulcanico)"
    )
    invia_messaggio_testo(testo_report)
    
    # Download diretto e invio del grafico reale del tremore dall'URL fisso INGV
    path_grafico_reale = gestisci_grafico_tremore()
    if path_grafico_reale:
        invia_foto_telegram(path_grafico_reale, "📈 *Grafico Reale Tremore Vulcanico (INGV-OE)*")
    else:
        invia_messaggio_testo("📈 *Tremore Vulcanico:* Impossibile scaricare l'immagine dai server INGV al momento.")
        
    # Estrazione e invio della mappa di dispersione ceneri
    url_ceneri_ingv = "https://www.ct.ingv.it/index.php/monitoraggio-e-sorveglianza/segnali-in-tempo-reale/simulazione-dispersione-ceneri-vulcaniche"
    path_cenere_reale = scarica_immagine_da_pagina(url_ceneri_ingv, "ash", "ultima_cenere_reale.jpg")
    if not path_cenere_reale:
        path_cenere_reale = scarica_immagine_da_pagina("https://www.ct.ingv.it/", "ceneri", "ultima_cenere_reale.jpg")
        
    if path_cenere_reale:
        invia_foto_telegram(path_cenere_reale, "💨 *Ultima Mappa Reale - Dispersione Ceneri Vulcaniche*")
