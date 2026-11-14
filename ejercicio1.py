# Curso: Programacion (213023) - Fase 4
# Grupo:360
# Empresa: Software FJ 
# Modulo 1 - Daniel Esteban Zapata Abadia
# Modulo 2 - JHOJHAN YEZID MENESES ARDILA
# Modulo 3 - Victor Olmedo Tello Padilla
# Modulo 4 - 
# Modulo 5 - 

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


# pequena prueba unitaria de tu modulo (para verificar que crea el archivo .log bien)
if __name__ == "__main__":
    print("Probando Modulo 1 (Logs, Excepciones y Clase Abstracta)...")
    GestorLogs.registrar_info("Inicio de pruebas del Modulo 1 por Daniel Zapata.")
    
    try:
        # forzamos un error de datos invalidos para probar que quede guardado en el archivo .log
        raise DatosInvalidosError("Prueba de error: correo de cliente sin formato valido.")

    
    except SoftwareFJError as err:
        GestorLogs.registrar_error(err, "Prueba unitaria Modulo 1")
        print("Error capturado y guardado en 'eventos_software_fj.log' correctamente.")


# Modulo 2: GESTION DE CLIENTES












# Modulo 3: SERVICIOS
try:
    from base import (EntidadBase, SoftwareFJError, ValidacionError,
                      ServicioNoDisponibleError, CalculoError, registrar_log)
except ImportError:
    print("AVISO: no se encontró base.py; se usan clases de respaldo solo para pruebas.")
 
    class EntidadBase(ABC):
        """Respaldo: clase abstracta general del sistema."""
 
        def __init__(self, identificador):
            self._identificador = identificador
 
        @property
        def identificador(self):
            return self._identificador
 
        @abstractmethod
        def describir(self):
            pass
 
    class SoftwareFJError(Exception):
        """Respaldo: excepción raíz del sistema."""
 
    class ValidacionError(SoftwareFJError):
        """Respaldo: datos o parámetros inválidos."""
 
    class ServicioNoDisponibleError(SoftwareFJError):
        """Respaldo: el servicio no se puede usar en este momento."""
 
    class CalculoError(SoftwareFJError):
        """Respaldo: cálculo inconsistente."""
 
    def registrar_log(mensaje, nivel="INFO"):
        print(f"[{nivel}] {mensaje}")
 
 
# ---------------------------------------------------------------
# Constantes del negocio
# ---------------------------------------------------------------
IVA = 0.19                  # impuesto (fracción: 0.19 = 19%)
RECARGO_PROYECTOR = 20000   # valor fijo si la sala usa proyector
RECARGO_SEGURO = 0.10       # 10% extra si el equipo lleva seguro
RECARGO_URGENTE = 0.25      # 25% extra si la asesoría es urgente
FACTOR_NIVEL = {"junior": 1.0, "senior": 1.5, "experto": 2.0}
 
 
def _error(clase, mensaje):
    """Registra el error en el log y devuelve la excepción lista para lanzar."""
    registrar_log(f"{clase.__name__}: {mensaje}", "ERROR")
    return clase(mensaje)
 
 
