# Diagrama de clases - Software FJ

Este diagrama está escrito en Mermaid: GitHub lo dibuja automáticamente al abrir este archivo.
Para exportarlo como imagen o PDF (el informe final lo pide), se puede pegar el bloque en
<https://mermaid.live> y descargar el resultado.

## 1. Modelo de dominio

```mermaid
classDiagram
    direction TB

    class EntidadBase {
        <<abstract>>
        -identificador
        +identificador() str
        +describir()* str
    }

    class Cliente {
        -nombre
        -correo
        -telefono
        +describir() str
    }

    class Servicio {
        <<abstract>>
        -nombre
        -disponible
        +calcular_costo(duracion, impuesto, descuento) float
        #_costo_base(duracion)* float
        +validar_parametros(duracion)*
        #_validar_rango_duracion(duracion, minimo, maximo, unidad)$
        +describir() str
    }

    class ReservaSala {
        -capacidad
        -tarifa_hora
        DURACION_MINIMA = 1
        DURACION_MAXIMA = 12
    }

    class AlquilerEquipo {
        -tarifa_dia
        -deposito
        DURACION_MINIMA = 1
        DURACION_MAXIMA = 30
    }

    class AsesoriaEspecializada {
        -tarifa_hora_base
        -nivel
        MULTIPLICADORES
        DURACION_MINIMA = 1
        DURACION_MAXIMA = 8
    }

    class EstadoReserva {
        <<enumeration>>
        PENDIENTE
        CONFIRMADA
        PROCESADA
        CANCELADA
    }

    class Reserva {
        -cliente
        -servicio
        -duracion
        -estado
        -costo_total
        -intentos_proceso
        +confirmar()
        +cancelar()
        +procesar(impuesto, descuento) float
        +describir() str
    }

    class GestorFJ {
        -clientes
        -servicios
        -reservas
        +registrar_cliente(...) Cliente
        +registrar_servicio(clase, ...) Servicio
        +crear_reserva(id_cliente, id_servicio, duracion, id_reserva) Reserva
        +confirmar_reserva(id) bool
        +cancelar_reserva(id) bool
        +procesar_reserva(id, impuesto, descuento) bool
        +resumen() dict
    }

    EntidadBase <|-- Cliente
    EntidadBase <|-- Servicio
    EntidadBase <|-- Reserva
    Servicio <|-- ReservaSala
    Servicio <|-- AlquilerEquipo
    Servicio <|-- AsesoriaEspecializada
    Reserva --> Cliente : un cliente
    Reserva --> Servicio : un servicio
    Reserva --> EstadoReserva : estado
    GestorFJ o-- Cliente : administra
    GestorFJ o-- Servicio : administra
    GestorFJ o-- Reserva : administra
```

## 2. Jerarquía de excepciones

```mermaid
classDiagram
    direction TB
    Exception <|-- ErrorSoftwareFJ
    ValueError <|-- ParametroFaltanteError
    ErrorSoftwareFJ <|-- ParametroFaltanteError
    ErrorSoftwareFJ <|-- ClienteInvalidoError
    ErrorSoftwareFJ <|-- ServicioInvalidoError
    ErrorSoftwareFJ <|-- ServicioNoDisponibleError
    ErrorSoftwareFJ <|-- ReservaInvalidaError
    ErrorSoftwareFJ <|-- OperacionNoPermitidaError
    ErrorSoftwareFJ <|-- CalculoInconsistenteError
    ErrorSoftwareFJ <|-- ErrorGestion

    class ErrorSoftwareFJ { codigo = FJ-100 }
    class ClienteInvalidoError { codigo = FJ-101 }
    class ServicioInvalidoError { codigo = FJ-102 }
    class ServicioNoDisponibleError { codigo = FJ-103 }
    class ReservaInvalidaError { codigo = FJ-104 }
    class OperacionNoPermitidaError { codigo = FJ-105 }
    class ParametroFaltanteError { codigo = FJ-106 }
    class CalculoInconsistenteError { codigo = FJ-107 }
```

## 3. Estados de una reserva

```mermaid
stateDiagram-v2
    [*] --> PENDIENTE
    PENDIENTE --> CONFIRMADA : confirmar()
    PENDIENTE --> CANCELADA : cancelar()
    CONFIRMADA --> PROCESADA : procesar()
    CONFIRMADA --> CANCELADA : cancelar()
    PROCESADA --> [*]
    CANCELADA --> [*]
```
