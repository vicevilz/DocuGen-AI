## Technical Documentation

# DocuGen

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/build-passing-brightgreen)

DocuGen es una herramienta de automatización de documentación de vanguardia diseñada para desarrolladores que buscan elevar la calidad de sus proyectos open-source. Al aprovechar la potencia de los LLMs (Large Language Models) mediante la API de Google Gemini, esta herramienta transforma metadatos abstractos extraídos del código fuente en archivos README.md profesionales, coherentes y listos para producción.

El motor de DocuGen realiza un análisis estático profundo del árbol sintáctico abstracto (AST) de cualquier proyecto Python. Esto garantiza que la documentación generada no solo sea descriptiva, sino técnica y estructuralmente precisa, reflejando fielmente la arquitectura de las clases, funciones y dependencias definidas por el desarrollador.

Al integrar DocuGen en su flujo de trabajo, elimina el tedioso proceso manual de redactar documentación de ingeniería, permitiendo que la narrativa de su proyecto evolucione al mismo ritmo que su código base. Es la solución definitiva para mantener una documentación técnica "viva" y siempre sincronizada con la realidad del software.

---

### Key Features

*   **🔍 Análisis AST Avanzado**: Escanea y descompone la estructura del código Python para comprender la jerarquía de objetos, firmas de métodos y tipos de parámetros.
*   **🤖 Integración con Gemini AI**: Utiliza modelos de lenguaje avanzados para redactar explicaciones semánticas sobre las capacidades del código, superando las limitaciones del autocompletado tradicional.
*   **📂 Gestión de Proyectos Inteligente**: Implementa un motor de escaneo compatible con `.gitignore`, evitando el procesamiento de archivos innecesarios o sensibles.
*   **⚙️ Configuración Flexible**: Soporta tanto argumentos de CLI como archivos de configuración TOML/dotenv para un control granular sobre el modelo utilizado y los parámetros de salida.
*   **⚡ Arquitectura Desacoplada**: El motor de plantillas y el pre-procesador de datos están diseñados para ser extensibles, facilitando la creación de nuevas salidas documentales (como Wiki, sitios estáticos o documentación técnica formal).

---

### Technical Architecture

DocuGen sigue una arquitectura de pipeline de datos en tres fases:

1.  **Ingestion & Scanning (`docugen/core/scanner.py`)**: Identifica el conjunto de archivos a procesar, respetando las reglas de exclusión y enfocándose en la lógica de negocio Python.
2.  **Parsing & Normalization (`docugen/core/parser.py` & `docugen/core/processor.py`)**: Convierte el código fuente en un grafo de metadatos estructurados. Los datos se "normalizan" para eliminar el ruido sintáctico, dejando solo la estructura necesaria para que el LLM comprenda el propósito del código.
3.  **Synthesis & Rendering (`docugen/api/gemini_client.py` & `docugen/templates/engine.py`)**: El cliente de Gemini recibe el contexto normalizado y genera contenido coherente. Finalmente, el motor de plantillas toma dicho contenido y lo estructura en un formato Markdown siguiendo estándares de la industria.

---

### Installation & Setup

#### Prerrequisitos
- Python 3.10 o superior.
- Una API Key válida de Google Gemini.

#### Pasos de instalación
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/docugen.git
   cd docugen
   ```
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

### Detailed API & Code Reference

#### `GeminiClient`
Actúa como el orquestador de comunicación con el modelo de IA. Responsable de la encapsulación de las peticiones a la API y la extracción limpia del texto resultante.

| Método | Responsabilidad |
| :--- | :--- |
| `_build_client` | Inicializa la sesión de conexión con la SDK de Gemini usando la credencial proporcionada. |
| `generate_markdown` | Envía el contexto del proyecto al modelo y gestiona la respuesta para retornar una cadena en formato Markdown. |

#### `Parser & Processor`
Conjunto de utilidades encargadas de la traducción de código a metadatos.

| Función | Descripción |
| :--- | :--- |
| `parse_project` | Recorre el árbol de archivos, delegando la extracción de clases y funciones al motor AST. |
| `prepare_for_ai` | Normaliza diccionarios complejos de metadatos a formatos planos, facilitando la interpretación por parte del modelo. |

---

### Usage Examples

**Ejecución básica desde la CLI:**

```bash
# Genera documentación para el directorio actual
uv run docugen generate . --output DOCUMENTATION.md
```

**Generación con configuración personalizada:**

```bash
# Utilizando un modelo específico y pasando instrucciones adicionales
uv run docugen generate ./src -o README.md --model gemini-3.1-pro-preview --prompt "Haz énfasis en la seguridad de las APIs"
```

---

### Development & Contributing

Para contribuir, asegúrate de mantener la cobertura de pruebas. El proyecto incluye una suite de tests robusta en `tests/` que utiliza `pytest`.

1. Instala los requisitos de desarrollo: `pip install -e .`
2. Ejecuta los tests: `pytest`
3. Al crear nuevos módulos, asegúrate de que el `processor.py` sea capaz de normalizar las nuevas estructuras de AST generadas.

---

### Roadmap

*   **Soporte Multi-Lenguaje**: Extender el `scanner` para procesar archivos JavaScript y Go.
*   **Modo Interactivo**: Implementar un CLI interactivo (mediante `questionary`) para configurar el proyecto paso a paso.
*   **Output en HTML/PDF**: Añadir un motor de plantillas avanzado basado en Jinja2 para generar reportes PDF exportables.
*   **Cache de LLM**: Implementar un sistema de caché para evitar llamadas redundantes a la API cuando el código no ha sufrido cambios significativos.

---

### License & Credits

Este proyecto se distribuye bajo la licencia **MIT**. Agradecimientos especiales a la comunidad de Python por proveer las librerías `ast` y `typer`, que han hecho posible este desarrollo.
