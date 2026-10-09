# Dashboard de comercio electrónico

Proyecto final 2026-2 · Herramientas de Visualización para la Inteligencia de Negocios · Maestría en Analítica

Dashboard interactivo para la gerencia de marketplace y operaciones de una plataforma nacional de comercio electrónico, construido a partir del dataset asignado al grupo 10.

## Integrantes

- Mariana Valle
- Cristian Zea
- Daniel Esquinas

## Datos

`data/raw/10_comercio_electronico.csv`: 62.000 órdenes (una fila por orden) entre enero de 2024 y septiembre de 2026, con 19 variables. Datos sintéticos y anonimizados. El archivo original no se modifica; la versión limpia se guarda en `data/processed/`.

## Estructura del repositorio

```text
.
├── .streamlit/
│   └── config.toml                          # configuración de Streamlit
├── data/
│   ├── raw/
│   │   └── 10_comercio_electronico.csv      # dataset asignado, sin modificar
│   └── processed/
│       ├── calendario.csv                   # calendario preparado para el análisis
│       └── ordenes_limpias.csv              # datos limpios que alimentan el dashboard
├── notebooks/
│   ├── 01_comprension_del_negocio.ipynb
│   ├── 02_comprension_de_los_datos.ipynb
│   ├── 03_preparacion_de_los_datos.ipynb
│   └── 04_hallazgos_conclusiones_recomendaciones.ipynb
├── reports/
│   ├── dashboard/                           # archivo editable del dashboard y enlace de publicación
│   │   ├── app.py                           # aplicación del dashboard en Streamlit
│   ├── figures/                             # figuras generadas durante el análisis
│   └── presentacion/                        # presentación final de la sustentación
├── README.md
├── requirements.txt
└── .gitignore
```

## Dashboard

El dashboard está organizado en cuatro pestañas:

- **1 · Ingreso y canales:** ventas netas, categorías, ticket promedio, fuentes de tráfico, medios de pago y evolución mensual.
- **2 · Descuentos:** valor promedio de las órdenes, ventas, descuentos y devoluciones por rango.
- **3 · Entrega y satisfacción:** puntualidad de las entregas, retrasos, calificaciones y devoluciones.
- **4 · Conclusiones:** hallazgos, respuestas a los objetivos, recomendaciones para la gerencia e indicadores por categoría, con opción de descargar las órdenes filtradas en CSV.

Los filtros permiten explorar los datos según las dimensiones disponibles en el dashboard.

## Notebooks y flujo de trabajo

Los notebooks documentan las etapas del proyecto y deben ejecutarse en orden:

1. `01_comprension_del_negocio.ipynb`: contexto, problema, objetivos y preguntas de análisis.
2. `02_comprension_de_los_datos.ipynb`: exploración y comprensión del dataset.
3. `03_preparacion_de_los_datos.ipynb`: limpieza y preparación de los datos para el análisis. Genera los archivos de `data/processed/` que utiliza el dashboard.
4. `04_hallazgos_conclusiones_recomendaciones.ipynb`: síntesis de los hallazgos, conclusiones y recomendaciones para la gerencia a partir de los resultados del dashboard.

## Instalación y ejecución

Se recomienda utilizar un entorno virtual de Python para instalar las dependencias del proyecto.

Crear el entorno virtual:

```bash
python -m venv .venv
```

Activar el entorno virtual:

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS o Linux**

```bash
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Abrir los notebooks:

```bash
jupyter notebook notebooks/
```

Ejecutar el dashboard desde la raíz del repositorio:

```bash
python -m streamlit run reports/dashboard/app.py
```

Los notebooks se ejecutan en orden (01 → 04). El notebook 03 genera los archivos de `data/processed/` que utiliza el dashboard. El notebook 04 resume los hallazgos y las recomendaciones; no es un paso de preparación de datos.
