"""Dashboard de comercio electrónico · gerencia de marketplace y operaciones (grupo 10).

Ejecutar desde la raíz del repositorio:
    python -m streamlit run reports/dashboard/app.py
Lee data/processed/ordenes_limpias.csv, generado por notebooks/03_preparacion_de_los_datos.ipynb.
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Marketplace · Dashboard", layout="wide")

# ── Paleta: cada color conserva su significado en todas las pestañas (la misma de la fase 02) ──
AZUL, AZUL_CLARO = "#1F4E79", "#6BAED6"   # AZUL: ventas e ingreso neto · AZUL_CLARO: volumen de órdenes y contexto
VERDE, ROJO = "#2A9D8F", "#D1495B"        # VERDE: lo que se cumple (sin retraso) · ROJO: riesgo (devoluciones)
GRIS_TEXTO, GRIS_CLARO = "#1F2933", "#E5E7EB"

RUTA_DATOS = Path(__file__).resolve().parents[2] / "data" / "processed" / "ordenes_limpias.csv"
COLUMNAS = ["id_orden", "fecha_orden", "anio", "anio_mes", "periodo_comparable", "region", "categoria",
            "tipo_vendedor", "fuente_trafico", "metodo_pago", "operador_entrega", "valor_bruto_cop",
            "descuento_pct", "valor_descuento_cop", "rango_descuento", "valor_neto_cop", "dias_retraso",
            "tipo_promesa", "devolucion_30d", "calificacion_producto_1a5"]
ORDEN_RANGOS = {"rango_descuento": ["0–5 %", "5–10 %", "10–15 %", "15–20 %", "20 % o más"],
                "tipo_promesa": ["Mismo día", "1–2 días", "3 o más días"]}
FILTROS = {"region": "Región", "categoria": "Categoría", "tipo_vendedor": "Tipo de vendedor",
           "fuente_trafico": "Fuente de tráfico", "metodo_pago": "Medio de pago",
           "operador_entrega": "Operador de entrega"}


# ── Utilidades ──
def es(v, dec=0):
    """Número con formato español: punto de miles y coma decimal."""
    return f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def resaltar(valores, color):
    """Un solo color de énfasis para el valor más alto; el resto queda en el tono de contexto."""
    v = list(valores)
    return [color if x == max(v) else AZUL_CLARO for x in v]


def barras(categorias, series, titulo, titulo_eje, formato, horizontal=False, rango=None):
    """Barras con el valor escrito en cada una y eje de valores que arranca en cero."""
    fig = go.Figure()
    for nombre, valores, color in series:
        valores = list(valores)
        fig.add_bar(name=nombre, x=valores if horizontal else list(categorias),
                    y=list(categorias) if horizontal else valores, orientation="h" if horizontal else "v",
                    marker_color=color, text=[formato(v) for v in valores], textposition="outside",
                    cliponaxis=False, hovertemplate=("%{y}" if horizontal else "%{x}") + ": %{text}<extra></extra>")
    tope = max(max(list(v)) for _, v, _ in series)
    val = dict(title=titulo_eje, range=rango or [0, tope * 1.2], gridcolor=GRIS_CLARO, zeroline=False)
    cat = dict(showgrid=False, autorange="reversed") if horizontal else dict(showgrid=False)
    fig.update_layout(title=dict(text=titulo, x=0, font=dict(size=15)), barmode="group", height=340,
                      xaxis=val if horizontal else cat, yaxis=cat if horizontal else val,
                      showlegend=len(series) > 1, legend=dict(orientation="h", y=1.14, x=0),
                      margin=dict(l=10, r=10, t=60, b=10), plot_bgcolor="white", font=dict(color=GRIS_TEXTO))
    st.plotly_chart(fig, config={"displayModeBar": False})


def kpis(x):
    """Los 6 KPI definidos en el notebook 03 (sección 3.8)."""
    return dict(ventas=x["valor_neto_cop"].sum() / 1e6, ticket=x["valor_neto_cop"].mean(),
                desc=x["descuento_pct"].mean(), a_tiempo=(x["dias_retraso"] == 0).mean() * 100,
                devol=x["devolucion_30d"].mean() * 100, calif=x["calificacion_producto_1a5"].mean())


def dif(valor, total, unidad="pts"):
    return f"{valor - total:+.1f}".replace(".", ",") + f" {unidad} vs. total"


# ── Carga y validación de datos (en caché: no se relee el CSV en cada interacción) ──
@st.cache_data
def cargar():
    df = pd.read_csv(RUTA_DATOS, parse_dates=["fecha_orden", "anio_mes"])
    for col, orden in ORDEN_RANGOS.items():          # el CSV no guarda el orden de las categorías
        df[col] = pd.Categorical(df[col], categories=orden, ordered=True)
    return df


if not RUTA_DATOS.exists():
    st.error(f"No se encontró {RUTA_DATOS}. Ejecute el notebook 03 para generarlo.")
    st.stop()
df = cargar()
faltantes = [c for c in COLUMNAS if c not in df.columns]
if faltantes:
    st.error(f"Faltan columnas requeridas: {faltantes}")
    st.stop()

# ── Barra lateral: filtros que afectan a todo el dashboard ──
st.sidebar.header("Filtros")
anios = sorted(df["anio"].unique())
sel_anios = st.sidebar.multiselect("Año", anios, default=anios)
solo_comparable = st.sidebar.checkbox("Solo enero–septiembre", help="2026 solo tiene datos hasta septiembre: "
                                      "este filtro compara los tres años sobre los mismos meses.")
mascara = df["anio"].isin(sel_anios)
if solo_comparable:
    mascara &= df["periodo_comparable"]
for col, etiqueta in FILTROS.items():
    opciones = sorted(df[col].unique())
    mascara &= df[col].isin(st.sidebar.multiselect(etiqueta, opciones, default=opciones))
d = df[mascara]

# ── Encabezado y KPI (lectura en Z: título → KPI → gráficos → conclusión) ──
st.title("Marketplace: dónde se gana y dónde se pierde valor")
st.caption("Plataforma nacional de comercio electrónico · datos sintéticos, enero 2024 – septiembre 2026 · "
           f"{es(len(d))} de {es(len(df))} órdenes con los filtros actuales")
if d.empty:
    st.warning("Los filtros actuales no dejan ninguna orden. Amplíe la selección en la barra lateral.")
    st.stop()

k, g = kpis(d), kpis(df)
c = st.columns(6)
c[0].metric("Ventas netas", f"${es(k['ventas'])} M", f"{es(k['ventas'] / g['ventas'] * 100)} % del total", delta_color="off")
c[1].metric("Ticket promedio", f"${es(k['ticket'])}", f"{(k['ticket'] / g['ticket'] - 1) * 100:+.1f}".replace(".", ",") + " % vs. total", delta_color="off")
c[2].metric("Descuento promedio", f"{es(k['desc'], 1)} %", dif(k["desc"], g["desc"]), delta_color="off")
c[3].metric("Entrega a tiempo", f"{es(k['a_tiempo'], 1)} %", dif(k["a_tiempo"], g["a_tiempo"]), delta_color="off")
c[4].metric("Devoluciones", f"{es(k['devol'], 1)} %", dif(k["devol"], g["devol"]), delta_color="off")
c[5].metric("Calificación promedio", f"{es(k['calif'], 2)} / 5", dif(k["calif"], g["calif"], ""), delta_color="off")

t1, t2, t3, t4 = st.tabs(["Ingreso y canales", "Descuentos", "Entrega y satisfacción", "Conclusiones y datos"])

# ── Pestaña 1 · Objetivo 1: qué categorías sostienen el ingreso y por dónde llegan las órdenes ──
with t1:
    a, b = st.columns(2)
    with a:
        pesos = pd.DataFrame({"ord": d["categoria"].value_counts(normalize=True) * 100,
                              "ven": d.groupby("categoria")["valor_neto_cop"].sum() / d["valor_neto_cop"].sum() * 100})
        pesos = pesos.sort_values("ven", ascending=False)
        barras(pesos.index, [("% de las órdenes", pesos["ord"], AZUL_CLARO), ("% de las ventas netas", pesos["ven"], AZUL)],
               "Peso de cada categoría: órdenes frente a ventas", "% del total", lambda v: f"{es(v, 1)} %", horizontal=True)
    with b:
        mensual = d.groupby("anio_mes")["valor_neto_cop"].sum().div(1e6).reset_index()
        fig = go.Figure(go.Scatter(x=mensual["anio_mes"], y=mensual["valor_neto_cop"], mode="lines+markers",
                                   line=dict(color=AZUL, width=3), hovertemplate="%{x|%b %Y}: $%{y:,.0f} M<extra></extra>"))
        fig.update_layout(title=dict(text="Ventas netas por mes", x=0, font=dict(size=15)), height=340,
                          yaxis=dict(title="Millones de COP", rangemode="tozero", gridcolor=GRIS_CLARO),
                          xaxis=dict(showgrid=False), margin=dict(l=10, r=10, t=60, b=10),
                          plot_bgcolor="white", font=dict(color=GRIS_TEXTO))
        st.plotly_chart(fig, config={"displayModeBar": False})
    for col_st, (col, titulo) in zip(st.columns(3), [("fuente_trafico", "Órdenes por fuente de tráfico"),
                                                     ("metodo_pago", "Órdenes por medio de pago"),
                                                     ("region", "Órdenes por región")]):
        with col_st:
            n = d[col].value_counts()
            barras(n.index, [("Órdenes", n.values, AZUL_CLARO)], titulo, "Órdenes", lambda v: es(v), horizontal=True)

# ── Pestaña 2 · Objetivo 2: ¿los descuentos generan más valor o solo bajan el ticket? ──
with t2:
    r = d.groupby("rango_descuento", observed=True).agg(bruto=("valor_bruto_cop", "mean"), neto=("valor_neto_cop", "mean"),
                                                         devol=("devolucion_30d", "mean"))
    cedido = d["valor_descuento_cop"].sum() / 1e6
    st.info(f"Los descuentos restaron **${es(cedido)} M** al ingreso, el {es(cedido / (cedido + k['ventas']) * 100, 1)} % del valor bruto.")
    a, b = st.columns(2)
    with a:
        barras(r.index.astype(str), [("Valor antes del descuento", r["bruto"], AZUL_CLARO), ("Valor pagado (ticket)", r["neto"], AZUL)],
               "Ticket promedio según el rango de descuento", "COP por orden", lambda v: es(v / 1000) + " mil")
    with b:
        dv = r["devol"] * 100
        barras(dv.index.astype(str), [("Devoluciones", dv, resaltar(dv, ROJO))],
               "Devoluciones según el rango de descuento", "% de las órdenes", lambda v: f"{es(v, 1)} %")

# ── Pestaña 3 · Objetivo 3: cuánto baja la calificación al aumentar el retraso ──
with t3:
    a, b = st.columns(2)
    with a:
        cr = d.groupby("dias_retraso")["calificacion_producto_1a5"].mean().dropna()
        barras(cr.index.astype(str), [("Calificación", cr, [VERDE if i == 0 else AZUL_CLARO for i in cr.index])],
               "Calificación promedio según los días de retraso", "Calificación (1 a 5)", lambda v: es(v, 2), rango=[0, 5])
    with b:
        dp = d.groupby("tipo_promesa", observed=True)["devolucion_30d"].mean().dropna() * 100
        barras(dp.index.astype(str), [("Devoluciones", dp, resaltar(dp, ROJO))],
               "Devoluciones según la promesa de entrega", "% de las órdenes", lambda v: f"{es(v, 1)} %")

# ── Pestaña 4 · Conclusión: lectura que se recalcula con los filtros + tabla de detalle ──
with t4:
    st.subheader("Lectura de los resultados filtrados")
    ventas_cat = d.groupby("categoria")["valor_neto_cop"].sum().sort_values(ascending=False)
    top = ventas_cat.index[0]
    st.markdown(f"- **Ingreso.** {top} genera el {es(ventas_cat.iloc[0] / ventas_cat.sum() * 100, 1)} % de las ventas netas "
                f"con el {es((d['categoria'] == top).mean() * 100, 1)} % de las órdenes.")
    tk = r["neto"].dropna()
    if len(tk) > 1:
        st.markdown(f"- **Descuentos.** El ticket pasa de ${es(tk.iloc[0])} ({tk.index[0]}) a ${es(tk.iloc[-1])} ({tk.index[-1]}), "
                    f"mientras que las devoluciones van de {es(r['devol'].dropna().iloc[0] * 100, 1)} % a {es(r['devol'].dropna().iloc[-1] * 100, 1)} %.")
    if len(cr) > 1:
        st.markdown(f"- **Entrega.** La calificación baja de {es(cr.iloc[0], 2)} ({cr.index[0]} días de retraso) a {es(cr.iloc[-1], 2)} ({cr.index[-1]} días).")
    if "Mismo día" in dp.index and len(dp) > 1:
        resto = d.loc[d["tipo_promesa"] != "Mismo día", "devolucion_30d"].mean() * 100
        st.markdown(f"- **Promesa.** Con entrega el mismo día las devoluciones son {es(dp['Mismo día'], 1)} %, frente a {es(resto, 1)} % en los demás plazos.")
    st.markdown("**Decisiones que apoya:** dónde moderar descuentos, qué categorías priorizar en inversión comercial y "
                "qué retrasos o promesas de entrega corregir para mejorar la calificación.")
    st.subheader("Órdenes filtradas")
    vista = d[["id_orden", "fecha_orden", "categoria", "region", "valor_bruto_cop", "descuento_pct", "valor_neto_cop",
               "dias_retraso", "devolucion_30d", "calificacion_producto_1a5"]]
    st.dataframe(vista.head(1000), hide_index=True)
    st.caption("Se muestran las primeras 1.000 filas; la descarga incluye todas las filtradas.")
    st.download_button("Descargar órdenes filtradas (CSV)", d.to_csv(index=False).encode("utf-8"), "ordenes_filtradas.csv", "text/csv")
