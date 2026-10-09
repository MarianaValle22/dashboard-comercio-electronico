"""Desempeño Comercial y Operativo del Marketplace · Dashboard del grupo 10.

Ejecutar desde la raíz del repositorio:
    python -m streamlit run reports/dashboard/app.py

Lee data/processed/ordenes_limpias.csv, generado por notebooks/03_preparacion_de_los_datos.ipynb.
Requiere streamlit >= 1.36 (selección en gráficos y contenedores con altura fija) y pandas >= 2.0.

Estructura (s2a, sección 4; de lo general a lo particular):
    título y contexto -> filtros (barra lateral) -> KPI -> una pestaña por objetivo -> conclusiones.
Cada pestaña responde un objetivo del notebook 01 y su «Lectura analítica» solo usa cifras que se ven en
los gráficos de esa pestaña. Porcentajes, calificaciones y millones se muestran con dos decimales.
"""
# 1. Importar librerías
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 2. Configurar la página
st.set_page_config(page_title="Marketplace · Dashboard", layout="wide")

# Paleta de colores del notebook 02: cada color tiene un significado fijo en todo el tablero.
AZUL = "#1F4E79"         # color principal: ventas netas, ticket, órdenes y distribuciones de valores
AZUL_CLARO = "#6BAED6"   # color secundario: categorías y valores de referencia
VERDE = "#2A9D8F"        # mejor resultado o el más frecuente: más órdenes, mayor calificación, sin retraso
AMBAR = "#F4A261"        # descuento
ROJO = "#D1495B"         # riesgo: el grupo con más devoluciones
GRIS_TEXTO = "#1F2933"   # títulos, números y etiquetas
GRIS_MEDIO = "#6B7280"   # líneas de referencia (promedio)
GRIS_CLARO = "#E5E7EB"   # cuadrícula y bordes
# Único cambio frente al notebook: los títulos de ejes usan un gris más oscuro que #6B7280 para que se lean
# bien con el modo claro y el oscuro del navegador (las gráficas llevan fondo blanco y texto oscuro).
GRIS_EJES = "#4B5563"

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
MESES_LARGO = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
               "septiembre", "octubre", "noviembre", "diciembre"]

LISTA_ALTO = 210     # alto máximo de la lista de opciones de cada filtro; si hay más opciones aparece una barra de desplazamiento
LISTA_MAX_SIN_BARRA = 5  # hasta este número de opciones la lista se muestra completa
ALTO_GRAFICO = 360

# Diferencias mínimas para recomendar un grupo concreto. En el análisis (notebook 02 y pruebas sobre la base limpia),
# las brechas de descuento por categoría (0,23 pts) y de entrega a tiempo por operador (0,35 pts) o región (0,99 pts)
# no fueron estadísticamente significativas (p > 0,4); por debajo de estos umbrales el desempeño se trata como parejo.
UMBRAL_DESCUENTO = 1.0     # puntos de descuento promedio entre categorías
UMBRAL_A_TIEMPO = 2.0      # puntos de entrega a tiempo entre operadores o regiones
UMBRAL_DEVOLUCION = 1.0    # puntos de devoluciones entre tipos de promesa de entrega

# Barra de herramientas de Plotly al pasar el cursor: zoom, desplazar, acercar, alejar y restablecer.
CONFIG = {"displayModeBar": "hover", "displaylogo": False, "scrollZoom": False,
          "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"]}


# Datos y columnas
RUTA_DATOS = Path(__file__).resolve().parents[2] / "data" / "processed" / "ordenes_limpias.csv"
COLUMNAS = [
    "id_orden", "fecha_orden", "anio", "anio_mes", "periodo_comparable",
    "region", "categoria", "tipo_vendedor", "dispositivo", "fuente_trafico", "metodo_pago",
    "operador_entrega", "valor_bruto_cop", "descuento_pct", "valor_descuento_cop",
    "rango_descuento", "valor_neto_cop", "alto_valor", "dias_retraso", "tipo_promesa",
    "devolucion_30d", "calificacion_producto_1a5",
]
ORDEN_RANGOS = {"rango_descuento": ["0–5 %", "5–10 %", "10–15 %", "15–20 %", "20 % o más"],  # notebook 03, sección 3.6
                "tipo_promesa": ["Mismo día", "1–2 días", "3 o más días"]}
FILTROS = {
    "categoria": "Categoría", "region": "Región", "tipo_vendedor": "Tipo de vendedor",
    "dispositivo": "Dispositivo", "fuente_trafico": "Fuente de tráfico",
    "metodo_pago": "Medio de pago", "operador_entrega": "Operador de entrega",
}
OPC_ALTO = ["Todas las órdenes", "Solo compras de alto valor", "Sin compras de alto valor"]


# 3. Funciones de carga, formato y gráficos
@st.cache_data
def cargar(columnas):
    """Carga la base procesada y valida que tenga lo necesario. Las columnas entran como argumento para que
    el caché se renueve si cambian (Streamlit no detecta cambios en variables globales)."""
    if not RUTA_DATOS.exists():
        st.error(f"No se encontró {RUTA_DATOS}. Ejecute el notebook 03 para generarlo.")
        st.stop()
    datos = pd.read_csv(RUTA_DATOS, parse_dates=["fecha_orden", "anio_mes"],
                        dtype={"calificacion_producto_1a5": "Int64"})
    faltantes = [col for col in columnas if col not in datos.columns]
    if faltantes:
        st.error(f"Faltan columnas en la base procesada: {faltantes}")
        st.stop()
    for col, orden in ORDEN_RANGOS.items():
        datos[col] = pd.Categorical(datos[col], categories=orden, ordered=True)
    return datos[list(columnas)]


@st.cache_data
def a_csv(datos):
    return datos.to_csv(index=False).encode("utf-8")


def es(valor, decimales=0):
    """Formato español: punto de miles y coma decimal."""
    if pd.isna(valor):
        return "–"
    return f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(valor):
    """Porcentaje con dos decimales: 52,16 %"""
    return f"{es(valor, 2)} %"


def millones(valor):
    """Millones de COP con dos decimales."""
    return es(valor, 2)


def md(texto):
    """Protege el signo $ en los textos de Streamlit: sin esto, dos $ en el mismo texto se interpretan
    como una fórmula matemática y el texto se ve deformado."""
    return texto.replace("$", "\\$")


def comparar(valor, referencia, unidad, relativa=False):
    """Diferencia frente al total de la base, con dos decimales."""
    cambio = (valor / referencia - 1) * 100 if relativa else valor - referencia
    return None if pd.isna(cambio) else f"{cambio:+.2f} {unidad}".replace(".", ",")


def tendencia(inicio, fin, verbos=("sube", "baja", "se mantiene")):
    """Dirección del cambio, comparando los valores tal como se muestran (dos decimales)."""
    inicio, fin = round(inicio, 2), round(fin, 2)
    return verbos[0] if fin > inicio else verbos[1] if fin < inicio else verbos[2]


def variacion(cambio):
    """Cambio porcentual en palabras: «sube 3,32 %» / «baja 19,79 %»."""
    return "no cambia" if round(cambio, 2) == 0 else f"{'sube' if cambio > 0 else 'baja'} {es(abs(cambio), 2)} %"


def plural(inicio, fin):
    return tendencia(inicio, fin, ("suben", "bajan", "se mantienen"))


def dias(n):
    n = int(n)
    return "sin retraso" if n == 0 else f"{n} día{'s' if n != 1 else ''} de retraso"


