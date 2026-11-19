# Curso: Programacion (213023) - Fase 4
# Grupo:360
# Empresa: Software FJ 
# Modulo 1 - Daniel Esteban Zapata Abadia
# Modulo 2 - Jhojhan Yezid Meneses Ardila
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

# importamos re para validar formatos (correo, nombre) con expresiones regulares
import re


# funcion auxiliar: crea la excepcion, la encadena con su causa original y la registra en el log
def _crear_error(mensaje, contexto, causa=None):
    error = DatosInvalidosError(mensaje)   # creamos la excepcion personalizada con el mensaje
    error.__cause__ = causa                # encadenamiento: guardamos el error original (si existe)
    GestorLogs.registrar_error(error, contexto)  # dejamos constancia en el archivo .log
    return error                           # devolvemos la excepcion para que quien llama haga "raise"


# clase Cliente: hereda de EntidadSistema (el ID de la entidad sera el documento del cliente)
class Cliente(EntidadSistema):

    # patron del nombre: solo letras (con tildes y ñ) y espacios
    _PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$")
    # patron del correo: texto@dominio.extension, sin espacios
    _PATRON_CORREO = re.compile(r"^[\w\.\-+]+@[\w\-]+(\.[\w\-]+)+$")

    # constructor: recibe los datos personales del cliente
    def __init__(self, documento, nombre, correo, telefono):
        documento_ok = Cliente._validar_documento(documento)  # validamos el documento ANTES de crear la entidad
        super().__init__(documento_ok)   # el constructor del padre guarda el ID y la fecha de creacion
        self._nombre = None              # atributo privado del nombre (se llena con el setter)
        self._correo = None              # atributo privado del correo (se llena con el setter)
        self._telefono = None            # atributo privado del telefono (se llena con el setter)
        self._activo = True              # atributo privado: indica si el cliente puede hacer reservas
        self.nombre = nombre             # el setter valida el nombre antes de guardarlo
        self.correo = correo             # el setter valida el correo antes de guardarlo
        self.telefono = telefono         # el setter valida el telefono antes de guardarlo
        GestorLogs.registrar_info(f"Cliente creado correctamente: {self._id_entidad} - {self._nombre}")

    # ---------- VALIDADORES (metodos estaticos reutilizables) ----------

    @staticmethod
    def _validar_documento(documento):
        # si es None o texto vacio, el dato falta
        if documento is None or str(documento).strip() == "":
            raise _crear_error("El documento es obligatorio.", "Validacion documento")
        texto = str(documento).strip()   # convertimos a texto y quitamos espacios sobrantes
        try:
            numero = int(texto)          # intentamos convertir a entero para comprobar que son solo digitos
        except ValueError as causa:      # si falla, capturamos el error original
            # lanzamos nuestra excepcion encadenada con "from" (encadenamiento de excepciones)
            raise _crear_error(f"El documento '{texto}' debe contener solo numeros.",
                               "Validacion documento", causa) from causa
        if numero <= 0 or not texto.isdigit():   # no se permiten negativos, ceros ni signos
            raise _crear_error(f"El documento '{texto}' no es valido.", "Validacion documento")
        if not 5 <= len(texto) <= 12:            # longitud razonable de un documento
            raise _crear_error("El documento debe tener entre 5 y 12 digitos.", "Validacion documento")
        return texto                             # documento correcto

    @staticmethod
    def _validar_nombre(nombre):
        # el nombre debe ser texto (no numero, ni None)
        if not isinstance(nombre, str) or nombre.strip() == "":
            raise _crear_error("El nombre es obligatorio y debe ser texto.", "Validacion nombre")
        limpio = " ".join(nombre.split())        # quitamos espacios repetidos o al inicio/final
        if len(limpio) < 3:                      # minimo 3 caracteres
            raise _crear_error("El nombre debe tener al menos 3 caracteres.", "Validacion nombre")
        if not Cliente._PATRON_NOMBRE.match(limpio):   # solo letras y espacios
            raise _crear_error(f"El nombre '{limpio}' contiene caracteres no permitidos.", "Validacion nombre")
        return limpio.title()                    # lo guardamos con formato "Juan Perez"

    @staticmethod
    def _validar_correo(correo):
        # el correo debe ser texto no vacio
        if not isinstance(correo, str) or correo.strip() == "":
            raise _crear_error("El correo es obligatorio.", "Validacion correo")
        limpio = correo.strip().lower()          # normalizamos a minusculas
        if not Cliente._PATRON_CORREO.match(limpio):   # verificamos el formato con la expresion regular
            raise _crear_error(f"El correo '{limpio}' no tiene un formato valido.", "Validacion correo")
        return limpio

    @staticmethod
    def _validar_telefono(telefono):
        # el telefono es obligatorio
        if telefono is None or str(telefono).strip() == "":
            raise _crear_error("El telefono es obligatorio.", "Validacion telefono")
        limpio = str(telefono).replace(" ", "").replace("-", "")   # quitamos espacios y guiones
        if not limpio.isdigit() or len(limpio) != 10:              # celular colombiano: 10 digitos
            raise _crear_error(f"El telefono '{telefono}' debe tener exactamente 10 digitos numericos.",
                               "Validacion telefono")
        return limpio

    # ---------- ENCAPSULACION: PROPERTIES (getters y setters) ----------

    @property
    def documento(self):
        return self._id_entidad          # solo lectura: el documento es el ID y no se puede cambiar

    @property
    def nombre(self):
        return self._nombre              # getter del nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = Cliente._validar_nombre(valor)    # solo asigna si la validacion pasa

    @property
    def correo(self):
        return self._correo              # getter del correo

    @correo.setter
    def correo(self, valor):
        self._correo = Cliente._validar_correo(valor)    # solo asigna si la validacion pasa

    @property
    def telefono(self):
        return self._telefono            # getter del telefono

    @telefono.setter
    def telefono(self, valor):
        self._telefono = Cliente._validar_telefono(valor)  # solo asigna si la validacion pasa

    @property
    def activo(self):
        return self._activo              # getter del estado (solo lectura desde afuera)

    # ---------- METODOS DE ESTADO ----------

    def desactivar(self):
        self._activo = False             # un cliente inactivo no deberia poder reservar
        GestorLogs.registrar_info(f"Cliente {self.documento} desactivado.")

    def activar(self):
        self._activo = True              # reactiva al cliente
        GestorLogs.registrar_info(f"Cliente {self.documento} activado.")

    # ---------- METODOS ABSTRACTOS DEL PADRE (obligatorio implementarlos) ----------

    def validar_datos(self):
        # vuelve a validar todos los datos del objeto; devuelve True si todo esta bien
        Cliente._validar_documento(self.documento)
        Cliente._validar_nombre(self._nombre)
        Cliente._validar_correo(self._correo)
        Cliente._validar_telefono(self._telefono)
        return True

    def mostrar_resumen(self):
        estado = "Activo" if self._activo else "Inactivo"   # convertimos el booleano en texto
        return (f"Cliente [{self.documento}] {self._nombre} | {self._correo} | "
                f"Tel: {self._telefono} | Estado: {estado}")

    def __str__(self):
        return self.mostrar_resumen()    # al hacer print(cliente) se muestra el resumen

    # ---------- REGISTRO SEGURO (try / except / else / finally) ----------

    @classmethod
    def registrar(cls, lista_clientes, documento, nombre, correo, telefono):
        """Crea un cliente y lo agrega a la lista SIN detener el programa si hay error."""
        try:
            nuevo = cls(documento, nombre, correo, telefono)   # puede lanzar DatosInvalidosError
            # evitamos clientes repetidos revisando la lista interna
            if any(c.documento == nuevo.documento for c in lista_clientes):
                raise _crear_error(f"Ya existe un cliente con documento {nuevo.documento}.",
                                   "Registro de cliente")
        except SoftwareFJError as error:    # capturamos cualquier error propio del sistema
            print(f"  [RECHAZADO] {error}")  # avisamos al usuario (el log ya se guardo antes)
            return None                      # devolvemos None: el programa sigue funcionando
        except Exception as error:           # cualquier error inesperado tambien se controla
            GestorLogs.registrar_error(error, "Error inesperado registrando cliente")
            print(f"  [ERROR INESPERADO] {error}")
            return None
        else:
            lista_clientes.append(nuevo)     # solo si NO hubo error, se agrega a la lista
            print(f"  [OK] {nuevo}")
            return nuevo
        finally:
            # el bloque finally se ejecuta SIEMPRE, haya o no error
            GestorLogs.registrar_info("Intento de registro de cliente finalizado.")


