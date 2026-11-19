# Módulo de Gestión (Rol 1)
 
**Responsable:** Edwin Usgame Alarcón
**Rama:** 'feature/integracion'
 
## Descripción
Este módulo contiene la clase principal `GestorFJ` que se encarga de administrar y procesar las operaciones del sistema (como el manejo de reservas, servicios y validación de reglas de negocio). Coordinando la lógica central del programa y conectando las excepciones con el sistema de registros.
 
## Clases y métodos públicos
- `GestorFJ`
  - `procesar_operacion(...)`: Este es el método encargado de recibir los datos y validar que todo esté correcto según las reglas del sistema y registrar el resultado de la operación.
 
## Excepciones que lanza
- es el encargado de capturar y manejar las excepciones personalizadas del sistema (códigos `FJ-101` a `FJ-107`) para evitar que el programa se caiga de forma inesperada.
 
## Ejemplo de uso
```python
# Así se inicializa y se usa el gestor principal
gestor = GestorFJ()
resultado = gestor.procesar_operacion(...)