def kpis(x):
    cal = x["calificacion_producto_1a5"].astype("float64")
    return dict(
        n=len(x), ventas_cop=x["valor_neto_cop"].sum(), ventas=x["valor_neto_cop"].sum() / 1e6,
        ticket=x["valor_neto_cop"].mean(), mediana=x["valor_neto_cop"].median(), desc=x["descuento_pct"].mean(),
        n_sin=int((x["dias_retraso"] == 0).sum()), a_tiempo=(x["dias_retraso"] == 0).mean() * 100,
        n_dev=int(x["devolucion_30d"].sum()), devol=x["devolucion_30d"].mean() * 100,
        calif=cal.mean(), n_cal=int(cal.notna().sum()))


def tarjeta(columna, etiqueta, valor, definicion, completo, comparacion=None, nota=""):
    """KPI con la misma estructura visual del dashboard de comercio: st.metric directo en cada columna."""
    ayuda = md(f"{definicion}\n\n**Valor completo:** {completo}")
    with columna:
        st.metric(etiqueta, valor, comparacion, delta_color="off", help=ayuda)
        if nota:
            st.caption(md(nota))


# Colores: degradado de azul y color de énfasis (notebook 02)
def _mezclar(c1, c2, t):
    a, b = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (c1, c2)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def degradado(valores):
    """El valor más alto en azul profundo y el más bajo en azul claro."""
    valores = list(valores)
    posicion = {i: r for r, i in enumerate(sorted(range(len(valores)), key=lambda i: -valores[i]))}
    ultimo = max(len(valores) - 1, 1)
    return [_mezclar(AZUL, AZUL_CLARO, posicion[i] / ultimo) for i in range(len(valores))]


def destacar(valores, color):
    """Degradado de azul, pero el valor más alto se pinta con un color semántico (verde o rojo)."""
    valores = list(valores)
    colores = degradado(valores)
    colores[valores.index(max(valores))] = color
    return colores


# Gráficos reutilizables: fondo blanco, cuadrícula suave, etiqueta en cada barra y zoom con la barra de Plotly
def _diseno(fig, titulo, leyenda=False, alto=ALTO_GRAFICO):
    fig.update_layout(
        # El título queda a 20 px del borde superior y con 14 px de margen a la izquierda.
        title=dict(text=titulo, x=0, xanchor="left", y=1 - 20 / alto, yanchor="top", pad=dict(l=14),
                   font=dict(size=15, color=GRIS_TEXTO)),
        height=alto, margin=dict(l=14, r=24, t=96 if leyenda else 70, b=12), separators=",.",
        paper_bgcolor="white", plot_bgcolor="white", font=dict(size=12, color=GRIS_TEXTO), dragmode="zoom",
        hoverlabel=dict(bgcolor="white", font=dict(color=GRIS_TEXTO), bordercolor=GRIS_CLARO),
        showlegend=leyenda, legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                                        font=dict(color=GRIS_TEXTO)))


def _ejes(fig, horizontal, eje_valor, eje_cat, rango):
    valor = dict(title=dict(text=eje_valor, font=dict(color=GRIS_EJES)), range=rango, gridcolor=GRIS_CLARO,
                 zeroline=False, tickfont=dict(color=GRIS_TEXTO), linecolor=GRIS_CLARO, automargin=True)
    cat = dict(title=dict(text=eje_cat, font=dict(color=GRIS_EJES)), showgrid=False,
               tickfont=dict(color=GRIS_TEXTO), linecolor=GRIS_CLARO, automargin=True)
    if horizontal:
        cat["autorange"] = "reversed"
    fig.update_xaxes(**(valor if horizontal else cat))
    fig.update_yaxes(**(cat if horizontal else valor))


def _referencia(fig, valor, texto, horizontal):
    """Línea punteada del promedio; su etiqueta va en la leyenda para no tapar títulos ni barras."""
    if valor is None or pd.isna(valor):
        return
    if horizontal:
        fig.add_vline(x=valor, line_dash="dash", line_color=GRIS_MEDIO, line_width=1.5)
    else:
        fig.add_hline(y=valor, line_dash="dash", line_color=GRIS_MEDIO, line_width=1.5)
    fig.add_scatter(x=[None], y=[None], mode="lines", name=texto, showlegend=True, hoverinfo="skip",
                    line=dict(color=GRIS_MEDIO, width=1.5, dash="dash"))


def _mostrar(fig, clave=None):
    if clave:
        try:
            st.plotly_chart(fig, theme=None, config=CONFIG, on_select="rerun", selection_mode="points", key=clave)
            return
        except TypeError:  # versiones de Streamlit sin selección en gráficos
            pass
    st.plotly_chart(fig, theme=None, config=CONFIG)


def barras(categorias, series, titulo, eje_valor, formato, horizontal=True, eje_cat=None,
           referencia=None, rango=None, detalle=None, clave=None):
    """Barras con etiqueta de valor. `series` = [(nombre, valores, color o lista de colores)].
    Las barras parten de cero. Con `clave` el gráfico permite seleccionar barras (selección cruzada)."""
    categorias = [str(c) for c in categorias]
    if not categorias:
        st.info(f"Sin datos para «{titulo}» con los filtros actuales.")
        return
    fig = go.Figure()
    for nombre, valores, color in series:
        valores = list(valores)
        fig.add_bar(
            name=nombre, x=valores if horizontal else categorias, y=categorias if horizontal else valores,
            orientation="h" if horizontal else "v", marker_color=color, cliponaxis=False, showlegend=len(series) > 1,
            text=[formato(v) for v in valores], textposition="outside", textfont=dict(color=GRIS_TEXTO, size=11),
            customdata=detalle, unselected=dict(marker=dict(opacity=0.35)),
            hovertemplate=("%{y}" if horizontal else "%{x}") + f" · {nombre}: %{{text}}"
                          + ("<br>%{customdata}" if detalle else "") + "<extra></extra>")
    tope = max(max(list(v)) for _, v, _ in series)
    if referencia and not pd.isna(referencia[0]):
        tope = max(tope, referencia[0])
    _diseno(fig, titulo, leyenda=len(series) > 1 or bool(referencia))
    _ejes(fig, horizontal, eje_valor, eje_cat, rango or [0, tope * 1.22])
    fig.update_layout(barmode="group", bargap=0.25)
    if referencia:
        _referencia(fig, referencia[0], referencia[1], horizontal)
    if clave:
        fig.update_layout(clickmode="event+select")
    _mostrar(fig, clave)


def linea(x, y, titulo, eje_valor, eje_x, formato, color=AZUL, marcadores=None, rango=None,
          referencia=None, etiquetas=True, ticks=None, detalle=None):
    """Línea con marcadores. `marcadores` permite pintar un punto con color semántico."""
    x, y = list(x), list(y)
    if not x:
        st.info(f"Sin datos para «{titulo}» con los filtros actuales.")
        return
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="lines+markers" + ("+text" if etiquetas else ""), line=dict(color=color, width=3),
        marker=dict(size=10 if etiquetas else 6, color=marcadores or color, line=dict(color="white", width=1.5)),
        text=[formato(v) for v in y], textposition="top center", textfont=dict(color=GRIS_TEXTO, size=11),
        customdata=detalle or [str(v) for v in x], showlegend=False,
        hovertemplate="%{customdata}: %{text}<extra></extra>"))
    _diseno(fig, titulo, leyenda=bool(referencia))
    _ejes(fig, False, eje_valor, eje_x, rango or [0, max(y + [referencia[0] if referencia else 0]) * 1.2])
    if ticks:
        fig.update_xaxes(tickmode="array", tickvals=ticks[0], ticktext=ticks[1])
    if referencia:
        _referencia(fig, referencia[0], referencia[1], False)
    _mostrar(fig)


