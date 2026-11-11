from datetime import datetime, timedelta

def controlla_terremoti_vicini():
    lat_ct = 37.5027
    lon_ct = 15.0872
    
    # Definiamo una finestra temporale (ultime 24 ore) per evitare risposte vuote o errori dall'API
    endtime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    starttime = (datetime.utcnow() - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S')
    
    url_eq = (
        f"https://webservices.ingv.it/fdsnws/event/1/query?"
        f"format=json&maxradiuskm=250&lat={lat_ct}&lon={lon_ct}"
        f"&starttime={starttime}&endtime={endtime}&orderby=time"
    )
    
    report_eq = "🌍 *Ultimi Terremoti (< 250 km da Catania):*\n"
    evento_significativo = False
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url_eq, headers=headers, timeout=10)
        
        # Controlliamo che lo status sia 200 e che la risposta sia effettivamente JSON
        if res.status_code == 200 and 'application/json' in res.headers.get('content-type', ''):
            data = res.json()
            features = data.get('features', [])
            if not features:
                report_eq += "• Nessun evento sismico rilevante registrato nelle ultime 24h.\n\n"
            else:
                for f in features[:5]: # Limitiamo ai primi 5 più recenti
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
            report_eq += "• Nessun evento sismico recente o servizio temporaneamente occupato.\n\n"
    except Exception as e:
        print(f"Errore parsing terremoti: {e}")
        report_eq += "• Nessun evento sismico rilevato in questo intervallo.\n\n"
        
    return report_eq, evento_significativo
