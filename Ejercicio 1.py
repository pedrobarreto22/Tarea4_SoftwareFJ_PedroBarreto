import datetime
from abc import ABC, abstractmethod

# ==========================================
# GESTIÓN DE ERRORES ESPECÍFICOS
# ==========================================
class ErrorSistemaFJ(Exception):
    """Clase base para errores del sistema Software FJ"""
    pass

class DatosInvalidosError(ErrorSistemaFJ):
    pass

class ServicioNoDisponibleError(ErrorSistemaFJ):
    pass

class ErrorFinanciero(ErrorSistemaFJ):
    pass

# ==========================================
# CLASES ABSTRACTAS (HERENCIA Y POLIMORFISMO)
# ==========================================
class EntidadSistema(ABC):
    def __init__(self):
        self.fecha_registro = datetime.datetime.now()

    @abstractmethod
    def mostrar_detalle(self):
        pass

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

# ==========================================
# CLASES DERIVADAS (SERVICIOS)
# ==========================================
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
        
        recargo = 1.20 if incluye_seguro else 1.0 
        return (self.precio_base * dias) * recargo

    def mostrar_detalle(self):
        return f"[EQUIPO] {self.nombre} | Tarifa: ${self.precio_base}/día"

class AsesoriaEspecializada(Servicio):
    def calcular_costo(self, sesiones, cupon_descuento=False):
        if not isinstance(sesiones, (int, float)) or sesiones <= 0:
            raise DatosInvalidosError(f"Cantidad de sesiones inválida: {sesiones}")
        
        multiplicador = 0.90 if cupon_descuento else 1.0 
        return (self.precio_base * sesiones) * multiplicador

    def mostrar_detalle(self):
        return f"[ASESORÍA] {self.nombre} | Precio/Sesión: ${self.precio_base}"

# ==========================================
# ENCAPSULAMIENTO Y VALIDACIONES
# ==========================================
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
            raise DatosInvalidosError("El nombre debe tener al menos 3 caracteres.")
        self.__nombre = valor

    @property
    def correo(self): return self.__correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            raise DatosInvalidosError(f"El email '{valor}' no tiene un formato válido.")
        self.__correo = valor

    def mostrar_detalle(self):
        return f"[CLIENTE] {self.nombre} | Correo: {self.correo}"

class Reserva(EntidadSistema):
    def __init__(self, cliente, servicio, cantidad, **params):
        super().__init__()
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Cliente o Servicio no válido.")
        
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.params = params
        self.estado = "PENDIENTE"

    def procesar(self):
        try:
            total = self.servicio.calcular_costo(self.cantidad, **self.params)
            self.estado = "COMPLETADA"
            return f"Total a pagar: ${total:,.2f}"
        except (DatosInvalidosError, ErrorFinanciero) as e:
            self.estado = "FALLIDA"
            raise ErrorSistemaFJ(f"Error de negocio: {e}") from e
        except Exception as e:
            self.estado = "ERROR_CRITICO"
            raise ErrorSistemaFJ(f"Falla técnica: {e}") from e

    def mostrar_detalle(self):
        return f"[RESERVA] {self.cliente.nombre} -> {self.servicio.nombre} ({self.estado})"

# ==========================================
# REGISTRO DE LOGS
# ==========================================
def registrar_log(mensaje, nivel="INFO"):
    try:
        with open("log_software_fj.txt", "a", encoding="utf-8") as f:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ts}] [{nivel}] {mensaje}\n")
    except Exception as e:
        print(f"Error al escribir log: {e}")

# ==========================================
# SIMULACIÓN AUTOMÁTICA (REQUISITO FASE 4)
# ==========================================
def ejecutar_simulacion():
    print("\n--- INICIANDO 10 PRUEBAS AUTOMÁTICAS ---")
    s1 = ReservaSala("Auditorio Central", 120000)
    s2 = AlquilerEquipos("PC Workstation Pro", 55000)
    c1 = Cliente("Pedro Luis Barreto", "pedro.barreto@usco.edu.co")
    c2 = Cliente("Angelica Ortiz", "angelica.ortiz@mail.com")

    operaciones = [
        lambda: Reserva(c1, s1, 5, aplicar_impuesto=True).procesar(), 
        lambda: Reserva(c1, s1, 2, descuento=300000).procesar(),      
        lambda: Reserva(c2, s2, 3, incluye_seguro=True).procesar(),   
        lambda: Reserva(c1, s2, -5).procesar(),                       
        lambda: Reserva(c2, s1, "texto").procesar(),                  
        lambda: Cliente("P", "p@p.com"),                              
        lambda: Cliente("Usuario Prueba", "correo_sin_arroba"),       
        lambda: Reserva(c1, s1, 8).procesar(),
        lambda: Reserva(c2, s2, 2).procesar(),
        lambda: Reserva(c1, s1, 1).procesar()
    ]

    for i, op in enumerate(operaciones, 1):
        try:
            res = op()
            if res:
                print(f"Prueba {i} Exitosa: {res}")
                registrar_log(f"Simulacion {i} Exitosa: {res}")
        except ErrorSistemaFJ as e:
            print(f"Prueba {i} - Excepción controlada: {e}")
            registrar_log(f"Simulacion {i} - Advertencia: {e}", "ADVERTENCIA")
    print("--- SIMULACIÓN FINALIZADA ---\n")

# ==========================================
# MENÚ DE INTERFAZ DE USUARIO (PETICIÓN TUTOR)
# ==========================================
def menu_principal():
    clientes_registrados = []
    servicios_disponibles = [
        ReservaSala("Sala VIP", 150000),
        AlquilerEquipos("Laptop 5ta Gen", 45000),
        AsesoriaEspecializada("Sistemas Operativos", 80000)
    ]

    while True:
        print("\n" + "="*50)
        print("🏢 MENÚ INTERACTIVO SOFTWARE FJ 🏢")
        print("1. Registrar nuevo Cliente")
        print("2. Mostrar Servicios Disponibles")
        print("3. Ejecutar 10 Simulaciones Automáticas (Prueba Fase 4)")
        print("4. Salir")
        print("="*50)
        
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            print("\n--- REGISTRO DE CLIENTE ---")
            nombre = input("Ingrese el nombre del cliente: ")
            correo = input("Ingrese el correo del cliente: ")
            try:
                nuevo_cliente = Cliente(nombre, correo)
                clientes_registrados.append(nuevo_cliente)
                print("✅ Cliente registrado exitosamente.")
                registrar_log(f"Cliente creado via Menú: {nombre}")
            except ErrorSistemaFJ as e:
                print(f"❌ Error al crear cliente: {e}")
                registrar_log(f"Error creando cliente via Menú: {e}", "ERROR")

        elif opcion == "2":
            print("\n--- SERVICIOS DISPONIBLES ---")
            for i, serv in enumerate(servicios_disponibles, 1):
                print(f"{i}. {serv.mostrar_detalle()}")

        elif opcion == "3":
            ejecutar_simulacion()

        elif opcion == "4":
            print("Saliendo del sistema... ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    menu_principal()