# 4. Cargar datos
df = cargar(tuple(COLUMNAS))
ANIOS = [int(a) for a in sorted(df["anio"].unique())]
ETIQUETAS = {"anio": "Año", **FILTROS}  # todos los filtros de lista, en el orden en que aparecen en la barra lateral
OPCIONES = {"anio": ANIOS, **{col: sorted(df[col].unique()) for col in FILTROS}}
ORDEN_FILTROS = ["anio", "categoria", "region", "fuente_trafico", "metodo_pago", "operador_entrega", "tipo_vendedor", "dispositivo"]


# 5. Crear filtros: cada filtro es un menú desplegable (cuadro cerrado con flecha) que, al abrirse, muestra una lista
# de casillas con barra de desplazamiento y «Seleccionar todo». Los valores viven en st.session_state para poder
# limpiarlos con un botón.
def valores_iniciales():
    ini = {"f_comparable": False, "f_alto": OPC_ALTO[0]}
    for col in ETIQUETAS:
        ini[f"todo_{col}"] = True
        ini.update({f"f_{col}_{i}": True for i in range(len(OPCIONES[col]))})
    return ini


def limpiar():
    for clave, valor in valores_iniciales().items():
        st.session_state[clave] = valor
    st.session_state["reinicio"] = st.session_state.get("reinicio", 0) + 1  # borra la selección del gráfico


def marcar_todo(col):
    """Casilla «Seleccionar todo»: marca o desmarca todas las opciones del filtro."""
    for i in range(len(OPCIONES[col])):
        st.session_state[f"f_{col}_{i}"] = st.session_state[f"todo_{col}"]


def sincronizar_todo(col):
    """«Seleccionar todo» se marca sola cuando todas las opciones están marcadas, y se desmarca si falta alguna."""
    st.session_state[f"todo_{col}"] = all(st.session_state[f"f_{col}_{i}"] for i in range(len(OPCIONES[col])))


def filtro(col):
    """Menú desplegable de un filtro; devuelve las opciones marcadas."""
    opciones = OPCIONES[col]
    with st.expander(ETIQUETAS[col]):
        st.checkbox("Seleccionar todo", key=f"todo_{col}", on_change=marcar_todo, args=(col,))
        lista = st.container(height=LISTA_ALTO) if len(opciones) > LISTA_MAX_SIN_BARRA else st.container()
        with lista:
            for i, opcion in enumerate(opciones):
                st.checkbox(str(opcion), key=f"f_{col}_{i}", on_change=sincronizar_todo, args=(col,))
    return [opcion for i, opcion in enumerate(opciones) if st.session_state[f"f_{col}_{i}"]]


for clave, valor in valores_iniciales().items():
    st.session_state.setdefault(clave, valor)

st.sidebar.header("Filtros")
st.sidebar.button("Limpiar filtros y selección", on_click=limpiar)  # arriba, siempre a la vista
resumen_filtros = st.sidebar.empty()  # se llena después de leer los filtros
st.sidebar.caption("Abra cada menú para marcar las opciones. Aplican a todo el tablero.")
seleccion = {}
for col in ORDEN_FILTROS:
    with st.sidebar:
        seleccion[col] = filtro(col)
        if col == "anio":  # la opción de comparar años va junto al menú de Año
            with st.expander("Comparar años"):
                solo_comparable = st.checkbox(
                    "Solo enero–septiembre", key="f_comparable",
                    help="2026 solo tiene datos de enero a septiembre. Con esta opción todos los años se comparan sobre los mismos meses.")
with st.sidebar.expander("Compras de alto valor"):
    alto = st.radio("Compras de alto valor", OPC_ALTO, key="f_alto", label_visibility="collapsed",
                    help="Órdenes cuyo valor neto supera el límite de valores atípicos (notebook 03). Se conservan y se pueden comparar.")
sel_anios = seleccion["anio"]

activos = [f"{ETIQUETAS[col]} ({len(seleccion[col])} de {len(OPCIONES[col])})" for col in ORDEN_FILTROS
           if len(seleccion[col]) != len(OPCIONES[col])]
if solo_comparable:
    activos.append("Solo enero–septiembre")
if alto != OPC_ALTO[0]:
    activos.append(alto)
resumen_filtros.caption("**Filtros activos:** " + (", ".join(activos) if activos else "ninguno, se muestran todas las órdenes."))

# 6. Aplicar filtros
mascara = pd.Series(True, index=df.index)
for col in ORDEN_FILTROS:
    mascara &= df[col].isin(seleccion[col])
if solo_comparable:
    mascara &= df["periodo_comparable"]
if alto == OPC_ALTO[1]:
    mascara &= df["alto_valor"]
elif alto == OPC_ALTO[2]:
    mascara &= ~df["alto_valor"]
d = df[mascara]  # filtros de la barra lateral


def categorias_seleccionadas():
    """Categorías elegidas con un clic en el gráfico de participación (selección cruzada)."""
    estado = st.session_state.get(f"sel_categoria_{st.session_state.get('reinicio', 0)}")
    try:
        puntos = estado["selection"]["points"]
    except (TypeError, KeyError):
        return []
    return sorted({p["y"] for p in puntos if p.get("y") in OPCIONES["categoria"]})


sel_cat = categorias_seleccionadas()
dx = d[d["categoria"].isin(sel_cat)] if sel_cat else d  # filtros + selección en el gráfico

# Encabezado y contexto: lo esencial queda a la vista; el detalle, en el recuadro
desde, hasta = df["fecha_orden"].min(), df["fecha_orden"].max()
st.title("Desempeño Comercial y Operativo del Marketplace")
st.caption("Plataforma nacional de comercio electrónico · Dirigido a la gerencia de marketplace y operaciones · "
           f"Datos sintéticos, de {MESES_LARGO[desde.month - 1]} {desde.year} a {MESES_LARGO[hasta.month - 1]} {hasta.year}")
st.markdown("**Pregunta guía:** ¿dónde se pierden ingresos y satisfacción del cliente, y dónde conviene actuar primero?")

with st.expander("Contexto: problema, audiencia, decisiones, preguntas e interacciones"):
    st.markdown(
        "**Problema.** La plataforma no sabe en qué parte de la compra pierde ingresos y satisfacción del cliente: "
        "si en la venta (descuentos, categorías, canales, medios de pago) o en la entrega (retrasos, devoluciones, calificaciones).\n\n"
        "**Audiencia.** Gerencia de marketplace y operaciones.\n\n"
        "**Decisiones que apoya.** Dónde concentrar o moderar los descuentos · qué categorías priorizar en la inversión comercial · "
        "cómo reducir los días de retraso y si conviene enfocarse en algún operador o región.\n\n"
        "**Tres preguntas, una por pestaña.** 1) ¿Qué categorías concentran el ingreso y por dónde llegan las órdenes? "
        "2) ¿Los descuentos generan más valor o solo reducen el valor de cada compra y aumentan las devoluciones? "
        "3) ¿Cuánto baja la calificación cuando aumentan los días de retraso y dónde conviene actuar?\n\n"
        "**Indicadores.** Ventas netas, ticket promedio, descuento promedio, entrega a tiempo, devoluciones y calificación. "
        "**Dimensiones para comparar.** Categoría, región, tipo de vendedor, dispositivo, fuente de tráfico, medio de pago, "
        "operador, rango de descuento, días de retraso, promesa de entrega y tiempo.\n\n"
        "**Cómo interactuar.** Los filtros de la barra lateral actualizan todos los indicadores y gráficos. Un clic en una categoría del "
        "primer gráfico filtra el resto del tablero. Los gráficos se amplían con la barra de herramientas que aparece al pasar el cursor, "
        "y el signo «?» de cada indicador muestra su definición y su valor completo. **Hallazgos priorizados:** pestaña 4.")

