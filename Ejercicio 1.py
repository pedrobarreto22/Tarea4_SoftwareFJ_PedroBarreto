import datetime
from abc import ABC, abstractmethod

# GESTIÓN DE ERRORES ESPECÍFICOS
class ErrorSistemaFJ(Exception):
    """Clase base para errores del sistema Software FJ"""
    pass

class DatosInvalidosError(ErrorSistemaFJ):
    pass

class ServicioNoDisponibleError(ErrorSistemaFJ):
    pass

class ErrorFinanciero(ErrorSistemaFJ):
    pass

# CLASE ABSTRACTA ENTIDAD
class EntidadSistema(ABC):
    def __init__(self):
        self.fecha_registro = datetime.datetime.now()

    @abstractmethod
    def mostrar_detalle(self):
        pass

# CLASE ABSTRACTA SERVICIO
class Servicio(EntidadSistema, ABC):
    def __init__(self, nombre, precio_base):
        super().__init__()
        self.nombre = nombre
        self.precio_base = precio_base

    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        pass

    def aplicar_iva(self, base, iva=0.19):
        return base * (1 + iva)

class ReservaSala(Servicio):
    def calcular_costo(self, horas, descuento=0, aplicar_impuesto=False):
        if not isinstance(horas, (int, float)) or horas <= 0:
            raise DatosInvalidosError(f"Horas inválidas: {horas}")
        
        costo = (self.precio_base * horas) - descuento
        if costo < 0:
            raise ErrorFinanciero("El descuento no puede superar el costo total.")
            
        if aplicar_impuesto:
            costo = self.aplicar_iva(costo)
        return costo

    def mostrar_detalle(self):
        return f"[SALA] {self.nombre} | Precio: ${self.precio_base}/hr"

class AlquilerEquipos(Servicio):
    def calcular_costo(self, dias, incluye_seguro=False):
        if not isinstance(dias, (int, float)) or dias <= 0:
            raise DatosInvalidosError(f"Días inválidos: {dias}")
        
        recargo = 1.20 if incluye_seguro else 1.0 # Seguro del 20%
        return (self.precio_base * dias) * recargo

    def mostrar_detalle(self):
        return f"[EQUIPO] {self.nombre} | Tarifa: ${self.precio_base}/día"

class AsesoriaEspecializada(Servicio):
    def calcular_costo(self, sesiones, cupon_descuento=False):
        if not isinstance(sesiones, (int, float)) or sesiones <= 0:
            raise DatosInvalidosError(f"Cantidad de sesiones inválida: {sesiones}")
        
        multiplicador = 0.90 if cupon_descuento else 1.0 # 10% de descuento con cupón
        return (self.precio_base * sesiones) * multiplicador

    def mostrar_detalle(self):
        return f"[ASESORÍA] {self.nombre} | Precio/Sesión: ${self.precio_base}"

# CLASE CLIENTE
class Cliente(EntidadSistema):
    def __init__(self, nombre, correo):
        super().__init__()
        self.nombre = nombre
        self.correo = correo

    @property
    def nombre(self): return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor) < 3:
            raise DatosInvalidosError("Nombre demasiado corto.")
        self.__nombre = valor

    @property
    def correo(self): return self.__correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor:
            raise DatosInvalidosError(f"Email '{valor}' no tiene formato válido.")
        self.__correo = valor

    def mostrar_detalle(self):
        return f"[CLIENTE] {self.nombre} | Registro: {self.fecha_registro.strftime('%Y-%m-%d')}"

