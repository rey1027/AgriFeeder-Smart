import os
import json
import time
from datetime import datetime , timedelta
import logging
from logging.handlers import TimedRotatingFileHandler
#import RPi.GPIO as GPIO

#----- DOCUMENTOS ------
CONFIG_FILE = './archivos/autoconfiguracion.json'
REPORT_FILE = './archivos/reportes.json'
NIVEL_FILE = './archivos/nivel_alimento.json'
ESTADO_FILE = './archivos/estado_auto.json'

# --- Logger configurado ---
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Solo el número del día
dia = datetime.now().strftime("%d")  # Ej: "16"
log_file_path = os.path.join(log_dir, f"auto_mode {dia}.log")
log_handler = TimedRotatingFileHandler(
    filename=log_file_path, when='midnight', interval=1,
    backupCount=7, encoding='utf-8', utc=False
)
log_handler.suffix = "%Y-%m-%d"
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

#Pines Servos
PWM_GPIO_ABAJO = 11  # Pin para el servo "Dispensar"
PWM_GPIO_ARRIBA = 12 # Pin para el servo "Rellenar"

# Pines para los LEDs
LED_ABAJO_GPIO = 7  # Pin para el LED del servo "Dispensar"
LED_ARRIBA_GPIO = 18 # Pin para el LED del servo "Rellenar"

#FRECUENCIA PWM
FREQUENCE = 50

# Setup
#GPIO.setmode(GPIO.BOARD) # Usar numeraciOn de pines BOARD (fI­sicos)
#GPIO.setwarnings(False)

# Configura el motor como sea necesario

#--- FUNCION DE LOS SERVOS ------
def activar_hardware():
    print(f"[GPIO] ✅ Simulando dispensado de un racion...")

def dispensar(raciones):
    now = datetime.now()
    logger.info(f"[DISPENSAR] 🕒 {now.strftime('%H:%M:%S')} - Raciones: {raciones}")
    for i in range(raciones):
        activar_hardware()
        print("Porción dispensada")

def leer_estado():
    try:
        with open(ESTADO_FILE, 'r') as f:
            data = json.load(f)
            return data.get('last_dispensed_count', 0), data.get('last_dispensed_day', datetime.now().day)
    except:
        return 0, datetime.now().day

def guardar_estado(count, day):
    try:
        with open(ESTADO_FILE, 'w') as f:
            json.dump({
                'last_dispensed_count': count,
                'last_dispensed_day': day
            }, f, indent=2)
    except Exception as e:
        logger.error(f"No se pudo guardar estado: {e}")

def guardar_reporte(now, raciones, modo):
    nuevo_registro = {
        'fecha': now.strftime('%Y-%m-%d'),
        'hora': now.strftime('%H:%M'),
        'raciones': raciones,
        'modo': modo
    }
    try:
        with open(REPORT_FILE, 'r+') as f:
            registros = json.load(f)
            registros.append(nuevo_registro)
            f.seek(0)
            json.dump(registros, f, indent=2)
            f.truncate()
    except Exception as e:
        logger.error(f"No se pudo guardar el reporte: {e}")


def actualizar_nivel(raciones):
    try:
        with open(NIVEL_FILE, 'r+') as f:
            nivel_data = json.load(f)
            nivel_actual = nivel_data.get('nivel', 100)

            nivel_actual = max(0, nivel_actual - (raciones * 2.5))
            nivel_data['nivel'] = nivel_actual

            f.seek(0)
            json.dump(nivel_data, f, indent=2)
            f.truncate()

            # 🚨 Alerta si el nivel es bajo
            if nivel_actual <= 5:
                logger.warning(f"⚠️ Nivel bajo de alimento: {nivel_actual}%")

    except Exception as e:
        logger.error(f"No se pudo actualizar el nivel: {e}")

def auto_mode_worker():
    last_dispensed_count, last_dispensed_day = leer_estado()

    while True:
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"No se pudo leer config: {e}")
            time.sleep(10)
            continue

        hora_inicio_str = config.get('hora_inicio')
        intervalo = config.get('intervalo')
        raciones = config.get('raciones')

        if not hora_inicio_str or intervalo is None or raciones is None:
            logger.info("Configuración incompleta. Esperando nueva configuración...")
            time.sleep(10)
            continue

        try:
            now = datetime.now()
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').replace(
                year=now.year, month=now.month, day=now.day
            )
        except ValueError:
            logger.error("Formato de hora inválido")
            time.sleep(10)
            continue

        # Reinicio diario del contador
        if now.day != last_dispensed_day:
            logger.info("Nuevo día. Reiniciando contador de dispensaciones.")
            last_dispensed_count = 0
            last_dispensed_day = now.day
            guardar_estado(last_dispensed_count, last_dispensed_day)

        # Hora de la próxima dispensación esperada
        next_dispense_time = hora_inicio + timedelta(hours=last_dispensed_count * int(intervalo))

        if now >= next_dispense_time:
            logger.info(f"⌛ Dispensando raciones programadas. Hora actual: {now.strftime('%H:%M:%S')}, programado: {next_dispense_time.strftime('%H:%M:%S')}")
            dispensar(raciones)
            last_dispensed_count += 1
            guardar_estado(last_dispensed_count, last_dispensed_day)
            guardar_reporte(now, raciones, 'automático')
            actualizar_nivel(int(raciones))
        else:
            logger.info(f"[ESPERA] 🕒 {now.strftime('%H:%M:%S')} - Próximo dispensado a las {next_dispense_time.strftime('%H:%M:%S')}")

        time.sleep(60)


def guardar_reporte(now, raciones, modo):
    nuevo_registro = {
        'fecha': now.strftime('%Y-%m-%d'),
        'hora': now.strftime('%H:%M'),
        'raciones': raciones,
        'modo': modo
    }
    try:
        with open(REPORT_FILE, 'r+') as f:
            registros = json.load(f)
            registros.append(nuevo_registro)
            f.seek(0)
            json.dump(registros, f, indent=2)
            f.truncate()
    except Exception as e:
        logger.error(f"No se pudo guardar el reporte: {e}")


def actualizar_nivel(raciones):
    try:
        with open(NIVEL_FILE, 'r+') as f:
            nivel_data = json.load(f)
            nivel_actual = nivel_data.get('nivel', 100)

            nivel_actual = max(0, nivel_actual - (raciones * 2.5))
            nivel_data['nivel'] = nivel_actual

            f.seek(0)
            json.dump(nivel_data, f, indent=2)
            f.truncate()

            # 🚨 Alerta si el nivel es bajo
            if nivel_actual <= 5:
                logger.warning(f"⚠️ Nivel bajo de alimento: {nivel_actual}%")

    except Exception as e:
        logger.error(f"No se pudo actualizar el nivel: {e}")