if d.empty or dx.empty:
    st.warning("Los filtros y la selección actuales no dejan ninguna orden. "
               "Amplíe los filtros o use «Limpiar filtros y selección» en la barra lateral.")
    st.stop()

# 7. Calcular indicadores
k, g = kpis(dx), kpis(df)
st.caption(f"{es(len(dx))} de {es(len(df))} órdenes con los filtros actuales. La variación de cada indicador se compara "
           "con el total de la base.")
c = st.columns(6)
tarjeta(c[0], "Ventas netas", f"${es(k['ventas'])}\u00a0M",
        "Suma del valor neto de las órdenes (después de descuentos), en millones de COP.",
        f"${es(k['ventas_cop'], 2)} COP", nota=f"{pct(k['ventas'] / g['ventas'] * 100)} del total")
tarjeta(c[1], "Ticket promedio", f"${es(k['ticket'])}",
        "Valor neto promedio por orden. La mediana se muestra como apoyo porque las compras de alto valor suben el promedio.",
        f"${es(k['ticket'], 2)} COP (mediana ${es(k['mediana'], 2)} COP)",
        comparacion=comparar(k["ticket"], g["ticket"], "%", relativa=True), nota=f"Mediana ${es(k['mediana'])}")
tarjeta(c[2], "Descuento promedio", pct(k["desc"]),
        "Promedio del porcentaje de descuento aplicado a cada orden.",
        f"{es(k['desc'], 4)} % del valor antes de descuento",
        comparacion=comparar(k["desc"], g["desc"], "pts"), nota="sobre el valor bruto")
tarjeta(c[3], "Entrega a tiempo", pct(k["a_tiempo"]),
        "Órdenes entregadas sin días de retraso sobre el total de órdenes.",
        f"{es(k['a_tiempo'], 4)} % ({es(k['n_sin'])} de {es(k['n'])} órdenes)",
        comparacion=comparar(k["a_tiempo"], g["a_tiempo"], "pts"), nota="órdenes sin retraso")
tarjeta(c[4], "Devoluciones", pct(k["devol"]),
        "Órdenes devueltas dentro de los 30 días sobre el total de órdenes.",
        f"{es(k['devol'], 4)} % ({es(k['n_dev'])} de {es(k['n'])} órdenes)",
        comparacion=comparar(k["devol"], g["devol"], "pts"), nota="devueltas en 30 días")
tarjeta(c[5], "Calificación promedio", f"{es(k['calif'], 2)} / 5",
        "Promedio de la calificación del producto (1 a 5). No cuenta las órdenes sin calificar.",
        f"{es(k['calif'], 4)} de 5, con {es(k['n_cal'])} órdenes calificadas",
        comparacion=comparar(k["calif"], g["calif"], "pts"), nota=f"{es(k['n_cal'])} calificadas")

if sel_cat:
    st.info(f"**Selección en el gráfico de categorías: {', '.join(sel_cat)}.** Los indicadores y los gráficos de canales, "
            "tiempo, descuentos y entrega usan solo esas categorías; los gráficos por categoría siguen mostrando todas. "
            "Para quitarla use «Limpiar filtros y selección».")
meses_por_anio = df.groupby("anio")["anio_mes"].nunique()
incompletos = [int(a) for a, m in meses_por_anio.items() if m < 12]
if not solo_comparable and len(sel_anios) > 1 and any(a in sel_anios for a in incompletos):
    st.warning(f"{', '.join(map(str, incompletos))} no tiene los 12 meses. Para comparar años sobre los mismos meses, "
               "active «Solo enero–septiembre» en la barra lateral.")

# Cálculos de los gráficos (una sola vez; las pestañas solo dibujan)
# Objetivo 1: categorías que concentran el ingreso, fuentes de tráfico, medios de pago y evolución en el tiempo
pesos = pd.DataFrame({
    "ord": d["categoria"].value_counts(normalize=True) * 100,
    "ven": d.groupby("categoria")["valor_neto_cop"].sum() / d["valor_neto_cop"].sum() * 100,
}).sort_values("ven", ascending=False)
top = pesos.index[0]
ticket_cat = d.groupby("categoria")["valor_neto_cop"].mean().sort_values(ascending=False)
fuentes, pagos = dx["fuente_trafico"].value_counts(), dx["metodo_pago"].value_counts()
fp, pp = fuentes / len(dx) * 100, pagos / len(dx) * 100
mensual = dx.groupby("anio_mes").agg(ventas=("valor_neto_cop", "sum"), ordenes=("id_orden", "size"))
mensual["ventas"] /= 1e6

# Objetivo 2: descuentos
rd = dx.groupby("rango_descuento", observed=True).agg(
    n=("id_orden", "size"), ventas=("valor_neto_cop", "sum"), bruto=("valor_bruto_cop", "mean"),
    neto=("valor_neto_cop", "mean"), devol=("devolucion_30d", "mean"))
rd["pct_ord"] = rd["n"] / rd["n"].sum() * 100
rd["pct_ven"] = rd["ventas"] / rd["ventas"].sum() * 100
rd["devol"] *= 100
desc_cat = d.groupby("categoria")["descuento_pct"].mean().sort_values(ascending=False)
cedido = dx["valor_descuento_cop"].sum() / 1e6
pct_cedido = dx["valor_descuento_cop"].sum() / dx["valor_bruto_cop"].sum() * 100

# Objetivo 3: retraso, calificación y devoluciones; dónde conviene actuar (operador y región)
cr = dx.assign(cal=dx["calificacion_producto_1a5"].astype("float64")).groupby("dias_retraso")["cal"].mean().dropna()
dev_retraso = dx.groupby("dias_retraso")["devolucion_30d"].mean() * 100
dx_t = dx.assign(a_tiempo=dx["dias_retraso"].eq(0))
a_operador = dx_t.groupby("operador_entrega")["a_tiempo"].mean().mul(100).sort_values(ascending=False)
a_region = dx_t.groupby("region")["a_tiempo"].mean().mul(100).sort_values(ascending=False)
dev_promesa = dx.groupby("tipo_promesa", observed=True)["devolucion_30d"].mean() * 100
brecha_desc = desc_cat.iloc[0] - desc_cat.iloc[-1] if len(desc_cat) > 1 else 0
brecha_op = a_operador.iloc[0] - a_operador.iloc[-1] if len(a_operador) > 1 else 0
brecha_reg = a_region.iloc[0] - a_region.iloc[-1] if len(a_region) > 1 else 0


PROMESA_TEXTO = {"Mismo día": "para el mismo día", "1–2 días": "a 1–2 días", "3 o más días": "a 3 o más días"}
PROMESA_DE = {"Mismo día": "del mismo día", "1–2 días": "de 1–2 días", "3 o más días": "de 3 o más días"}
NUMEROS = {2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve", 10: "diez",
           11: "once", 12: "doce"}
