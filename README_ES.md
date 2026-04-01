# Claude Code v2.1.88 — Análisis del Código Fuente

> **Descargo de responsabilidad**: Todo el código fuente de este repositorio es propiedad intelectual de **Anthropic y Claude**. Este repositorio se proporciona estrictamente para investigación técnica, estudio e intercambio educativo entre entusiastas. **El uso comercial está estrictamente prohibido.** Ninguna persona, organización o entidad puede utilizar este contenido para fines comerciales, actividades con fines de lucro, actividades ilegales o cualquier otro escenario no autorizado. Si algún contenido infringe sus derechos legales, propiedad intelectual u otros intereses, contáctenos y lo verificaremos y eliminaremos de inmediato.

> Extraído del paquete npm `@anthropic-ai/claude-code` versión **2.1.88**.
> El paquete publicado incluye un único archivo empaquetado `cli.js` (~12 MB). El directorio `src/` en este repositorio contiene el **código fuente TypeScript sin empaquetar** extraído del archivo tarball de npm.

**Idioma**: [Inglés](README.md) | [Chino](README_CN.md) | [Coreano](README_KR.md) | [Japonés](README_JA.md) | [**Español**](README_ES.md)

---

## Índice

- [Informes de Análisis Profundo (`docs/es/`)](#informes-de-análisis-profundo-docses) — Telemetría, nombres en clave, modo encubierto, control remoto, hoja de ruta futura.
- [Aviso de Módulos Faltantes](#aviso-de-módulos-faltantes-108-módulos) — 108 módulos protegidos por flags de funciones no incluidos en el paquete npm.
- [Resumen de la Arquitectura](#resumen-de-la-arquitectura) — Entrada → Motor de Consultas → Herramientas/Servicios/Estado.
- [Sistema de Herramientas y Permisos](#sistema-de-herramientas-y-arquitectura-de-permisos) — Más de 40 herramientas, flujo de permisos, sub-agentes.
- [Los 12 Mecanismos Progresivos del Arnés](#los-12-mecanismos-progresivos-del-arnés) — Cómo Claude Code añade capas de funciones de producción sobre el bucle del agente.
- [Notas de Construcción](#notas-de-construcción) — Por qué este código fuente no es directamente compilable.

---

## Informes de Análisis Profundo (`docs/es/`)

Informes de análisis del código fuente derivados de la versión v2.1.88 descompilada en español.

```
docs/es/
├── [01-telemetria-y-privacidad.md](docs/es/01-telemetria-y-privacidad.md)          # Telemetría y Privacidad — qué se recopila, por qué no puedes excluirte
├── [02-funciones-ocultas-y-nombres-clave.md](docs/es/02-funciones-ocultas-y-nombres-clave.md)  # Nombres clave (Capybara/Tengu/Numbat), flags de funciones, interno vs externo
├── [03-modo-encubierto.md](docs/es/03-modo-encubierto.md)                # Modo Encubierto — ocultando la autoría de IA en repositorios de código abierto
├── [04-control-remoto-y-interruptores.md](docs/es/04-control-remoto-y-interruptores.md) # Control Remoto — configuraciones gestionadas, killswitches, sobrescrituras de modelos
└── [05-hoja-de-ruta-futura.md](docs/es/05-hoja-de-ruta-futura.md)                # Hoja de Ruta Futura — Numbat, KAIROS, modo de voz, herramientas no lanzadas
```

> Haz clic en cualquier nombre de archivo arriba para saltar al informe completo.

| # | Tema | Hallazgos Clave |
|---|-------|-------------|
| 01 | **Telemetría y Privacidad** | Dos sumideros de análisis (1P → Anthropic, Datadog). Huella digital del entorno, métricas de procesos, hash del repositorio en cada evento. **Sin exclusión expuesta en la UI** para el registro de primera parte. `OTEL_LOG_TOOL_DETAILS=1` permite la captura completa de las entradas de las herramientas. |
| 02 | **Funciones Ocultas y Nombres Clave** | Nombres en clave de animales (Capybara v8, Tengu, Fennec→Opus 4.6, **Numbat** el próximo). Los flags de funciones usan pares de palabras aleatorias (`tengu_frond_boric`) para ocultar su propósito. Los usuarios internos obtienen mejores prompts, agentes de verificación y anclajes de esfuerzo. Comandos ocultos: `/btw`, `/stickers`. |
| 03 | **Modo Encubierto** | Los empleados de Anthropic entran automáticamente en modo encubierto en los repositorios públicos. Se instruye al modelo: *"No reveles tu cobertura"* — eliminar toda atribución de IA, escribir commits "como lo haría un desarrollador humano". **No existe una opción de desactivación forzada.** Plantea preguntas de transparencia para las comunidades de código abierto. |
| 04 | **Control Remoto** | Consulta por hora de `/api/claude_code/settings`. Los cambios peligrosos muestran un diálogo de bloqueo — **rechazar = la aplicación se cierra**. Más de 6 killswitches (omitir permisos, modo rápido, modo de voz, sumidero de análisis). Los flags de GrowthBook pueden cambiar el comportamiento de cualquier usuario sin su consentimiento. |
| 05 | **Hoja de Ruta Futura** | Nombre en clave **Numbat** confirmado. Opus 4.7 / Sonnet 4.8 en desarrollo. **KAIROS** = modo de agente totalmente autónomo con latidos `<tick>`, notificaciones push, suscripciones a PR. Modo de voz (push-to-talk) listo pero protegido por flag. Se encontraron 17 herramientas no lanzadas. |

---

## Aviso de Módulos Faltantes (108 módulos)

> **Este código fuente está incompleto.** 108 módulos referenciados por ramas protegidas por `feature()` **no se incluyen** en el paquete npm.
> Existen solo en el monorepositorio interno de Anthropic y fueron eliminados como código muerto (Dead Code Elimination) en el momento de la compilación.
> **No pueden** recuperarse de `cli.js`, `sdk-tools.d.ts` ni de ningún artefacto publicado.

### Código Interno de Anthropic (~70 módulos, nunca publicados)

Estos módulos no tienen archivos fuente en ninguna parte del paquete npm. Son infraestructura interna de Anthropic.

<details>
<summary>Haz clic para expandir la lista completa</summary>

| Módulo | Propósito | Flag de Función |
|--------|---------|-------------|
| `daemon/main.js` | Supervisor del demonio de fondo | `DAEMON` |
| `daemon/workerRegistry.js` | Registro de trabajadores del demonio | `DAEMON` |
| `proactive/index.js` | Sistema de notificación proactiva | `PROACTIVE` |
| `contextCollapse/index.js` | Servicio de colapso de contexto (experimental) | `CONTEXT_COLLAPSE` |
| `contextCollapse/operations.js` | Operaciones de colapso | `CONTEXT_COLLAPSE` |
| `contextCollapse/persist.js` | Persistencia del colapso | `CONTEXT_COLLAPSE` |
| `skillSearch/featureCheck.js` | Verificación de función de habilidad remota | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/remoteSkillLoader.js` | Cargador de habilidades remotas | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/remoteSkillState.js` | Estado de habilidad remota | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/telemetry.js` | Telemetría de búsqueda de habilidades | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/localSearch.js` | Búsqueda local de habilidades | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/prefetch.js` | Precarga de habilidades | `EXPERIMENTAL_SKILL_SEARCH` |
| `coordinator/workerAgent.js` | Trabajador coordinador multi-agente | `COORDINATOR_MODE` |
| `bridge/peerSessions.js` | Gestión de sesiones de pares del puente | `BRIDGE_MODE` |
| `assistant/index.js` | Modo asistente Kairos | `KAIROS` |
| `assistant/AssistantSessionChooser.js` | Selector de sesión de asistente | `KAIROS` |
| `compact/reactiveCompact.js` | Compactación de contexto reactivo | `CACHED_MICROCOMPACT` |
| `compact/snipCompact.js` | Compactación basada en recortes | `HISTORY_SNIP` |
| `compact/snipProjection.js` | Proyección de recortes | `HISTORY_SNIP` |
| `compact/cachedMCConfig.js` | Configuración de micro-compactación en caché | `CACHED_MICROCOMPACT` |
| `sessionTranscript/sessionTranscript.js` | Servicio de transcripción de sesión | `TRANSCRIPT_CLASSIFIER` |
| `commands/agents-platform/index.js` | Plataforma de agentes internos | `ant` (interno) |
| `commands/assistant/index.js` | Comando de asistente | `KAIROS` |
| `commands/buddy/index.js` | Notificaciones del sistema Buddy | `BUDDY` |
| `commands/fork/index.js` | Comando de sub-agente Fork | `FORK_SUBAGENT` |
| `commands/peers/index.js` | Comandos multi-pares | `BRIDGE_MODE` |
| `commands/proactive.js` | Comando proactivo | `PROACTIVE` |
| `commands/remoteControlServer/index.js` | Servidor de control remoto | `DAEMON` + `BRIDGE_MODE` |
| `commands/subscribe-pr.js` | Suscripción a PR de GitHub | `KAIROS_GITHUB_WEBHOOKS` |
| `commands/torch.js` | Herramienta de depuración interna | `TORCH` |
| `commands/workflows/index.js` | Comandos de flujo de trabajo | `WORKFLOW_SCRIPTS` |
| `jobs/classifier.js` | Clasificador de trabajos interno | `TEMPLATES` |
| `memdir/memoryShapeTelemetry.js` | Telemetría de forma de memoria | `MEMORY_SHAPE_TELEMETRY` |
| `services/sessionTranscript/sessionTranscript.js` | Transcripción de sesión | `TRANSCRIPT_CLASSIFIER` |
| `tasks/LocalWorkflowTask/LocalWorkflowTask.js` | Tarea de flujo de trabajo local | `WORKFLOW_SCRIPTS` |
| `protectedNamespace.js` | Guardia de espacio de nombres interno | `ant` (interno) |
| `protectedNamespace.js` (envUtils) | Tiempo de ejecución de espacio de nombres protegido | `ant` (interno) |
| `coreTypes.generated.js` | Tipos principales generados | `ant` (interno) |
| `devtools.js` | Herramientas de desarrollo internas | `ant` (interno) |
| `attributionHooks.js` | Ganchos de atribución internos | `COMMIT_ATTRIBUTION` |
| `systemThemeWatcher.js` | Observador del tema del sistema | `AUTO_THEME` |
| `udsClient.js` / `udsMessaging.js` | Cliente de mensajería UDS | `UDS_INBOX` |

</details>

### Herramientas Protegidas por Flags de Función (~20 módulos, eliminados del paquete)

Estas herramientas tienen firmas de tipo en `sdk-tools.d.ts` pero sus implementaciones fueron eliminadas en el momento de la compilación.

<details>
<summary>Haz clic para expandir la lista completa</summary>

| Herramienta | Propósito | Flag de Función |
|------|---------|-------------|
| `REPLTool` | REPL interactivo (sandbox de VM) | `ant` (interno) |
| `SnipTool` | Recorte de contexto | `HISTORY_SNIP` |
| `SleepTool` | Sueño/retraso en el bucle del agente | `PROACTIVE` / `KAIROS` |
| `MonitorTool` | Monitoreo de MCP | `MONITOR_TOOL` |
| `OverflowTestTool` | Pruebas de desbordamiento | `OVERFLOW_TEST_TOOL` |
| `WorkflowTool` | Ejecución de flujos de trabajo | `WORKFLOW_SCRIPTS` |
| `WebBrowserTool` | Automatización del navegador | `WEB_BROWSER_TOOL` |
| `TerminalCaptureTool` | Captura de terminal | `TERMINAL_PANEL` |
| `TungstenTool` | Monitoreo de rendimiento interno | `ant` (interno) |
| `VerifyPlanExecutionTool` | Verificación de planes | `CLAUDE_CODE_VERIFY_PLAN` |
| `SendUserFileTool` | Enviar archivos a los usuarios | `KAIROS` |
| `SubscribePRTool` | Suscripción a PR de GitHub | `KAIROS_GITHUB_WEBHOOKS` |
| `SuggestBackgroundPRTool` | Sugerir PRs en segundo plano | `KAIROS` |
| `PushNotificationTool` | Notificaciones push | `KAIROS` |
| `CtxInspectTool` | Inspección de contexto | `CONTEXT_COLLAPSE` |
| `ListPeersTool` | Listar pares activos | `UDS_INBOX` |
| `DiscoverSkillsTool` | Descubrimiento de habilidades | `EXPERIMENTAL_SKILL_SEARCH` |

</details>

### Activos de Texto/Prompts (~6 archivos)

Estos son plantillas de prompts y documentación interna, nunca publicados.

<details>
<summary>Haz clic para expandir</summary>

| Archivo | Propósito |
|------|---------|
| `yolo-classifier-prompts/auto_mode_system_prompt.txt` | Prompt del sistema del modo automático para el clasificador |
| `yolo-classifier-prompts/permissions_anthropic.txt` | Prompt de permiso interno de Anthropic |
| `yolo-classifier-prompts/permissions_external.txt` | Prompt de permiso de usuario externo |
| `verify/SKILL.md` | Documentación de la habilidad de verificación |
| `verify/examples/cli.md` | Ejemplos de verificación de CLI |
| `verify/examples/server.md` | Ejemplos de verificación de servidor |

</details>

### Por qué faltan

```
  Monorepositorio Interno de Anthropic       Paquete npm Publicado
  ──────────────────────────               ─────────────────────
  feature('DAEMON') → true    ──build──→   feature('DAEMON') → false
  ↓                                         ↓
  daemon/main.js  ← INCLUIDO    ──bundle─→  daemon/main.js  ← ELIMINADO (DCE)
  tools/REPLTool  ← INCLUIDO    ──bundle─→  tools/REPLTool  ← ELIMINADO (DCE)
  proactive/      ← INCLUIDO    ──bundle─→  (referenciado pero ausente de src/)
```

`feature()` de Bun es un **intrínseco de tiempo de compilación**:

- Devuelve `true` en la construcción interna de Anthropic → el código se mantiene en el paquete.
- Devuelve `false` en la construcción publicada → el código se elimina como código muerto (DCE).
- Los 108 módulos simplemente no existen en ninguna parte del artefacto publicado.

---

## Derechos de Autor y Descargo de Responsabilidad

```
Copyright (c) Anthropic. Todos los derechos reservados.

Todo el código fuente de este repositorio es propiedad intelectual de Anthropic y Claude.
Este repositorio se proporciona estrictamente para fines de investigación técnica y educativos.
El uso comercial está estrictamente prohibido.

Si usted es el propietario de los derechos de autor y cree que este repositorio infringe sus derechos,
comuníquese con el propietario del repositorio para su eliminación inmediata.
```

---

## Estadísticas

| Ítem | Cantidad |
|------|-------|
| Archivos fuente (.ts/.tsx) | ~1.884 |
| Líneas de código | ~512.664 |
| Archivo individual más grande | `query.ts` (~785 KB) |
| Herramientas integradas | ~40+ |
| Comandos de barra diagonal (slash commands) | ~80+ |
| Dependencias (node_modules) | ~192 paquetes |
| Tiempo de ejecución | Bun (compilado a un paquete Node.js >= 18) |

---

## El Patrón de Agente

```
                     EL BUCLE CENTRAL
                     ================

    Usuario --> mensajes[] --> API de Claude --> respuesta
                                           |
                                ¿stop_reason == "tool_use"?
                               /                          \
                              sí                           no
                               |                             |
                         ejecutar herramientas          devolver texto
                         añadir tool_result
                         volver al bucle -----------> mensajes[]


    Ese es el bucle de agente mínimo. Claude Code envuelve este bucle
    con un arnés de grado de producción: permisos, streaming,
    concurrencia, compactación, sub-agentes, persistencia y MCP.
```

---

## Referencia de Directorios

```
src/
├── main.tsx                 # Bootstrap del REPL, 4.683 líneas
├── QueryEngine.ts           # Motor del ciclo de vida de consulta SDK/sin cabeza
├── query.ts                 # Bucle principal del agente (785 KB, el archivo más grande)
├── Tool.ts                  # Interfaz de herramienta + fábrica buildTool
├── Task.ts                  # Tipos de tareas, IDs, base de estado
├── tools.ts                 # Registro de herramientas, ajustes preestablecidos, filtrado
├── commands.ts              # Definiciones de comandos de barra diagonal
├── context.ts               # Contexto de entrada del usuario
├── cost-tracker.ts          # Acumulación de costos de API
├── setup.ts                 # Flujo de configuración de la primera ejecución
│
├── bridge/                  # Claude Desktop / puente remoto
│   ├── bridgeMain.ts        #   Gestor del ciclo de vida de la sesión
│   ├── bridgeApi.ts         #   Cliente HTTP
│   ├── bridgeConfig.ts      #   Configuración de la conexión
│   ├── bridgeMessaging.ts   #   Relé de mensajes
│   ├── sessionRunner.ts     #   Generación de procesos
│   ├── jwtUtils.ts          #   Utilidades JWT
│   ├── workSecret.ts        #   Tokens de autenticación
│   └── capacityWake.ts      #   Activación basada en la capacidad
│
├── cli/                     # Infraestructura de CLI
│   ├── handlers/            #   Manejadores de comandos
│   └── transports/          #   Transportes de E/S (stdio, estructurado)
│
├── commands/                # ~80 comandos de barra diagonal
│   ├── agents/              #   Gestión de agentes
│   ├── compact/             #   Compactación de contexto
│   ├── config/              #   Gestión de configuraciones
│   ├── help/                #   Visualización de ayuda
│   ├── login/               #   Autenticación
│   ├── mcp/                 #   Gestión de servidores MCP
│   ├── memory/              #   Sistema de memoria
│   ├── plan/                #   Modo plan
│   ├── resume/              #   Reanudación de sesión
│   ├── review/              #   Revisión de código
│   └── ...                  #   70+ comandos más
│
├── components/              # Interfaz de usuario de terminal React/Ink
│   ├── design-system/       #   Primitivas de UI reutilizables
│   ├── messages/            #   Renderizado de mensajes
│   ├── permissions/         #   Diálogos de permisos
│   ├── PromptInput/         #   Campo de entrada + sugerencias
│   ├── LogoV2/              #   Marca + pantalla de bienvenida
│   ├── Settings/            #   Paneles de configuración
│   ├── Spinner.tsx          #   Indicadores de carga
│   └── ...                  #   40+ grupos de componentes
│
├── entrypoints/             # Puntos de entrada de la aplicación
│   ├── cli.tsx              #   Principal de CLI (versión, ayuda, demonio)
│   ├── sdk/                 #   SDK de agente (tipos, sesiones)
│   └── mcp.ts               #   Entrada del servidor MCP
│
├── hooks/                   # Ganchos de React
│   ├── useCanUseTool.tsx    #   Verificación de permisos
│   ├── useReplBridge.tsx    #   Conexión de puente
│   ├── notifs/              #   Ganchos de notificación
│   └── toolPermission/      #   Manejadores de permisos de herramientas
│
├── services/                # Capa de lógica de negocios
│   ├── api/                 #   Cliente de la API de Claude
│   │   ├── claude.ts        #     Llamadas a la API de streaming
│   │   ├── errors.ts        #     Categorización de errores
│   │   └── withRetry.ts     #     Lógica de reintentos
│   ├── analytics/           #   Telemetría + GrowthBook
│   ├── compact/             #   Compresión de contexto
│   ├── mcp/                 #   Gestión de conexiones MCP
│   ├── tools/               #   Motor de ejecución de herramientas
│   │   ├── StreamingToolExecutor.ts  # Ejecutor de herramientas en paralelo
│   │   └── toolOrchestration.ts      # Orquestación por lotes
│   ├── plugins/             #   Cargador de complementos
│   └── settingsSync/        #   Sincronización de configuraciones entre dispositivos
│
├── state/                   # Estado de la aplicación
│   ├── AppStateStore.ts     #   Definición del almacén
│   └── AppState.tsx         #   Proveedor de React + ganchos
│
├── tasks/                   # Implementaciones de tareas
│   ├── LocalShellTask/      #   Ejecución de comandos Bash
│   ├── LocalAgentTask/      #   Ejecución de sub-agentes
│   ├── RemoteAgentTask/     #   Agente remoto a través de puente
│   ├── InProcessTeammateTask/ # Compañero en el proceso
│   └── DreamTask/           #   Pensamiento de fondo
│
├── tools/                   # 40+ implementaciones de herramientas
│   ├── AgentTool/           #   Generación de sub-agentes + fork
│   ├── BashTool/            #   Ejecución de comandos de shell
│   ├── FileReadTool/        #   Lectura de archivos (PDF, imagen, etc)
│   ├── FileEditTool/        #   Edición mediante reemplazo de cadenas
│   ├── FileWriteTool/       #   Creación completa de archivos
│   ├── GlobTool/            #   Búsqueda de patrones de archivos
│   ├── GrepTool/            #   Búsqueda de contenido (ripgrep)
│   ├── WebFetchTool/        #   Obtención HTTP
│   ├── WebSearchTool/       #   Búsqueda web
│   ├── MCPTool/             #   Envoltorio de herramienta MCP
│   ├── SkillTool/           #   Invocación de habilidades
│   ├── AskUserQuestionTool/ #   Interacción con el usuario
│   └── ...                  #   30+ herramientas más
│
├── types/                   # Definiciones de tipos
│   ├── message.ts           #   Uniones discriminadas de mensajes
│   ├── permissions.ts       #   Tipos de permisos
│   ├── tools.ts             #   Tipos de progreso de herramientas
│   └── ids.ts               #   Tipos de IDs con marca
│
├── utils/                   # Utilidades (directorio más grande)
│   ├── permissions/         #   Motor de reglas de permisos
│   ├── messages/            #   Formateo de mensajes
│   ├── model/               #   Lógica de selección de modelo
│   ├── settings/            #   Gestión de configuraciones
│   ├── sandbox/             #   Adaptador de tiempo de ejecución de sandbox
│   ├── hooks/               #   Ejecución de ganchos
│   ├── memory/              #   Utilidades del sistema de memoria
│   ├── git/                 #   Operaciones de Git
│   ├── github/              #   API de GitHub
│   ├── bash/                #   Ayudantes de ejecución de Bash
│   ├── swarm/               #   Enjambre multi-agente
│   ├── telemetry/           #   Informes de telemetría
│   └── ...                  #   30+ grupos más de utilidades
│
└── vendor/                  # Stubs de código fuente de módulos nativos
    ├── audio-capture-src/   #   Captura de audio
    ├── image-processor-src/ #   Procesamiento de imágenes
    ├── modifiers-napi-src/  #   Modificadores nativos
    └── url-handler-src/     #   Manejo de URLs
```

---

## Resumen de la Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CAPA DE ENTRADA                            │
│  cli.tsx ──> main.tsx ──> REPL.tsx (interactivo)                   │
│                     └──> QueryEngine.ts (sin cabeza/SDK)            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       MOTOR DE CONSULTA                             │
│  submitMessage(prompt) ──> AsyncGenerator<SDKMessage>               │
│    │                                                                │
│    ├── fetchSystemPromptParts()    ──> ensamblar prompt del sistema │
│    ├── processUserInput()          ──> manejar comandos de barra /  │
│    ├── query()                     ──> bucle principal del agente   │
│    │     ├── StreamingToolExecutor ──> ejecución de herramientas en paralelo│
│    │     ├── autoCompact()         ──> compresión de contexto       │
│    │     └── runTools()            ──> orquestación de herramientas │
│    └── yield SDKMessage            ──> stream al consumidor         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
┌──────────────────┐ ┌─────────────────┐ ┌──────────────────┐
│ SISTEMA HERRAM.  │ │CAPA DE SERVICIOS│ │CAPA DE ESTADO    │
│                  │ │                 │ │                  │
│ Interfaz Herram. │ │ api/claude.ts   │ │ Almacén AppState │
│  ├─ call()       │ │  Cliente API    │ │  ├─ permisos     │
│  ├─ validate()   │ │ compact/        │ │  ├─ fileHistory  │
│  ├─ checkPerms() │ │  auto-compact   │ │  ├─ agentes      │
│  ├─ render()     │ │ mcp/            │ │  └─ fastMode     │
│  └─ prompt()     │ │  Protocolo MCP  │ │                  │
│                  │ │ analytics/      │ │ Contexto de React│
│ 40+ Integradas:  │ │  telemetría     │ │  ├─ useAppState  │
│  ├─ BashTool     │ │ tools/          │ │  └─ useSetState  │
│  ├─ FileRead     │ │  ejecutor       │ │                  │
│  ├─ FileEdit     │ │ plugins/        │ └──────────────────┘
│  ├─ Glob/Grep    │ │  cargador       │
│  ├─ AgentTool    │ │ settingsSync/   │
│  ├─ WebFetch     │ │  sinc. dispos.  │
│  └─ MCPTool      │ │ oauth/          │
│                  │ │  flujo auth     │
└──────────────────┘ └─────────────────┘
              │                │
              ▼                ▼
┌──────────────────┐ ┌─────────────────┐
│ SISTEMA TAREAS   │ │ CAPA DE PUENTE  │
│                  │ │                 │
│ Tipos de Tareas: │ │ bridgeMain.ts   │
│  ├─ local_bash   │ │  gestión sesión │
│  ├─ local_agent  │ │ bridgeApi.ts    │
│  ├─ remote_agent │ │  cliente HTTP   │
│  ├─ in_process   │ │ workSecret.ts   │
│  ├─ dream        │ │  tokens auth    │
│  └─ workflow     │ │ sessionRunner   │
│                  │ │  gener. proceso │
│ ID: prefijo+8car │ └─────────────────┘
│  b=bash a=agent  │
│  r=remote t=team │
└──────────────────┘
```

---

## Flujo de Datos: Ciclo de Vida de una Sola Consulta

```
  ENTRADA DEL USUARIO (prompt / comando de barra diagonal)
      │
      ▼
  processUserInput()                ← analizar /comandos, construir UserMessage
      │
      ▼
  fetchSystemPromptParts()          ← herramientas → secciones de prompt, memoria CLAUDE.md
      │
      ▼
  recordTranscript()                ← persistir mensaje del usuario en disco (JSONL)
      │
      ▼
  ┌─→ normalizeMessagesForAPI()     ← limpiar campos solo de UI, compactar si es necesario
  │   │
  │   ▼
  │   API de Claude (streaming)     ← POST /v1/messages con herram. + prompt de sistema
  │   │
  │   ▼
  │   eventos de stream             ← message_start → content_block_delta → message_stop
  │   │
  │   ├─ bloque de texto ──────────→ yield al consumidor (SDK / REPL)
  │   │
  │   └─ ¿bloque tool_use?
  │       │
  │       ▼
  │   StreamingToolExecutor         ← partición: seguro para concurrencia vs serial
  │       │
  │       ▼
  │   canUseTool()                  ← verifica permisos (ganchos + reglas + prompt UI)
  │       │
  │       ├─ DENEGAR ──────────────→ añadir tool_result(error), continuar bucle
  │       │
  │       └─ PERMITIR
  │           │
  │           ▼
  │       tool.call()               ← ejecutar herramienta (Bash, Leer, Editar, etc.)
  │           │
  │           ▼
  │       añadir tool_result        ← push a messages[], recordTranscript()
  │           │
  └─────────┘                      ← volver al bucle de la llamada a la API
      │
      ▼ (stop_reason != "tool_use")
  yield mensaje de resultado       ← texto final, uso, costo, session_id
```

---

## Arquitectura del Sistema de Herramientas

```
                    INTERFAZ DE HERRAMIENTA
                    =======================

    buildTool(definición) ──> Tool<Input, Output, Progress>

    Cada herramienta implementa:
    ┌────────────────────────────────────────────────────────┐
    │  CICLO DE VIDA                                         │
    │  ├── validateInput()      → rechazar entradas malas pronto│
    │  ├── checkPermissions()   → autoriz. esp. de herramienta│
    │  └── call()               → ejecutar y devolver resultado│
    │                                                        │
    │  CAPACIDADES                                           │
    │  ├── isEnabled()          → verificación de flag hito   │
    │  ├── isConcurrencySafe()  → ¿puede correr en paralelo? │
    │  ├── isReadOnly()         → ¿sin efectos secundarios?   │
    │  ├── isDestructive()      → ¿operaciones irreversibles? │
    │  └── interruptBehavior()  → ¿cancelar o bloquear usuario?│
    │                                                        │
    │  RENDERIZADO (React/Ink)                               │
    │  ├── renderToolUseMessage()     → visualización entrada│
    │  ├── renderToolResultMessage()  → visualización salida │
    │  ├── renderToolUseProgressMessage() → spinner/estado   │
    │  └── renderGroupedToolUse()     → grupos de herram. par.│
    │                                                        │
    │  ORIENTADO A IA                                        │
    │  ├── prompt()             → desc. herramienta para LLM │
    │  ├── description()        → descripción dinámica       │
    │  └── mapToolResultToAPI() → formato resp. para API     │
    └────────────────────────────────────────────────────────┘
```

### Inventario Completo de Herramientas

```
    OPERACIONES ARCHIVOS     BÚSQUEDA Y DESCUBRIMIENTO   EJECUCIÓN
    ═════════════════        ══════════════════════     ══════════
    FileReadTool             GlobTool                  BashTool
    FileEditTool             GrepTool                  PowerShellTool
    FileWriteTool            ToolSearchTool
    NotebookEditTool                                   INTERACCIÓN
                                                       ═══════════
    WEB Y RED               AGENTE / TAREA             AskUserQuestionTool
    ════════════════        ══════════════════        BriefTool
    WebFetchTool             AgentTool
    WebSearchTool            SendMessageTool           PLANIF. Y FLUJO
                             TeamCreateTool            ════════════════════
    PROTOCOLO MCP            TeamDeleteTool            EnterPlanModeTool
    ══════════════           TaskCreateTool            ExitPlanModeTool
    MCPTool                  TaskGetTool               EnterWorktreeTool
    ListMcpResourcesTool     TaskUpdateTool            ExitWorktreeTool
    ReadMcpResourceTool      TaskListTool              TodoWriteTool
                             TaskStopTool
                             TaskOutputTool            SISTEMA
                                                       ════════
                             HABILID. Y EXTENSIONES    ConfigTool
                             ═════════════════════     SkillTool
                             SkillTool                 ScheduleCronTool
                             LSPTool                   SleepTool
                                                       TungstenTool
```

---

## Sistema de Permisos

```
    SOLICITUD DE LLAMADA A HERRAMIENTA
          │
          ▼
    ┌─ validateInput() ──────────────────────────────────┐
    │  rechazar entradas inválidas antes de verificación │
    └────────────────────┬───────────────────────────────┘
                         │
                         ▼
    ┌─ Ganchos PreToolUse ───────────────────────────────┐
    │  comandos shell de usuario (hooks en settings.json)│
    │  puede: aprobar, denegar o modificar la entrada    │
    └────────────────────┬───────────────────────────────┘
                         │
                         ▼
    ┌─ Reglas de Permisos ───────────────────────────────┐
    │  alwaysAllowRules: coincide herram./patrón → auto  │
    │  alwaysDenyRules:  coincide herram./patrón → deneg.│
    │  alwaysAskRules:   coincide herram./patrón → pedir │
    │  Fuentes: settings, args CLI, decisiones sesión    │
    └────────────────────┬───────────────────────────────┘
                         │
                  ¿sin coincidencia?
                         │
                         ▼
    ┌─ Prompt Interactivo ───────────────────────────────┐
    │  Usuario ve nombre de herramienta + entrada        │
    │  Opciones: Permitir una vez / Siempre / Denegar    │
    └────────────────────┬───────────────────────────────┘
                         │
                         ▼
    ┌─ checkPermissions() ───────────────────────────────┐
    │  Lógica específica (ej. sandboxing de rutas)       │
    └────────────────────┬───────────────────────────────┘
                         │
                    APROBADO → tool.call()
```

---

## Arquitectura de Sub-Agentes y Multi-Agente

```
                        AGENTE PRINCIPAL
                        ================
                             │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────────┐
     │ AGENTE FORK  │ │ AGENTE   │ │ COMPAÑERO EN │
     │              │ │ REMOTO   │ │ EL PROCESO   │
     │ Proceso hijo │ │ Sesión en │ │ Mismo proceso│
     │ Caché compart│ │ el puente │ │ Contexto asín│
     │ Msgs[] nuevos│ │ Aislado   │ │ Estado compat│
     └──────────────┘ └──────────┘ └──────────────┘

    MODOS DE GENERACIÓN (SPAWN):
    ├─ default    → en el proceso, conversación compartida.
    ├─ fork       → proceso hijo, messages[] nuevos, caché de archivos compartida.
    ├─ worktree   → worktree de git aislado + fork.
    └─ remote     → puente a Claude Code Remote / contenedor.

    COMUNICACIÓN:
    ├─ SendMessageTool     → mensajes de agente a agente.
    ├─ TaskCreate/Update   → tablero de tareas compartido.
    └─ TeamCreate/Delete   → gestión del ciclo de vida del equipo.

    MODO ENJAMBRE (SWARM) (protegido por flag):
    ┌──────────────────────────────────────────────┐
    │  Agente Líder                                │
    │    ├── Compañero A ──> reclama Tarea 1       │
    │    ├── Compañero B ──> reclama Tarea 2       │
    │    └── Compañero C ──> reclama Tarea 3       │
    │                                              │
    │  Compartido: tablero tareas, buzón mensajes  │
    │  Aislado: messages[], caché archivos, cwd    │
    └──────────────────────────────────────────────┘
```

---

## Gestión de Contexto (Sistema de Compactación)

```
    PRESUPUESTO VENTANA DE CONTEXTO
    ═══════════════════════════════

    ┌─────────────────────────────────────────────────────┐
    │  Prompt de Sistema (herram., permisos, CLAUDE.md)   │
    │  ══════════════════════════════════════════════      │
    │                                                     │
    │  Historial de Conversación                          │
    │  ┌─────────────────────────────────────────────┐    │
    │  │ [resumen compactado de msjs antiguos]        │    │
    │  │ ═══════════════════════════════════════════  │    │
    │  │ [marcador compact_boundary]                  │    │
    │  │ ─────────────────────────────────────────── │    │
    │  │ [mensajes recientes — fidelidad completa]    │    │
    │  │ usuario → asistente → tool_use → tool_result│    │
    │  └─────────────────────────────────────────────┘    │
    │                                                     │
    │  Turno actual (usuario + respuesta asistente)       │
    └─────────────────────────────────────────────────────┘

    TRES ESTRATEGIAS DE COMPRESIÓN:
    ├─ autoCompact     → se dispara cuando el conteo de tokens excede el umbral.
    │                     Resume mensajes antiguos mediante una llamada compact API.
    ├─ snipCompact     → elimina mensajes zombis y marcadores obsoletos.
    │                     (Flag de función: HISTORY_SNIP)
    └─ contextCollapse → reestructura el contexto para mayor eficiencia.
                         (Flag de función: CONTEXT_COLLAPSE)

    FLUJO DE COMPACTACIÓN:
    messages[] ──> getMessagesAfterCompactBoundary()
                        │
                        ▼
                  msjs antiguos ──> API de Claude (resumir) ──> resumen compacto
                        │
                        ▼
                  [resumen] + [compact_boundary] + [mensajes recientes]
```

---

## Integración con MCP (Model Context Protocol)

```
    ┌─────────────────────────────────────────────────────────┐
    │                   ARQUITECTURA MCP                       │
    │                                                         │
    │  MCPConnectionManager.tsx                               │
    │    ├── Descubrimiento Servidores (config settings.json) │
    │    │     ├── stdio  → generar proceso hijo              │
    │    │     ├── sse    → HTTP EventSource                  │
    │    │     ├── http   → HTTP de transmisión               │
    │    │     ├── ws     → WebSocket                         │
    │    │     └── sdk    → transporte en el proceso          │
    │    │                                                    │
    │    ├── Ciclo de Vida del Cliente                        │
    │    │     ├── conectar → inicializar → listar herram.    │
    │    │     ├── llamadas herram. vía envase MCPTool        │
    │    │     └── desconectar / reconectar con backoff       │
    │    │                                                    │
    │    ├── Autenticación                                    │
    │    │     ├── Flujo OAuth 2.0 (McpOAuthConfig)           │
    │    │     ├── Acceso entre aplicaciones (XAA / SEP-990)  │
    │    │     └── Claves API vía cabeceras                   │
    │    │                                                    │
    │    └── Registro de Herramientas                          │
    │          ├── convención mcp__<servidor>__<herram.>      │
    │          ├── Esquema dinámico desde servidor MCP        │
    │          ├── Paso de permisos a Claude Code             │
    │          └── Listado recursos (ListMcpResourcesTool)    │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
```

---

## Capa de Puente (Claude Desktop / Remoto)

```
    Claude Desktop / Web / Cowork          Claude Code CLI
    ══════════════════════════            ═════════════════

    ┌───────────────────┐                 ┌──────────────────┐
    │ Cliente de Puente │  ←─ HTTP ──→   │  bridgeMain.ts   │
    │ (App de Escritor.)│                 │                  │
    └───────────────────┘                 │  Gestor Sesión   │
                                          │  ├── generar CLI │
    PROTOCOLO:                            │  ├── poll estado │
    ├─ Autenticación JWT                  │  ├── relé msgs   │
    ├─ Intercambio work secret            │  └── capacityWake│
    ├─ Ciclo de vida sesión               │                  │
    │  ├── crear                          │  Backoff:        │
    │  ├── ejecutar                       │  ├─ conn: 2s→2m  │
    │  └─ detener                         │  └─ gen: 500m→30s│
    └─ Program. de refresco de tokens     └──────────────────┘
```

---

## Persistencia de Sesión

```
    ALMACENAMIENTO DE SESIÓN
    ════════════════════════

    ~/.claude/projects/<hash>/sessions/
    └── <session-id>.jsonl           ← registro solo de adición
        ├── {"type":"user",...}
        ├── {"type":"assistant",...}
        ├── {"type":"progress",...}
        └── {"type":"system","subtype":"compact_boundary",...}

    FLUJO DE REANUDACIÓN:
    getLastSessionLog() ──> parsear JSONL ──> reconstruir messages[]
         │
         ├── --continue     → última sesión en el cwd.
         ├── --resume <id>  → sesión específica.
         └── --fork-session → ID nueva, copia historial.

    ESTRATEGIA DE PERSISTENCIA:
    ├─ Mensajes usuario    → esperar escritura (bloqueante, recuperación fallas).
    ├─ Mensajes asistente  → fire-and-forget (cola preservando orden).
    ├─ Progreso            → escritura en línea (dedup en siguiente consulta).
    └─ Flush               → al entregar resultado / cowork flush ansioso.
```

---

## Sistema de Flags de Función

```
    ELIMINACIÓN CÓDIGO MUERTO (Bun en tiempo de construcción)
    ═════════════════════════════════════════════════════════

    feature('FLAG_NAME')  ──→  true  → incluido en paquete
                           ──→  false → eliminado del paquete

    FLAGS (observados en el código):
    ├─ COORDINATOR_MODE      → coordinador multi-agente.
    ├─ HISTORY_SNIP          → recorte agresivo de historial.
    ├─ CONTEXT_COLLAPSE      → reestructuración de contexto.
    ├─ DAEMON                → trabajadores de demonio de fondo.
    ├─ AGENT_TRIGGERS        → activadores cron/remotos.
    ├─ AGENT_TRIGGERS_REMOTE → soporte de activadores remotos.
    ├─ MONITOR_TOOL          → herramienta de monitoreo MCP.
    ├─ WEB_BROWSER_TOOL      → automatización del navegador.
    ├─ VOICE_MODE            → entrada/salida de voz.
    ├─ TEMPLATES             → clasificador de trabajos.
    ├─ EXPERIMENTAL_SKILL_SEARCH → descubrimiento de habilidades.
    ├─ KAIROS                → notificaciones push, envíos archivos.
    ├─ PROACTIVE             → herramienta de sueño, comp. proactivo.
    ├─ OVERFLOW_TEST_TOOL    → herramienta de prueba.
    ├─ TERMINAL_PANEL        → captura de terminal.
    ├─ WORKFLOW_SCRIPTS      → herramienta de flujo de trabajo.
    ├─ CHICAGO_MCP           → uso de computadora MCP.
    ├─ DUMP_SYSTEM_PROMPT    → extracción de prompt (solo interno).
    ├─ UDS_INBOX             → descubrimiento de pares.
    ├─ ABLATION_BASELINE     → ablación de experimentos.
    └─ UPGRADE_NOTICE        → notificaciones de actualización.

    GATES EN TIEMPO DE EJECUCIÓN:
    ├─ process.env.USER_TYPE === 'ant'  → funciones internas de Anthropic.
    └─ Flags de GrowthBook              → experimentos A/B en ejecución.
```

---

## Gestión de Estado

```
    ┌──────────────────────────────────────────────────────────┐
    │                   Almacén AppState                        │
    │                                                          │
    │  AppState {                                              │
    │    toolPermissionContext: {                              │
    │      mode: PermissionMode,           ← default/plan/etc  │
    │      additionalWorkingDirectories,                        │
    │      alwaysAllowRules,               ← auto-aprobar      │
    │      alwaysDenyRules,                ← auto-rechazar     │
    │      alwaysAskRules,                 ← siempre preguntar │
    │      isBypassPermissionsModeAvailable                    │
    │    },                                                    │
    │    fileHistory: FileHistoryState,    ← snapshots deshacer│
    │    attribution: AttributionState,    ← rastreo de commits│
    │    verbose: boolean,                                     │
    │    mainLoopModel: string,           ← modelo activo      │
    │    fastMode: FastModeState,                              │
    │    speculation: SpeculationState                          │
    │  }                                                       │
    │                                                          │
    │  Integración con React:                                  │
    │  ├── AppStateProvider   → crea almacén mediante createContext│
    │  ├── useAppState(sel)   → suscripción basada en selectores│
    │  └── useSetAppState()   → función actualizadora tipo immer│
    └──────────────────────────────────────────────────────────┘
```

---

## Los 12 Mecanismos Progresivos del Arnés

Este código fuente muestra 12 mecanismos en capas que requiere un arnés de agente de IA de producción más allá del bucle básico. Cada uno se basa en el anterior:

```
    s01  EL BUCLE             "Un bucle y Bash es todo lo que necesitas"
         query.ts: el bucle while-true que llama a la API de Claude,
         verifica stop_reason, ejecuta herram., añade resultados.

    s02  DESPACHO HERRAM.     "Añadir una herram. = añadir un manejador"
         Tool.ts + tools.ts: cada herramienta se registra en el mapa
         de despacho. El bucle permanece idéntico. La fábrica
         buildTool() proporciona valores predeterminados seguros.

    s03  PLANIFICACIÓN        "Un agente sin un plan va a la deriva"
         EnterPlanModeTool/ExitPlanModeTool + TodoWriteTool:
         listar pasos primero, luego ejecutar. Duplica la tasa de éxito.

    s04  SUB-AGENTES           "Divide grandes tareas; limpia contexto por subtarea"
         AgentTool + forkSubagent.ts: cada hijo obtiene messages[] frescos,
         manteniendo limpia la conversación principal.

    s05  CONOCIM. BAJO DEMANDA "Carga conocimiento cuando lo necesites"
         SkillTool + memdir/: inyectar vía tool_result, no sistem prompt.
         Los archivos CLAUDE.md se cargan de forma perezosa por directorio.

    s06  COMPRESIÓN CONTEXTO   "El contexto se llena; haz espacio"
         services/compact/: estrategia de tres capas:
         autoCompact (resumir) + snipCompact (recortar) + contextCollapse.

    s07  TAREAS PERSISTENTES   "Grandes metas → pequeñas tareas → disco"
         TaskCreate/Update/Get/List: grafo de tareas basado en archivos
         con seguimiento de estado, dependencias y persistencia.

    s08  TAREAS EN SEGUNDO PLANO "Ops lentas en fondo; el agente sigue pensando"
         DreamTask + LocalShellTask: hilos de demonio ejecutan comandos,
         inyecta notificaciones al completar.

    s09  EQUIPOS DE AGENTES     "Demasiado para uno → delegar a compañeros"
         TeamCreate/Delete + InProcessTeammateTask: compañeros
         persistentes con buzones de correo asíncronos.

    s10  PROTOCOLOS DE EQUIPO   "Reglas de comunicación compartidas"
         SendMessageTool: un patrón de solicitud-respuesta impulsa
         toda negociación entre agentes.

    s11  AGENTES AUTÓNOMOS      "Compañeros escanean y reclaman tareas solos"
         coordinator/coordinatorMode.ts: ciclo de inactividad + auto-reclamo,
         sin necesidad de que el líder asigne cada tarea.

    s12  AISLAMIENTO WORKTREE   "Cada uno trabaja en su propio directorio"
         EnterWorktreeTool/ExitWorktreeTool: tareas gestionan metas,
         worktrees gestionan directorios, vinculados por ID.
```

---

## Patrones de Diseño Clave

| Patrón | Dónde | Propósito |
|---------|-------|---------|
| **AsyncGenerator streaming** | `QueryEngine`, `query()` | Streaming de cadena completa de API a consumidor |
| **Builder + Factory** | `buildTool()` | Valores seguros por defecto para herramientas |
| **Tipos con Marca (Branded)** | `SystemPrompt`, `asSystemPrompt()` | Prevenir confusión de strings/arrays |
| **Flags Función + DCE** | `feature()` de `bun:bundle` | Eliminación de código muerto en construcción |
| **Uniones Discriminadas** | Tipos `Message` | Manejo de mensajes de forma segura por tipo |
| **Observer + State Machine** | `StreamingToolExecutor` | Rastreo del ciclo de vida de herram. |
| **Estado de Snapshot** | `FileHistoryState` | Deshacer/rehacer para opes de archivos |
| **Ring Buffer** | Error log | Memoria acotada para sesiones largas |
| **Fire-and-Forget Write** | `recordTranscript()` | Persistencia no bloqueante con ordenación |
| **Lazy Schema** | `lazySchema()` | Diferir evaluac. de esquema Zod para rendimiento |
| **Context Isolation** | `AsyncLocalStorage` | Contexto por agente en proceso compartido |

---

## Notas de Construcción

Este código fuente **no es directamente compilable** solo desde este repositorio:

- Faltan `tsconfig.json`, scripts de construcción y configuración del empaquetador de Bun.
- Las llamadas `feature()` son intrínsecos de tiempo de compilación de Bun — resueltos al empaquetar.
- `MACRO.VERSION` se inyecta en el momento de la construcción.
- Las secciones `process.env.USER_TYPE === 'ant'` son internas de Anthropic.
- El `cli.js` compilado es un paquete autónomo de 12 MB que solo requiere Node.js >= 18.
- Los mapas de origen (`cli.js.map`, 60 MB) apuntan de vuelta a estos archivos fuente para depuración.

**Consulta [QUICKSTART.md](QUICKSTART.md) para instrucciones de construcción y soluciones alternativas.**

---

## Licencia

Todo el código fuente de este repositorio tiene copyright de **Anthropic y Claude**. Este repositorio es solo para investigación técnica y educación. Consulta el paquete npm original para conocer los términos completos de la licencia.
