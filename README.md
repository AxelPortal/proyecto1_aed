# Proyecto 1 AED — Suffix Tree

Video educativo animado (estilo 3Blue1Brown) que explica y demuestra visualmente el funcionamiento de la estructura de datos **Suffix Tree** (Árbol de Sufijos).

## Descripción

Un Suffix Tree es un trie comprimido que almacena todos los sufijos de una cadena, permitiendo búsquedas de patrones en tiempo $O(m)$ donde $m$ es la longitud del patrón.
La animación está dividida en las siguientes secciones:

1. **Título del proyecto y Suffix Tree**
2. **Introducción** (Qué es, Tipo de Dato Abstracto, uso práctico)
3. **Inserción paso a paso** de la cadena `"BANANA$"`
4. **Búsqueda** (2 casos: "ANA" que se encuentra con éxito, y "BANS" que falla en medio del proceso)
5. **Recorrido DFS** (mostrando paso por paso cómo se obtienen todos los sufijos en orden lexicográfico)
6. **Casos Borde** (Cadena con trampa sin `$`, y cadena repetitiva `"AAAA$"` que genera ramas largas)
7. **Análisis de Complejidad**
8. **Créditos**

## Integrantes

| # | Nombre |
|---|--------|
| 1 | Axel Roberth Portal Ruiz |
| 2 | Dayron Saiyuk Cueva Loayza |
| 3 | Mariel Azucena Reyes Neyra |

## Estructura del Proyecto

```
proyecto1_aed/
├── suffix_tree.py          # Implementación del Suffix Tree (lógica pura)
├── suffix_tree_scene.py    # Escena de Manim (animación)
├── README.md               # Este archivo
└── media/                  # Videos generados (creado automáticamente)
```

## Software Requerido

| Software | Versión mínima | Instalación |
|----------|---------------|-------------|
| **Python** | 3.10+ | [python.org](https://www.python.org/downloads/) |
| **Manim Community Edition** | 0.18+ | `pip install manim` |
| **FFmpeg** | 4.0+ | Incluido con Manim en Windows, o [ffmpeg.org](https://ffmpeg.org/) |

### Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/<TU-USUARIO>/proyecto1_aed.git
cd proyecto1_aed

# 2. Crear entorno virtual (recomendado)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instalar dependencias
pip install manim
```

## Comandos de Ejecución

### Ejecutar tests del Suffix Tree (sin Manim)

```bash
python suffix_tree.py
```

Esto ejecuta pruebas unitarias de inserción, búsqueda, DFS y los casos borde (como string vacío o un solo carácter).

### Generar el video

```bash
# Baja calidad (480p, rápido para desarrollo)
manim -pql suffix_tree_scene.py SuffixTreeScene

# Calidad media (720p)
manim -pqm suffix_tree_scene.py SuffixTreeScene

# Alta calidad (1080p, para entrega final)
manim -pqh suffix_tree_scene.py SuffixTreeScene
```

El flag `-p` abre el video automáticamente después de renderizar. El video se guarda en el directorio de salida (ej. `media/videos/suffix_tree_scene/1080p60/SuffixTreeScene.mp4`).

## Arquitectura del Código

La lógica algorítmica emite eventos paso a paso mediante generadores (`yield`). La escena de Manim consume estos eventos y los traduce en animaciones visuales.