# CLASE RESERVA
class Reserva(EntidadSistema):
    def __init__(self, cliente, servicio, cantidad, **params):
        super().__init__()
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Cliente o Servicio no válido para la reserva.")
        
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.params = params
        self.estado = "PENDIENTE"

    def procesar(self):
        print(f"Procesando: {self.servicio.nombre} para el cliente {self.cliente.nombre}...")
        try:
            total = self.servicio.calcular_costo(self.cantidad, **self.params)
            self.estado = "COMPLETADA"
            return f"Reserva exitosa. Total a pagar: ${total:,.2f}"
        except (DatosInvalidosError, ErrorFinanciero) as e:
            self.estado = "FALLIDA"
            raise ErrorSistemaFJ(f"Error de negocio: {e}") from e
        except Exception as e:
            self.estado = "ERROR_CRITICO"
            raise ErrorSistemaFJ(f"Falla técnica: {e}") from e
        finally:
            print(f"Resultado de operación: {self.estado}")

    def mostrar_detalle(self):
        return f"[RESERVA] {self.cliente.nombre} -> {self.servicio.nombre}"

def registrar_log(mensaje, nivel="INFO"):
    try:
        with open("log_software_fj.txt", "a", encoding="utf-8") as f:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ts}] [{nivel}] {mensaje}\n")
    except Exception as e:
        print(f"No se pudo escribir el log: {e}")

# EJECUCIÓN DEL SISTEMA
def ejecutar_sistema():
    print("="*60)
    print("SOFTWARE FJ - GESTIÓN INTEGRAL (VERSIÓN PEDRO BARRETO)")
    print("="*60)
    
    # 1. Crear Servicios
    sala_reuniones = ReservaSala("Auditorio Central", 120000)
    pc_gamer = AlquilerEquipos("PC Workstation Pro", 55000)
    mentoria_python = AsesoriaEspecializada("Arquitectura de Software", 95000)

    # 2. Crear Clientes
    try:
        c1 = Cliente("Pedro Luis Barreto", "pedro.barreto@usco.edu.co")
        c2 = Cliente("Angelica Ortiz", "angelica.ortiz@mail.com")
    except ErrorSistemaFJ as e:
        print(f"Error inicial: {e}")
        return

    # 3. 10 OPERACIONES SIMULADAS
    operaciones = [
        lambda: Reserva(c1, sala_reuniones, 5, aplicar_impuesto=True).procesar(), # 1. Válido
        lambda: Reserva(c1, sala_reuniones, 2, descuento=300000).procesar(),      # 2. Error Financiero
        lambda: Reserva(c2, pc_gamer, 3, incluye_seguro=True).procesar(),         # 3. Válido
        lambda: Reserva(c1, pc_gamer, -5).procesar(),                             # 4. Dato Inválido
        lambda: Reserva(c2, mentoria_python, 4, cupon_descuento=True).procesar(), # 5. Válido
        lambda: Reserva(c1, sala_reuniones, "muchas horas").procesar(),           # 6. Error Tipo Dato
        lambda: Reserva(c2, pc_gamer, 1, incluye_seguro=False).procesar(),        # 7. Válido
        lambda: Reserva(c1, mentoria_python, 1).procesar(),                       # 8. Válido
        lambda: Cliente("P", "p@p.com"),                                          # 9. Nombre inválido
        lambda: Cliente("Usuario Prueba", "correo_sin_arroba"),                   # 10. Email inválido
    ]

    for i, op in enumerate(operaciones, 1):
        print(f"\n>>> EJECUTANDO PRUEBA #{i}")
        try:
            res = op()
            if res:
                print(res)
                registrar_log(f"Op {i} Exitosa: {res}")
            else:
                print("Operación completada sin retorno.")
        except ErrorSistemaFJ as e:
            msg = f"Excepción capturada: {e}"
            print(msg)
            registrar_log(msg, "ADVERTENCIA")
        except Exception as e:
            msg = f"Error no esperado: {e}"
            print(msg)
            registrar_log(msg, "CRÍTICO")

    print("\n" + "="*60)
    print("PROCESO FINALIZADO. REVISE EL ARCHIVO 'log_software_fj.txt'")
    print("="*60)

if __name__ == "__main__":
    ejecutar_sistema()