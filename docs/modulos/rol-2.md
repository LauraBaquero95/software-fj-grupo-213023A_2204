# Módulo de excepciones, validaciones y registro de eventos (Rol 2)

**Responsable:** Laura Catalina Baquero Rodríguez · **Rama:** feature/excepciones-logs

**Archivos del módulo:**
`src/excepciones/errores.py`, `src/excepciones/__init__.py`,
`src/utilidades/validadores.py`, `src/utilidades/logger.py`, `src/utilidades/__init__.py`

## ¿Qué hace?

Es la base sobre la que se apoyan todos los demás módulos del sistema. Define los tipos de
error propios de Software FJ, cada uno con un código `FJ-xxx` y un formato uniforme
`[CÓDIGO] mensaje`; ofrece funciones reutilizables que revisan que un dato sea correcto antes
de aceptarlo; y configura el registro de eventos y errores en `logs/sistema.log`, incluyendo la
causa original de cada error.

## Clases y métodos públicos

### `src/excepciones/errores.py`

- `ErrorSoftwareFJ(Exception)`: clase base de todas las excepciones del sistema. Con una clase
  común, un solo `except ErrorSoftwareFJ` atrapa cualquier error propio.
  - `codigo`: atributo de clase con el código del error (`FJ-100` por defecto).
  - `__init__(mensaje="")`: guarda el mensaje.
  - `__str__()`: devuelve el texto con el formato `[CÓDIGO] mensaje`.
- Clases hijas, que solo sobrescriben `codigo`:

| Código | Clase | Se usa cuando |
|---|---|---|
| FJ-100 | `ErrorGestion` | El gestor no pudo completar una operación (encadena la causa). |
| FJ-101 | `ClienteInvalidoError` | Dato de cliente incorrecto, cliente inexistente o duplicado. |
| FJ-102 | `ServicioInvalidoError` | Dato de servicio incorrecto (tarifa, nivel, disponibilidad). |
| FJ-103 | `ServicioNoDisponibleError` | El servicio no existe, está repetido o no está disponible. |
| FJ-104 | `ReservaInvalidaError` | Dato de reserva incorrecto o duración fuera de rango. |
| FJ-105 | `OperacionNoPermitidaError` | Cambio de estado no permitido (por ejemplo, cancelar una reserva procesada). |
| FJ-106 | `ParametroFaltanteError` | Falta un dato (`None`, vacío o solo espacios). |
| FJ-107 | `CalculoInconsistenteError` | Error de cálculo (descuento fuera de rango, impuesto negativo). |

### `src/utilidades/validadores.py`

- `validar_texto(valor, campo, longitud_minima, longitud_maxima)`: comprueba que sea texto y
  que su longitud esté en el rango. Devuelve el texto sin espacios sobrantes.
- `validar_nombre_persona(valor, campo)`: nombre con solo letras, espacios, apóstrofos y
  guiones. Colapsa los espacios repetidos y devuelve el nombre limpio.
- `validar_correo(valor, campo)`: formato `usuario@dominio.extension`. Devuelve el correo en
  minúsculas.
- `validar_telefono(valor, campo)`: de 7 a 15 dígitos con un `+` inicial opcional. Acepta
  espacios, guiones y paréntesis y los elimina; devuelve solo `+` y dígitos.
- `validar_numero_positivo(valor, campo, permitir_cero, solo_entero)`: número `int` o
  `float`, finito y mayor que cero (o con cero permitido). Rechaza `bool`, `nan` e infinito.

### `src/utilidades/logger.py`

- `obtener_logger()`: devuelve el logger `SoftwareFJ`, listo para usar. Crea la carpeta
  `logs/` si no existe, escribe en `logs/sistema.log` en modo *append* y evita manejadores
  duplicados.
- `describir_error(error)`: arma el texto de un error incluyendo toda su cadena de causas
  (`__cause__`).
- `registrar_evento(mensaje)`: escribe una línea de nivel INFO.
- `registrar_error(mensaje, error=None)`: escribe una línea de nivel ERROR; si se pasa la
  excepción, añade su cadena de causas.
