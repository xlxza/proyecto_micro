import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS CSS
# ==============================================================================
st.set_page_config(
    page_title="Hong Kong: Vivir en una Caja | Microeconomía",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados para tarjetas de alerta y diseño limpio
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .alert-box-red {
        background-color: #FEF2F2;
        border-left: 6px solid #EF4444;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #991B1B;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .alert-box-yellow {
        background-color: #FFFBEB;
        border-left: 6px solid #F59E0B;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #92400E;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .alert-box-green {
        background-color: #F0FDF4;
        border-left: 6px solid #22C55E;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #166534;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# CARGA DE DATOS ROBUSTA CON CACHÉ
# ==============================================================================
@st.cache_data
def cargar_datos():
    """
    Carga los datasets macroeconómicos y microeconómicos locales
    respetando el separador ';' y el marcador decimal ','.
    """
    try:
        df_macro = pd.read_csv('hong_kong_guatemala_macro_es.csv', sep=';', decimal=',')
        df_micro = pd.read_csv('hong_kong_housing_micro_es.csv', sep=';', decimal=',')
        
        # Asegurar tipos numéricos adecuados
        cols_num_macro = ['Anio', 'Inflacion_IPC_Pct', 'PIB_Per_Capita_USD', 
                          'Indice_Gini', 'Subindice_Vivienda_Alimentos_Pct']
        for col in cols_num_macro:
            df_macro[col] = pd.to_numeric(df_macro[col])
            
        cols_num_micro = ['Anio', 'Ingreso_Decil_1_HKD', 'Renta_Coffin_Home_HKD', 
                          'Renta_Subdividido_HKD', 'Renta_Publica_HKD', 
                          'Esfuerzo_Coffin_Pct', 'Esfuerzo_Subdiv_Pct', 
                          'Espera_Vivienda_Publica_Anios']
        for col in cols_num_micro:
            df_micro[col] = pd.to_numeric(df_micro[col])
            
        return df_macro, df_micro
    except FileNotFoundError as e:
        st.error(f"Error crítico: No se encontró uno de los archivos CSV en el directorio './'. Detalle: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error inesperado al procesar los archivos CSV: {e}")
        st.stop()

df_macro, df_micro = cargar_datos()

# ==============================================================================
# BARRA LATERAL (SIDEBAR) E INFORMACIÓN CONTEXTUAL
# ==============================================================================
with st.sidebar:
    st.markdown("## 🏙️ Caso de Estudio")
    st.markdown("**Hong Kong: VIVIR EN UNA CAJA**")
    st.caption("El Algoritmo de las *Coffin Homes* y su Espejo Estructural con Guatemala.")
    st.divider()
    
    st.markdown("### 🎛️ Filtro Temporal Global")
    min_anio = int(df_macro['Anio'].min())
    max_anio = int(df_macro['Anio'].max())
    rango_anios = st.slider(
        "Seleccione el rango de años (2019 - 2026):",
        min_value=min_anio,
        max_value=max_anio,
        value=(min_anio, max_anio),
        step=1
    )
    
    st.divider()
    st.markdown("### 📌 Resumen Metodológico")
    st.info(
        "Esta herramienta modela cómo la rigidez de oferta inmobiliaria y la inflación en bienes "
        "esenciales acorralan el conjunto presupuestario del Decil 1 en Hong Kong, forzando la "
        "demanda inelástica de habitáculos de menos de 2 m² (*Coffin Homes*)."
    )

# Filtrado global según el rango de años seleccionado
df_macro_filt = df_macro[(df_macro['Anio'] >= rango_anios[0]) & (df_macro['Anio'] <= rango_anios[1])].copy()
df_micro_filt = df_micro[(df_micro['Anio'] >= rango_anios[0]) & (df_micro['Anio'] <= rango_anios[1])].copy()

# ==============================================================================
# ENCABEZADO PRINCIPAL
# ==============================================================================
st.markdown('<div class="main-header">🏙️ Hong Kong: VIVIR EN UNA CAJA — El Algoritmo de las Coffin Homes</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Laboratorio Interactivo de Microeconomía Cuantitativa: Teoría del Consumidor, Rigidez de Oferta y Espejo Macroeconómico con Guatemala</div>', unsafe_allow_html=True)

# Estructura multipestaña solicitada
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Pestaña 1: Fase 1 y 4 - Radiografía Macro y Espejo Guatemala",
    "📐 Pestaña 2: Fase 2 - Impacto Microeconómico y Recta Presupuestaria",
    "⚖️ Pestaña 3: Fase 2 y 3 - Modelado de Mercado y Elasticidad",
    "🗂️ Pestaña 4: Fase 3 - Explorador y Segmentación de Datos"
])

