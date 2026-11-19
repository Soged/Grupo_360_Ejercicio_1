# Curso: Programacion (213023) - Fase 4
# Grupo:360
# Empresa: Software FJ
# Modulo 1 - Daniel Esteban Zapata Abadia
# Modulo 2 - Jhojhan Yezid Meneses Ardila
# Modulo 3 - Victor Olmedo Tello Padilla
# Modulo 4 - (Daniel Esteban Zapata - Jhojhan Yezid Meneses Ardila - Victor Olmedo Tello Padilla)
# Modulo 5 - (Daniel Esteban Zapata - Jhojhan Yezid Meneses Ardila - Victor Olmedo Tello Padilla)

import math
import re
import sys
from abc import ABC, abstractmethod
from datetime import datetime

# Modulo 1: CIMIENTOS, LOGS Y EXCEPCIONES

# gestor del archivo de logs para registrar eventos y errores sin detener el programa
class GestorLogs:
    archivo_log = "eventos_software_fj.log"

    @classmethod
    def registrar_evento(cls, tipo, mensaje):
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{fecha_hora}] [{tipo}] {mensaje}\n"
        try:
            with open(cls.archivo_log, "a", encoding="utf-8") as archivo:
                archivo.write(linea)
        except Exception as e:
            print(f"Error critico al escribir en el log: {e}")

    @classmethod
    def registrar_info(cls, mensaje):
        cls.registrar_evento("INFO", mensaje)

    @classmethod
    def registrar_error(cls, error, contexto=""):
        detalle = f"{contexto} -> {type(error).__name__}: {error}"
        # si hay encadenamiento de excepciones (__cause__), tambien lo guarda en el log
        if error.__cause__:
            detalle += f" | Causa original: {type(error.__cause__).__name__}: {error.__cause__}"
        cls.registrar_evento("ERROR", detalle)


# excepciones personalizadas para el sistema
class SoftwareFJError(Exception):
    """Clase base para todas las excepciones personalizadas del sistema."""
    pass

class DatosInvalidosError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente o parametro son incorrectos o faltan."""
    pass

class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un servicio no existe, no tiene cupo o sus parametros fallan."""
    pass

class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando hay errores al confirmar, cancelar o procesar una reserva."""
    pass

class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un calculo de costo, descuento o duracion da valores invalidos."""
    pass


# clase abstracta general para todas las entidades del sistema
class EntidadSistema(ABC):
    def __init__(self, id_entidad):
        if not id_entidad or str(id_entidad).strip() == "":
            error = DatosInvalidosError("El identificador (ID) de la entidad no puede estar vacio.")
            GestorLogs.registrar_error(error, "Creacion de EntidadSistema")
            raise error
        self._id_entidad = str(id_entidad).strip()
        self._fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def id_entidad(self):
        return self._id_entidad

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    # metodos abstractos que obligan a las clases hijas (Cliente, Servicio, Reserva) a implementarlos
    @abstractmethod
    def validar_datos(self):
        pass

    @abstractmethod
    def mostrar_resumen(self):
        pass


# pequena prueba unitaria del modulo 1 (se ejecuta con: python ejercicio1.py pruebas)
def probar_modulo_1():
    print("Probando Modulo 1 (Logs, Excepciones y Clase Abstracta)...")
    GestorLogs.registrar_info("Inicio de pruebas del Modulo 1 por Daniel Zapata.")

    try:
        # forzamos un error de datos invalidos para probar que quede guardado en el archivo .log
        raise DatosInvalidosError("Prueba de error: correo de cliente sin formato valido.")

    except SoftwareFJError as err:
        GestorLogs.registrar_error(err, "Prueba unitaria Modulo 1")
        print("Error capturado y guardado en 'eventos_software_fj.log' correctamente.")