FUENTE_TEXTO = {"Orgánico": "el canal orgánico", "Pago": "publicidad pagada", "Redes sociales": "redes sociales",
                "Directo": "tráfico directo", "Email": "email"}
PAGO_TEXTO = {"Tarjeta": "tarjeta", "PSE/Transferencia": "PSE/transferencia", "Billetera": "billetera",
              "Contraentrega": "pago contra entrega"}
VARIACION_ESTABLE = 0.30   # si (máximo − mínimo) / promedio de las ventas mensuales es menor, se describen como estables


def cuantos(n):
    return NUMEROS.get(n, str(n))


def con_retraso(n):
    """«las órdenes sin retraso» / «las que llegan con cuatro días de retraso»."""
    n = int(n)
    if n == 0:
        return "las órdenes sin retraso"
    return f"las que llegan con {'un día' if n == 1 else cuantos(n) + ' días'} de retraso"


def enumerar(partes):
    return partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " y " + partes[-1]


def frase_promesa():
    """Destaca el tipo de promesa con más devoluciones solo si se separa del resto por al menos UMBRAL_DEVOLUCION."""
    if len(dev_promesa) < 2:
        return None
    resto = dev_promesa.drop(dev_promesa.idxmax())
    if dev_promesa.max() - resto.max() < UMBRAL_DEVOLUCION:
        return None
    otros = [f"{pct(v)} en {'las promesas' if i == 0 else 'las'} {PROMESA_DE[str(nombre)]}"
             for i, (nombre, v) in enumerate(resto.items())]
    return (f"**Donde sí aparecen más devoluciones es en la entrega prometida {PROMESA_TEXTO[str(dev_promesa.idxmax())]}**: "
            f"{pct(dev_promesa.max())}, frente a {enumerar(otros)}.")


# Lecturas analíticas: un párrafo por idea, empezando por el hallazgo principal. Todas las cifras salen de los
# gráficos de la pestaña y se recalculan con los filtros.
# Objetivo 1
p1 = []
ven, ord_ = pesos.loc[top, "ven"], pesos.loc[top, "ord"]
if len(pesos) == 1:
    p1.append(f"Con los filtros actuales solo se analiza **{top}**.")
else:
    frase = (f"**{top} sostiene el ingreso.** Con solo el {pct(ord_)} de las órdenes genera el {pct(ven)} de las ventas netas"
             if ord_ < ven else f"**{top} es la categoría con más ventas.** Genera el {pct(ven)} de las ventas netas con el "
                                f"{pct(ord_)} de las órdenes")
    if ticket_cat.index[0] == top and len(ticket_cat) > 1:
        segunda = ticket_cat.index[1]
        frase += (f", porque su ticket promedio (${es(ticket_cat[top])}) es {es(ticket_cat[top] / ticket_cat[segunda], 1)} veces "
                  f"el de {segunda} (${es(ticket_cat[segunda])}), la categoría que le sigue.")
    else:
        frase += "."
    p1.append(frase)
p1.append(f"**Los canales{', en cambio,' if len(pesos) > 1 else ''} solo cambian el volumen de órdenes.** La mayor cantidad de órdenes llega por "
          f"{FUENTE_TEXTO.get(fp.index[0], fp.index[0])} ({pct(fp.iloc[0])}) y se paga con "
          f"{PAGO_TEXTO.get(pp.index[0], pp.index[0])} ({pct(pp.iloc[0])}).")
v_min, v_max = mensual["ventas"].min(), mensual["ventas"].max()
dec_m = 0 if v_min >= 100 else 2  # con montos pequeños (filtros muy estrechos) se muestran decimales
if len(mensual) > 1 and (v_max - v_min) / mensual["ventas"].mean() < VARIACION_ESTABLE:
    p1.append(f"**En general, las ventas se mantienen estables mes a mes**, entre ${es(v_min, dec_m)} M y ${es(v_max, dec_m)} M.")
elif len(mensual) > 1:
    p1.append(f"**Las ventas cambian bastante de un mes a otro**: van de ${es(v_min, dec_m)} M a ${es(v_max, dec_m)} M.")
l1 = "\n\n".join(p1)

# Objetivo 2
hay_rangos = len(rd) > 1
if hay_rangos:
    r0, r1 = rd.index[0], rd.index[-1]
    cambio_bruto = (rd["bruto"].iloc[-1] / rd["bruto"].iloc[0] - 1) * 100
    cambio_neto = (rd["neto"].iloc[-1] / rd["neto"].iloc[0] - 1) * 100
    ticket_baja = round(rd["neto"].iloc[-1], 2) < round(rd["neto"].iloc[0], 2)
    p2 = []
    if ticket_baja and abs(cambio_bruto) < 10:
        p2.append(f"**Los descuentos no hacen que el cliente compre más; solo hacen que pague menos.** El valor de la orden antes "
                  f"del descuento es casi el mismo en los {cuantos(len(rd))} rangos de descuento (entre ${es(rd['bruto'].min())} y "
                  f"${es(rd['bruto'].max())}), así que el ticket pagado cae {es(abs(cambio_neto), 2)} %: de ${es(rd['neto'].iloc[0])} "
                  f"en el rango de {r0} a ${es(rd['neto'].iloc[-1])} en el de {r1}.")
    else:
        p2.append(f"**El ticket pagado {variacion(cambio_neto)} entre el rango de {r0} y el de {r1}** "
                  f"(de ${es(rd['neto'].iloc[0])} a ${es(rd['neto'].iloc[-1])}), mientras que el valor antes del descuento "
                  f"{variacion(cambio_bruto)}.")
    dif_dev = rd["devol"].iloc[-1] - rd["devol"].iloc[0]
    p2.append((f"**Las devoluciones apenas cambian con el descuento**: " if abs(dif_dev) < UMBRAL_DEVOLUCION else
               f"**Las devoluciones {'suben' if dif_dev > 0 else 'bajan'} con el descuento**: ")
              + f"van de {pct(rd['devol'].iloc[0])} en el rango de {r0} a {pct(rd['devol'].iloc[-1])} en el de {r1}.")
    if len(desc_cat) > 1:
        p2.append((f"**El descuento se reparte de forma pareja entre las {cuantos(len(desc_cat))} categorías**: el promedio va de "
                   if brecha_desc < UMBRAL_DESCUENTO else f"**{desc_cat.index[0]} recibe más descuento que el resto**: el promedio va de ")
                  + f"{pct(desc_cat.iloc[-1])} en {desc_cat.index[-1]} a {pct(desc_cat.iloc[0])} en {desc_cat.index[0]}.")
    l2 = "\n\n".join(p2)
else:
    l2 = "Con estos filtros solo hay un rango de descuento: amplíe la selección para compararlos."

# Objetivo 3
hay_retraso = len(cr) > 1
p3 = []
if hay_retraso:
    c0, c1 = round(cr.iloc[0], 2), round(cr.iloc[-1], 2)
    pasos = cr.diff().dropna()
    if c1 < c0 and (pasos < 0).all():
        p3.append(f"**El retraso es lo que más afecta la experiencia del cliente.** La calificación baja con cada día de retraso, "
                  f"de {es(c0, 2)} en {con_retraso(cr.index[0])} a {es(c1, 2)} en {con_retraso(cr.index[-1])}.")
    else:
        p3.append(f"**La calificación {tendencia(c0, c1)} con el retraso**: va de {es(c0, 2)} en {con_retraso(cr.index[0])} a "
                  f"{es(c1, 2)} en {con_retraso(cr.index[-1])}.")
