import os
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def invia_messaggio_telegram(testo):
    # Stampa di controllo nei log per verificare la presenza delle variabili
    print(f"TELEGRAM_TOKEN presente: {bool(TELEGRAM_TOKEN)}")
    print(f"CHAT_ID letto: '{CHAT_ID}'")

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Errore critico: TELEGRAM_TOKEN o CHAT_ID mancanti tra i Secrets di GitHub.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": testo,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Stato HTTP risposta Telegram: {response.status_code}")
        print(f"Dettaglio risposta Telegram: {response.text}")
    except Exception as e:
        print(f"Errore di connessione durante l'invio: {e}")

if __name__ == "__main__":
    print("Avvio script di monitoraggio Etna...")
    invia_messaggio_telegram("🌋 *Test Monitor Etna*: Verifica connessione e invio riuscita!")
  
