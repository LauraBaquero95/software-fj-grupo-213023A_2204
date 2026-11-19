# Módulo de clientes (Rol 3)

**Responsable:** Cristian Andrés Moreno · **Rama:** feature/clientes

**Archivos del módulo:** `src/modelos/entidad_base.py`, `src/modelos/cliente.py`, `docs/modulos/rol-3.md`

## ¿Qué hace?

Define la base común de las entidades del sistema y a la persona que hace las reservas. La clase abstracta `EntidadBase` guarda y valida el identificador (que no se puede cambiar) y obliga a cada clase hija a implementar `describir()`. `Cliente` hereda de ella y agrega nombre, correo y teléfono, que se validan cada vez que se asignan. Los errores de los validadores se traducen a una excepción propia con `raise ... from error`, para no perder la causa original.

## Clases y métodos públicos

### `src/modelos/entidad_base.py`

- **`EntidadBase(ABC)`**: clase abstracta de la que heredan `Cliente`, `Servicio` y `Reserva`. No se instancia directamente.
  - `__init__(identificador)`: valida el identificador (texto de 3 a 30 caracteres) y lo guarda en un atributo privado.
  - `identificador`: propiedad de solo lectura (tiene getter pero no setter).
  - `describir()`: método abstracto. Cada clase hija debe implementarlo y devolver un texto con su descripción.
  - `__str__()`: devuelve `describir()`, así `print(objeto)` usa la descripción de cada clase.

### `src/modelos/cliente.py`

- **`Cliente(EntidadBase)`**: persona que hace las reservas. Sus datos son privados y se validan en cada asignación.
  - `__init__(identificador, nombre, correo, telefono)`: llama al constructor del padre y asigna los demás datos mediante los setters.
  - `nombre`: propiedad con setter. Valida con `validar_nombre_persona`.
  - `correo`: propiedad con setter. Valida con `validar_correo`.
  - `telefono`: propiedad con setter. Valida con `validar_telefono`.
  - `describir()`: devuelve un texto con el id, el nombre, el correo y el teléfono. Implementa el método abstracto del padre.

## Excepciones que lanza

| Código | Excepción | Cuándo |
|---|---|---|
| FJ-xxx | `ClienteInvalidoError` | Identificador, nombre, correo o teléfono inválidos, ya sea al crear el cliente o al modificar sus datos con los setters. |

Los validadores de `src/utilidades/validadores.py` lanzan `ValueError` (o una subclase, como `ParametroFaltanteError` cuando el dato viene vacío). `Cliente` los captura y los convierte en `ClienteInvalidoError` con `raise ... from error`, de modo que la causa original queda en `__cause__`.

## Ejemplo de uso

```python
from src.modelos.cliente import Cliente
from src.excepciones.errores import ClienteInvalidoError

cliente = Cliente("C-001", "Ana Pérez", "ana.perez@correo.com", "3001234567")

print(cliente)
# Cliente C-001: Ana Pérez <ana.perez@correo.com> Tel. 3001234567

cliente.correo = "ana.nueva@correo.com"   # el setter valida el nuevo correo

try:
    cliente.correo = "correo-sin-arroba"
except ClienteInvalidoError as error:
    print(type(error).__name__)           # ClienteInvalidoError
    print(error.__cause__)                # el ValueError original del validador
```

Intentar crear una `EntidadBase` directamente falla porque es abstracta:

```python
from src.modelos.entidad_base import EntidadBase

EntidadBase("X-001")
# TypeError: Can't instantiate abstract class EntidadBase ...
```

## Conceptos de POO aplicados

| Concepto | Dónde se ve | Archivo |
|---|---|---|
| Abstracción / clase abstracta | `EntidadBase(ABC)` con `@abstractmethod` en `describir()`; no se puede instanciar. | `entidad_base.py` |
| Herencia | `Cliente` hereda de `EntidadBase` y reutiliza su constructor con `super().__init__`. | `cliente.py` |
| Polimorfismo | `describir()` se declara en el padre y cada hija lo implementa a su manera; `__str__` lo usa sin saber qué clase es. | ambos |
| Encapsulación | Atributos privados (`__identificador`, `__nombre`, `__correo`, `__telefono`) accesibles solo mediante propiedades. | ambos |
| Propiedades con validación | Los setters de `nombre`, `correo` y `telefono` validan cada asignación, incluso la del constructor. | `cliente.py` |
| Solo lectura | `identificador` solo tiene getter, así que no se puede cambiar después de crear el objeto. | `entidad_base.py` |
| Reutilización de código | Uso de los validadores compartidos (`validar_texto`, `validar_correo`, etc.) en lugar de repetir lógica. | ambos |
| Manejo de excepciones propias | `ValueError` traducido a `ClienteInvalidoError` con `raise ... from error`. | `cliente.py` |