# ===============================================================
# CLASE ABSTRACTA: SERVICIO
# ===============================================================
class Servicio(EntidadBase, ABC):
    """Servicio general que ofrece Software FJ (no se puede instanciar)."""
 
    def __init__(self, identificador, nombre, tarifa_hora):
        identificador = self._validar_texto(identificador, "El identificador", 20)
        nombre = self._validar_texto(nombre, "El nombre del servicio")
        tarifa_hora = self._validar_tarifa(tarifa_hora)
 
        super().__init__(identificador)
        self._nombre = nombre
        self._tarifa_hora = tarifa_hora
        self._disponible = True
        registrar_log(f"Servicio creado: [{identificador}] {nombre}")
 
    # ---------- encapsulación: acceso controlado a los datos ----------
    @property
    def nombre(self):
        return self._nombre
 
    @property
    def tarifa_hora(self):
        return self._tarifa_hora
 
    @tarifa_hora.setter
    def tarifa_hora(self, nueva_tarifa):
        self._tarifa_hora = self._validar_tarifa(nueva_tarifa)
        registrar_log(f"Nueva tarifa para '{self._nombre}': ${self._tarifa_hora:,.0f}/hora")
 
    @property
    def disponible(self):
        return self._disponible
 
    # ---------- validaciones reutilizables ----------
    @staticmethod
    def _validar_texto(valor, campo, maximo=60):
        if not isinstance(valor, str) or not valor.strip():
            raise _error(ValidacionError, f"{campo} no puede estar vacío.")
        if len(valor.strip()) > maximo:
            raise _error(ValidacionError, f"{campo} no puede superar {maximo} caracteres.")
        return valor.strip()
 
    @staticmethod
    def _a_numero(valor, campo):
        """Convierte a número; si falla, encadena la excepción original."""
        if isinstance(valor, bool):
            raise _error(ValidacionError, f"{campo} debe ser un número, no un valor lógico.")
        try:
            numero = float(valor)
        except (TypeError, ValueError) as error:
            raise _error(ValidacionError, f"{campo} debe ser un número (recibido: {valor!r}).") from error
        if not math.isfinite(numero):
            raise _error(ValidacionError, f"{campo} no es un número válido.")
        return numero
 
    @staticmethod
    def _a_entero(valor, campo):
        numero = Servicio._a_numero(valor, campo)
        if numero != int(numero):
            raise _error(ValidacionError, f"{campo} debe ser un número entero.")
        return int(numero)
 
    @staticmethod
    def _validar_tarifa(valor):
        tarifa = Servicio._a_numero(valor, "La tarifa")
        if tarifa <= 0:
            raise _error(ValidacionError, "La tarifa por hora debe ser mayor que 0.")
        return tarifa
 
    @staticmethod
    def _validar_fraccion(valor, campo, incluye_uno):
        """Valida impuesto/descuento expresados como fracción (0.19 = 19%)."""
        numero = Servicio._a_numero(valor, campo)
        limite_ok = numero <= 1 if incluye_uno else numero < 1
        if numero < 0 or not limite_ok:
            raise _error(ValidacionError, f"{campo} debe ser una fracción entre 0 y 1 (recibido: {numero:g}).")
        return numero
 
    def _validar_horas(self, horas, maximo):
        if horas is None:
            raise _error(ValidacionError, "Falta la duración del servicio (horas).")
        horas = self._a_numero(horas, "La duración")
        if horas <= 0:
            raise _error(ValidacionError, "La duración debe ser mayor que 0 horas.")
        if horas > maximo:
            raise _error(ValidacionError,
                         f"'{self._nombre}' no se puede reservar por más de {maximo} horas (recibido: {horas:g}).")
        return horas
 
    def _rechazar_opciones_desconocidas(self, opciones, permitidas):
        desconocidas = [clave for clave in opciones if clave not in permitidas]
        if desconocidas:
            raise _error(ValidacionError,
                         f"Opciones no reconocidas para '{self._nombre}': {', '.join(desconocidas)}.")
 
    # ---------- disponibilidad ----------
    def habilitar(self):
        self._disponible = True
        registrar_log(f"Servicio habilitado: '{self._nombre}'")
 
    def deshabilitar(self):
        self._disponible = False
        registrar_log(f"Servicio deshabilitado: '{self._nombre}'")
 
    def verificar_disponibilidad(self):
        """Lanza ServicioNoDisponibleError si el servicio no se puede usar."""
        if not self._disponible:
            raise _error(ServicioNoDisponibleError, f"El servicio '{self._nombre}' no está disponible.")
 
    # ---------- métodos abstractos: cada servicio los sobrescribe ----------
    @abstractmethod
    def describir(self):
        """Devuelve una descripción del servicio."""
 
    @abstractmethod
    def validar_parametros(self, horas, **opciones):
        """Valida los parámetros del servicio y devuelve (horas, opciones) ya limpios."""
 
    @abstractmethod
    def calcular_costo_base(self, horas, **opciones):
        """Devuelve el costo sin descuento ni impuesto (fórmula propia de cada servicio)."""
 
    # ---------- SOBRECARGA (parámetros opcionales) ----------
    def calcular_costo(self, horas=None, impuesto=0.0, descuento=0.0, **opciones):
        """
        Calcula el costo total. Python no permite varios métodos con el mismo
        nombre, así que la sobrecarga se simula con parámetros opcionales:
 
            calcular_costo(2)                     -> costo base
            calcular_costo(2, 0.19)               -> con impuesto
            calcular_costo(2, 0.19, 0.10)         -> con impuesto y descuento
            calcular_costo(2, proyector=True)     -> con opciones propias del servicio
 
        El descuento se aplica antes que el impuesto.
        """
        try:
            self.verificar_disponibilidad()
            horas, opciones = self.validar_parametros(horas, **opciones)
            impuesto = self._validar_fraccion(impuesto, "El impuesto", incluye_uno=True)
            descuento = self._validar_fraccion(descuento, "El descuento", incluye_uno=False)
 
            costo = self.calcular_costo_base(horas, **opciones)
            costo = costo * (1 - descuento) * (1 + impuesto)
 
            if not math.isfinite(costo) or costo <= 0:
                raise _error(CalculoError, f"Cálculo inconsistente para '{self._nombre}': costo = {costo}")
        except SoftwareFJError:
            raise       # el error ya fue registrado en el log
        except Exception as error:
            raise _error(CalculoError,
                         f"Error inesperado al calcular el costo de '{self._nombre}'.") from error
        else:
            costo = round(costo, 2)
            registrar_log(f"Costo calculado para '{self._nombre}': ${costo:,.2f}")
            return costo
 
    def __str__(self):
        return self.describir()
 
 