partes = []
if len(a_operador) > 1:
    partes.append((f"entre los {cuantos(len(a_operador))} operadores, de {pct(a_operador.iloc[-1])} en {a_operador.index[-1]} a "
                   f"{pct(a_operador.iloc[0])} en {a_operador.index[0]}", brecha_op, "un operador"))
if len(a_region) > 1:
    partes.append((f"entre las {cuantos(len(a_region))} regiones, de {pct(a_region.iloc[-1])} en {a_region.index[-1]} a "
                   f"{pct(a_region.iloc[0])} en {a_region.index[0]}", brecha_reg, "una región"))
if partes:
    textos = ", y ".join(t for t, _, _ in partes)
    if all(b < UMBRAL_A_TIEMPO for _, b, _ in partes):
        quien = " ni de ".join(q for _, _, q in partes)
        p3.append(f"**No es un problema de {quien} en particular.** La entrega a tiempo es casi igual {textos}.")
    else:
        p3.append(f"**La entrega a tiempo cambia según dónde y quién entrega**: {textos}.")
if frase_promesa():
    p3.append(frase_promesa())
l3_txt = "\n\n".join(p3) if p3 else "Con estos filtros no hay suficientes grupos para comparar."

# 8. Construir visualizaciones
t1, t2, t3, t4 = st.tabs(["1 · Ingreso y canales", "2 · Descuentos", "3 · Entrega y satisfacción", "4 · Conclusiones"])

with t1:
    st.subheader("¿Qué categorías concentran el ingreso y por dónde llegan las órdenes?")
    a, b = st.columns(2)
    with a:
        barras(pesos.index, [("% de las órdenes", pesos["ord"], AZUL_CLARO), ("% de las ventas netas", pesos["ven"], AZUL)],
               "Participación de cada categoría en órdenes y en ventas netas", "% del total", pct,
               eje_cat="Categoría", clave=f"sel_categoria_{st.session_state.get('reinicio', 0)}")
        st.caption("Haga clic en una categoría para filtrar con ella el resto del tablero.")
    with b:
        barras(ticket_cat.index, [("Ticket promedio", ticket_cat.values, destacar(ticket_cat.values, VERDE))],
               "Ticket promedio por categoría", "Ticket promedio (COP)", es, eje_cat="Categoría",
               referencia=(d["valor_neto_cop"].mean(), f"Promedio general ${es(d['valor_neto_cop'].mean())}"))
    a, b = st.columns(2)
    with a:
        barras(fp.index, [("% de las órdenes", fp.values, destacar(fp.values, VERDE))], "Órdenes por fuente de tráfico",
               "% de las órdenes", pct, eje_cat="Fuente de tráfico", detalle=[f"{es(v)} órdenes" for v in fuentes.values])
    with b:
        barras(pp.index, [("% de las órdenes", pp.values, destacar(pp.values, VERDE))], "Órdenes por medio de pago",
               "% de las órdenes", pct, eje_cat="Medio de pago", detalle=[f"{es(v)} órdenes" for v in pagos.values])
    metrica = st.radio("Evolución mensual de", ["Ventas netas", "Órdenes"], horizontal=True, key="m_tiempo")
    col_m, formato_m, eje_m, color_m = (("ventas", lambda v: f"${millones(v)} M", "Ventas netas (millones de COP)", AZUL)
                                       if metrica == "Ventas netas" else ("ordenes", es, "Órdenes", AZUL_CLARO))
    fechas = list(mensual.index)
    rotulos = [f"{MESES[f.month - 1]} {f.year}" for f in fechas]
    linea(fechas, mensual[col_m], f"{metrica} por mes", eje_m, "Mes", formato_m, color=color_m, etiquetas=False,
          ticks=(fechas[::3], rotulos[::3]), detalle=rotulos)
    st.info(md("**Lectura analítica.**\n\n" + l1))

with t2:
    st.subheader("¿Los descuentos generan más valor o solo reducen el valor de cada compra y aumentan las devoluciones?")
    rangos = [str(r) for r in rd.index]
    a, b = st.columns(2)
    with a:
        barras(rangos, [("Antes del descuento", rd["bruto"], AZUL_CLARO), ("Pagado (ticket)", rd["neto"], AZUL)],
               "Valor promedio de la orden según el descuento", "Valor promedio de la orden (COP)",
               lambda v: f"{es(v / 1000, 2)} mil", horizontal=False, eje_cat="Rango de descuento")
    with b:
        barras(rangos, [("% de las órdenes", rd["pct_ord"], AZUL_CLARO), ("% de las ventas netas", rd["pct_ven"], AZUL)],
               "Órdenes y ventas netas según el descuento", "% del total", pct,
               horizontal=False, eje_cat="Rango de descuento")
    a, b = st.columns(2)
    with a:
        mayor_i = list(rd["devol"]).index(rd["devol"].max())
        linea(rangos, rd["devol"], "% de devoluciones según el descuento", "% de órdenes devueltas", "Rango de descuento",
              pct, marcadores=[ROJO if i == mayor_i else AZUL for i in range(len(rd))],
              rango=[0, max(rd["devol"].max(), k["devol"]) * 1.35], referencia=(k["devol"], f"Promedio {pct(k['devol'])}"))
    with b:
        barras(desc_cat.index, [("Descuento promedio", desc_cat.values, AMBAR)], "Descuento promedio por categoría",
               "% de descuento promedio", pct, eje_cat="Categoría",
               referencia=(d["descuento_pct"].mean(), f"Promedio general {pct(d['descuento_pct'].mean())}"))
    st.caption(md(f"Con los filtros actuales, los descuentos restaron ${millones(cedido)} M, el {pct(pct_cedido)} del valor antes de descuento."))
    st.info(md("**Lectura analítica.**\n\n" + l2))

