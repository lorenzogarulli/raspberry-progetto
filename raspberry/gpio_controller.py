import platform
import threading
import time
import video_player

# Su Raspberry Pi usa RPi.GPIO, altrimenti simula (per test su PC)
if platform.machine().startswith("arm") or platform.machine() == "aarch64":
    import RPi.GPIO as GPIO
else:
    GPIO = None
    print("⚠ GPIO non disponibile - modalità simulazione (non sei su Raspberry Pi)")

# Pin GPIO collegati ai relè (usa la numerazione BCM)
# Modulo 8 relè: attivo a livello BASSO (LOW = acceso, HIGH = spento)
RELAY_PINS = {
    "lampeggiante1": 17,   # IN1 - lampeggia per 1 minuto
    "lampeggiante2": 27,   # IN2 - lampeggia per 1 minuto
    "fisso": 22,           # IN3 - acceso fisso per 1 minuto
    "rele4": 5,            # IN4 - libero
    "rele5": 6,            # IN5 - libero
    "rele6": 13,           # IN6 - libero
    "rele7": 19,           # IN7 - libero
    "rele8": 26,           # IN8 - libero
}

# Flag per fermare il lampeggio
_stop_blinking = threading.Event()
# Flag per evitare attivazioni sovrapposte
_attivazione_in_corso = False
_lock = threading.Lock()


def setup():
    """Inizializza i pin GPIO (tutti spenti = HIGH per modulo attivo-basso)."""
    if GPIO is None:
        print("[SIM] Setup GPIO simulato")
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for name, pin in RELAY_PINS.items():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
        print(f"Pin {pin} ({name}) inizializzato - SPENTO")


def relay_on(relay_name):
    """Accende un relè (LOW per modulo attivo-basso)."""
    pin = RELAY_PINS.get(relay_name)
    if pin is None:
        return False
    if GPIO is None:
        print(f"[SIM] Relè {relay_name} (pin {pin}) → ON")
        return True
    GPIO.output(pin, GPIO.LOW)
    print(f"Relè {relay_name} (pin {pin}) → ON")
    return True


def relay_off(relay_name):
    """Spegne un relè (HIGH per modulo attivo-basso)."""
    pin = RELAY_PINS.get(relay_name)
    if pin is None:
        return False
    if GPIO is None:
        print(f"[SIM] Relè {relay_name} (pin {pin}) → OFF")
        return True
    GPIO.output(pin, GPIO.HIGH)
    print(f"Relè {relay_name} (pin {pin}) → OFF")
    return True


def spegni_tutto():
    """Spegne tutti i relè."""
    for name in RELAY_PINS:
        relay_off(name)
    print("Tutti i relè spenti")


def attiva_sequenza_visita():
    """Attiva la sequenza completa per una visita:
    - 2 relè lampeggiano ad intermittenza per 60 secondi
    - 1 relè resta acceso fisso per 60 secondi
    Ritorna False se una sequenza è già in corso.
    """
    global _attivazione_in_corso
    with _lock:
        if _attivazione_in_corso:
            return False
        _attivazione_in_corso = True

    _stop_blinking.clear()

    def sequenza():
        global _attivazione_in_corso
        try:
            # Cambia video: da loop a evento
            video_player.avvia_evento()

            # Accendi il relè fisso
            relay_on("fisso")
            print("Sequenza visita avviata: fisso ON, lampeggianti partono, video evento")

            # Lampeggia i 2 relè per 60 secondi (0.5s on, 0.5s off)
            inizio = time.time()
            while time.time() - inizio < 60 and not _stop_blinking.is_set():
                relay_on("lampeggiante1")
                relay_on("lampeggiante2")
                if _stop_blinking.wait(0.5):
                    break
                relay_off("lampeggiante1")
                relay_off("lampeggiante2")
                if _stop_blinking.wait(0.5):
                    break

            # Spegni tutto e torna al video loop
            spegni_tutto()
            video_player.avvia_loop()
            print("Sequenza visita completata - tutto spento, video loop ripristinato")
        finally:
            with _lock:
                _attivazione_in_corso = False

    threading.Thread(target=sequenza, daemon=True).start()
    return True


def get_status():
    """Restituisce lo stato di tutti i relè."""
    global _attivazione_in_corso
    status = {}
    for name, pin in RELAY_PINS.items():
        if GPIO is None:
            status[name] = {"pin": pin, "state": "off"}
        else:
            # Per modulo attivo-basso: LOW = acceso, HIGH = spento
            state = "on" if not GPIO.input(pin) else "off"
            status[name] = {"pin": pin, "state": state}
    status["sequenza_in_corso"] = _attivazione_in_corso
    return status


def cleanup():
    """Spegne tutti i relè e ferma il lampeggio."""
    _stop_blinking.set()
    if GPIO is not None:
        for name, pin in RELAY_PINS.items():
            GPIO.output(pin, GPIO.HIGH)
        print("Cleanup: tutti i relè spenti")
