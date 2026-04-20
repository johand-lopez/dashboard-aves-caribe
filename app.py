# =============================================================================
#  Avifauna del Caribe Colombiano 2025-2026
#  Dashboard EDA — Johan Diaz & Katherin Barrera
#  Framework: Dash + Plotly  |  Tema: dark editorial
# =============================================================================

import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# PALETA
# ---------------------------------------------------------------------------
BG_DEEP     = "#0A0F0D"
BG_CARD     = "#111A14"
BG_CARD2    = "#162019"
VERDE_NEO   = "#39FF82"
VERDE_MED   = "#1DB954"
ORO         = "#F0C040"
AZUL_ACENTO = "#00C6FF"
ROJO_ACENTO = "#FF5A5F"
TEXTO_PRIM  = "#E8F5E9"
TEXTO_SEC   = "#8BA98C"
BORDE       = "#1F3424"

CATEGORICA = [VERDE_NEO, ORO, AZUL_ACENTO, ROJO_ACENTO, "#BF7FFF",
              "#FF9F45", "#00E5FF", "#FF6B9D", "#A8FF3E", "#FFD700",
              "#7FDBFF", "#FF851B", "#01FF70", "#F012BE", "#AAAAAA"]

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(family="'Rajdhani', sans-serif", color=TEXTO_PRIM, size=13),
    title_font=dict(family="'Playfair Display', serif", size=17, color=VERDE_NEO),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXTO_PRIM)),
    margin=dict(l=16, r=16, t=50, b=16),
    coloraxis_colorbar=dict(
        tickfont=dict(color=TEXTO_PRIM),
        title_font=dict(color=TEXTO_PRIM),
    ),
)

MESES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
         7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

# ---------------------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------------------
RUTA = "aves_caribe_2025_2026_limpio.csv"

try:
    datos = pd.read_csv(RUTA, encoding="utf-8", low_memory=False)
    datos["eventDate"] = pd.to_datetime(datos["eventDate"], errors="coerce")
    datos["month"]     = pd.to_numeric(datos["month"], errors="coerce").astype("Int64")
    datos["year"]      = pd.to_numeric(datos["year"],  errors="coerce").astype("Int64")
    ERROR_CARGA        = None
except Exception as e:
    datos       = pd.DataFrame()
    ERROR_CARGA = str(e)

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def opciones(serie):
    vals = sorted(serie.dropna().unique().tolist())
    return [{"label": v, "value": v} for v in vals]

def aplic_filtros(df, deptos=None, familias=None, ordenes=None, especies=None):
    if deptos:   df = df[df["stateProvince"].isin(deptos)]
    if familias: df = df[df["family"].isin(familias)]
    if ordenes:  df = df[df["order"].isin(ordenes)]
    if especies: df = df[df["species"].isin(especies)]
    return df

def ax_style(fig):
    fig.update_xaxes(gridcolor=BORDE, zerolinecolor=BORDE, tickfont=dict(color=TEXTO_SEC))
    fig.update_yaxes(gridcolor=BORDE, zerolinecolor=BORDE, tickfont=dict(color=TEXTO_SEC))
    return fig

def card(titulo, badge_texto, badge_cls, grafico):
    return html.Div([
        html.Div(style={
            "marginBottom":"12px","paddingBottom":"8px","borderBottom":f"1px solid {BORDE}"
        }, children=[
            html.Span(titulo, style={
                "color": VERDE_NEO,"fontFamily":"'Playfair Display',serif",
                "fontSize":"1.05rem","fontWeight":"700"
            }),
        ]),
        grafico,
    ], style={
        "background": BG_CARD,"border": f"1px solid {BORDE}",
        "borderRadius": "10px","padding": "20px","height":"100%",
    })

def filtro_box(children, acento=VERDE_NEO):
    return html.Div(children, style={
        "background": BG_CARD2,
        "border": f"1px solid {acento}44",
        "borderLeft": f"3px solid {acento}",
        "borderRadius":"8px","padding":"16px 20px","marginBottom":"20px",
    })

def lbl(texto):
    return html.Label(texto, style={"color":TEXTO_SEC,"fontSize":"0.78rem",
                                     "fontFamily":"'Rajdhani',sans-serif",
                                     "textTransform":"uppercase","letterSpacing":"1px"})

def empty_fig(msg="Sin datos para la seleccion"):
    f = go.Figure()
    f.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                      showarrow=False, font=dict(color=TEXTO_SEC, size=13))
    f.update_layout(**LAYOUT_BASE)
    return f

# ---------------------------------------------------------------------------
# OPCIONES DROPDOWNS (precalculadas)
# ---------------------------------------------------------------------------
if not datos.empty:
    OPT_DEPTO   = opciones(datos["stateProvince"])
    OPT_FAMILIA = opciones(datos["family"])
    OPT_ORDEN   = opciones(datos["order"])
    OPT_ESPECIE = opciones(datos["species"])
else:
    OPT_DEPTO = OPT_FAMILIA = OPT_ORDEN = OPT_ESPECIE = []

