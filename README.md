# PulseDesk RAD
```
Centro de Control de Eventos en Tiempo Real
```
De un prototipo en timebox a una aplicación de escritorio orientada a eventos: RAD, event loop, patrones y asincronía.

PulseDesk RAD es una aplicación de escritorio desarrollada en Python para demostrar el diseño de un sistema orientado a eventos, capaz de recibir información desde múltiples fuentes, procesarla mediante un EventBus y reflejar su estado en una interfaz gráfica en tiempo real.

El proyecto fue desarrollado como proyecto integrador del Módulo 3 — RAD / Event-Driven Python del Diplomado Certificación Especialista en Desarrollo de Software con Python SSR.

⸻

## Objetivos

PulseDesk busca demostrar:

* Desarrollo rápido mediante iteraciones y timeboxes.
* Arquitectura orientada a eventos.
* Uso de asyncio y event loops.
* Integración de una interfaz gráfica con tareas asíncronas.
* Implementación propia del patrón EventBus / PubSub.
* Uso de referencias débiles para evitar retención permanente de subscribers.
* Separación entre fuentes, dominio y UI.
* Ejecución de operaciones bloqueantes fuera del event loop.
* Pruebas automatizadas y pruebas asíncronas.
* Medición y optimización de rendimiento.
* Cierre limpio de tareas y recursos.

⸻

Arquitectura

La aplicación está organizada en capas para evitar que la interfaz dependa directamente de las fuentes de eventos.
```
                         ┌─────────────────────┐
                         │     PulseDesk UI    │
                         │       PyQt6         │
                         └──────────┬──────────┘
                                    │
                               UiBridge
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     AppState        │
                         └──────────┬──────────┘
                                    │
                                    │
Sources ───────────────► EventBus ◄─┴── Handlers
   │                       │
   │                       │
   ├── Heartbeat           ├── HeartbeatEvent
   ├── Telemetry File      ├── TelemetryEvent
   ├── Alerts API          └── AlertEvent
   └── System Status
```
## Regla principal

La interfaz no consume directamente las fuentes.

Las fuentes publican eventos:
```text
Source
   ↓
EventBus
   ↓
Handler
   ↓
UiBridge
   ↓
Dashboard
```
Esto permite agregar nuevas fuentes sin modificar directamente la interfaz.

⸻

## Estructura del proyecto
```text
PulseDesk/
├── pulsedesk/
│   ├── core/
│   │   ├── event_bus.py
│   │   ├── events.py
│   │   ├── handlers.py
│   │   ├── loop.py
│   │   └── state.py
│   │
│   ├── sources/
│   │   ├── base.py
│   │   ├── telemetry_file.py
│   │   ├── alerts_api.py
│   │   ├── heartbeat.py
│   │   └── system_status.py
│   │
│   ├── ui/
│   │   ├── app.py
│   │   ├── bridge.py
│   │   ├── console.py
│   │   ├── model.py
│   │   ├── run.py
│   │   └── panels/
│   │
│   ├── workers/
│   │   └── executor.py
│   │
│   ├── demo.py
│   └── main.py
│
├── tests/
├── tools/
│   └── profile_run.py
│
├── docs/
│   └── performance_baseline.txt
│
├── data/
│   └── telemetry.txt
│
├── pyproject.toml
├── README.md
└── .gitignore
```
⸻

## Tecnologías

* Python 3.11+
* Python 3.12
* asyncio
* PyQt6
* qasync
* pytest
* pytest-asyncio
* pytest-cov
* cProfile
* pstats
* Black
* Ruff
* Mypy
* Git

⸻

## Fuentes de eventos

PulseDesk utiliza diferentes fuentes para demostrar la arquitectura orientada a eventos.

### Heartbeat

Genera periódicamente eventos que indican que el sistema continúa activo.
```text
HeartbeatSource
      ↓
HeartbeatEvent
```
### Telemetry File

Lee nuevas líneas de un archivo de telemetría y genera eventos únicamente para información nueva.
```text
data/telemetry.txt
        ↓
TelemetryFileSource
        ↓
TelemetryEvent
```
### Alerts API

Simula una fuente externa de alertas.
```text
AlertsApiSource
      ↓
AlertEvent
```
### System Status

Genera periódicamente información sobre el estado del sistema.
```text
SystemStatusSource
        ↓
TelemetryEvent
```
⸻

## EventBus

PulseDesk implementa un EventBus propio.

Sus responsabilidades principales son:

* subscribe()
* unsubscribe()
* publish()
* manejo de errores de handlers
* limpieza de referencias débiles
* consulta de subscribers activos

Los handlers se almacenan mediante weakref, evitando que el EventBus mantenga objetos vivos indefinidamente.

Además, un error producido por un subscriber no detiene la entrega del evento a los demás subscribers.

⸻

## Asincronía

El procesamiento de eventos utiliza asyncio.

Las fuentes se ejecutan como tareas independientes dentro del event loop.
```text
                 asyncio event loop
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      heartbeat     telemetry       alerts
        task          task            task
```
La integración gráfica utiliza qasync, permitiendo coordinar el event loop de Qt con asyncio.

La interfaz permanece responsiva mientras las fuentes continúan generando eventos.

