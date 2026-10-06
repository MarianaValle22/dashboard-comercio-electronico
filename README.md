# Dashboard de comercio electrónico

Proyecto final 2026-2 · Herramientas de Visualización para la Inteligencia de Negocios · Maestría en Analítica

Dashboard interactivo para la gerencia de marketplace y operaciones de una plataforma nacional de comercio electrónico, construido a partir del dataset asignado al grupo 10.

## Datos

`data/raw/10_comercio_electronico.csv`: 62.000 órdenes (una fila por orden) entre enero de 2024 y septiembre de 2026, con 19 variables. Datos sintéticos y anonimizados. El archivo original no se modifica; la versión limpia se guarda en `data/processed/`.

## Estructura del repositorio

```
.
├── data/
│   ├── raw/            # dataset asignado, sin modificar
│   └── processed/      # dataset limpio que alimenta el dashboard
├── notebooks/
│   ├── 01_comprension_del_negocio.ipynb
│   ├── 02_comprension_de_los_datos.ipynb
│   └── 03_preparacion_de_los_datos.ipynb
├── reports/
│   ├── dashboard/      # archivo editable del dashboard y enlace de publicación
│   └── presentacion/   # presentación final de la sustentación
├── README.md
├── requirements.txt
└── .gitignore
```

## Instrucciones de ejecución

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

Los notebooks se ejecutan en orden (01 → 03). El 03 genera el archivo de `data/processed/` que usa el dashboard.

## Integrantes

- _Nombre 1_
- _Nombre 2_
- _Nombre 3_