# ---------------------------------------------------------------------------
# ESTILOS CSS GLOBALES
# ---------------------------------------------------------------------------
CSS_GLOBAL = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: #0A0F0D; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0A0F0D; }
::-webkit-scrollbar-thumb { background: #1F3424; border-radius: 3px; }

/* Tabs */
.tab-custom .tab {
    background: #111A14 !important;
    border: 1px solid #1F3424 !important;
    color: #8BA98C !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.82rem !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 10px 20px !important;
    border-radius: 5px 5px 0 0 !important;
    transition: color 0.2s;
}
.tab-custom .tab--selected {
    background: #0A0F0D !important;
    border-bottom: 2px solid #39FF82 !important;
    color: #39FF82 !important;
}
.tab-custom .tab:hover { color: #E8F5E9 !important; }
.tab-custom .tab-content { background: transparent !important; border: none !important; }

/* Dropdowns */
.Select-control {
    background: #111A14 !important;
    border-color: #1F3424 !important;
    border-radius: 5px !important;
}
.Select-value-label, .Select-placeholder, .Select-input input {
    color: #E8F5E9 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.88rem !important;
}
.Select-menu-outer {
    background: #111A14 !important;
    border-color: #1F3424 !important;
    z-index: 9999 !important;
}
.Select-option { background: #111A14 !important; color: #8BA98C !important; font-family: 'Rajdhani', sans-serif !important; }
.Select-option.is-focused { background: #162019 !important; color: #39FF82 !important; }
.Select--multi .Select-value {
    background: #1F3424 !important; border-color: #39FF82 !important;
    color: #39FF82 !important; border-radius: 4px !important;
}

/* Metric cards */
.mcard {
    background: #111A14;
    border: 1px solid #1F3424;
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.mcard::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }
.mcard.g::before { background: #39FF82; }
.mcard.o::before { background: #F0C040; }
.mcard.a::before { background: #00C6FF; }
.mcard.r::before { background: #FF5A5F; }
.mval {
    font-family: 'Playfair Display', serif;
    font-size: 1.55rem; font-weight: 900; line-height: 1.1;
    margin-bottom: 4px;
}
.mlbl {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.65rem; text-transform: uppercase;
    letter-spacing: 1.5px; color: #8BA98C;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Hero */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.4rem, 3vw, 2.5rem);
    font-weight: 900; line-height: 1.15;
    background: linear-gradient(130deg, #39FF82 0%, #00C6FF 55%, #F0C040 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub {
    font-family: 'Rajdhani', sans-serif; font-size: 0.82rem;
    color: #8BA98C; text-transform: uppercase; letter-spacing: 3px; margin-top: 4px;
}
.divider {
    height: 2px;
    background: linear-gradient(90deg, #39FF82, #00C6FF, #F0C040, transparent);
    margin: 18px 0;
}

/* DataTable */
.dash-table-container .dash-spreadsheet td,
.dash-table-container .dash-spreadsheet th {
    background-color: #111A14 !important; color: #E8F5E9 !important;
    border-color: #1F3424 !important;
    font-family: 'Rajdhani', sans-serif !important; font-size: 0.83rem !important;
}
.dash-table-container .dash-spreadsheet th {
    color: #39FF82 !important; text-transform: uppercase; letter-spacing: 1px;
}

/* Boton descarga */
.btn-dl {
    background: #162019; border: 1px solid #39FF82; color: #39FF82;
    font-family: 'Rajdhani', sans-serif; font-size: 0.8rem;
    text-transform: uppercase; letter-spacing: 1.5px;
    padding: 8px 20px; border-radius: 6px; cursor: pointer;
    transition: background 0.2s;
}
.btn-dl:hover { background: #1F3424; }
"""

# ---------------------------------------------------------------------------
# APP
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Rajdhani:wght@300;400;600&display=swap"
    ],
)
app.title = "Avifauna Caribe CO"

server = app.server

app.index_string = f"""
<!DOCTYPE html>
<html>
<head>
{{%metas%}}
<title>{{%title%}}</title>
{{%favicon%}}
{{%css%}}
<style>{CSS_GLOBAL}</style>
</head>
<body>
{{%app_entry%}}
<footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# LAYOUT PRINCIPAL
# ---------------------------------------------------------------------------
app.layout = html.Div(style={"background":BG_DEEP,"minHeight":"100vh","color":TEXTO_PRIM},
children=[
    # HEADER
    html.Div(style={
        "background":f"linear-gradient(160deg, {BG_DEEP} 60%, #0D2E18 100%)",
        "borderBottom":f"1px solid {BORDE}","padding":"30px 48px 22px",
    }, children=[
        html.Div(style={"display":"flex","justifyContent":"space-between",
                        "alignItems":"flex-start","flexWrap":"wrap","gap":"16px"}, children=[
            html.Div([
                html.Div("Radiografia de la Biodiversidad Aviaria", className="hero-title"),
                html.Div("en el Caribe Colombiano · 2025 – 2026", className="hero-title",
                         style={"fontSize":"clamp(1rem,2.2vw,1.8rem)"}),
                html.Div("Caracterizacion EDA · SiB Colombia · BRISC 2025-2026", className="hero-sub"),
            ]),
            html.Div(style={"textAlign":"right"}, children=[
                html.Span("Johan Diaz", style={
                    "color":VERDE_NEO,"background":f"{VERDE_NEO}18",
                    "border":f"1px solid {VERDE_NEO}","borderRadius":"20px",
                    "padding":"4px 14px","fontFamily":"'Rajdhani',sans-serif",
                    "fontSize":"0.75rem","fontWeight":"600","textTransform":"uppercase",
                    "letterSpacing":"2px","marginRight":"8px",
                }),
                html.Span("Katherin Barrera", style={
                    "color":ORO,"background":f"{ORO}18",
                    "border":f"1px solid {ORO}","borderRadius":"20px",
                    "padding":"4px 14px","fontFamily":"'Rajdhani',sans-serif",
                    "fontSize":"0.75rem","fontWeight":"600","textTransform":"uppercase","letterSpacing":"2px",
                }),
                html.Div("Clase: Aves del Caribe", style={
                    "fontFamily":"'Rajdhani',sans-serif","fontSize":"0.72rem",
                    "color":TEXTO_SEC,"marginTop":"8px",
                }),
            ]),
        ]),
        html.Div(className="divider"),
    ]),

    # ERROR BANNER
    html.Div(id="err-banner", style={
        "display":"block" if ERROR_CARGA else "none",
        "background":"#2D0000","border":f"1px solid {ROJO_ACENTO}",
        "borderRadius":"8px","padding":"14px 20px","margin":"16px 40px 0",
        "color":ROJO_ACENTO,"fontFamily":"'Rajdhani',sans-serif","fontSize":"0.9rem",
    }, children=f"Error al cargar los datos: {ERROR_CARGA}. Ajusta la variable RUTA en app.py."),

    # CUERPO
    html.Div(style={"padding":"24px 40px 60px","maxWidth":"1600px","margin":"0 auto"}, children=[
        dcc.Tabs(id="tabs", value="inicio", className="tab-custom",
                 style={"marginBottom":"26px"}, children=[
            dcc.Tab(label="Inicio",                value="inicio"),
            dcc.Tab(label="Distribucion Espacial", value="espacial"),
            dcc.Tab(label="Analisis Taxonomico",   value="taxonomico"),
            dcc.Tab(label="Dinamica Temporal",     value="temporal"),
            dcc.Tab(label="Diversidad & Riqueza",  value="diversidad"),
            dcc.Tab(label="Explorador",            value="explorador"),
        ]),
        html.Div(id="tab-content"),
    ]),
])

# =============================================================================
# RENDER CENTRAL DE TABS
# =============================================================================
@app.callback(Output("tab-content","children"), Input("tabs","value"))
def render_tab(tab):
    if datos.empty and tab != "inicio":
        return html.P("Sin datos cargados.", style={"color":ROJO_ACENTO,"fontFamily":"'Rajdhani',sans-serif"})
    if tab == "inicio":      return layout_inicio()
    if tab == "espacial":    return layout_espacial()
    if tab == "taxonomico":  return layout_taxonomico()
    if tab == "temporal":    return layout_temporal()
    if tab == "diversidad":  return layout_diversidad()
    if tab == "explorador":  return layout_explorador()
    return html.P("Seccion no encontrada.")


# =============================================================================
# TAB INICIO — layout
# =============================================================================
def layout_inicio():
    if datos.empty:
        n_reg=n_spp=n_fam=n_dep=0; top_fam=top_dep=top_ord="N/D"
    else:
        n_reg  = len(datos)
        n_spp  = datos["species"].nunique()
        n_fam  = datos["family"].nunique()
        n_dep  = datos["stateProvince"].nunique()
        top_fam = datos["family"].value_counts().idxmax()
        top_dep = datos["stateProvince"].value_counts().idxmax()
        top_ord = datos["order"].value_counts().idxmax()

    def mc(val, lbl_txt, cls, clr):
        return html.Div([
            html.Div(val, className="mval", style={"color":clr}),
            html.Div(lbl_txt, className="mlbl"),
        ], className=f"mcard {cls}")

    return html.Div([
        # Metricas
        html.Div(style={
            "display":"grid",
            "gridTemplateColumns":"repeat(auto-fit, minmax(160px, 1fr))",
            "gap":"14px","marginBottom":"26px",
        }, children=[
            mc(f"{n_reg:,}",   "Total registros",      "g", VERDE_NEO),
            mc(f"{n_spp:,}",   "Especies unicas",       "o", ORO),
            mc(f"{n_fam}",     "Familias",              "a", AZUL_ACENTO),
            mc(f"{n_dep}",     "Departamentos",         "r", ROJO_ACENTO),
            mc(top_fam[:16],   "Familia top",           "o", ORO),
            mc(top_dep[:16],   "Depto. mas activo",     "g", VERDE_NEO),
            mc(top_ord[:16],   "Orden dominante",       "a", AZUL_ACENTO),
        ]),

        card("Resumen Ejecutivo", "Ambos", "johan", html.Div([
            html.P([
                html.Strong("La ciencia ciudadana ", style={"color":VERDE_NEO}),
                "representa hoy una de las fuentes mas democraticas y escalables para el "
                "monitoreo de biodiversidad. Plataformas como ",
                html.Strong("SiB Colombia ", style={"color":ORO}),
                "agregan observaciones de naturalistas, ornitologos aficionados y comunidades "
                "locales, construyendo registros abiertos que antes solo existian en expediciones academicas.",
            ], style={"marginBottom":"12px","lineHeight":"1.8",
                      "fontFamily":"'Rajdhani',sans-serif","fontSize":"0.95rem"}),
            html.P([
                "El Caribe colombiano alberga una riqueza aviaria excepcional: humedales costeros, "
                "bosques secos, manglares y ",
                html.Strong("corredores de migracion ", style={"color":AZUL_ACENTO}),
                "convergen en un territorio que actua como nodo critico del flyway americano. "
                "Este dashboard analiza ",
                html.Strong(f"{n_reg:,} registros de {n_spp:,} especies ", style={"color":VERDE_NEO}),
                "reportados entre 2025 y 2026, caracterizando taxonomia, distribucion espacial, "
                "dinamica temporal y diversidad de la avifauna regional.",
            ], style={"lineHeight":"1.8","fontFamily":"'Rajdhani',sans-serif","fontSize":"0.95rem"}),
        ])),
    ])


# =============================================================================
# TAB ESPACIAL — layout + callback
# =============================================================================
def layout_espacial():
    return html.Div([
        filtro_box([
            html.Div("Filtros — Distribucion Espacial", style={
                "color":VERDE_NEO,"fontFamily":"'Rajdhani',sans-serif",
                "textTransform":"uppercase","letterSpacing":"2px","marginBottom":"10px","fontSize":"0.78rem"
            }),
            html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"14px"}, children=[
                html.Div([lbl("Departamento"),
                          dcc.Dropdown(id="esp-dep", options=OPT_DEPTO, multi=True,
                                        placeholder="Todos", style={"marginTop":"4px"})]),
                html.Div([lbl("Familia"),
                          dcc.Dropdown(id="esp-fam", options=OPT_FAMILIA, multi=True,
                                        placeholder="Todas", style={"marginTop":"4px"})]),
            ]),
        ]),
        html.Div(style={"display":"grid","gridTemplateColumns":"2fr 1fr","gap":"20px"}, children=[
            card("Mapa de Densidad — Avistamientos", "Johan", "johan",
                 dcc.Graph(id="esp-mapa", config={"scrollZoom":True}, style={"height":"500px"})),
            card("Registros por Departamento", "Katherin", "katherin",
                 dcc.Graph(id="esp-bar-dep", config={"displayModeBar":False}, style={"height":"500px"})),
        ]),
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr 1fr","gap":"20px","marginTop":"4px"}, children=[
            card("Dispersion Geografica — Top 8 Familias", "Johan", "johan",
                 dcc.Graph(id="esp-scatter", config={"scrollZoom":True}, style={"height":"420px"})),
            card("Top 10 Localidades con mas Avistamientos", "Katherin", "katherin",
                 dcc.Graph(id="esp-localidades", config={"displayModeBar":False}, style={"height":"420px"})),
            card("Tipo de Registro (basisOfRecord)", "Katherin", "katherin",
                 dcc.Graph(id="esp-basis", config={"displayModeBar":False}, style={"height":"420px"})),
        ]),
    ])

@app.callback(
    Output("esp-mapa","figure"), Output("esp-bar-dep","figure"),
    Output("esp-scatter","figure"), Output("esp-localidades","figure"),
    Output("esp-basis","figure"),
    Input("esp-dep","value"), Input("esp-fam","value"),
)
def cb_espacial(deptos, familias):
    df = aplic_filtros(datos.copy(), deptos=deptos, familias=familias)
    dm = df.dropna(subset=["decimalLatitude","decimalLongitude"])

    # Mapa densidad
    if dm.empty:
        fig_map = empty_fig("Sin coordenadas para los filtros seleccionados")
    else:
        fig_map = px.density_mapbox(dm, lat="decimalLatitude", lon="decimalLongitude",
                                     radius=14, zoom=6,
                                     center=dict(lat=10.4, lon=-74.8),
                                     mapbox_style="carto-darkmatter", opacity=0.55,
                                     color_continuous_scale=[[0,"#0A0F0D"],[0.3,VERDE_MED],[0.7,VERDE_NEO],[1,ORO]],
                                     title="Concentracion geografica de avistamientos")
        fig_map.update_layout(**LAYOUT_BASE)

    # Barras dep (horizontal)
    dc = df["stateProvince"].value_counts().reset_index()
    dc.columns = ["Departamento","n"]
    fig_dep = px.bar(dc, y="Departamento", x="n", orientation="h",
                      color="n", color_continuous_scale=[[0,AZUL_ACENTO],[1,VERDE_NEO]],
                      title="Registros por departamento")
    fig_dep.update_layout(**LAYOUT_BASE, coloraxis_showscale=False,
                           yaxis={"categoryorder":"total ascending"})
    ax_style(fig_dep)

    # Scatter geo top 8 familias
    t8 = df["family"].value_counts().head(8).index.tolist()
    ds = dm[dm["family"].isin(t8)].dropna(subset=["family"])
    if ds.empty:
        fig_sc = empty_fig()
    else:
        muestra = ds.sample(min(len(ds), 3000), random_state=42)
        fig_sc = px.scatter_mapbox(muestra, lat="decimalLatitude", lon="decimalLongitude",
                                    color="family", color_discrete_sequence=CATEGORICA,
                                    zoom=5, center=dict(lat=10.4, lon=-74.8),
                                    mapbox_style="carto-darkmatter", opacity=0.75,
                                    title="Dispersion por familia (muestra 3k pt.)")
        fig_sc.update_layout(**LAYOUT_BASE)

    # Top 10 localidades
    lc = df["locality"].value_counts().head(10).reset_index()
    lc.columns = ["Localidad","n"]
    lc = lc.sort_values("n", ascending=True)
    fig_loc = px.bar(lc, x="n", y="Localidad", orientation="h",
                      color="n", color_continuous_scale=[[0,ROJO_ACENTO],[0.5,ORO],[1,VERDE_NEO]],
                      title="Top 10 localidades con mas avistamientos",
                      labels={"n":"Registros","Localidad":""})
    fig_loc.update_layout(**LAYOUT_BASE, coloraxis_showscale=False)
    ax_style(fig_loc)

    # Pie basisOfRecord
    bc = df["basisOfRecord"].value_counts().reset_index()
    bc.columns = ["Tipo","n"]
    if bc.empty:
        fig_basis = empty_fig()
    else:
        fig_basis = px.pie(bc, names="Tipo", values="n", hole=0.50,
                            color_discrete_sequence=CATEGORICA,
                            title="Tipo de registro (basisOfRecord)")
        fig_basis.update_layout(**LAYOUT_BASE)
        fig_basis.update_traces(textinfo="percent+label", textfont_color=TEXTO_PRIM)

    return fig_map, fig_dep, fig_sc, fig_loc, fig_basis


# =============================================================================
# TAB TAXONOMICO — layout + callback
# =============================================================================
def layout_taxonomico():
    return html.Div([
        filtro_box([
            html.Div("Filtros — Analisis Taxonomico", style={
                "color":ORO,"fontFamily":"'Rajdhani',sans-serif",
                "textTransform":"uppercase","letterSpacing":"2px","marginBottom":"10px","fontSize":"0.78rem"
            }),
            html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr 1fr","gap":"14px"}, children=[
                html.Div([lbl("Orden"),
                          dcc.Dropdown(id="tax-ord", options=OPT_ORDEN, multi=True,
                                        placeholder="Todos", style={"marginTop":"4px"})]),
                html.Div([lbl("Familia"),
                          dcc.Dropdown(id="tax-fam", options=OPT_FAMILIA, multi=True,
                                        placeholder="Todas", style={"marginTop":"4px"})]),
                html.Div([lbl("Departamento"),
                          dcc.Dropdown(id="tax-dep", options=OPT_DEPTO, multi=True,
                                        placeholder="Todos", style={"marginTop":"4px"})]),
            ]),
        ], acento=ORO),
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"20px"}, children=[
            card("Top 15 Especies mas Reportadas", "Johan", "johan",
                 dcc.Graph(id="tax-bar-sp", config={"displayModeBar":False}, style={"height":"500px"})),
            card("Composicion Orden → Familia (Sunburst)", "Katherin", "katherin",
                 dcc.Graph(id="tax-sun", config={"displayModeBar":False}, style={"height":"500px"})),
        ]),
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"20px","marginTop":"4px"}, children=[
            card("Abundancia de Familias — Treemap", "Johan", "johan",
                 dcc.Graph(id="tax-tree", config={"displayModeBar":False}, style={"height":"420px"})),
            card("Riqueza Especifica por Familia — Barras (top 15)", "Katherin", "katherin",
                 dcc.Graph(id="tax-riq", config={"displayModeBar":False}, style={"height":"420px"})),
        ]),
    ])

@app.callback(
    Output("tax-bar-sp","figure"), Output("tax-sun","figure"),
    Output("tax-tree","figure"),   Output("tax-riq","figure"),
    Input("tax-ord","value"), Input("tax-fam","value"), Input("tax-dep","value"),
)
def cb_taxonomico(ordenes, familias, deptos):
    df = aplic_filtros(datos.copy(), deptos=deptos, familias=familias, ordenes=ordenes)

    # Top 15 especies horizontal (alta cardinalidad)
    t15 = df["species"].value_counts().head(15).reset_index()
    t15.columns = ["Especie","n"]
    t15 = t15.sort_values("n", ascending=True)
    fig_sp = px.bar(t15, x="n", y="Especie", orientation="h",
                     color="n", color_continuous_scale=[[0,AZUL_ACENTO],[0.5,VERDE_MED],[1,VERDE_NEO]],
                     title="Top 15 especies por numero de observaciones",
                     labels={"n":"Registros","Especie":""})
    fig_sp.update_layout(**LAYOUT_BASE, coloraxis_showscale=False); ax_style(fig_sp)

    # Sunburst orden -> familia
    agg = df.dropna(subset=["order","family"]).groupby(["order","family"]).size().reset_index(name="n")
    if agg.empty:
        fig_sun = empty_fig()
    else:
        fig_sun = px.sunburst(agg, path=["order","family"], values="n",
                               color="n", color_continuous_scale=[[0,BG_DEEP],[0.4,VERDE_MED],[1,VERDE_NEO]],
                               title="Composicion Orden → Familia")
        fig_sun.update_layout(**LAYOUT_BASE, coloraxis_showscale=False)
        fig_sun.update_traces(textfont_color=TEXTO_PRIM)

    # Treemap familias
    fc = df["family"].value_counts().head(20).reset_index()
    fc.columns = ["Familia","n"]
    if fc.empty:
        fig_tree = empty_fig()
    else:
        fig_tree = px.treemap(fc, path=["Familia"], values="n",
                               color="n", color_continuous_scale=[[0,BG_CARD],[0.4,AZUL_ACENTO],[1,ORO]],
                               title="Abundancia relativa — top 20 familias")
        fig_tree.update_layout(**LAYOUT_BASE, coloraxis_showscale=False)
        fig_tree.update_traces(textfont=dict(color=TEXTO_PRIM, size=12))

    # Riqueza por familia (barras verticales — <= 15 items, cardinalidad baja)
    riq = (df.groupby("family")["species"].nunique()
             .sort_values(ascending=False).head(15).reset_index())
    riq.columns = ["Familia","sp_unicas"]
    fig_riq = px.bar(riq, x="Familia", y="sp_unicas",
                      color="sp_unicas", color_continuous_scale=[[0,AZUL_ACENTO],[1,ORO]],
                      title="Riqueza especifica por familia (top 15)",
                      labels={"sp_unicas":"Especies unicas","Familia":""})
    fig_riq.update_layout(**LAYOUT_BASE, coloraxis_showscale=False); ax_style(fig_riq)
    fig_riq.update_xaxes(tickangle=-35)

    return fig_sp, fig_sun, fig_tree, fig_riq


# =============================================================================
# TAB TEMPORAL — layout + callback
# =============================================================================
def layout_temporal():
    return html.Div([
        filtro_box([
            html.Div("Filtros — Dinamica Temporal", style={
                "color":AZUL_ACENTO,"fontFamily":"'Rajdhani',sans-serif",
                "textTransform":"uppercase","letterSpacing":"2px","marginBottom":"10px","fontSize":"0.78rem"
            }),
            html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"14px"}, children=[
                html.Div([lbl("Departamento"),
                          dcc.Dropdown(id="tmp-dep", options=OPT_DEPTO, multi=True,
                                        placeholder="Todos", style={"marginTop":"4px"})]),
                html.Div([lbl("Familia"),
                          dcc.Dropdown(id="tmp-fam", options=OPT_FAMILIA, multi=True,
                                        placeholder="Todas", style={"marginTop":"4px"})]),
            ]),
        ], acento=AZUL_ACENTO),
        html.Div(style={"display":"grid","gridTemplateColumns":"2fr 1fr","gap":"20px"}, children=[
            card("Evolucion Mensual de Avistamientos", "Johan", "johan",
                 dcc.Graph(id="tmp-linea", config={"displayModeBar":False}, style={"height":"380px"})),
            card("Distribucion Diaria por Mes — Violin", "Katherin", "katherin",
                 dcc.Graph(id="tmp-violin", config={"displayModeBar":False}, style={"height":"380px"})),
        ]),
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"20px","marginTop":"4px"}, children=[
            card("Heatmap Estacional — Mes x Ano", "Johan", "johan",
                 dcc.Graph(id="tmp-heat", config={"displayModeBar":False}, style={"height":"320px"})),
            card("Acumulado Mensual Comparativo", "Katherin", "katherin",
                 dcc.Graph(id="tmp-area", config={"displayModeBar":False}, style={"height":"320px"})),
        ]),
    ])

