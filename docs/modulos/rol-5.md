# Módulo de reservas y pruebas (Rol 5)

**Responsable:** Juan Daniel Granados Torres · **Rama:** feature/reservas-pruebas

**Archivos del módulo:**
`src/modelos/reserva.py`, `src/modelos/__init__.py`,
`tests/__init__.py`, `tests/test_basico.py`

## ¿Qué hace?

Une a un cliente con un servicio durante una duración y controla el ciclo de vida de esa
reserva: nace pendiente, se puede confirmar, cancelar o procesar (calcular su costo final), y
cada cambio de estado se valida para que no ocurran operaciones imposibles. Además,
`src/modelos/__init__.py` reúne las clases del modelo en un solo punto de importación y la
carpeta `tests/` comprueba con 23 pruebas automáticas que todo lo anterior funciona.

## Clases y métodos públicos

### `src/modelos/reserva.py`

- `EstadoReserva(Enum)`: los cuatro estados posibles: `PENDIENTE`, `CONFIRMADA`,
  `PROCESADA` y `CANCELADA`.
- `Reserva(EntidadBase)`: reserva de un servicio hecha por un cliente.
  - `__init__(identificador, cliente, servicio, duracion)`: valida el identificador, que
    `cliente` sea un `Cliente`, que `servicio` sea un `Servicio`, que el servicio esté
    disponible y que la duración sea válida para ese servicio. La reserva empieza `PENDIENTE`.
  - Propiedades de solo lectura: `cliente`, `servicio`, `duracion`, `estado`, `costo_total`
    (vale `None` hasta procesar) e `intentos_proceso` (cuántas veces se intentó procesar).
    El `identificador` lo hereda de `EntidadBase`.
  - `confirmar()`: pasa de `PENDIENTE` a `CONFIRMADA`.
  - `cancelar()`: pasa de `PENDIENTE` o `CONFIRMADA` a `CANCELADA`.
  - `procesar(impuesto=0.0, descuento=0.0)`: desde `CONFIRMADA` calcula el costo con el servicio,
    lo guarda en `costo_total`, pasa a `PROCESADA` y lo devuelve.
  - `describir()`: texto resumen, por ejemplo
    `Reserva RES-001 [PROCESADA] - Ana Gómez -> Sala Ejecutiva x 3, total $160,650.00`.

Cambios de estado permitidos:

```
PENDIENTE  -> CONFIRMADA  o  CANCELADA
CONFIRMADA -> PROCESADA   o  CANCELADA
PROCESADA y CANCELADA son estados finales: de ahí no se sale.
```

### `src/modelos/__init__.py`

Reexporta `EntidadBase`, `Cliente`, `Servicio`, `ReservaSala`, `AlquilerEquipo`,
`AsesoriaEspecializada`, `EstadoReserva` y `Reserva`, para poder escribir
`from src.modelos import Cliente, Reserva`.

### `tests/`

- `tests/__init__.py`: convierte la carpeta en paquete para que `unittest discover` encuentre
  las pruebas.
- `tests/test_basico.py`, con dos clases:
  - `PruebasSoftwareFJ` (17 pruebas): clientes, servicios y reservas. Su `setUp` crea un cliente
    y una sala válidos antes de cada prueba. Incluye las seis de la guía: correo inválido, costo
    con impuesto y descuento (160.650), costo base (100.000), descuento excesivo, cancelar una
    reserva procesada y servicio no disponible.
  - `PruebasUtilidades` (6 pruebas): `validadores.py` y `describir_error()` de `logger.py`.
  - Se ejecutan con: `python -m unittest discover -s tests -t .`

## Excepciones que lanza

| Código | Excepción | Cuándo la lanza `Reserva` |
|---|---|---|
| FJ-104 | `ReservaInvalidaError` | Identificador inválido, cliente o servicio que no son del tipo correcto, o duración fuera del rango del servicio. |
| FJ-103 | `ServicioNoDisponibleError` | Se intenta reservar un servicio que no está disponible. |
| FJ-105 | `OperacionNoPermitidaError` | Se confirma, cancela o procesa desde un estado que no lo permite. |
| FJ-107 | `CalculoInconsistenteError` | El cálculo del costo falla (por ejemplo, descuento mayor al 100 %). Si el error original no es de Software FJ, se convierte con `raise ... from error` y se conserva la causa. |

## Ejemplo de uso

```python
from src.modelos import Cliente, ReservaSala, Reserva
from src.excepciones.errores import ErrorSoftwareFJ

cliente = Cliente("CLI-001", "Ana Gómez", "ana@correo.com", "3001234567")
sala = ReservaSala("SAL-001", "Sala Ejecutiva", 10, 50000)

reserva = Reserva("RES-001", cliente, sala, 3)
reserva.confirmar()
reserva.procesar(impuesto=0.19, descuento=0.10)
print(reserva.describir())
# Reserva RES-001 [PROCESADA] - Ana Gómez -> Sala Ejecutiva x 3, total $160,650.00

try:
    reserva.cancelar()          # PROCESADA es un estado final
except ErrorSoftwareFJ as error:
    print(error)
# [FJ-105] No se puede cancelar la reserva RES-001: estado PROCESADA.
```

El costo sale de 3 horas × $50.000 = $150.000, menos 10 % de descuento ($135.000), más 19 % de
impuesto: $160.650.

## Conceptos de POO aplicados

- **Herencia:** `Reserva` hereda de `EntidadBase` y reutiliza su `identificador`
  (`src/modelos/reserva.py`).
- **Abstracción:** `EntidadBase` y `Servicio` son clases abstractas con métodos
  `@abstractmethod`; `Reserva` trabaja con un `Servicio` sin saber de qué tipo es.
- **Polimorfismo:** `servicio.validar_parametros(duracion)` y `servicio.calcular_costo(...)` se
  comportan distinto en una sala, un equipo o una asesoría, y `Reserva` las llama igual en todos
  los casos.
- **Encapsulación:** los datos de la reserva son atributos privados (`__cliente`, `__estado`,
  etc.) con propiedades de solo lectura; el estado solo cambia con `confirmar()`, `cancelar()` y
  `procesar()`.
- **Parámetros opcionales (sobrecarga en Python):** `procesar(impuesto=0.0, descuento=0.0)` y
  `calcular_costo(duracion, impuesto=0.0, descuento=0.0)` se pueden llamar con distintas
  combinaciones de argumentos.
- **Manejo de excepciones:** `procesar()` usa `try/except/else/finally`: el `else` guarda el costo
  y cambia el estado solo si no hubo error, y el `finally` cuenta el intento siempre. Además
  encadena errores con `raise ... from error` y usa las excepciones propias del sistema.
- **Enumeraciones:** `EstadoReserva` evita errores de escritura al nombrar los estados.
