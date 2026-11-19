# -*- coding: utf-8 -*-
# Archivo: test_gestor.py
# Pruebas automáticas del GestorFJ (clase administradora de clientes, servicios y reservas).
# Se ejecutan junto con las demás desde la carpeta principal del proyecto con:
#     python -m unittest discover -s tests -t .
#
# Por qué existe este archivo: test_basico.py prueba el modelo (Cliente, Servicio, Reserva),
# pero ninguna prueba pasaba por el gestor. Un error en el gestor (usar .id en lugar de
# .identificador) hacía que todos los registros fallaran en silencio, porque el gestor
# captura las excepciones y devuelve None/False. Estas pruebas cubren ese hueco.
import logging
import unittest

from src.gestion import GestorFJ
from src.modelos.alquiler_equipo import AlquilerEquipo
from src.modelos.asesoria import AsesoriaEspecializada
from src.modelos.cliente import Cliente
from src.modelos.reserva import EstadoReserva
from src.modelos.reserva_sala import ReservaSala


def setUpModule():
    # El gestor escribe en logs/sistema.log, que es la EVIDENCIA de la simulación.
    # Para que las pruebas no ensucien ese archivo, se desconecta el manejador de
    # archivo del logger mientras corren las pruebas de este módulo.
    logger = logging.getLogger("SoftwareFJ")
    for manejador in list(logger.handlers):
        logger.removeHandler(manejador)
        manejador.close()
    logger.addHandler(logging.NullHandler())