@app.callback(
    Output("tmp-linea","figure"), Output("tmp-violin","figure"),
    Output("tmp-heat","figure"),  Output("tmp-area","figure"),
    Input("tmp-dep","value"), Input("tmp-fam","value"),
)
def cb_temporal(deptos, familias):
    df = aplic_filtros(datos.copy(), deptos=deptos, familias=familias)
    df = df.dropna(subset=["year","month"])
    df["year"]  = df["year"].astype(int)
    df["month"] = df["month"].astype(int)

    if df.empty:
        e = empty_fig()
        return e, e, e, e

    # Linea mensual por ano
    s = df.groupby(["year","month"]).size().reset_index(name="n")
    s["mes"]    = s["month"].map(MESES)
    s["yr_str"] = s["year"].astype(str)
    s = s.sort_values(["year","month"])
    fig_lin = px.line(s, x="mes", y="n", color="yr_str", markers=True, line_shape="spline",
                       color_discrete_map={"2025":VERDE_NEO,"2026":ORO},
                       title="Avistamientos mensuales — 2025 vs 2026",
                       labels={"mes":"","n":"Registros","yr_str":"Año"},
                       category_orders={"mes":list(MESES.values())})
    fig_lin.update_traces(line_width=2.5, marker_size=7)
    fig_lin.update_layout(**LAYOUT_BASE); ax_style(fig_lin)
    fig_lin.update_xaxes(tickangle=-25)

    # Violin distribución diaria
    diario = df.groupby(["year","month","day"]).size().reset_index(name="cnt")
    diario["mes"] = diario["month"].map(MESES)
    fig_vio = px.violin(diario, x="mes", y="cnt", box=True, points=False,
                         color_discrete_sequence=[AZUL_ACENTO],
                         title="Distribucion diaria de registros por mes",
                         labels={"mes":"","cnt":"Registros/dia"},
                         category_orders={"mes":list(MESES.values())})
    fig_vio.update_layout(**LAYOUT_BASE); ax_style(fig_vio)

    # Heatmap
    piv = (df.groupby(["year","month"]).size().reset_index(name="n")
             .pivot(index="year", columns="month", values="n").fillna(0))
    fig_heat = go.Figure(go.Heatmap(
        z=piv.values, x=[MESES[m] for m in piv.columns], y=piv.index.astype(str),
        colorscale=[[0,BG_DEEP],[0.3,VERDE_MED],[0.7,VERDE_NEO],[1,ORO]],
        showscale=True,
        colorbar=dict(tickfont=dict(color=TEXTO_PRIM),
                      title=dict(text="n",font=dict(color=TEXTO_PRIM))),
    ))
    fig_heat.update_layout(**LAYOUT_BASE, title="Registros por mes y ano"); ax_style(fig_heat)

    # Area acumulada
    ac = df.groupby(["year","month"]).size().reset_index(name="n")
    ac = ac.sort_values(["year","month"])
    ac["acum"] = ac.groupby("year")["n"].cumsum()
    ac["mes"]   = ac["month"].map(MESES)
    ac["yr_str"]= ac["year"].astype(str)
    fig_area = px.area(ac, x="mes", y="acum", color="yr_str", line_shape="spline",
                        color_discrete_map={"2025":VERDE_NEO,"2026":ORO},
                        title="Registros acumulados por mes",
                        labels={"mes":"","acum":"Acumulado","yr_str":"Año"},
                        category_orders={"mes":list(MESES.values())})
    fig_area.update_layout(**LAYOUT_BASE); ax_style(fig_area)

    return fig_lin, fig_vio, fig_heat, fig_area