# ===============================================================
# SERVICIO 1: RESERVA DE SALAS
# ===============================================================
class ReservaSala(Servicio):
    """Reserva de salas de reuniones. Opciones: asistentes, proyector."""
 
    HORAS_MAXIMAS = 12
    OPCIONES = ("asistentes", "proyector")
 
    def __init__(self, identificador, nombre, tarifa_hora, capacidad):
        capacidad = self._a_entero(capacidad, "La capacidad")
        if not 1 <= capacidad <= 200:
            raise _error(ValidacionError, "La capacidad de la sala debe estar entre 1 y 200 personas.")
        super().__init__(identificador, nombre, tarifa_hora)
        self._capacidad = capacidad
 
    def describir(self):
        return (f"Sala '{self._nombre}' [{self.identificador}] - capacidad: {self._capacidad} personas - "
                f"tarifa: ${self._tarifa_hora:,.0f}/hora")
 
    def validar_parametros(self, horas, **opciones):
        horas = self._validar_horas(horas, self.HORAS_MAXIMAS)
        self._rechazar_opciones_desconocidas(opciones, self.OPCIONES)
 
        asistentes = self._a_entero(opciones.get("asistentes", 1), "El número de asistentes")
        if not 1 <= asistentes <= self._capacidad:
            raise _error(ValidacionError,
                         f"La sala '{self._nombre}' admite máximo {self._capacidad} asistentes "
                         f"(recibido: {asistentes}).")
 
        proyector = opciones.get("proyector", False)
        if not isinstance(proyector, bool):
            raise _error(ValidacionError, "La opción 'proyector' debe ser True o False.")
 
        return horas, {"asistentes": asistentes, "proyector": proyector}
 
    def calcular_costo_base(self, horas, **opciones):
        costo = self._tarifa_hora * horas
        if opciones.get("proyector", False):
            costo += RECARGO_PROYECTOR
        return costo
 
 
# ===============================================================
# SERVICIO 2: ALQUILER DE EQUIPOS
# ===============================================================
class AlquilerEquipo(Servicio):
    """Alquiler de equipos por hora. Opciones: cantidad, seguro."""
 
    HORAS_MAXIMAS = 72
    OPCIONES = ("cantidad", "seguro")
 
    def __init__(self, identificador, nombre, tarifa_hora, unidades):
        unidades = self._a_entero(unidades, "Las unidades")
        if unidades < 1:
            raise _error(ValidacionError, "Debe haber al menos 1 unidad del equipo.")
        super().__init__(identificador, nombre, tarifa_hora)
        self._unidades_totales = unidades
        self._unidades_disponibles = unidades
 
    def describir(self):
        return (f"Equipo '{self._nombre}' [{self.identificador}] - unidades disponibles: "
                f"{self._unidades_disponibles} de {self._unidades_totales} - "
                f"tarifa: ${self._tarifa_hora:,.0f}/hora")
 
    def verificar_disponibilidad(self):
        super().verificar_disponibilidad()
        if self._unidades_disponibles == 0:
            raise _error(ServicioNoDisponibleError, f"No quedan unidades de '{self._nombre}'.")
 
    def reservar_unidades(self, cantidad):
        """Descuenta unidades del inventario (lo usará la clase Reserva)."""
        cantidad = self._a_entero(cantidad, "La cantidad")
        if cantidad < 1:
            raise _error(ValidacionError, "La cantidad a reservar debe ser al menos 1.")
        if cantidad > self._unidades_disponibles:
            raise _error(ServicioNoDisponibleError,
                         f"Solo quedan {self._unidades_disponibles} unidad(es) de '{self._nombre}' "
                         f"(solicitadas: {cantidad}).")
        self._unidades_disponibles -= cantidad
        registrar_log(f"Unidades reservadas de '{self._nombre}': {cantidad}")
 
    def liberar_unidades(self, cantidad):
        """Devuelve unidades al inventario (cancelación de una reserva)."""
        cantidad = self._a_entero(cantidad, "La cantidad")
        if cantidad < 1 or self._unidades_disponibles + cantidad > self._unidades_totales:
            raise _error(ValidacionError, "No se pueden liberar esa cantidad de unidades.")
        self._unidades_disponibles += cantidad
        registrar_log(f"Unidades liberadas de '{self._nombre}': {cantidad}")
 
    def validar_parametros(self, horas, **opciones):
        horas = self._validar_horas(horas, self.HORAS_MAXIMAS)
        self._rechazar_opciones_desconocidas(opciones, self.OPCIONES)
 
        cantidad = self._a_entero(opciones.get("cantidad", 1), "La cantidad")
        if cantidad < 1:
            raise _error(ValidacionError, "La cantidad debe ser al menos 1.")
        if cantidad > self._unidades_disponibles:
            raise _error(ServicioNoDisponibleError,
                         f"Solo quedan {self._unidades_disponibles} unidad(es) de '{self._nombre}' "
                         f"(solicitadas: {cantidad}).")
 
        seguro = opciones.get("seguro", False)
        if not isinstance(seguro, bool):
            raise _error(ValidacionError, "La opción 'seguro' debe ser True o False.")
 
        return horas, {"cantidad": cantidad, "seguro": seguro}
 
    def calcular_costo_base(self, horas, **opciones):
        costo = self._tarifa_hora * horas * opciones.get("cantidad", 1)
        if opciones.get("seguro", False):
            costo = costo * (1 + RECARGO_SEGURO)
        return costo
 
 