# prueba del modulo: 5 casos validos e invalidos (ejecutar este archivo directamente)
if __name__ == "__main__":
    print("Probando Modulo 2 (Clientes)...")
    clientes = []   # lista interna donde se guardan los clientes (sin base de datos)

    print("1) Cliente valido:")
    Cliente.registrar(clientes, "1061234567", "jhojhan meneses", "jhojhan@correo.com", "3101234567")
    print("2) Documento con letras (error encadenado):")
    Cliente.registrar(clientes, "10A6B", "Ana Lopez", "ana@correo.com", "3001112233")
    print("3) Correo invalido:")
    Cliente.registrar(clientes, "52123456", "Carlos Ruiz", "carlos.correo.com", "3201112233")
    print("4) Telefono incompleto:")
    Cliente.registrar(clientes, "79456123", "Laura Gomez", "laura@correo.com", "31012")
    print("5) Documento duplicado:")
    Cliente.registrar(clientes, "1061234567", "Otro Nombre", "otro@correo.com", "3101234567")

    print(f"\nClientes registrados correctamente: {len(clientes)}")
    for c in clientes:
        print(" -", c)

# Modulo 3 Victor Tello

 Modulo 2: GESTION DE CLIENTES

# funcion auxiliar: crea la excepcion, la encadena con su causa original y la registra en el log
def _crear_error(mensaje, contexto, causa=None):
    error = DatosInvalidosError(mensaje)   # creamos la excepcion personalizada con el mensaje
    error.__cause__ = causa                # encadenamiento: guardamos el error original (si existe)
    GestorLogs.registrar_error(error, contexto)  # dejamos constancia en el archivo .log
    return error                           # devolvemos la excepcion para que quien llama haga "raise"