# =============================================================================
# TAB DIVERSIDAD — layout + callback
# =============================================================================
def layout_diversidad():
    return html.Div([
        filtro_box([
            html.Div("Filtros — Diversidad & Riqueza", style={
                "color":ROJO_ACENTO,"fontFamily":"'Rajdhani',sans-serif",
                "textTransform":"uppercase","letterSpacing":"2px","marginBottom":"10px","fontSize":"0.78rem"
            }),
            html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"14px"}, children=[
                html.Div([lbl("Departamento"),
                          dcc.Dropdown(id="div-dep", options=OPT_DEPTO, multi=True,
                                        placeholder="Todos", style={"marginTop":"4px"})]),
                html.Div([lbl("Orden"),
                          dcc.Dropdown(id="div-ord", options=OPT_ORDEN, multi=True,
                                        placeholder="Todos", style={"marginTop":"4px"})]),
            ]),
        ], acento=ROJO_ACENTO),
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"20px"}, children=[
            card("Riqueza de Especies por Departamento", "Johan", "johan",
                 dcc.Graph(id="div-riq-dep", config={"displayModeBar":False}, style={"height":"420px"})),
            card("Curva Rango-Abundancia (Whittaker)", "Katherin", "katherin",
                 dcc.Graph(id="div-rank", config={"displayModeBar":False}, style={"height":"420px"})),
        ]),
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"20px","marginTop":"4px"}, children=[
            card("Top 10 Ordenes por Numero de Registros", "Johan", "johan",
                 dcc.Graph(id="div-bar-ord", config={"displayModeBar":False}, style={"height":"380px"})),
            card("Generos mas Representados — Barras (top 12)", "Katherin", "katherin",
                 dcc.Graph(id="div-genero", config={"displayModeBar":False}, style={"height":"380px"})),
        ]),
    ])

