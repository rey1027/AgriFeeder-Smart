import os
import json
import time
from datetime import datetime , timedelta
import logging
from logging.handlers import TimedRotatingFileHandler
import RPi.GPIO as GPIO

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
GPIO.setmode(GPIO.BOARD) # Usar numeraciOn de pines BOARD (fI­sicos)
GPIO.setwarnings(False)

# Configura el motor como sea necesario

# --- Funcion para Calcular el Ciclo de Trabajo (Duty Cycle) desde el angulo ---
def angle_to_percent(angle):
    """
    Convierte un angulo en grados (0-180) a un porcentaje de ciclo de trabajo PWM para controlar un servo.
    """
    if not (0 <= angle <= 180):
        print(f"Advertencia: Ãngulo fuera de rango (0-180): {angle}")
        # Se puede manejar el error o clamp el valor
        angle = max(0, min(180, angle))

    
    start = 4.0   # Porcentaje de ciclo de trabajo para 0 grados
    end = 12.5  # Porcentaje de ciclo de trabajo para 180 grados
    ratio = (end - start) / 180 # Calcula la proporcion por grado

    angle_as_percent = angle * ratio

    return start + angle_as_percent

# --- Funcion para Inicializar y Mover un Servo con el indicador LED ---
def mover_servo_con_led(pwm_pin, led_pin, mensaje_servo, tiempo, duracion_movimiento=1):
    """
    Inicializa un servo y un LED, mueve el servo y enciende/apaga el LED.

    Args:
        pwm_pin (int): El numero de pin GPIO para el servo PWM.
        led_pin (int): El numero de pin GPIO para el LED.
        mensaje_servo (str): Mensaje descriptivo del servo (ej. "Servo Abajo").
        duracion_movimiento (int): Tiempo en segundos para mantener el servo en posicion.
        tiempo (int): Tiempo en segundos para esperar que ingrese una cantidad de comida.
    """
    print(f"\n--- Iniciando secuencia para {mensaje_servo} (PWM: Pin {pwm_pin}, LED: Pin {led_pin}) ---")

    # Configurar pines
    GPIO.setup(pwm_pin, GPIO.OUT)
    GPIO.setup(led_pin, GPIO.OUT)

    # Inicializar PWM para el servo
    pwm = GPIO.PWM(pwm_pin, FREQUENCE)

    try:
        # 1. Mover a 0 grados y encender LED
        print("Iniciando Movimiento")
        GPIO.output(led_pin, GPIO.HIGH) # Encender LED
        pwm.start(angle_to_percent(0))
        time.sleep(duracion_movimiento)

        # 2. Mover a 90 grados y mantener LED encendido
        pwm.ChangeDutyCycle(angle_to_percent(90))
        time.sleep(duracion_movimiento)

        
        time.sleep(tiempo) # Tiempo de espera 

        # 4. Volver a 0 grados y mantener LED encendido durante el movimiento
        print(f"{mensaje_servo}: Volviendo a 0 grados...")
        pwm.ChangeDutyCycle(angle_to_percent(0))
        time.sleep(duracion_movimiento)

        # 5. Apagar LED despues del movimiento de retorno
        print("Movimiento completado.")
        GPIO.output(led_pin, GPIO.LOW) # Apagar LED

    except Exception as e:
        print(f"Error en {mensaje_servo}: {e}")
    finally:
        # Detener PWM y limpiar el pin del servo
        pwm.stop()
        pass # La limpieza global se hace al final


#--- FUNCION DE LOS SERVOS ------
def activar_hardware():
    try:
        print("Iniciando secuencia de servos y LEDs...")

        # 1. Secuencia para el Servo Dispensado
        mover_servo_con_led(PWM_GPIO_ABAJO, LED_ABAJO_GPIO, "Servo Abajo",5,)

        # Pausa entre secuencias de servo, si lo deseas
        time.sleep(2)

        # 2. Secuencia para el Servo Rellenado
        mover_servo_con_led(PWM_GPIO_ARRIBA, LED_ARRIBA_GPIO, "Servo Arriba",3,)

        print("\nSecuencia de servos completada.")

    except KeyboardInterrupt:
        print("\nSecuencia interrumpida por el usuario.")
    except Exception as e:
        print(f"\nOcurrio un error inesperado: {e}")
    finally:
        print("Limpiando pines GPIO...")
        GPIO.cleanup() # Siempre limpiar los pines al finalizar el script
        print("Pines GPIO limpiados.")


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