⸻

## Operaciones bloqueantes

Las operaciones potencialmente bloqueantes no deben ejecutarse directamente dentro del event loop.

Para ello PulseDesk incluye:
```bash
pulsedesk/workers/executor.py
```
que utiliza ThreadPoolExecutor.

Esto permite trasladar trabajo bloqueante a un pool de hilos sin bloquear el event loop principal.

⸻

## Estado y comunicación con la UI

El estado de la aplicación se centraliza en AppState.

La comunicación con la interfaz se realiza mediante UiBridge.
```text
Event
  ↓
Handler
  ↓
AppState
  ↓
UiBridge
  ↓
DashboardData
  ↓
PyQt6
```
El bridge utiliza sincronización mediante Lock para proteger las estructuras compartidas.

⸻

## Ejecución

Entorno virtual

Crear el entorno:
```bash
python3.12 -m venv .venv
```
Activarlo:
```bash
source .venv/bin/activate
```
Instalar dependencias:
```bash
pip install -e ".[dev]"
```
Aplicación gráfica
```bash
python -m pulsedesk.ui.run
```
La aplicación muestra:

* estado del sistema
* eventos procesados
* alertas activas
* última fuente
* actividad reciente

### Demo de consola
```bash
python -m pulsedesk.demo
```
Para detenerla:

Ctrl + C

El sistema realiza un cierre controlado de sus fuentes y tareas.

⸻

## Pruebas

Ejecutar todas las pruebas:
```bash
pytest -q
```
Resultado validado:

44 passed

Cobertura
```text
pytest --cov=pulsedesk/core \
       --cov=pulsedesk/sources \
       --cov=pulsedesk/workers \
       --cov-report=term-missing
```
Resultado validado:

TOTAL    278    0    100%

La cobertura del núcleo, fuentes y workers alcanza el 100%.

⸻

## Calidad de código

### Black
```bash
black --check .
```

### Ruff
```bash
ruff check .
```

### Mypy
```bash
mypy pulsedesk
```
El proyecto utiliza Mypy en modo estricto:
```toml
strict = true
```
Las tres herramientas fueron ejecutadas y validadas durante la integración final.

⸻

## Profiling y optimización

PulseDesk incluye un escenario reproducible de profiling:
```bash
python tools/profile_run.py
```
El escenario procesa:

10,000 TelemetryEvent

Baseline
```text
Tiempo total:       0.023307 s
Llamadas totales:   60,420
```
Después de la optimización
```text
Tiempo total:       0.021735 s
Llamadas totales:   50,420
```
Resultado:

Mejora aproximada: 6.74%

La optimización se realizó sobre EventBus.publish() para evitar reconstruir innecesariamente la lista de referencias activas cuando no existen referencias débiles muertas.

La documentación completa se encuentra en:
```bash
docs/performance_baseline.txt
```
⸻

## Cierre limpio

PulseDesk contempla el cierre controlado de:

* tareas asyncio
* fuentes de eventos
* event loop
* executor
* interfaz gráfica

La cancelación de tareas se maneja mediante asyncio.CancelledError.

La aplicación fue validada manualmente verificando que el cierre de la interfaz no produce:

* traceback
* tareas pendientes
* warnings de recursos
* errores de cancelación no controlados

⸻

## Decisiones arquitectónicas

### EventBus

Se utiliza un EventBus propio para desacoplar productores y consumidores.

### PubSub

Las fuentes publican eventos sin conocer quién los consume.

### Weak References

Los subscribers se almacenan mediante referencias débiles para evitar retención innecesaria de objetos.

### Bridge

UiBridge separa los eventos del dominio de la representación utilizada por PyQt6.

### Executor

Las operaciones bloqueantes pueden ejecutarse fuera del event loop mediante un ThreadPoolExecutor.
```text
asyncio + PyQt6
```
qasync permite integrar el event loop de Qt con asyncio.

⸻

## Principios aplicados

Durante el desarrollo se aplicaron los siguientes principios:

* separación de responsabilidades
* bajo acoplamiento
* alta cohesión
* programación orientada a eventos
* asincronía
* testabilidad
* observabilidad
* profiling basado en evidencia
* optimización antes/después
* cierre limpio de recursos

⸻

## Evidencias del proyecto

El repositorio contiene evidencia de:

* planificación RAD
* definición de eventos
* event loop
* interfaz gráfica
* EventBus
* PubSub
* manejo de estado
* concurrencia
* pruebas automatizadas
* cobertura
* profiling
* optimización
* documentación
* integración final

⸻

## Estado del proyecto
```text
PulseDesk RAD — Proyecto integrador
```
Estado:

✓ Arquitectura orientada a eventos
✓ EventBus / PubSub
✓ asyncio
✓ PyQt6 + qasync
✓ Múltiples fuentes de eventos
✓ UI en tiempo real
✓ Concurrencia
✓ Cierre limpio
✓ 44 pruebas
✓ 100% cobertura
✓ Black
✓ Ruff
✓ Mypy
✓ Profiling
✓ Optimización
✓ Documentación

⸻

## Licencia

Este proyecto se desarrolla con fines académicos y demostrativos.