- `registrar_advertencia(mensaje)`: escribe una línea de nivel WARNING.

Cada línea del log tiene el formato `fecha y hora | nivel | módulo | mensaje`.

## Excepciones que lanza

Convención del proyecto (documentada en `validadores.py`):

- **Dato ausente** (`None`, texto vacío o solo espacios): lanza `ParametroFaltanteError`
  (**FJ-106**).
- **Dato presente pero incorrecto** (formato, rango o tipo equivocado): lanza `ValueError`.
  Las clases que invocan al validador (`Cliente`, `Servicio`, etc.) capturan ese `ValueError` y
  lo traducen a su excepción propia con `raise ... from error`.

`ParametroFaltanteError` hereda también de `ValueError` a propósito, para que esas clases
traduzcan también los datos ausentes y conserven el error original en `__cause__`.

Los códigos FJ-101 a FJ-105 y FJ-107 los lanzan los demás módulos (clientes, servicios,
reservas y gestor); este módulo solo los define.

## Ejemplo de uso

```python
from src.excepciones import ClienteInvalidoError
from src.utilidades.validadores import validar_nombre_persona, validar_correo, validar_telefono
from src.utilidades.logger import describir_error, registrar_error

print(ClienteInvalidoError("prueba"))
# [FJ-101] prueba

print(validar_nombre_persona("  María   José "))   # María José
print(validar_correo("Ana@Correo.COM"))             # ana@correo.com
print(validar_telefono("+57 (300) 123-4567"))       # +573001234567
```

Un dato incorrecto lanza `ValueError`, y uno ausente lanza `ParametroFaltanteError`:

```python
validar_correo("ana@correo")
# ValueError: El correo 'ana@correo' no tiene un formato válido.

validar_texto(None, "nombre")
# ParametroFaltanteError: [FJ-106] El campo 'nombre' es obligatorio.
```

Encadenamiento de excepciones y registro en el log:

```python
try:
    try:
        int("abc")
    except ValueError as causa:
        raise ClienteInvalidoError("Dato inválido") from causa
except ClienteInvalidoError as error:
    print(describir_error(error))
    registrar_error("Falló la operación", error)
```

Salida en pantalla:

```
ClienteInvalidoError: [FJ-101] Dato inválido <- causa: ValueError: invalid literal for int() with base 10: 'abc'
```

Línea que queda en `logs/sistema.log` (el tercer campo es el módulo que llamó a la función; aquí, el archivo `ejemplo.py`):

```
2026-11-18 05:52:55 | ERROR | ejemplo | Falló la operación | ClienteInvalidoError: [FJ-101] Dato inválido <- causa: ValueError: invalid literal for int() with base 10: 'abc'
```

## Conceptos de POO aplicados

| Concepto | Dónde se ve | Archivo |
|---|---|---|
| **Herencia** | Todas las excepciones heredan de `ErrorSoftwareFJ`, que a su vez hereda de `Exception`. | `errores.py` |
| **Herencia múltiple** | `ParametroFaltanteError(ErrorSoftwareFJ, ValueError)`. | `errores.py` |
| **Polimorfismo** | Todas usan el mismo `__str__` heredado, pero cada una sobrescribe `codigo`; el formato `[CÓDIGO] mensaje` sale distinto según la clase. | `errores.py` |
| **Excepciones personalizadas** | Una por cada tipo de problema del negocio, con código propio. | `errores.py` |
| **Encadenamiento `raise ... from`** | `describir_error` recorre `__cause__` para mostrar la cadena completa. | `logger.py` |
| **Reutilización de código** | Las validaciones se escriben una sola vez y las usan `Cliente`, `Servicio` y sus hijas. | `validadores.py` |
| **Encapsulación del registro** | Un único punto (`obtener_logger`) configura el log y evita manejadores duplicados. | `logger.py` |

## Pruebas relacionadas

En `tests/test_basico.py`: `test_formato_y_codigo_de_las_excepciones`,
`test_texto_vacio_es_parametro_faltante`, `test_nombre_se_limpia_y_se_valida`,
`test_correo`, `test_telefono`, `test_numero_positivo` y
`test_describir_error_incluye_causa_original`.