@app.callback(
    Output("div-riq-dep","figure"), Output("div-rank","figure"),
    Output("div-bar-ord","figure"), Output("div-genero","figure"),
    Input("div-dep","value"), Input("div-ord","value"),
)
def cb_diversidad(deptos, ordenes):
    df = aplic_filtros(datos.copy(), deptos=deptos, ordenes=ordenes)

    # Riqueza por depto (horizontal)
    rd = (df.groupby("stateProvince")["species"].nunique()
            .sort_values(ascending=True).reset_index())
    rd.columns = ["Departamento","sp"]
    fig_rd = px.bar(rd, x="sp", y="Departamento", orientation="h",
                     color="sp", color_continuous_scale=[[0,ROJO_ACENTO],[0.5,ORO],[1,VERDE_NEO]],
                     title="Riqueza especifica por departamento",
                     labels={"sp":"Especies unicas","Departamento":""})
    fig_rd.update_layout(**LAYOUT_BASE, coloraxis_showscale=False); ax_style(fig_rd)

    # Rango-abundancia (scatter con eje log)
    sc = df["species"].value_counts().reset_index()
    sc.columns = ["sp","n"]
    sc["rango"] = range(1, len(sc)+1)
    sc["log_n"] = np.log10(sc["n"].clip(lower=1))
    fig_ra = px.scatter(sc, x="rango", y="log_n", hover_name="sp",
                         hover_data={"n":True,"rango":False},
                         color="log_n", color_continuous_scale=[[0,AZUL_ACENTO],[0.5,VERDE_NEO],[1,ORO]],
                         title="Curva rango-abundancia (escala log)",
                         labels={"rango":"Rango de abundancia","log_n":"log₁₀(Registros)"})
    fig_ra.update_traces(marker_size=4, marker_opacity=0.65)
    fig_ra.update_layout(**LAYOUT_BASE, coloraxis_showscale=False)
    fig_ra.update_xaxes(type="log", gridcolor=BORDE, tickfont=dict(color=TEXTO_SEC))
    fig_ra.update_yaxes(gridcolor=BORDE, tickfont=dict(color=TEXTO_SEC))

    # Barras horizontales top 10 ordenes (reemplaza donut)
    oc = df["order"].value_counts().head(10).reset_index()
    oc.columns = ["Orden","n"]
    oc = oc.sort_values("n", ascending=True)
    fig_ord = px.bar(oc, x="n", y="Orden", orientation="h",
                      color="n", color_continuous_scale=[[0,AZUL_ACENTO],[0.5,VERDE_MED],[1,VERDE_NEO]],
                      title="Top 10 ordenes por numero de registros",
                      labels={"n":"Registros","Orden":""})
    fig_ord.update_layout(**LAYOUT_BASE, coloraxis_showscale=False); ax_style(fig_ord)

    # Barras genero (media cardinalidad -> vertical top 12)
    gc = df["genus"].value_counts().head(12).reset_index()
    gc.columns = ["Genero","n"]
    fig_gen = px.bar(gc, x="Genero", y="n",
                      color="n", color_continuous_scale=[[0,AZUL_ACENTO],[1,ROJO_ACENTO]],
                      title="Generos mas representados (top 12)",
                      labels={"n":"Registros","Genero":""})
    fig_gen.update_layout(**LAYOUT_BASE, coloraxis_showscale=False); ax_style(fig_gen)
    fig_gen.update_xaxes(tickangle=-35)

    return fig_rd, fig_ra, fig_ord, fig_gen