# ===============================================================
# SERVICIO 3: ASESORÍAS ESPECIALIZADAS
# ===============================================================
class Asesoria(Servicio):
    """Asesoría especializada. El nivel del asesor multiplica la tarifa. Opción: urgente."""
 
    HORAS_MAXIMAS = 8
    OPCIONES = ("urgente",)
 
    def __init__(self, identificador, nombre, tarifa_hora, especialidad, nivel="junior"):
        especialidad = self._validar_texto(especialidad, "La especialidad")
        nivel = self._validar_texto(nivel, "El nivel").lower()
        if nivel not in FACTOR_NIVEL:
            raise _error(ValidacionError,
                         f"Nivel no válido: '{nivel}'. Use: {', '.join(FACTOR_NIVEL)}.")
        super().__init__(identificador, nombre, tarifa_hora)
        self._especialidad = especialidad
        self._nivel = nivel
 
    def describir(self):
        return (f"Asesoría '{self._nombre}' [{self.identificador}] - especialidad: {self._especialidad} - "
                f"nivel: {self._nivel} (x{FACTOR_NIVEL[self._nivel]:g}) - "
                f"tarifa base: ${self._tarifa_hora:,.0f}/hora")
 
    def validar_parametros(self, horas, **opciones):
        horas = self._validar_horas(horas, self.HORAS_MAXIMAS)
        self._rechazar_opciones_desconocidas(opciones, self.OPCIONES)
 
        urgente = opciones.get("urgente", False)
        if not isinstance(urgente, bool):
            raise _error(ValidacionError, "La opción 'urgente' debe ser True o False.")
 
        return horas, {"urgente": urgente}
 
    def calcular_costo_base(self, horas, **opciones):
        costo = self._tarifa_hora * horas * FACTOR_NIVEL[self._nivel]
        if opciones.get("urgente", False):
            costo = costo * (1 + RECARGO_URGENTE)
        return costo
 
 
# ===============================================================
# DEMOSTRACIÓN DE ESTA PARTE (se puede borrar al integrar)
# ===============================================================
if __name__ == "__main__":
    servicios = [
        ReservaSala("S-001", "Sala Ejecutiva", 50000, 10),
        AlquilerEquipo("E-001", "Portátil Dell", 15000, 5),
        Asesoria("A-001", "Ciberseguridad", 80000, "Seguridad informática", "experto"),
    ]
 
    print("\n--- POLIMORFISMO: el mismo código, resultados distintos ---")
    for servicio in servicios:
        print(servicio.describir())
        print("   2 h, costo base:          ", servicio.calcular_costo(2))
        print("   2 h, con IVA:             ", servicio.calcular_costo(2, IVA))
        print("   2 h, con IVA y 10% dscto: ", servicio.calcular_costo(2, IVA, 0.10))
 
    print("\n--- OPCIONES PROPIAS DE CADA SERVICIO ---")
    print("Sala con proyector, 8 asistentes:", servicios[0].calcular_costo(2, asistentes=8, proyector=True))
    print("3 equipos con seguro:            ", servicios[1].calcular_costo(2, cantidad=3, seguro=True))
    print("Asesoría urgente:                ", servicios[2].calcular_costo(2, urgente=True))
 
    print("\n--- ERRORES CONTROLADOS (el programa sigue funcionando) ---")
    intentos = [
        ("Sala con 50 asistentes", lambda: servicios[0].calcular_costo(2, asistentes=50)),
        ("Duración 'abc'", lambda: servicios[1].calcular_costo("abc")),
        ("Falta la duración", lambda: servicios[2].calcular_costo()),
        ("Sala con tarifa negativa", lambda: ReservaSala("S-002", "Sala Rota", -5, 10)),
        ("Nivel de asesor inventado", lambda: Asesoria("A-002", "X", 50000, "Redes", "genio")),
    ]
    for descripcion, accion in intentos:
        try:
            accion()
        except SoftwareFJError as error:
            print(f"   {descripcion}: {type(error).__name__} -> {error}")
 