class PruebasGestorFJ(unittest.TestCase):
    """Pruebas del GestorFJ: registros, reservas y cambios de estado."""

    def setUp(self):
        # Se ejecuta antes de cada prueba: cada una parte de un gestor vacío.
        self.gestor = GestorFJ()
        self.cliente = self.gestor.registrar_cliente(
            "CLI-001", "Ana Gómez", "ana@correo.com", "3001234567")
        self.sala = self.gestor.registrar_servicio(
            ReservaSala, "SAL-001", "Sala Ejecutiva", 10, 50000)

    # ------------------------------------------------------------------
    # Clientes
    # ------------------------------------------------------------------
    def test_registrar_cliente_valido(self):
        self.assertIsInstance(self.cliente, Cliente)
        self.assertEqual(self.gestor.resumen()["clientes"], 1)

    def test_registrar_cliente_invalido_devuelve_none(self):
        cliente = self.gestor.registrar_cliente(
            "CLI-002", "Luis Pérez", "correo-sin-arroba", "3001234567")
        self.assertIsNone(cliente)
        self.assertEqual(self.gestor.resumen()["clientes"], 1)

    def test_registrar_cliente_duplicado_devuelve_none(self):
        duplicado = self.gestor.registrar_cliente(
            "CLI-001", "Otra Persona", "otra@correo.com", "3001112233")
        self.assertIsNone(duplicado)
        self.assertEqual(self.gestor.resumen()["clientes"], 1)

    # ------------------------------------------------------------------
    # Servicios
    # ------------------------------------------------------------------
    def test_registrar_los_tres_tipos_de_servicio(self):
        equipo = self.gestor.registrar_servicio(
            AlquilerEquipo, "EQP-001", "Proyector", 30000, 100000)
        asesoria = self.gestor.registrar_servicio(
            AsesoriaEspecializada, "ASE-001", "Asesoría Legal", 80000, nivel="senior")
        self.assertIsNotNone(self.sala)
        self.assertIsNotNone(equipo)
        self.assertIsNotNone(asesoria)
        self.assertEqual(self.gestor.resumen()["servicios"], 3)

    def test_registrar_servicio_con_clase_invalida(self):
        # str no es una subclase de Servicio
        self.assertIsNone(self.gestor.registrar_servicio(str, "XXX-001", "Falso", 1))

    def test_registrar_servicio_duplicado(self):
        duplicado = self.gestor.registrar_servicio(
            ReservaSala, "SAL-001", "Otra Sala", 5, 20000)
        self.assertIsNone(duplicado)
        self.assertEqual(self.gestor.resumen()["servicios"], 1)

    def test_registrar_servicio_con_datos_invalidos(self):
        asesoria = self.gestor.registrar_servicio(
            AsesoriaEspecializada, "ASE-002", "Asesoría", 80000, nivel="maestro")
        self.assertIsNone(asesoria)

    # ------------------------------------------------------------------
    # Reservas
    # ------------------------------------------------------------------
    def test_crear_reserva_genera_identificador_automatico(self):
        primera = self.gestor.crear_reserva("CLI-001", "SAL-001", 2)
        segunda = self.gestor.crear_reserva("CLI-001", "SAL-001", 3)
        self.assertEqual(primera.identificador, "RES-0001")
        self.assertEqual(segunda.identificador, "RES-0002")
        self.assertEqual(primera.estado, EstadoReserva.PENDIENTE)

    def test_crear_reserva_con_identificador_propio_y_duplicado(self):
        propia = self.gestor.crear_reserva("CLI-001", "SAL-001", 2, id_reserva="RES-900")
        self.assertEqual(propia.identificador, "RES-900")
        # Repetir el mismo identificador debe rechazarse
        repetida = self.gestor.crear_reserva("CLI-001", "SAL-001", 2, id_reserva="RES-900")
        self.assertIsNone(repetida)
        self.assertEqual(self.gestor.resumen()["reservas"], 1)

    def test_crear_reserva_con_cliente_o_servicio_inexistente(self):
        self.assertIsNone(self.gestor.crear_reserva("CLI-999", "SAL-001", 2))
        self.assertIsNone(self.gestor.crear_reserva("CLI-001", "SAL-999", 2))
        self.assertEqual(self.gestor.resumen()["reservas"], 0)

    def test_crear_reserva_con_servicio_no_disponible(self):
        self.gestor.registrar_servicio(
            AlquilerEquipo, "EQP-002", "Cámara", 45000, 150000, disponible=False)
        self.assertIsNone(self.gestor.crear_reserva("CLI-001", "EQP-002", 1))

    def test_crear_reserva_con_duracion_fuera_de_rango(self):
        self.assertIsNone(self.gestor.crear_reserva("CLI-001", "SAL-001", 15))  # máx. 12
        self.assertIsNone(self.gestor.crear_reserva("CLI-001", "SAL-001", 2.5))  # no entero

    # ------------------------------------------------------------------
    # Cambios de estado (confirmar, procesar, cancelar)
    # ------------------------------------------------------------------
    def test_flujo_completo_confirmar_y_procesar(self):
        reserva = self.gestor.crear_reserva("CLI-001", "SAL-001", 4)
        self.assertTrue(self.gestor.confirmar_reserva(reserva.identificador))
        self.assertTrue(self.gestor.procesar_reserva(
            reserva.identificador, impuesto=0.19, descuento=0.10))
        # 4 h x 50.000 = 200.000 -> descuento 10 % = 180.000 -> IVA 19 % = 214.200
        self.assertAlmostEqual(reserva.costo_total, 214200.0, places=2)
        self.assertEqual(reserva.estado, EstadoReserva.PROCESADA)

    def test_procesar_sin_confirmar_devuelve_false(self):
        reserva = self.gestor.crear_reserva("CLI-001", "SAL-001", 2)
        self.assertFalse(self.gestor.procesar_reserva(reserva.identificador))
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)

    def test_descuento_invalido_no_cambia_el_estado_y_permite_reintento(self):
        reserva = self.gestor.crear_reserva("CLI-001", "SAL-001", 2)
        self.gestor.confirmar_reserva(reserva.identificador)
        self.assertFalse(self.gestor.procesar_reserva(reserva.identificador, descuento=1.5))
        self.assertEqual(reserva.estado, EstadoReserva.CONFIRMADA)
        self.assertEqual(reserva.intentos_proceso, 1)
        # Reintento con un descuento válido
        self.assertTrue(self.gestor.procesar_reserva(reserva.identificador, descuento=0.05))
        self.assertEqual(reserva.estado, EstadoReserva.PROCESADA)
        self.assertEqual(reserva.intentos_proceso, 2)

    def test_cancelar_y_luego_operar_es_rechazado(self):
        reserva = self.gestor.crear_reserva("CLI-001", "SAL-001", 2)
        self.assertTrue(self.gestor.cancelar_reserva(reserva.identificador))
        self.assertEqual(reserva.estado, EstadoReserva.CANCELADA)
        # CANCELADA es un estado final
        self.assertFalse(self.gestor.confirmar_reserva(reserva.identificador))
        self.assertFalse(self.gestor.procesar_reserva(reserva.identificador))

    def test_operar_reserva_inexistente_devuelve_false(self):
        self.assertFalse(self.gestor.confirmar_reserva("RES-999"))

    # ------------------------------------------------------------------
    # Encapsulación
    # ------------------------------------------------------------------
    def test_las_consultas_devuelven_copias(self):
        # Modificar la lista devuelta no debe alterar las listas internas del gestor
        copia = self.gestor.clientes
        copia.clear()
        self.assertEqual(len(self.gestor.clientes), 1)


if __name__ == "__main__":
    unittest.main()
