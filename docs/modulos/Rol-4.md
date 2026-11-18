# Módulo de servicios (Rol 3)

**Responsable:** Jesus Adrian Anaya Sarria . **Rama:**  feature/servicios

**Archivos del módulo:** `src/modelos/servicio.py`, `src/modelos/reserva_sala.py`, `src/modelos/alquiler_equipo.py`, `src/modelos/asesoria.py`

## ¿Qué hace?

Define los servicios que ofrece Software FJ. Una clase abstracta `Servicio` valida los datos comunes (identificador, nombre y disponibilidad) y concentra el cálculo del costo total, que es igual para todos: **costo base → descuento → impuesto**. Tres clases hijas (`ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada`) solo aportan lo propio de cada servicio: sus datos, el rango de duración permitido y cómo se calcula su costo base. Todos los datos se revisan con los validadores del módulo de excepciones y los errores se traducen a excepciones propias con `raise ... from error`.

## Clases y métodos públicos

### `src/modelos/servicio.py`

- **`Servicio(EntidadBase, ABC)`**: clase abstracta, padre de los tres servicios. No se instancia directamente.
  - `__init__(identificador, nombre, disponible=True)`: valida el id, el nombre (3 a 80 caracteres) y la disponibilidad.
  - `nombre`: propiedad de solo lectura.
  - `disponible`: propiedad con setter; solo acepta `True` o `False`.
  - `_costo_base(duracion)`: método abstracto. Costo sin descuento ni impuesto.
  - `validar_parametros(duracion)`: método abstracto. Revisa que la duración sea válida para ese servicio.
  - `calcular_costo(duracion, impuesto=0.0, descuento=0.0)`: devuelve el costo total redondeado a 2 decimales. Impuesto y descuento van como fracción (`0.19` = 19 %). Simula la sobrecarga con parámetros opcionales.
  - `_validar_rango_duracion(duracion, minimo, maximo, unidad)`: método estático. La duración debe ser entera (no `bool`) y estar dentro del rango.
  - `describir()`: texto con la clase, el id, el nombre y el estado (disponible / NO disponible).

### `src/modelos/reserva_sala.py`

- **`ReservaSala(Servicio)`**: sala que se reserva por hora, de 1 a 12 horas.
  - `__init__(identificador, nombre, capacidad, tarifa_hora, disponible=True)`.
  - `capacidad`, `tarifa_hora`: propiedades de solo lectura.
  - Costo base: `tarifa_hora × horas`.

### `src/modelos/alquiler_equipo.py`

- **`AlquilerEquipo(Servicio)`**: equipo que se alquila por día más un depósito, de 1 a 30 días.
  - `__init__(identificador, nombre, tarifa_dia, deposito=0, disponible=True)`.
  - `tarifa_dia`, `deposito`: propiedades de solo lectura. El depósito puede ser 0.
  - Costo base: `tarifa_dia × días + depósito`.

### `src/modelos/asesoria.py`

- **`AsesoriaEspecializada(Servicio)`**: asesoría por hora cuya tarifa depende del nivel del asesor, de 1 a 8 horas.
  - `__init__(identificador, nombre, tarifa_hora_base, nivel="junior", disponible=True)`. El nivel se pasa a minúsculas (`"Senior"` y `"SENIOR"` se aceptan).
  - `tarifa_hora_base`, `nivel`: propiedades de solo lectura.
  - `MULTIPLICADORES`: `junior` 1.0, `senior` 1.5, `experto` 2.0.
  - Costo base: `tarifa_hora_base × multiplicador × horas`.

Las tres hijas sobrescriben `_costo_base`, `validar_parametros` y `describir` (que extiende al padre con `super().describir()`).

| Servicio | Duración permitida | Unidad |
|---|---|---|
| `ReservaSala` | 1 a 12 | horas |
| `AlquilerEquipo` | 1 a 30 | días |
| `AsesoriaEspecializada` | 1 a 8 | horas |

## Excepciones que lanza

| Código | Excepción | Cuándo |
|---|---|---|
| FJ-102 | `ServicioInvalidoError` | Dato de servicio incorrecto: id o nombre inválido, tarifa, capacidad o depósito incorrectos, nivel inexistente, disponibilidad que no es `bool`. |
| FJ-104 | `ReservaInvalidaError` | Duración que no es un entero o que está fuera del rango del servicio. |
| FJ-107 | `CalculoInconsistenteError` | Descuento no numérico, no finito o fuera de 0 % a 100 %; impuesto no numérico, no finito o negativo. |