with t3:
    st.subheader("¿Cuánto baja la calificación cuando aumentan los días de retraso y dónde conviene actuar?")
    a, b, e = st.columns(3)
    with a:
        mejor = list(cr.values).index(max(cr.values)) if len(cr) else 0
        linea([str(int(i)) for i in cr.index], cr.values, "Calificación promedio según los días de retraso",
              "Calificación promedio (escala 1 a 5)", "Días de retraso (0 = sin retraso)", lambda v: es(v, 2),
              marcadores=[VERDE if i == mejor else AZUL for i in range(len(cr))],
              rango=[max(1, cr.min() - 0.3), min(5, cr.max() + 0.3)] if len(cr) else None,
              referencia=(k["calif"], f"Promedio {es(k['calif'], 2)}"))
        st.caption("Línea con eje ajustado a la escala de calificación para ver la variación entre grupos.")
    with b:
        barras([str(int(i)) for i in dev_retraso.index], [("% de devoluciones", dev_retraso.values, destacar(dev_retraso.values, ROJO))],
               "% de devoluciones según los días de retraso", "% de órdenes devueltas", pct,
               horizontal=False, eje_cat="Días de retraso (0 = sin retraso)", referencia=(k["devol"], f"Promedio {pct(k['devol'])}"))
        st.caption("Barras desde cero: la altura es proporcional al porcentaje.")
    with e:
        barras([str(p) for p in dev_promesa.index],
               [("% de devoluciones", dev_promesa.values, destacar(dev_promesa.values, ROJO))],
               "% de devoluciones según la promesa de entrega", "% de órdenes devueltas", pct,
               horizontal=False, eje_cat="Días de entrega prometidos", referencia=(k["devol"], f"Promedio {pct(k['devol'])}"))
        st.caption("Mismo día = entrega prometida para el mismo día de la compra.")
    a, b = st.columns(2)
    with a:
        barras(a_operador.index, [("Entrega a tiempo", a_operador.values, destacar(a_operador.values, VERDE))],
               "Entrega a tiempo por operador", "% de órdenes sin retraso", pct,
               eje_cat="Operador de entrega", rango=[0, 118], referencia=(k["a_tiempo"], f"Promedio {pct(k['a_tiempo'])}"))
    with b:
        barras(a_region.index, [("Entrega a tiempo", a_region.values, destacar(a_region.values, VERDE))],
               "Entrega a tiempo por región", "% de órdenes sin retraso", pct,
               eje_cat="Región", rango=[0, 118], referencia=(k["a_tiempo"], f"Promedio {pct(k['a_tiempo'])}"))
    st.info(md("**Lectura analítica.**\n\n" + l3_txt))
    st.caption("La relación entre retraso y calificación es una asociación observada en los datos, no prueba que una cause la otra. "
               f"El promedio de calificación excluye {es(len(dx) - k['n_cal'])} órdenes sin calificar.")