# =============================================================================
# TAB EXPLORADOR — layout + callbacks
# =============================================================================
def layout_explorador():
    return html.Div([
        filtro_box([
            html.Div("Filtros — Explorador de Datos", style={
                "color":TEXTO_PRIM,"fontFamily":"'Rajdhani',sans-serif",
                "textTransform":"uppercase","letterSpacing":"2px","marginBottom":"10px","fontSize":"0.78rem"
            }),
            html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr 1fr","gap":"14px"}, children=[
                html.Div([lbl("Departamento"),
                          dcc.Dropdown(id="exp-dep", options=OPT_DEPTO, multi=True,
                                        placeholder="Todos", style={"marginTop":"4px"})]),
                html.Div([lbl("Familia"),
                          dcc.Dropdown(id="exp-fam", options=OPT_FAMILIA, multi=True,
                                        placeholder="Todas", style={"marginTop":"4px"})]),
                html.Div([lbl("Especie"),
                          dcc.Dropdown(id="exp-sp", options=OPT_ESPECIE, multi=True,
                                        placeholder="Todas", style={"marginTop":"4px"})]),
            ]),
            html.Div(style={"marginTop":"14px","display":"flex","gap":"12px","flexWrap":"wrap","alignItems":"center"}, children=[
                html.Button("Descargar seleccion CSV", id="btn-dl", className="btn-dl"),
                dcc.Download(id="dl-csv"),
                html.Span(id="exp-cnt", style={
                    "color":TEXTO_SEC,"fontFamily":"'Rajdhani',sans-serif","fontSize":"0.82rem"
                }),
            ]),
        ]),
        html.Div(id="exp-tabla"),
    ])

