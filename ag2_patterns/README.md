# AG2 Patterns — Extracted from Claude Code

Patrones de orquestación agéntica extraídos del código fuente de Claude Code (TypeScript)
y traducidos a Python idiomático sobre el framework [AG2 (AutoGen)](https://github.com/ag2ai/ag2).

**Agnóstico al modelo**: usa `OAI_CONFIG_LIST`. Compatible con GPT, Claude, Llama, Mistral, Qwen, etc.

## Estructura

| Módulo | Descripción | Estado |
|--------|-------------|--------|
| `config.py` | Configuración agnóstica OAI_CONFIG_LIST | ✅ done |
| `context/` | Gestión de contexto y ventana de tokens | 🔲 pending |
| `tools/` | Sistema de herramientas (tool-use) | 🔲 pending |
| `retry/` | Reintentos, fallbacks, error recovery | 🔲 pending |
| `prompts/` | Composición dinámica de system prompts | 🔲 pending |
| `execution/` | Control de ejecución, permisos, sandboxing | 🔲 pending |
| `planning/` | Planificación y descomposición de tareas | 🔲 pending |
| `memory/` | Gestión de memoria y estado entre turnos | 🔲 pending |
| `examples/` | Ejemplos funcionales integrando patrones | 🔲 pending |

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

```bash
# Opción 1: Variables de entorno
export OPENAI_API_KEY="sk-..."
export AG2_DEFAULT_MODEL="gpt-4o"

# Opción 2: Base URL para APIs compatibles (vLLM, Ollama, LiteLLM, etc.)
export AG2_BASE_URL="http://localhost:8000/v1"
export AG2_DEFAULT_MODEL="Qwen/Qwen2.5-72B-Instruct"

# Opción 3: OAI_CONFIG_LIST (JSON)
export OAI_CONFIG_LIST='[{"model":"gpt-4o","api_key":"sk-..."}]'
```

## Origen

Cada módulo documenta en sus docstrings el fichero TypeScript original del que se extrajo el patrón.