# 9. Mostrar tablas e interpretación
with t4:
    st.subheader("Conclusiones")

    # Tarjetas de conclusiones: misma lectura que el notebook 04 (secciones 4.3 a 4.7), con cifras que se recalculan.
    def dias_tarjeta(n):
        n = int(n)
        return "sin retraso" if n == 0 else f"con {'un día' if n == 1 else cuantos(n) + ' días'}"

    # Objetivo 1
    if len(pesos) > 1 and ticket_cat.index[0] == top and len(ticket_cat) > 1:
        segunda = ticket_cat.index[1]
        r1_txt = (f"{top} concentra el {pct(pesos.loc[top, 'ven'])} de las ventas netas con el {pct(pesos.loc[top, 'ord'])} de las "
                  f"órdenes, porque su ticket promedio (${es(ticket_cat[top])}) es el más alto: "
                  f"{es(ticket_cat[top] / ticket_cat[segunda], 1)} veces el de {segunda}.")
    else:
        r1_txt = f"{top} concentra el {pct(pesos.loc[top, 'ven'])} de las ventas netas con el {pct(pesos.loc[top, 'ord'])} de las órdenes."
    r1_txt += (f" La mayor cantidad de órdenes llega por {FUENTE_TEXTO.get(fp.index[0], fp.index[0])} ({pct(fp.iloc[0])}) y se paga "
               f"con {PAGO_TEXTO.get(pp.index[0], pp.index[0])} ({pct(pp.iloc[0])}), aunque el número de órdenes por canal no permite "
               "saber por sí solo cuál es más rentable.")
    d1_txt = (f"Proteger el desempeño comercial de {top}, la categoría que sostiene el ingreso. Usar las fuentes de tráfico y los "
              "medios de pago como línea base de seguimiento: antes de mover inversión entre canales hacen falta datos de costo "
              "de adquisición y conversión, que el dataset no incluye.")

    # Objetivo 2
    if hay_rangos:
        if ticket_baja and abs(cambio_bruto) < 10:
            r2_txt = (f"Solo reducen el valor de cada compra. Entre los rangos de {r0} y {r1}, el valor de la orden antes del descuento "
                      f"{variacion(cambio_bruto)}, pero el ticket pagado cae {es(abs(cambio_neto), 2)} %.")
        else:
            r2_txt = (f"Entre los rangos de {r0} y {r1}, el ticket pagado {variacion(cambio_neto)} y el valor de la orden antes del "
                      f"descuento {variacion(cambio_bruto)}.")
        dif_dev = rd["devol"].iloc[-1] - rd["devol"].iloc[0]
        if abs(dif_dev) < UMBRAL_DEVOLUCION:
            r2_txt += f" Las devoluciones apenas cambian (de {pct(rd['devol'].iloc[0])} a {pct(rd['devol'].iloc[-1])})"
            r2_txt += (f" y no crecen de forma continua: su valor más alto está en el rango de {rd['devol'].idxmax()} "
                       f"({pct(rd['devol'].max())})." if rd["devol"].idxmax() != r1 else ".")
        else:
            r2_txt += (f" Las devoluciones {'suben' if dif_dev > 0 else 'bajan'} de {pct(rd['devol'].iloc[0])} a "
                       f"{pct(rd['devol'].iloc[-1])}.")
        if ticket_baja:
            altos = f"{rd.index[-2]} y {r1}" if len(rd) > 2 else r1
            d2_txt = f"Revisar los descuentos de los rangos más altos ({altos}), sobre todo los de {r1}."
            if len(desc_cat) > 1 and brecha_desc < UMBRAL_DESCUENTO:
                d2_txt += (f" Como el descuento promedio es casi igual en las {cuantos(len(desc_cat))} categorías (de "
                           f"{pct(desc_cat.iloc[-1])} en {desc_cat.index[-1]} a {pct(desc_cat.iloc[0])} en {desc_cat.index[0]}), "
                           "la revisión aplica a toda la política.")
                if len(desc_cat) > 2:
                    d2_txt += (f" {desc_cat.index[0]} y {desc_cat.index[1]}, con los promedios más altos, pueden ser el punto de "
                               "partida, sin asumir que una diferencia tan pequeña sea un problema por sí misma.")
            elif len(desc_cat) > 1:
                d2_txt += (f" Empezar por {desc_cat.index[0]}, la categoría con mayor descuento promedio ({pct(desc_cat.iloc[0])}, "
                           f"frente a {pct(desc_cat.iloc[-1])} en {desc_cat.index[-1]}).")
        else:
            d2_txt = "Revisar el equilibrio entre descuento y volumen con los gráficos de la pestaña 2."
    else:
        r2_txt, d2_txt = l2, "Amplíe los filtros para comparar rangos de descuento."

    # Objetivo 3
    if hay_retraso:
        pasos = cr.diff().dropna()
        verbo = "baja con cada día de retraso" if (pasos < 0).all() else tendencia(cr.iloc[0], cr.iloc[-1])
        r3_txt = (f"La calificación {verbo}: de {es(cr.iloc[0], 2)} {dias_tarjeta(cr.index[0])} a {es(cr.iloc[-1], 2)} "
                  f"{dias_tarjeta(cr.index[-1])}, {es(abs(cr.iloc[0] - cr.iloc[-1]), 2)} puntos "
                  f"{'menos' if cr.iloc[-1] < cr.iloc[0] else 'más'}.")
    else:
        r3_txt = ""
    tramos = []
    if len(a_operador) > 1:
        tramos.append((f"entre los {cuantos(len(a_operador))} operadores (de {pct(a_operador.iloc[-1])} en {a_operador.index[-1]} a "
                       f"{pct(a_operador.iloc[0])} en {a_operador.index[0]})", brecha_op, a_operador.index[-1], "operadores"))
    if len(a_region) > 1:
        tramos.append((f"entre las {cuantos(len(a_region))} regiones (de {pct(a_region.iloc[-1])} en {a_region.index[-1]} a "
                       f"{pct(a_region.iloc[0])} en {a_region.index[0]})", brecha_reg, a_region.index[-1], "regiones"))
    parejo = bool(tramos) and all(b < UMBRAL_A_TIEMPO for _, b, _, _ in tramos)
    r3_txt += f" El {pct(100 - k['a_tiempo'])} de las órdenes llega con retraso"
    if tramos:
        r3_txt += (", y la entrega a tiempo es casi igual " if parejo else ", y la entrega a tiempo cambia ") + \
                  " y ".join(t for t, _, _, _ in tramos)
    r3_txt += "."
    sin_relacion = len(dev_retraso) > 1 and abs(dev_retraso.iloc[-1] - dev_retraso.iloc[0]) < UMBRAL_DEVOLUCION
    if frase_promesa():
        r3_txt += ((" Las devoluciones no siguen al retraso, pero sí" if sin_relacion else " Las devoluciones")
                   + f" son mayores en la entrega prometida {PROMESA_TEXTO[str(dev_promesa.idxmax())]} ({pct(dev_promesa.max())}).")
    elif sin_relacion:
        r3_txt += " Las devoluciones no cambian de forma clara con el retraso."
    r3_txt = r3_txt.strip()

    d3_txt = "Hacer de la reducción de los retrasos una prioridad operativa para proteger la calificación."
    if parejo:
        quienes = " y ".join(g for _, _, _, g in tramos)
        mas_bajos = " y ".join(peor for _, _, peor, _ in tramos)
        d3_txt += (f" Como las diferencias entre {quienes} son de {es(max(b for _, b, _, _ in tramos), 2)} puntos o menos, el esfuerzo "
                   f"debe cubrir toda la operación. {mas_bajos}, {'los' if len(tramos) > 1 else 'el'} de menor entrega a tiempo, "
                   f"{'pueden' if len(tramos) > 1 else 'puede'} revisarse primero para verificar si la diferencia se mantiene en el tiempo.")
    elif tramos:
        _, brecha, peor, grupo = max(tramos, key=lambda t: t[1])
        d3_txt += (f" Empezar por {peor}, {'el operador' if grupo == 'operadores' else 'la región'} con menor entrega a tiempo, "
                   f"a {es(brecha, 2)} puntos {'del mejor' if grupo == 'operadores' else 'de la mejor'}.")
    if frase_promesa():
        d3_txt += f" Revisar también la promesa de entrega {PROMESA_TEXTO[str(dev_promesa.idxmax())].replace('para el ', 'el ')}."

    tarjetas = [
        ("Objetivo 1 · Ingreso y canales", "¿Qué categorías concentran el ingreso y por dónde llegan las órdenes?", r1_txt, d1_txt),
        ("Objetivo 2 · Descuentos",
         "¿Los descuentos generan más valor o solo reducen el valor de cada compra y aumentan las devoluciones?", r2_txt, d2_txt),
        ("Objetivo 3 · Entrega y satisfacción",
         "¿Cuánto baja la calificación cuando aumentan los días de retraso y dónde conviene actuar?", r3_txt, d3_txt),
    ]
    for columna, (titulo, pregunta, respuesta, decision) in zip(st.columns(3), tarjetas):
        with columna, st.container(border=True):
            st.markdown(md(f"**{titulo}**\n\n*{pregunta}*\n\n**Respuesta.** {respuesta}\n\n**Decisión.** {decision}"))

    # Cierre: responde la pregunta guía con el orden de actuación del notebook 04 (sección 4.7)
    st.markdown(md(
        f"**¿Dónde conviene actuar primero?** Primero en los descuentos, que tienen un costo directo de ${es(cedido)} M "
        f"({pct(pct_cedido)} del valor antes del descuento); después en la puntualidad, porque el {pct(100 - k['a_tiempo'])} de las "
        f"órdenes llega con retraso y eso baja la calificación; y por último en el seguimiento de {top}, que sostiene el ingreso."))
    st.markdown(
        "| Prioridad | Frente | Acción principal | Qué monitorear en el dashboard |\n"
        "|---|---|---|---|\n"
        "| 1 | Descuentos | Revisar la profundidad de los descuentos por rango, empezando por los de 15 % o más. "
        "| Ticket antes y después del descuento, participación en ventas y devoluciones (pestaña 2). |\n"
        "| 2 | Entregas | Reducir los días de retraso en toda la operación y revisar la promesa de entrega el mismo día. "
        "| Entrega a tiempo, calificación según los días de retraso y devoluciones según la promesa (pestaña 3). |\n"
        f"| 3 | Desempeño comercial | Mantener el seguimiento a {top} y a la composición de las órdenes por canal y medio de pago. "
        "| Participación por categoría y órdenes por fuente de tráfico y medio de pago (pestaña 1). |")

    st.subheader("Detalle por categoría")
    resumen = dx.assign(cal=dx["calificacion_producto_1a5"].astype("float64"), a_tiempo=dx["dias_retraso"].eq(0)).groupby("categoria").agg(
        ordenes=("id_orden", "size"), ventas=("valor_neto_cop", lambda s: s.sum() / 1e6), ticket=("valor_neto_cop", "mean"),
        descuento=("descuento_pct", "mean"), devol=("devolucion_30d", lambda s: s.mean() * 100),
        a_tiempo=("a_tiempo", lambda s: s.mean() * 100), calif=("cal", "mean")).sort_values("ventas", ascending=False).reset_index()
    st.dataframe(resumen, hide_index=True, column_config={
        "categoria": "Categoría", "ordenes": st.column_config.NumberColumn("Órdenes", format="%d"),
        "ventas": st.column_config.NumberColumn("Ventas netas (M COP)", format="%.2f"),
        "ticket": st.column_config.NumberColumn("Ticket promedio (COP)", format="%d"),
        "descuento": st.column_config.NumberColumn("Descuento (%)", format="%.2f"),
        "devol": st.column_config.NumberColumn("Devoluciones (%)", format="%.2f"),
        "a_tiempo": st.column_config.NumberColumn("Entrega a tiempo (%)", format="%.2f"),
        "calif": st.column_config.NumberColumn("Calificación promedio", format="%.2f")})

    st.subheader("Órdenes filtradas")
    vista = dx[["id_orden", "fecha_orden", "categoria", "region", "fuente_trafico", "metodo_pago", "operador_entrega",
                "valor_neto_cop", "descuento_pct", "dias_retraso", "devolucion_30d", "calificacion_producto_1a5"]]
    vista = vista.assign(devolucion_30d=vista["devolucion_30d"].map({1: "Sí", 0: "No"}))  # más legible que 1/0
    st.dataframe(vista.head(1000), hide_index=True, column_config={
        "id_orden": "Orden", "fecha_orden": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
        "categoria": "Categoría", "region": "Región", "fuente_trafico": "Fuente de tráfico", "metodo_pago": "Medio de pago",
        "operador_entrega": "Operador", "valor_neto_cop": st.column_config.NumberColumn("Valor neto (COP)", format="$ %d"),
        "descuento_pct": st.column_config.NumberColumn("Descuento (%)", format="%.2f"),
        "dias_retraso": "Días de retraso", "devolucion_30d": "Devuelta (30 días)", "calificacion_producto_1a5": "Calificación"})
    st.caption(f"Se muestran las primeras 1.000 de {es(len(dx))} órdenes filtradas.")
    st.download_button("Descargar datos filtrados (CSV)", a_csv(dx), "ordenes_filtradas.csv", "text/csv")