# ==============================================================================
# PESTAÑA 1: RADIOGRAFÍA MACRO Y ESPEJO GUATEMALA
# ==============================================================================
with tab1:
    st.subheader(f"📊 Comparativa Macroeconómica: Hong Kong vs. Guatemala ({rango_anios[0]} - {rango_anios[1]})")
    
    # Obtener el último año disponible dentro del filtro seleccionado
    ultimo_anio = rango_anios[1]
    datos_hk_ult = df_macro[(df_macro['Pais'] == 'Hong Kong') & (df_macro['Anio'] == ultimo_anio)].iloc[0]
    datos_gt_ult = df_macro[(df_macro['Pais'] == 'Guatemala') & (df_macro['Anio'] == ultimo_anio)].iloc[0]
    
    # Obtener año inicial del filtro para calcular variaciones
    primer_anio = rango_anios[0]
    datos_hk_ini = df_macro[(df_macro['Pais'] == 'Hong Kong') & (df_macro['Anio'] == primer_anio)].iloc[0]
    datos_gt_ini = df_macro[(df_macro['Pais'] == 'Guatemala') & (df_macro['Anio'] == primer_anio)].iloc[0]

    st.markdown(f"#### Tarjetas KPI Comparativas (Corte al año {ultimo_anio})")
    col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5, col_kpi6 = st.columns(6)
    
    with col_kpi1:
        delta_pib_hk = ((datos_hk_ult['PIB_Per_Capita_USD'] - datos_hk_ini['PIB_Per_Capita_USD']) / datos_hk_ini['PIB_Per_Capita_USD']) * 100
        st.metric(
            label="🇭🇰 PIB per Cápita (HK)",
            value=f"${datos_hk_ult['PIB_Per_Capita_USD']:,.0f}",
            delta=f"{delta_pib_hk:+.1f}% vs {primer_anio}"
        )
    with col_kpi2:
        delta_pib_gt = ((datos_gt_ult['PIB_Per_Capita_USD'] - datos_gt_ini['PIB_Per_Capita_USD']) / datos_gt_ini['PIB_Per_Capita_USD']) * 100
        st.metric(
            label="🇬🇹 PIB per Cápita (GT)",
            value=f"${datos_gt_ult['PIB_Per_Capita_USD']:,.0f}",
            delta=f"{delta_pib_gt:+.1f}% vs {primer_anio}"
        )
    with col_kpi3:
        delta_inf_hk = datos_hk_ult['Inflacion_IPC_Pct'] - datos_hk_ini['Inflacion_IPC_Pct']
        st.metric(
            label="🇭🇰 Inflación IPC (HK)",
            value=f"{datos_hk_ult['Inflacion_IPC_Pct']:.1f}%",
            delta=f"{delta_inf_hk:+.1f} pp vs {primer_anio}",
            delta_color="inverse"
        )
    with col_kpi4:
        delta_inf_gt = datos_gt_ult['Inflacion_IPC_Pct'] - datos_gt_ini['Inflacion_IPC_Pct']
        st.metric(
            label="🇬🇹 Inflación IPC (GT)",
            value=f"{datos_gt_ult['Inflacion_IPC_Pct']:.1f}%",
            delta=f"{delta_inf_gt:+.1f} pp vs {primer_anio}",
            delta_color="inverse"
        )
    with col_kpi5:
        delta_gini_hk = datos_hk_ult['Indice_Gini'] - datos_hk_ini['Indice_Gini']
        st.metric(
            label="🇭🇰 Índice de Gini (HK)",
            value=f"{datos_hk_ult['Indice_Gini']:.3f}",
            delta=f"{delta_gini_hk:+.3f} vs {primer_anio}",
            delta_color="inverse"
        )
    with col_kpi6:
        delta_gini_gt = datos_gt_ult['Indice_Gini'] - datos_gt_ini['Indice_Gini']
        st.metric(
            label="🇬🇹 Índice de Gini (GT)",
            value=f"{datos_gt_ult['Indice_Gini']:.3f}",
            delta=f"{delta_gini_gt:+.3f} vs {primer_anio}",
            delta_color="inverse"
        )

    st.divider()

    # Gráficos interactivos de evolución temporal
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_pib = px.line(
            df_macro_filt,
            x="Anio",
            y="PIB_Per_Capita_USD",
            color="Pais",
            markers=True,
            title="Evolución del PIB per Cápita (USD Nominales)",
            labels={"Anio": "Año", "PIB_Per_Capita_USD": "PIB per Cápita (USD)", "Pais": "Economía"},
            color_discrete_map={"Hong Kong": "#E11D48", "Guatemala": "#0284C7"}
        )
        fig_pib.update_layout(hovermode="x unified", template="plotly_white")
        st.plotly_chart(fig_pib, use_container_width=True)

    with col_g2:
        fig_gini = px.line(
            df_macro_filt,
            x="Anio",
            y="Indice_Gini",
            color="Pais",
            markers=True,
            title="Curva de Desigualdad de Ingresos (Índice de Gini)",
            labels={"Anio": "Año", "Indice_Gini": "Coeficiente de Gini", "Pais": "Economía"},
            color_discrete_map={"Hong Kong": "#E11D48", "Guatemala": "#0284C7"}
        )
        fig_gini.add_hline(
            y=0.50, line_dash="dash", line_color="gray",
            annotation_text="Umbral de Desigualdad Severa (0.50)", annotation_position="bottom right"
        )
        fig_gini.update_layout(hovermode="x unified", template="plotly_white")
        st.plotly_chart(fig_gini, use_container_width=True)

    # Gráfico de Inflación General vs Subíndice de Vivienda y Alimentos
    st.markdown("#### Dinámica Inflacionaria: IPC General vs. Subíndice de Vivienda y Alimentos")
    df_inflacion_melt = df_macro_filt.melt(
        id_vars=['Anio', 'Pais'],
        value_vars=['Inflacion_IPC_Pct', 'Subindice_Vivienda_Alimentos_Pct'],
        var_name='Tipo_Indicador',
        value_name='Tasa_Pct'
    )
    df_inflacion_melt['Tipo_Indicador'] = df_inflacion_melt['Tipo_Indicador'].replace({
        'Inflacion_IPC_Pct': 'IPC General (%)',
        'Subindice_Vivienda_Alimentos_Pct': 'Subíndice Vivienda y Alimentos (%)'
    })

    fig_inf = px.line(
        df_inflacion_melt,
        x="Anio",
        y="Tasa_Pct",
        color="Tipo_Indicador",
        facet_col="Pais",
        markers=True,
        title="Comparativa de Inflación General frente al Costo de Bienes Esenciales (Vivienda y Alimentos)",
        labels={"Anio": "Año", "Tasa_Pct": "Variación Anual (%)", "Tipo_Indicador": "Indicador"},
        color_discrete_sequence=["#475569", "#EA580C"]
    )
    fig_inf.update_layout(hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig_inf, use_container_width=True)

    # Sección de análisis automatizado
    ratio_pib = datos_hk_ult['PIB_Per_Capita_USD'] / datos_gt_ult['PIB_Per_Capita_USD']
    brecha_subindice_hk = datos_hk_ult['Subindice_Vivienda_Alimentos_Pct'] - datos_hk_ult['Inflacion_IPC_Pct']
    
    st.markdown("### 🧠 Análisis Estructural Automatizado: El Espejo Hong Kong - Guatemala")
    st.info(f"""
    * **Asimetría de Riqueza Agregada vs. Concentración del Ingreso:** En el año **{ultimo_anio}**, el PIB per cápita de Hong Kong (**${datos_hk_ult['PIB_Per_Capita_USD']:,.0f} USD**) supera en **{ratio_pib:.1f} veces** al de Guatemala (**${datos_gt_ult['PIB_Per_Capita_USD']:,.0f} USD**). Sin embargo, Hong Kong exhibe un Índice de Gini de **{datos_hk_ult['Indice_Gini']:.3f}** frente al **{datos_gt_ult['Indice_Gini']:.3f}** de Guatemala, demostrando que la altísima generación de riqueza financiera coexiste con una polarización distributiva extrema.
    * **Inflación Regresiva por Rubros Vitales:** Mientras que la inflación general (IPC) en Hong Kong para {ultimo_anio} es moderada (**{datos_hk_ult['Inflacion_IPC_Pct']:.1f}%**), el subíndice de Vivienda y Alimentos escala al **{datos_hk_ult['Subindice_Vivienda_Alimentos_Pct']:.1f}%** (una brecha regresiva de **+{brecha_subindice_hk:.1f} puntos porcentuales**). Esto castiga desproporcionadamente al Decil 1, cuya cesta de consumo depende casi en su totalidad de estos dos rubros.
    * **Paralelismo de Vulnerabilidad Estructural:** En Guatemala, el shock inflacionario de 2022 (**9.2%**) erosionó la capacidad adquisitiva alimentaria de los hogares vulnerables; en Hong Kong, la rigidez extrema del suelo traslada la presión hacia el costo por metro cuadrado, confinando a los trabajadores de bajos ingresos a las *Coffin Homes*.
    """)

