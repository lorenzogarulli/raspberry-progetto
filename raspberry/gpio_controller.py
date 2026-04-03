import platform

# Su Raspberry Pi usa RPi.GPIO, altrimenti simula (per test su PC)
if platform.machine().startswith("arm") or platform.machine() == "aarch64":
    import RPi.GPIO as GPIO
else:
    GPIO = None
    print("⚠ GPIO non disponibile - modalità simulazione (non sei su Raspberry Pi)")

# Pin GPIO collegati ai relè (usa la numerazione BCM)
RELAY_PINS = {
    "rele1": 17,
    "rele2": 27,
    "rele3": 22,
}


def setup():
    """Inizializza i pin GPIO."""
    if GPIO is None:
        print("[SIM] Setup GPIO simulato")
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for name, pin in RELAY_PINS.items():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        print(f"Pin {pin} ({name}) inizializzato")


def relay_on(relay_name):
    """Accende un relè."""
    pin = RELAY_PINS.get(relay_name)
    if pin is None:
        return False
    if GPIO is None:
        print(f"[SIM] Relè {relay_name} (pin {pin}) → ON")
        return True
    GPIO.output(pin, GPIO.HIGH)
    print(f"Relè {relay_name} (pin {pin}) → ON")
    return True


def relay_off(relay_name):
    """Spegne un relè."""
    pin = RELAY_PINS.get(relay_name)
    if pin is None:
        return False
    if GPIO is None:
        print(f"[SIM] Relè {relay_name} (pin {pin}) → OFF")
        return True
    GPIO.output(pin, GPIO.LOW)
    print(f"Relè {relay_name} (pin {pin}) → OFF")
    return True


def get_status():
    """Restituisce lo stato di tutti i relè."""
    status = {}
    for name, pin in RELAY_PINS.items():
        if GPIO is None:
            status[name] = {"pin": pin, "state": "off"}
        else:
            state = "on" if GPIO.input(pin) else "off"
            status[name] = {"pin": pin, "state": state}
    return status


def cleanup():
    """Spegne tutti i relè."""
    if GPIO is not None:
        for name, pin in RELAY_PINS.items():
            GPIO.output(pin, GPIO.LOW)
        print("Tutti i relè spenti")