# clase Cliente: hereda de EntidadSistema (el ID de la entidad sera el documento del cliente)
class Cliente(EntidadSistema):

    # patron del nombre: solo letras (con tildes y ñ) y espacios
    _PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$")
    # patron del correo: texto@dominio.extension, sin espacios
    _PATRON_CORREO = re.compile(r"^[\w\.\-+]+@[\w\-]+(\.[\w\-]+)+$")

    # constructor: recibe los datos personales del cliente
    def __init__(self, documento, nombre, correo, telefono):
        documento_ok = Cliente._validar_documento(documento)  # validamos el documento ANTES de crear la entidad
        super().__init__(documento_ok)   # el constructor del padre guarda el ID y la fecha de creacion
        self._nombre = None              # atributo privado del nombre (se llena con el setter)
        self._correo = None              # atributo privado del correo (se llena con el setter)
        self._telefono = None            # atributo privado del telefono (se llena con el setter)
        self._activo = True              # atributo privado: indica si el cliente puede hacer reservas
        self.nombre = nombre             # el setter valida el nombre antes de guardarlo
        self.correo = correo             # el setter valida el correo antes de guardarlo
        self.telefono = telefono         # el setter valida el telefono antes de guardarlo
        GestorLogs.registrar_info(f"Cliente creado correctamente: {self._id_entidad} - {self._nombre}")

    # ---------- VALIDADORES (metodos estaticos reutilizables) ----------

    @staticmethod
    def _validar_documento(documento):
        # si es None o texto vacio, el dato falta
        if documento is None or str(documento).strip() == "":
            raise _crear_error("El documento es obligatorio.", "Validacion documento")
        texto = str(documento).strip()   # convertimos a texto y quitamos espacios sobrantes
        try:
            numero = int(texto)          # intentamos convertir a entero para comprobar que son solo digitos
        except ValueError as causa:      # si falla, capturamos el error original
            # lanzamos nuestra excepcion encadenada con "from" (encadenamiento de excepciones)
            raise _crear_error(f"El documento '{texto}' debe contener solo numeros.",
                               "Validacion documento", causa) from causa
        if numero <= 0 or not texto.isdigit():   # no se permiten negativos, ceros ni signos
            raise _crear_error(f"El documento '{texto}' no es valido.", "Validacion documento")
        if not 5 <= len(texto) <= 12:            # longitud razonable de un documento
            raise _crear_error("El documento debe tener entre 5 y 12 digitos.", "Validacion documento")
        return texto                             # documento correcto

    @staticmethod
    def _validar_nombre(nombre):
        # el nombre debe ser texto (no numero, ni None)
        if not isinstance(nombre, str) or nombre.strip() == "":
            raise _crear_error("El nombre es obligatorio y debe ser texto.", "Validacion nombre")
        limpio = " ".join(nombre.split())        # quitamos espacios repetidos o al inicio/final
        if len(limpio) < 3:                      # minimo 3 caracteres
            raise _crear_error("El nombre debe tener al menos 3 caracteres.", "Validacion nombre")
        if not Cliente._PATRON_NOMBRE.match(limpio):   # solo letras y espacios
            raise _crear_error(f"El nombre '{limpio}' contiene caracteres no permitidos.", "Validacion nombre")
        return limpio.title()                    # lo guardamos con formato "Juan Perez"

    @staticmethod
    def _validar_correo(correo):
        # el correo debe ser texto no vacio
        if not isinstance(correo, str) or correo.strip() == "":
            raise _crear_error("El correo es obligatorio.", "Validacion correo")
        limpio = correo.strip().lower()          # normalizamos a minusculas
        if not Cliente._PATRON_CORREO.match(limpio):   # verificamos el formato con la expresion regular
            raise _crear_error(f"El correo '{limpio}' no tiene un formato valido.", "Validacion correo")
        return limpio

    @staticmethod
    def _validar_telefono(telefono):
        # el telefono es obligatorio
        if telefono is None or str(telefono).strip() == "":
            raise _crear_error("El telefono es obligatorio.", "Validacion telefono")
        limpio = str(telefono).replace(" ", "").replace("-", "")   # quitamos espacios y guiones
        if not limpio.isdigit() or len(limpio) != 10:              # celular colombiano: 10 digitos
            raise _crear_error(f"El telefono '{telefono}' debe tener exactamente 10 digitos numericos.",
                               "Validacion telefono")
        return limpio

    # ENCAPSULACION: PROPERTIES (getters y setters)

    @property
    def documento(self):
        return self._id_entidad          # solo lectura: el documento es el ID y no se puede cambiar

    @property
    def nombre(self):
        return self._nombre              # getter del nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = Cliente._validar_nombre(valor)    # solo asigna si la validacion pasa

    @property
    def correo(self):
        return self._correo              # getter del correo

    @correo.setter
    def correo(self, valor):
        self._correo = Cliente._validar_correo(valor)    # solo asigna si la validacion pasa

    @property
    def telefono(self):
        return self._telefono            # getter del telefono

    @telefono.setter
    def telefono(self, valor):
        self._telefono = Cliente._validar_telefono(valor)  # solo asigna si la validacion pasa

    @property
    def activo(self):
        return self._activo              # getter del estado (solo lectura desde afuera)

    # METODOS DE ESTADO

    def desactivar(self):
        self._activo = False             # un cliente inactivo no deberia poder reservar
        GestorLogs.registrar_info(f"Cliente {self.documento} desactivado.")

    def activar(self):
        self._activo = True              # reactiva al cliente
        GestorLogs.registrar_info(f"Cliente {self.documento} activado.")

    # METODOS ABSTRACTOS DEL PADRE (obligatorio implementarlos)

    def validar_datos(self):
        # vuelve a validar todos los datos del objeto; devuelve True si todo esta bien
        Cliente._validar_documento(self.documento)
        Cliente._validar_nombre(self._nombre)
        Cliente._validar_correo(self._correo)
        Cliente._validar_telefono(self._telefono)
        return True

    def mostrar_resumen(self):
        estado = "Activo" if self._activo else "Inactivo"   # convertimos el booleano en texto
        return (f"Cliente [{self.documento}] {self._nombre} | {self._correo} | "
                f"Tel: {self._telefono} | Estado: {estado}")

    def __str__(self):
        return self.mostrar_resumen()    # al hacer print(cliente) se muestra el resumen

    # REGISTRO SEGURO (try / except / else / finally)

    @classmethod
    def registrar(cls, lista_clientes, documento, nombre, correo, telefono):
        """Crea un cliente y lo agrega a la lista SIN detener el programa si hay error."""
        try:
            nuevo = cls(documento, nombre, correo, telefono)   # puede lanzar DatosInvalidosError
            # evitamos clientes repetidos revisando la lista interna
            if any(c.documento == nuevo.documento for c in lista_clientes):
                raise _crear_error(f"Ya existe un cliente con documento {nuevo.documento}.",
                                   "Registro de cliente")
        except SoftwareFJError as error:    # capturamos cualquier error propio del sistema
            print(f"  [RECHAZADO] {error}")  # avisamos al usuario (el log ya se guardo antes)
            return None                      # devolvemos None: el programa sigue funcionando
        except Exception as error:           # cualquier error inesperado tambien se controla
            GestorLogs.registrar_error(error, "Error inesperado registrando cliente")
            print(f"  [ERROR INESPERADO] {error}")
            return None
        else:
            lista_clientes.append(nuevo)     # solo si NO hubo error, se agrega a la lista
            print(f"  [OK] {nuevo}")
            return nuevo
        finally:
            # el bloque finally se ejecuta SIEMPRE, haya o no error
            GestorLogs.registrar_info("Intento de registro de cliente finalizado.")


# prueba del modulo 2: 5 casos validos e invalidos
def probar_modulo_2():
    print("Probando Modulo 2 (Clientes)...")
    clientes = []   # lista interna donde se guardan los clientes (sin base de datos)

    print("1) Cliente valido:")
    Cliente.registrar(clientes, "1061234567", "jhojhan meneses", "jhojhan@correo.com", "3101234567")
    print("2) Documento con letras (error encadenado):")
    Cliente.registrar(clientes, "10A6B", "Ana Lopez", "ana@correo.com", "3001112233")
    print("3) Correo invalido:")
    Cliente.registrar(clientes, "52123456", "Carlos Ruiz", "carlos.correo.com", "3201112233")
    print("4) Telefono incompleto:")
    Cliente.registrar(clientes, "79456123", "Laura Gomez", "laura@correo.com", "31012")
    print("5) Documento duplicado:")
    Cliente.registrar(clientes, "1061234567", "Otro Nombre", "otro@correo.com", "3101234567")

    print(f"\nClientes registrados correctamente: {len(clientes)}")
    for c in clientes:
        print(" -", c)
