from flask import Flask, jsonify, request
from flask_cors import CORS
import gpio_controller
import threading

app = Flask(__name__)
CORS(app)  # Permette richieste dal sito web esterno

# Inizializza i GPIO all'avvio
gpio_controller.setup()


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
    """Chiamato quando qualcuno visita il sito - attiva il relè 1 per 60 secondi."""
    gpio_controller.relay_on("rele1")

    def spegni_dopo():
        threading.Event().wait(60)
        gpio_controller.relay_off("rele1")
        print("Relè 1 spento dopo 60 secondi")

    threading.Thread(target=spegni_dopo, daemon=True).start()

    return jsonify({
        "messaggio": "Visita registrata! Relè 1 attivato per 60 secondi",
        "successo": True
    })


if __name__ == "__main__":
    try:
        # 0.0.0.0 rende il server accessibile dalla rete locale
        app.run(host="0.0.0.0", port=5000)
    finally:
        gpio_controller.cleanup()
