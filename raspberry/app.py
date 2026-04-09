from flask import Flask, jsonify, request
from flask_cors import CORS
import gpio_controller
import video_player

app = Flask(__name__)
CORS(app)  # Permette richieste dal sito web esterno

# Inizializza i GPIO e avvia il video in loop all'avvio
gpio_controller.setup()
video_player.avvia_loop()


@app.route("/")
def home():
    return jsonify({"messaggio": "API Raspberry Pi attiva", "stato": "online"})


@app.route("/rele/<nome>/on", methods=["POST"])
def accendi_rele(nome):
    """Accende un relè specifico."""
    successo = gpio_controller.relay_on(nome)
    if successo:
        return jsonify({"rele": nome, "azione": "on", "successo": True})
    return jsonify({"errore": f"Relè '{nome}' non trovato"}), 404


@app.route("/rele/<nome>/off", methods=["POST"])
def spegni_rele(nome):
    """Spegne un relè specifico."""
    successo = gpio_controller.relay_off(nome)
    if successo:
        return jsonify({"rele": nome, "azione": "off", "successo": True})
    return jsonify({"errore": f"Relè '{nome}' non trovato"}), 404


@app.route("/rele/status", methods=["GET"])
def stato_rele():
    """Restituisce lo stato di tutti i relè."""
    return jsonify(gpio_controller.get_status())


@app.route("/visita", methods=["POST"])
def nuova_visita():
    """Chiamato quando qualcuno visita splax.app.
    Attiva la sequenza: 2 relè lampeggiano + 1 relè fisso per 60 secondi.
    """
    avviata = gpio_controller.attiva_sequenza_visita()
    if avviata:
        return jsonify({
            "messaggio": "Sequenza attivata! 2 lampeggianti + 1 fisso per 60 secondi",
            "successo": True,
            "durata_secondi": 60
        })
    return jsonify({
        "messaggio": "Sequenza già in corso, attendi che finisca",
        "successo": False
    }), 429


if __name__ == "__main__":
    try:
        # 0.0.0.0 rende il server accessibile dalla rete locale
        app.run(host="0.0.0.0", port=5000)
    finally:
        video_player.ferma()
        gpio_controller.cleanup()
