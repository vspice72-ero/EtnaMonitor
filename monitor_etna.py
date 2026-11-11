import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def invia_messaggio_telegram(testo):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Errore: TELEGRAM_TOKEN o CHAT_ID mancanti tra i Secrets.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": testo,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Stato HTTP invio Telegram: {response.status_code}")
    except Exception as e:
        print(f"Errore durante l'invio su Telegram: {e}")

def raccogli_dati_etna():
    url_ingv = "https://www.ct.ingv.it/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    report = "🌋 *Report Monitoraggio Etna (fonti varie)*\n\n"
    
    try:
        response = requests.get(url_ingv, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            report += "📡 *Stato dai canali ufficiali:*\n"
            
            # Estrazione dinamica dell'ultimo VONA
            if "Aviation Color Code" in page_text:
                idx = page_text.find("Aviation Color Code")
                vona_snippet = page_text[idx:idx+180].strip().replace('\n', ' ')
                report += f"✈️ *Ultimo VONA da INGV-OE / Avviso Aviazione:*\n`{vona_snippet}`\n\n"
            else:
                report += "✈️ *VONA da INGV-OE:* Nessuna nuova allerta aviation in evidenza nella home.\n\n"
                
            # Sezione dedicata a ceneri e dispersione
            report += "💨 *Dispersione Ceneri e Modelli:*\n"
            report += "• [Simulazione Dispersione Ceneri INGV](https://www.ct.ingv.it/index.php/monitoraggio-e-sorveglianza/segnali-in-tempo-reale/simulazione-dispersione-ceneri-vulcaniche)\n"
            report += "• [Advisory VAAC Tolosa](https://vaac.meteo.fr/)\n\n"
                
            report += "🔗 *Link Utili in Tempo Reale:*\n"
            report += "• [Portale Ufficiale INGV-OE](https://www.ct.ingv.it/)\n"
            report += "• [Andamento Tremore Vulcanico (EtnaMonitor)](https://www.ct.ingv.it/index.php/monitoraggio-e-sorveglianza/segnali-in-tempo-reale/tremore-vulcanico)\n"
        else:
            report += f"⚠️ Impossibile raggiungere il portale INGV (Codice HTTP: {response.status_code})\n"
            
    except Exception as e:
        report += f"❌ Errore tecnico durante il recupero dei dati: {str(e)}\n"
        
    return report

if __name__ == "__main__":
    print("Avvio controllo dati vulcano e ceneri...")
    messaggio_finale = raccogli_dati_etna()
    print("Invio notifica al bot Telegram...")
    invia_messaggio_telegram(messaggio_finale)
  
