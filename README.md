# Raspberry Pi - Controllo Relè via Web

Progetto IoT che permette di controllare relè collegati a un Raspberry Pi 3 tramite un sito web.

## Struttura

```
raspberry/       → codice che gira sul Raspberry Pi (API Flask)
web/             → sito web da hostare su Splax (HTML/CSS/JS)
```

## Setup Raspberry Pi

1. Copia la cartella `raspberry/` sul tuo Raspberry Pi
2. Installa le dipendenze:
   ```bash
   cd raspberry
   pip install -r requirements.txt
   ```
3. Avvia il server:
   ```bash
   python app.py
   ```
   Il server sarà attivo su `http://<IP_RASPBERRY>:5000`

## Setup Sito Web

1. Apri `web/script.js` e sostituisci `INDIRIZZO_IP_RASPBERRY` con l'IP del tuo Pi
2. Carica la cartella `web/` su Splax

## Collegamento Relè

| Relè   | Pin GPIO (BCM) |
|--------|-----------------|
| rele1  | 17              |
| rele2  | 27              |
| rele3  | 22              |

## API Endpoints

| Metodo | URL                  | Descrizione                    |
|--------|----------------------|--------------------------------|
| GET    | `/`                  | Stato del server               |
| GET    | `/rele/status`       | Stato di tutti i relè          |
| POST   | `/rele/<nome>/on`    | Accende un relè                |
| POST   | `/rele/<nome>/off`   | Spegne un relè                 |
| POST   | `/visita`            | Notifica visita → attiva relè1 |