@app.callback(
    Output("exp-tabla","children"), Output("exp-cnt","children"),
    Input("exp-dep","value"), Input("exp-fam","value"), Input("exp-sp","value"),
)
def cb_explorador(deptos, familias, especies):
    df = aplic_filtros(datos.copy(), deptos=deptos, familias=familias, especies=especies)
    cols = ["species","family","order","genus","scientificName","stateProvince",
            "locality","decimalLatitude","decimalLongitude","eventDate","basisOfRecord"]
    cols_ok = [c for c in cols if c in df.columns]
    df_s = df[cols_ok].head(2000).reset_index(drop=True)

    tabla = dash_table.DataTable(
        data=df_s.to_dict("records"),
        columns=[{"name":c,"id":c} for c in cols_ok],
        page_size=20, sort_action="native", filter_action="native",
        style_table={"overflowX":"auto"},
        style_cell={
            "backgroundColor":BG_CARD,"color":TEXTO_PRIM,
            "border":f"1px solid {BORDE}",
            "fontFamily":"'Rajdhani',sans-serif","fontSize":"0.82rem",
            "padding":"7px 12px","textAlign":"left",
        },
        style_header={
            "backgroundColor":BG_CARD2,"color":VERDE_NEO,
            "fontWeight":"600","border":f"1px solid {BORDE}",
            "textTransform":"uppercase","letterSpacing":"1px",
        },
        style_data_conditional=[{"if":{"row_index":"odd"},"backgroundColor":"#0D1710"}],
    )
    cnt = f"Mostrando {len(df_s):,} de {len(df):,} registros (maximo 2000 en vista)"
    return tabla, cnt

@app.callback(
    Output("dl-csv","data"),
    Input("btn-dl","n_clicks"),
    State("exp-dep","value"), State("exp-fam","value"), State("exp-sp","value"),
    prevent_initial_call=True,
)
def cb_descargar(_, deptos, familias, especies):
    df = aplic_filtros(datos.copy(), deptos=deptos, familias=familias, especies=especies)
    return dcc.send_data_frame(df.to_csv, "aves_caribe_seleccion.csv", index=False)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
