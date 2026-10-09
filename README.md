# Desempeño Comercial y Operativo del Marketplace

Herramientas de Visualización para la Inteligencia de Negocios · Universidad de La Sabana

## Integrantes

- Mariana Valle
- Cristian Zea
- Daniel Esquinas

## Dashboard publicado

🔗 **Enlace:** 

## Contexto del proyecto

El comercio electrónico, es decir, la compra y venta de productos por internet, ya hace parte de la vida diaria: en 2025 una de cada cinco compras minoristas en el mundo se hizo en línea, y en Colombia las ventas en línea llegaron a $145,4 billones de pesos. Sin embargo, vender por internet no termina cuando el cliente paga. En cada etapa de la compra una plataforma puede perder dinero o clientes: con descuentos que reducen lo que se cobra, con entregas que llegan tarde y con productos que se devuelven.

Este proyecto analiza una **plataforma nacional de comercio electrónico** (grupo 10) a partir de un conjunto de datos **sintético y anonimizado** de **62.000 órdenes**, una por fila, realizadas entre el **1 de enero de 2024 y el 30 de septiembre de 2026**.

## Qué busca el proyecto

El dashboard está dirigido a la **gerencia de marketplace y operaciones** y responde la pregunta:

> **¿Dónde se pierden ingresos y satisfacción del cliente, y dónde conviene actuar primero?**

Para eso se plantearon tres objetivos, cada uno con su pestaña en el dashboard:

1. **Ingreso y canales:** identificar qué categorías concentran el ingreso y comparar cuántas órdenes llegan por cada fuente de tráfico y medio de pago.
2. **Descuentos:** evaluar si los descuentos generan más valor o si solo reducen el valor de cada compra y aumentan las devoluciones.
3. **Entrega y satisfacción:** medir cuánto disminuye la calificación del cliente a medida que aumentan los días de retraso en la entrega.

La cuarta pestaña reúne las **conclusiones**: la respuesta y la decisión para cada objetivo, y el orden recomendado de actuación.

**Indicadores (KPI):** ventas netas, ticket promedio, descuento promedio, % de entrega a tiempo, % de devoluciones y calificación promedio.

**Con el dashboard, la gerencia puede decidir:**

- Dónde concentrar o moderar los descuentos.
- Qué categorías priorizar en la inversión comercial, según cuánto aporta cada una al ingreso.
- Cómo reducir los días de retraso en la entrega para mejorar la calificación del cliente, y si conviene enfocar ese esfuerzo en algún operador o región en particular.

## Herramientas utilizadas y por qué

| Herramienta | Para qué se usó |
|---|---|
| **Python** (pandas, NumPy) | Comprensión, limpieza y preparación de los datos. |
| **Jupyter Notebook** | Documentar cada fase del proyecto con su código, sus resultados y sus decisiones. |
| **Matplotlib y Seaborn** | Gráficos exploratorios de la comprensión de los datos (`reports/figures/`). |
| **Streamlit** | Construcción del dashboard interactivo. |
| **Plotly** | Gráficos interactivos del dashboard: tooltips, zoom y selección de barras. |
| **Git y GitHub** | Trabajo en equipo y control de versiones. |

**¿Por qué Streamlit?**

- **Un solo flujo en Python.** La preparación de los datos y el dashboard usan el mismo lenguaje, así que todo el proceso, desde el archivo original hasta el tablero, se puede revisar y volver a ejecutar sin pasos manuales.
- **Interactividad completa.** Permite filtros en la barra lateral, pestañas, tooltips, selección cruzada (un clic en una categoría filtra el resto del tablero) y descarga de los datos filtrados.
- **Textos que se ajustan a los filtros.** Las lecturas analíticas y las conclusiones se recalculan con cada filtro, de modo que las cifras escritas siempre coinciden con las que se ven en los gráficos.
- **Publicación gratuita con enlace.** La aplicación se publica en Streamlit Community Cloud directamente desde este repositorio.
- **Control de versiones.** El dashboard es código (`app.py`), así que cada cambio queda registrado en GitHub y el equipo puede trabajar sobre el mismo archivo.

## Cómo ejecutar el dashboard

Requisitos: Python 3.10 o superior.

1. **Clonar el repositorio** y entrar a la carpeta:

   ```bash
   git clone https://github.com/MarianaValle22/dashboard-comercio-electronico.git
   cd dashboard-comercio-electronico
   ```

2. **Crear y activar un entorno virtual** (recomendado):

   ```bash
   python -m venv .venv
   ```

   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - macOS o Linux: `source .venv/bin/activate`


3. **Instalar las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar el dashboard desde la raíz del repositorio:**

   ```bash
   python -m streamlit run reports/dashboard/app.py
   ```

   El dashboard se abre en el navegador en `http://localhost:8501`. Para cerrarlo, presione `Ctrl + C` en la terminal.

El dashboard lee `data/processed/ordenes_limpias.csv`, que ya está incluido en el repositorio. Si se quiere regenerar desde el archivo original, se pueden ejecutar los notebooks en orden.

## Flujo de trabajo

| Fase | Notebook | Resultado |
|---|---|---|
| 1. Comprensión del negocio | `01_comprension_del_negocio.ipynb` | Contexto, audiencia, objetivos, KPI y criterios de éxito. |
| 2. Comprensión de los datos | `02_comprension_de_los_datos.ipynb` | Perfilamiento, calidad de los datos, primeros hallazgos y figuras en `reports/figures/`. |
| 3. Preparación de los datos | `03_preparacion_de_los_datos.ipynb` | Base limpia y tabla calendario en `data/processed/`. |
| 4. Construcción del dashboard | `reports/dashboard/app.py` | Dashboard interactivo en Streamlit. |
| 5. Hallazgos y conclusiones | `04_hallazgos_conclusiones_recomendaciones.ipynb` | Conclusiones y recomendaciones para la gerencia. |

## Estructura del repositorio

```text
.
├── .streamlit/
│   └── config.toml                          # colores y tema del dashboard
├── data/
│   ├── raw/
│   │   └── 10_comercio_electronico.csv      # dataset asignado, sin modificar
│   └── processed/
│       ├── calendario.csv                   # tabla calendario
│       └── ordenes_limpias.csv              # datos limpios que alimentan el dashboard
├── notebooks/
│   ├── 01_comprension_del_negocio.ipynb
│   ├── 02_comprension_de_los_datos.ipynb
│   ├── 03_preparacion_de_los_datos.ipynb
│   └── 04_hallazgos_conclusiones_recomendaciones.ipynb
├── reports/
│   ├── dashboard/
│   │   └── app.py                           # aplicación del dashboard en Streamlit
│   └── figures/                             # gráficos
├── README.md
├── requirements.txt
└── .gitignore
```