Los datos ausentes (`None`, vacío o solo espacios) llegan desde los validadores como `ParametroFaltanteError` (FJ-106). Como esta clase también hereda de `ValueError`, los constructores la capturan y la traducen a `ServicioInvalidoError` conservando la causa original en `__cause__`.

## Ejemplo de uso

```python
from src.modelos.reserva_sala import ReservaSala
from src.modelos.alquiler_equipo import AlquilerEquipo
from src.modelos.asesoria import AsesoriaEspecializada

sala = ReservaSala("S-01", "Sala Norte", 10, 50000)
equipo = AlquilerEquipo("E-01", "Proyector", 40000, deposito=100000)
asesoria = AsesoriaEspecializada("A-01", "Asesoría en datos", 80000, nivel="Senior")

print(sala.describir())
# ReservaSala S-01 'Sala Norte' (disponible) - capacidad 10 personas, $50,000/hora

print(sala.calcular_costo(3))                                  # 150000.0
print(equipo.calcular_costo(5, impuesto=0.19))                 # 357000.0
print(asesoria.calcular_costo(2, impuesto=0.19, descuento=0.10))  # 257040.0
```

Una duración fuera de rango lanza `ReservaInvalidaError`, y un descuento imposible lanza `CalculoInconsistenteError`:

```python
sala.calcular_costo(13)
# ReservaInvalidaError: [FJ-104] La duración debe estar entre 1 y 12 horas (recibido: 13).

sala.calcular_costo(3, descuento=1.5)
# CalculoInconsistenteError: [FJ-107] El descuento debe estar entre 0 % y 100 % (recibido: 150 %).
```

Un dato incorrecto en el constructor se traduce a `ServicioInvalidoError` con la causa encadenada:

```python
from src.excepciones import ErrorSoftwareFJ
from src.utilidades.logger import describir_error, registrar_error

try:
    AsesoriaEspecializada("A-02", "Asesoría", 80000, nivel="maestro")
except ErrorSoftwareFJ as error:
    print(describir_error(error))
    registrar_error("No se pudo crear la asesoría", error)
```

Salida en pantalla:

```
ServicioInvalidoError: [FJ-102] Datos de la asesoría inválidos: nivel 'maestro' no existe (opciones: junior, senior, experto). <- causa: ValueError: nivel 'maestro' no existe (opciones: junior, senior, experto).
```

## Conceptos de POO aplicados

| Concepto | Dónde se ve | Archivo |
|---|---|---|
| Clase abstracta | `Servicio(EntidadBase, ABC)` con `@abstractmethod` en `_costo_base` y `validar_parametros`. | `servicio.py` |
| Herencia | `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada` heredan de `Servicio`, que hereda de `EntidadBase`. | todos |
| Polimorfismo | `calcular_costo` llama a `_costo_base` y `validar_parametros`; cada hijo los implementa a su manera. | `servicio.py` y las hijas |
| Encapsulación | Atributos privados (`__nombre`, `__tarifa_hora`, etc.) con propiedades de solo lectura; `disponible` con setter validado. | todos |
| Sobrecarga simulada | `calcular_costo` con parámetros opcionales `impuesto` y `descuento`. | `servicio.py` |
| Método estático | `_validar_rango_duracion` no usa `self` y lo reutilizan las tres hijas. | `servicio.py` |
| Constantes de clase | `DURACION_MINIMA`, `DURACION_MAXIMA` y `MULTIPLICADORES`. | las hijas |
| Reutilización de código | `super().__init__`, `super().describir()` y los validadores del módulo de excepciones. | todos |
| Encadenamiento `raise ... from` | Los `ValueError` de los validadores se traducen a `ServicioInvalidoError` sin perder la causa. | todos |

## Pruebas relacionadas

En `tests/test_basico.py` (nombres sugeridos, ajustar a los reales): `test_servicio_abstracto_no_se_instancia`, `test_costo_sala_con_descuento_e_impuesto`, `test_costo_equipo_incluye_deposito`, `test_costo_asesoria_segun_nivel`, `test_nivel_se_normaliza_a_minusculas`, `test_duracion_fuera_de_rango`, `test_descuento_fuera_de_rango`, `test_impuesto_negativo_o_nan` y `test_datos_de_servicio_invalidos`.
