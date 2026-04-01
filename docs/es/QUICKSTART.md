# Inicio Rápido — Construcción desde el Código Fuente

> **Resumen (TL;DR)**: Una reconstrucción completa requiere **Bun** (no Node.js) por sus
> intrínsecos de tiempo de compilación (`feature()`, `MACRO`, `bun:bundle`). Una construcción
> de "mejor esfuerzo" con **esbuild** llega al ~95 % del camino, pero necesita correcciones
> manuales para unos 108 módulos protegidos por flags de funciones.

## Opción A: Ejecutar el CLI pre-construido (Recomendado)

El paquete npm ya contiene un archivo `cli.js` compilado:

```bash
cd /ruta/al/directorio/           # donde residen package.json y cli.js
node cli.js --version           # → 2.1.88 (Claude Code)
node cli.js -p "Hola Claude"     # Modo no interactivo
```

**Autenticación requerida**: Establece la variable `ANTHROPIC_API_KEY` o ejecuta `node cli.js login`.

## Opción B: Construir desde el Código Fuente (Mejor Esfuerzo)

### Requisitos previos

```bash
node --version   # >= 18
npm --version    # >= 9
```

### Pasos

1. **Instalar dependencias de construcción**:
   ```bash
   npm install --save-dev esbuild
   ```

2. **Ejecutar el script de construcción**:
   ```bash
   node scripts/build.mjs
   ```

3. **Si tiene éxito, ejecuta el resultado**:
   ```bash
   node dist/cli.js --version
   ```

### Qué hace el script de construcción

| Fase | Acción |
|-------|--------|
| **1. Copia** | `src/` → `build-src/` (el original no se toca) |
| **2. Transformación** | `feature('X')` → `false` (habilita la eliminación de código muerto) |
| **2b. Transformación** | `MACRO.VERSION` → `'2.1.88'` (inyección de versión en tiempo de compilación) |
| **2c. Transformación** | `import from 'bun:bundle'` → importación simulada (stub) |
| **3. Entrada** | Crea un envoltorio que inyecta las globales de MACRO |
| **4. Empaquetado** | esbuild con creación iterativa de stubs para los módulos faltantes |

### Problemas Conocidos

El código fuente utiliza **intrínsecos de tiempo de compilación de Bun** que no pueden replicarse completamente con esbuild:

1. **`feature('FLAG')` de `bun:bundle`**: Bun resuelve esto en tiempo de compilación como `true`/`false` y elimina las ramas muertas. Nuestra transformación lo reemplaza con `false`, pero esbuild aún intenta resolver los `require()` dentro de esas ramas.

2. **`MACRO.X`**: El `--define` de Bun los reemplaza en tiempo de compilación. Nosotros usamos el reemplazo de cadenas, que funciona en la mayoría de los casos, pero puede fallar en expresiones complejas.

3. **108 módulos faltantes**: Estos son módulos internos protegidos por flags (daemon, asistente de puente, colapso de contexto, etc.) que no existen en el código fuente publicado. Normalmente son eliminados por Bun como código muerto, pero esbuild no puede eliminarlos porque las llamadas a `require()` siguen presentes sintácticamente.

4. **`bun:ffi`**: Utilizado para el soporte de proxies nativos. Se ha simulado (stubbed).

5. **TypeScript `import type` de archivos generados**: Algunos archivos de tipos generados no están en el código fuente publicado.

### Para corregir los problemas restantes

1. **Verifica qué falta todavía**:
   ```bash
   npx esbuild build-src/entry.ts --bundle --platform=node \
     --packages=external --external:'bun:*' \
     --log-level=error --log-limit=0 --outfile=/dev/null 2>&1 | \
     grep "Could not resolve" | sort -u
   ```

2. **Crea stubs para cada módulo faltante en `build-src/src/`**:
   - Para JS/TS: crea un archivo que exporte funciones vacías.
   - Para texto: crea un archivo vacío.

3. **Vuelve a ejecutar**:
   ```bash
   node scripts/build.mjs
   ```

## Opción C: Construir con Bun (Reconstrucción Completa — Requiere Acceso Interno)

```bash
# Instalar Bun
curl -fsSL https://bun.sh/install | bash

# La construcción real utiliza el empaquetador de Bun con flags de hito:
# bun build src/entrypoints/cli.tsx \
#   --define:feature='(flag) => flag === "SOME_FLAG"' \
#   --define:MACRO.VERSION='"2.1.88"' \
#   --target=bun \
#   --outfile=dist/cli.js

# Sin embargo, la configuración de construcción interna no se incluye en el
# paquete publicado. Necesitarías acceso al repositorio interno de Anthropic.
```

## Estructura del Proyecto

```
claude-code-2.1.88/
├── src/                  # Código fuente TypeScript original (1,884 archivos, 512K LOC)
├── stubs/                # Stubs de construcción para intrínsecos de Bun
│   ├── bun-bundle.ts     #   stub de feature() → siempre devuelve false
│   ├── macros.ts         #   Constantes de versión MACRO
│   └── global.d.ts       #   Declaraciones de tipos globales
├── scripts/
│   └── build.mjs         # Script de construcción (basado en esbuild)
├── node_modules/         # 192 dependencias npm
├── vendor/               # Stubs de código fuente de módulos nativos
├── build-src/            # Creado por el script de construcción (copia transformada)
└── dist/                 # Resultado de la construcción (creado por build.mjs)
```