# ==============================================================================
# PESTAÑA 2: IMPACTO MICROECONÓMICO Y RECTA PRESUPUESTARIA
# ==============================================================================
with tab2:
    st.subheader("📐 Teoría del Consumidor: Restricción Presupuestaria del Decil 1 en Hong Kong")
    
    st.markdown("""
    Modelamos el problema de optimización microeconómica de un individuo perteneciente al **Decil 1 de ingresos** en Hong Kong mediante la ecuación de la **Recta Presupuestaria**:
    $$I = P_x \cdot X + P_y \cdot Y$$
    Donde:
    * **$I$**: Ingreso mensual disponible del consumidor (en HKD).
    * **$X$**: Espacio habitable demandado en metros cuadrados ($\text{m}^2$).
    * **$P_x$**: Precio implícito por metro cuadrado de alquiler mensual ($\text{HKD/m}^2$), derivado de la tipología habitacional seleccionada.
    * **$Y$**: Cantidad de canastas básicas de alimentos y otros bienes esenciales al mes.
    * **$P_y$**: Precio unitario de una canasta alimentaria/vital básica mensual (en HKD).
    """)

    st.divider()

    col_sim_ctrl, col_sim_graf = st.columns([1, 2])

    with col_sim_ctrl:
        st.markdown("#### 🎛️ Controles del Simulador")
        
        anio_ref_micro = st.selectbox(
            "Año base de referencia (Datos CSV):",
            options=df_micro['Anio'].tolist(),
            index=len(df_micro) - 1
        )
        fila_micro_base = df_micro[df_micro['Anio'] == anio_ref_micro].iloc[0]
        
        ingreso_base_csv = int(fila_micro_base['Ingreso_Decil_1_HKD'])
        ingreso_sim = st.slider(
            "Ingreso Mensual Disponible ($I$ en HKD):",
            min_value=6000,
            max_value=18000,
            value=ingreso_base_csv,
            step=100,
            help=f"Valor real del Decil 1 en {anio_ref_micro}: {ingreso_base_csv:,} HKD"
        )
        
        tipo_vivienda = st.radio(
            "Tipología de Vivienda (Determina base de $P_x$):",
            options=[
                "Coffin Home (~1.8 m²)",
                "Piso Subdividido / SDU (~10.0 m²)",
                "Vivienda Pública (~14.0 m²)"
            ]
        )
        
        # Asignación del costo mensual base y área promedio según la tipología seleccionada
        if "Coffin Home" in tipo_vivienda:
            renta_base_csv = int(fila_micro_base['Renta_Coffin_Home_HKD'])
            area_ref_m2 = 1.8
        elif "Subdividido" in tipo_vivienda:
            renta_base_csv = int(fila_micro_base['Renta_Subdividido_HKD'])
            area_ref_m2 = 10.0
        else:
            renta_base_csv = int(fila_micro_base['Renta_Publica_HKD'])
            area_ref_m2 = 14.0
            
        costo_alquiler_sim = st.slider(
            "Costo Mensual del Alquiler (HKD):",
            min_value=1200,
            max_value=9000,
            value=renta_base_csv,
            step=50,
            help=f"Renta promedio en {anio_ref_micro} para esta categoría: {renta_base_csv:,} HKD"
        )
        
        precio_canasta_py = st.slider(
            "Precio Canasta Alimentaria Básica ($P_y$ en HKD):",
            min_value=800,
            max_value=3500,
            value=1500,
            step=50,
            help="Costo unitario de una canasta mensual de subsistencia alimentaria y servicios básicos."
        )
        
        shock_inflacion_pct = st.slider(
            "Shock de Inflación Acumulada en Alquiler y Alimentos (%):",
            min_value=0.0,
            max_value=50.0,
            value=12.0,
            step=1.0,
            help="Simula un encarecimiento simultáneo de Px y Py."
        )

    # Cálculos matemáticos de la Recta Presupuestaria
    # Precio por m2 (Px) = Costo del alquiler de la unidad / m2 de la unidad de referencia
    px_base = costo_alquiler_sim / area_ref_m2
    py_base = float(precio_canasta_py)
    
    factor_shock = 1.0 + (shock_inflacion_pct / 100.0)
    px_shock = px_base * factor_shock
    py_shock = py_base * factor_shock

    # Interceptos de la Recta Presupuestaria Original (Sin Shock, con ingreso base del CSV)
    x_max_orig = ingreso_base_csv / px_base
    y_max_orig = ingreso_base_csv / py_base

    # Interceptos de la Recta Presupuestaria Simulada (Con Ingreso Simulado y Shock de Inflación)
    x_max_sim = ingreso_sim / px_shock
    y_max_sim = ingreso_sim / py_shock

    # Cálculo de esfuerzo financiero
    alquiler_efectivo_shock = costo_alquiler_sim * factor_shock
    esfuerzo_financiero_pct = (alquiler_efectivo_shock / ingreso_sim) * 100.0
    ingreso_remanente_hkd = ingreso_sim - alquiler_efectivo_shock
    canastas_alimentos_posibles = max(0.0, ingreso_remanente_hkd / py_shock)

    with col_sim_graf:
        # Construcción del gráfico de la Recta Presupuestaria en Plotly
        fig_rp = go.Figure()

        # Recta Presupuestaria Original (Año Base sin Shock)
        fig_rp.add_trace(go.Scatter(
            x=[0, x_max_orig],
            y=[y_max_orig, 0],
            mode='lines+markers',
            name=f'Recta Base ({anio_ref_micro} sin shock)',
            line=dict(color='#0284C7', width=3, dash='dash'),
            fill='tozeroy',
            fillcolor='rgba(2, 132, 199, 0.10)'
        ))

        # Recta Presupuestaria Simulada (Con Shock / Ajustes)
        fig_rp.add_trace(go.Scatter(
            x=[0, x_max_sim],
            y=[y_max_sim, 0],
            mode='lines+markers',
            name=f'Recta Simulada (Shock +{shock_inflacion_pct:.0f}%)',
            line=dict(color='#E11D48', width=4),
            fill='tozeroy',
            fillcolor='rgba(225, 29, 72, 0.20)'
        ))

        # Punto de elección actual del consumidor (Espacio de la tipología elegida vs Canastas posibles)
        if canastas_alimentos_posibles >= 0:
            fig_rp.add_trace(go.Scatter(
                x=[area_ref_m2],
                y=[canastas_alimentos_posibles],
                mode='markers+text',
                name='Cesta de Consumo Efectiva',
                marker=dict(color='#1E293B', size=12, symbol='diamond'),
                text=[f"  ({area_ref_m2:.1f} m², {canastas_alimentos_posibles:.1f} canastas)"],
                textposition="top right"
            ))

        # Umbral de subsistencia alimentaria (Mínimo 2 canastas básicas al mes para nutrición y salud)
        fig_rp.add_hline(
            y=2.0,
            line_dash="dot",
            line_color="#D97706",
            annotation_text="Umbral Mínimo de Subsistencia Alimentaria/Vital (Y = 2.0 canastas)",
            annotation_position="top right"
        )

        # Umbral de espacio físico mínimo digno ONU/Estándar Internacional (7 m2 por persona)
        fig_rp.add_vline(
            x=7.0,
            line_dash="dot",
            line_color="#16A34A",
            annotation_text="Umbral Habitacional Digno (X = 7.0 m²)",
            annotation_position="top right"
        )

        fig_rp.update_layout(
            title=f"Contracción/Rotación de la Recta Presupuestaria — {tipo_vivienda}",
            xaxis_title="Espacio de Vivienda X (Metros Cuadrados - m²)",
            yaxis_title="Alimentos y Otros Bienes Y (Unidades de Canasta Básica)",
            xaxis=dict(range=[0, max(x_max_orig, x_max_sim, 8.5) * 1.1]),
            yaxis=dict(range=[0, max(y_max_orig, y_max_sim, 3.0) * 1.1]),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_rp, use_container_width=True)

        # Indicadores de Esfuerzo Financiero y Alerta Visual
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Precio Implícito ($P_x$ c/shock)", f"{px_shock:,.0f} HKD/m²", f"Base: {px_base:,.0f} HKD/m²")
        m_col2.metric("Esfuerzo Financiero en Alquiler", f"{esfuerzo_financiero_pct:.1f}%", f"{alquiler_efectivo_shock:,.0f} HKD/mes", delta_color="inverse")
        m_col3.metric("Ingreso Restante para $Y$", f"{ingreso_remanente_hkd:,.0f} HKD", f"{canastas_alimentos_posibles:.2f} canastas")

        if esfuerzo_financiero_pct >= 50.0:
            st.markdown(
                f'<div class="alert-box-red">🚨 ALERTA ROJA CRÍTICA (Esfuerzo > 50%): El hogar destina el '
                f'{esfuerzo_financiero_pct:.1f}% de su ingreso al alquiler. Esto configura una situación de '
                f'pobreza habitacional severa e insolvencia alimentaria ({canastas_alimentos_posibles:.2f} canastas restantes), '
                f'obligando al desplazamiento forzoso hacia una Coffin Home.</div>',
                unsafe_allow_html=True
            )
        elif esfuerzo_financiero_pct >= 30.0:
            st.markdown(
                f'<div class="alert-box-yellow">⚠️ ALERTA ROJA / SOBRECARGA HABITACIONAL (Esfuerzo > 30%): El alquiler absorbe el '
                f'{esfuerzo_financiero_pct:.1f}% del ingreso mensual, superando el umbral internacional de asequibilidad '
                f'(30% según ONU-Hábitat) y comprimiendo severamente el consumo de alimentos y salud.</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="alert-box-green">✅ NIVEL ASEQUIBLE (< 30%): El gasto en alquiler representa el '
                f'{esfuerzo_financiero_pct:.1f}% del ingreso mensual, permitiendo cubrir el umbral básico de '
                f'alimentación ({canastas_alimentos_posibles:.2f} canastas). Sin embargo, verifique si el área '
                f'física ({area_ref_m2} m²) cumple el estándar mínimo de dignidad humana.</div>',
                unsafe_allow_html=True
            )

# ==============================================================================
# PESTAÑA 3: MODELADO DE MERCADO Y ELASTICIDAD
# ==============================================================================
with tab3:
    st.subheader("⚖️ Equilibrio de Mercado y Elasticidad Precio en Vivienda Precaria (Coffin Homes)")

    st.markdown("""
    Modelamos el mercado de las *Coffin Homes* mediante un sistema de ecuaciones lineales donde la demanda está impulsada por la población de bajos ingresos que aguarda en la lista de espera de Vivienda Pública, mientras que la oferta presenta una **alta rigidez estructural** debido a las restricciones geográficas y normativas de Hong Kong:
    * **Demanda Lineal:** $Q_d = a - b \cdot P$
    * **Oferta Rígida/Inelástica:** $Q_s = c + d \cdot P$
    * **Condición de Equilibrio ($Q_d = Q_s$):** $P^* = \\frac{a - c}{b + d}$  y  $Q^* = c + d \cdot P^*$
    """)

    col_mkt_ctrl, col_mkt_graf = st.columns([1, 2])

    with col_mkt_ctrl:
        st.markdown("#### ⚙️ Parámetros del Mercado")
        
        st.caption("**Parámetros Base (Calibrados al mercado de HK):**")
        a_base = st.number_input("Intercepto Demanda Autónoma ($a$):", value=48000, step=1000)
        b_pendiente = st.slider("Sensibilidad de Demanda al Precio ($b$):", min_value=1.0, max_value=8.0, value=2.5, step=0.5)
        c_base = st.number_input("Capacidad Base Instalada ($c$):", value=35000, step=1000)
        d_pendiente = st.slider("Rigidez de Oferta ($d$ — menor valor = más inelástica):", min_value=0.2, max_value=5.0, value=1.2, step=0.2)

        st.divider()
        st.markdown("#### ⚡ Simulador de Shocks Exógenos")
        shock_demanda = st.slider(
            "Desplazamiento de Demanda ($\Delta a$ por saturación en lista de espera pública):",
            min_value=-5000,
            max_value=15000,
            value=4500,
            step=500,
            help="Un aumento en los años de espera de vivienda pública expulsa familias hacia las Coffin Homes."
        )
        shock_oferta = st.slider(
            "Shock de Costos de Propietarios ($\Delta c$ — contracción de oferta si es negativo):",
            min_value=-8000,
            max_value=5000,
            value=-1500,
            step=500,
            help="Mayores costos eléctricos, subdivisión o regulaciones reducen la oferta disponible a cada precio."
        )

    # Cálculo del Equilibrio Inicial (Sin Shocks)
    p_eq_0 = (a_base - c_base) / (b_pendiente + d_pendiente)
    q_eq_0 = a_base - b_pendiente * p_eq_0

    # Cálculo del Nuevo Equilibrio (Con Shocks de Demanda y Oferta)
    a_nuevo = a_base + shock_demanda
    c_nuevo = c_base + shock_oferta
    p_eq_1 = max(100.0, (a_nuevo - c_nuevo) / (b_pendiente + d_pendiente))
    q_eq_1 = a_nuevo - b_pendiente * p_eq_1

    # Cálculo de la Elasticidad Precio de la Demanda (Ep) y de la Oferta (Es) en el nuevo equilibrio
    ep_puntual = (-b_pendiente) * (p_eq_1 / q_eq_1)
    es_puntual = (d_pendiente) * (p_eq_1 / q_eq_1)

    with col_mkt_graf:
        # Rango de precios para graficar las curvas
        p_rango = np.linspace(500, max(p_eq_0, p_eq_1) * 1.6, 200)
        qd_0_curva = a_base - b_pendiente * p_rango
        qs_0_curva = c_base + d_pendiente * p_rango
        qd_1_curva = a_nuevo - b_pendiente * p_rango
        qs_1_curva = c_nuevo + d_pendiente * p_rango

        fig_mkt = go.Figure()

        # Curvas Originales
        fig_mkt.add_trace(go.Scatter(
            x=qd_0_curva, y=p_rango, mode='lines', name='Demanda Inicial (D₀)',
            line=dict(color='#94A3B8', width=2, dash='dash')
        ))
        fig_mkt.add_trace(go.Scatter(
            x=qs_0_curva, y=p_rango, mode='lines', name='Oferta Inicial (S₀)',
            line=dict(color='#64748B', width=2, dash='dash')
        ))

        # Curvas Desplazadas
        fig_mkt.add_trace(go.Scatter(
            x=qd_1_curva, y=p_rango, mode='lines', name='Demanda con Shock (D₁)',
            line=dict(color='#0284C7', width=3.5)
        ))
        fig_mkt.add_trace(go.Scatter(
            x=qs_1_curva, y=p_rango, mode='lines', name='Oferta Rígida con Shock (S₁)',
            line=dict(color='#E11D48', width=3.5)
        ))

        # Puntos de Equilibrio
        fig_mkt.add_trace(go.Scatter(
            x=[q_eq_0], y=[p_eq_0], mode='markers+text', name='Equilibrio Inicial (E₀)',
            marker=dict(color='#475569', size=11),
            text=[f"E₀ ({q_eq_0:,.0f} u, {p_eq_0:,.0f} HKD)"], textposition="bottom right"
        ))
        fig_mkt.add_trace(go.Scatter(
            x=[q_eq_1], y=[p_eq_1], mode='markers+text', name='Nuevo Equilibrio (E₁)',
            marker=dict(color='#B91C1C', size=14, symbol='star'),
            text=[f"E₁ ({q_eq_1:,.0f} u, {p_eq_1:,.0f} HKD)"], textposition="top left"
        ))

        fig_mkt.update_layout(
            title="Equilibrio en el Mercado de Coffin Homes (Impacto de Lista de Espera y Rigidez de Suelo)",
            xaxis_title="Cantidad de Unidades Habitacionales Precarias (Q)",
            yaxis_title="Precio de Alquiler Mensual P (HKD)",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_mkt, use_container_width=True)

        # KPIs del Equilibrio y Elasticidades
        eq_c1, eq_c2, eq_c3, eq_c4 = st.columns(4)
        delta_p_pct = ((p_eq_1 - p_eq_0) / p_eq_0) * 100
        delta_q_pct = ((q_eq_1 - q_eq_0) / q_eq_0) * 100

        eq_c1.metric("Precio de Equilibrio ($P^*$)", f"{p_eq_1:,.0f} HKD", f"{delta_p_pct:+.1f}% vs E₀", delta_color="inverse")
        eq_c2.metric("Cantidad de Equilibrio ($Q^*$)", f"{q_eq_1:,.0f} unidades", f"{delta_q_pct:+.1f}% vs E₀")
        eq_c3.metric("Elasticidad Demanda ($|E_p|$)", f"{abs(ep_puntual):.3f}", "Inelástica (< 1)" if abs(ep_puntual) < 1 else "Elástica (> 1)")
        eq_c4.metric("Elasticidad Oferta ($E_s$)", f"{es_puntual:.3f}", "Altamente Rígida")

    # Interpretación didáctica de la Elasticidad Precio de la Demanda
    st.markdown("### 📚 Interpretación Microeconómica de la Elasticidad Precio ($E_p$)")
    st.success(f"""
    * **Cálculo en el Punto de Equilibrio $E_1$:**
      $$E_p = \\frac{{dQ_d}}{{dP}} \\cdot \\frac{{P^*}}{{Q^*}} = (-{b_pendiente}) \\cdot \\frac{{{p_eq_1:,.0f}}}{{{q_eq_1:,.0f}}} = {ep_puntual:.3f} \\implies |E_p| = {abs(ep_puntual):.3f}$$
    * **¿Por qué $|E_p| < 1$ (Demanda Altamente Inelástica)?** Para el Decil 1 de Hong Kong, las *Coffin Homes* constituyen un **bien de subsistencia extrema sin sustitutos cercanos**: los pisos subdivididos (*SDU*) superan el 50% de su ingreso mensual y la vivienda pública tiene una barrera de entrada temporal superior a los 5 años de espera. En consecuencia, ante un aumento del 10% en el alquiler ($P$), la cantidad demandada ($Q_d$) apenas se reduce en un **{abs(ep_puntual)*10:.2f}%**, permitiendo a los arrendadores extraer casi todo el excedente del consumidor.
    """)

    st.divider()

    # Gráfico de serie temporal y relación entre Espera de Vivienda Pública y Renta de Coffin Homes
    st.markdown("#### ⏳ Dinámica Temporal: Años de Espera en Vivienda Pública vs. Renta de Coffin Homes y Esfuerzo Financiero")
    
    col_corr1, col_corr2 = st.columns(2)
    
    with col_corr1:
        fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_dual.add_trace(
            go.Bar(
                x=df_micro_filt['Anio'],
                y=df_micro_filt['Espera_Vivienda_Publica_Anios'],
                name="Espera Vivienda Pública (Años)",
                marker_color='rgba(2, 132, 199, 0.35)'
            ),
            secondary_y=False
        )
        
        fig_dual.add_trace(
            go.Scatter(
                x=df_micro_filt['Anio'],
                y=df_micro_filt['Renta_Coffin_Home_HKD'],
                name="Renta Coffin Home (HKD)",
                mode="lines+markers",
                line=dict(color='#E11D48', width=3.5)
            ),
            secondary_y=True
        )
        
        fig_dual.update_layout(
            title="Evolución Histórica: Cuello de Botella Público vs. Alquiler de Coffin Homes",
            template="plotly_white",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_dual.update_xaxes(title_text="Año")
        fig_dual.update_yaxes(title_text="Tiempo de Espera (Años)", secondary_y=False, range=[0, 7.5])
        fig_dual.update_yaxes(title_text="Renta Mensual Coffin Home (HKD)", secondary_y=True)
        st.plotly_chart(fig_dual, use_container_width=True)

    with col_corr2:
        fig_esfuerzo = px.line(
            df_micro_filt,
            x="Anio",
            y=["Esfuerzo_Coffin_Pct", "Esfuerzo_Subdiv_Pct"],
            markers=True,
            title="Evolución de la Carga Financiera sobre el Ingreso del Decil 1 (%)",
            labels={"Anio": "Año", "value": "Esfuerzo sobre el Ingreso (%)", "variable": "Modalidad"},
            color_discrete_map={
                "Esfuerzo_Coffin_Pct": "#E11D48",
                "Esfuerzo_Subdiv_Pct": "#7C3AED"
            }
        )
        fig_esfuerzo.add_hline(
            y=30.0, line_dash="dash", line_color="#D97706",
            annotation_text="Límite de Asequibilidad ONU (30%)"
        )
        fig_esfuerzo.add_hline(
            y=50.0, line_dash="dash", line_color="#DC2626",
            annotation_text="Umbral de Pobreza Habitacional Severa (50%)"
        )
        fig_esfuerzo.update_layout(
            template="plotly_white",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_esfuerzo, use_container_width=True)

# ==============================================================================
# PESTAÑA 4: EXPLORADOR Y SEGMENTACIÓN DE DATOS
# ==============================================================================
with tab4:
    st.subheader("🗂️ Explorador, Segmentación y Descarga de Datos Procesados")
    st.markdown("Utilice los controles inferiores para filtrar por año, país y métricas específicas, o exportar los datasets consolidados para su informe final.")

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        st.markdown("#### 1️⃣ Dataset Macroeconómico (`hong_kong_guatemala_macro_es.csv`)")
        paises_sel = st.multiselect(
            "Filtrar por País:",
            options=df_macro['Pais'].unique().tolist(),
            default=df_macro['Pais'].unique().tolist()
        )
        cols_macro_disponibles = [c for c in df_macro.columns if c not in ['Anio', 'Pais']]
        metricas_macro_sel = st.multiselect(
            "Seleccionar Métricas Macroeconómicas:",
            options=cols_macro_disponibles,
            default=cols_macro_disponibles
        )
        
        df_macro_tabla = df_macro_filt[df_macro_filt['Pais'].isin(paises_sel)][['Anio', 'Pais'] + metricas_macro_sel]
        st.dataframe(df_macro_tabla, use_container_width=True, hide_index=True)
        
        csv_macro_bytes = df_macro_tabla.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
        st.download_button(
            label="📥 Descargar Datos Macro Filtrados (CSV)",
            data=csv_macro_bytes,
            file_name=f"macro_hk_gt_{rango_anios[0]}_{rango_anios[1]}.csv",
            mime="text/csv"
        )

    with col_f2:
        st.markdown("#### 2️⃣ Dataset Microeconómico (`hong_kong_housing_micro_es.csv`)")
        cols_micro_disponibles = [c for c in df_micro.columns if c != 'Anio']
        metricas_micro_sel = st.multiselect(
            "Seleccionar Métricas Microeconómicas (Hong Kong):",
            options=cols_micro_disponibles,
            default=cols_micro_disponibles
        )
        
        df_micro_tabla = df_micro_filt[['Anio'] + metricas_micro_sel]
        st.dataframe(df_micro_tabla, use_container_width=True, hide_index=True)
        
        csv_micro_bytes = df_micro_tabla.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
        st.download_button(
            label="📥 Descargar Datos Micro Filtrados (CSV)",
            data=csv_micro_bytes,
            file_name=f"micro_hk_housing_{rango_anios[0]}_{rango_anios[1]}.csv",
            mime="text/csv"
        )

    st.divider()
    st.markdown("#### 📈 Resumen Estadístico Descriptivo (Periodo Seleccionado)")
    tab_stat1, tab_stat2 = st.tabs(["Estadísticas Macroeconómicas por País", "Estadísticas Microeconómicas (Hong Kong)"])
    
    with tab_stat1:
        st.dataframe(
            df_macro_filt.groupby('Pais')[cols_macro_disponibles].agg(['mean', 'std', 'min', 'max']).round(3),
            use_container_width=True
        )
    with tab_stat2:
        st.dataframe(
            df_micro_filt[cols_micro_disponibles].describe().T[['count', 'mean', 'std', 'min', '50%', 'max']].round(2),
            use_container_width=True
        )