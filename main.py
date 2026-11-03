import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuración de la página
st.set_page_config(page_title="Inventario", layout="wide")

# 2. Inyección de CSS (Adaptable a Modo Claro y Oscuro nativamente)
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color); 
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #1E88E5; 
    }
    h1, h2, h3 { color: #1E88E5 !important; }
</style>
""", unsafe_allow_html=True)

# Listas de opciones predefinidas
OPCIONES_MARCA = ["Chevrolet", "Ford", "Toyota", "Nissan", "Hino", "Mazda", "Renault", "Kia", "Hyundai", "Volkswagen",
                  "Suzuki", "Mercedes-Benz", "BMW", "Foton", "JAC", "Audi", "Lexus", "Mitsubishi"]
OPCIONES_COLOR = ["Blanco", "Negro", "Gris", "Plata", "Rojo", "Azul", "Amarillo", "Verde", "Beige", "Otro"]
OPCIONES_MODELO = list(range(2027, 1979, -1))
OPCIONES_SINO = ["Sí", "No"]
OPCIONES_CONDICION = ["Nuevo", "Usado"]
OPCIONES_PROPIETARIO = ["Autocamiones", "Consignación"]
OPCIONES_ESTADO = ["Disponible", "En Reparación"]
COLUMNAS_ORDEN = ["Marca", "Línea", "Modelo", "Color", "Condición", "Propietario", "Estado", "Mercado Libre", "Pautado",
                  "Precio de Venta"]

# 3. Funciones JSON
ARCHIVO_JSON = "inventario.json"


def cargar_datos():
    if os.path.exists(ARCHIVO_JSON):
        df = pd.read_json(ARCHIVO_JSON)
        if "Propio de Autocamiones" in df.columns:
            df.rename(columns={"Propio de Autocamiones": "Propietario"}, inplace=True)
            df["Propietario"] = df["Propietario"].replace({"Sí": "Autocamiones", "No": "Consignación"})
        if "Estado" not in df.columns:
            df["Estado"] = "Disponible"

        df = df[COLUMNAS_ORDEN]
        df.to_json(ARCHIVO_JSON, orient="records", indent=4)
    else:
        data = {
            "Marca": ["Chevrolet", "Ford", "Toyota", "Nissan", "Hino"],
            "Línea": ["NHR", "Cargo", "Hilux", "Frontier", "Dutro"],
            "Modelo": [2024, 2018, 2023, 2020, 2025],
            "Color": ["Blanco", "Rojo", "Gris", "Blanco", "Azul"],
            "Condición": ["Nuevo", "Usado", "Usado", "Usado", "Nuevo"],
            "Propietario": ["Autocamiones", "Consignación", "Autocamiones", "Autocamiones", "Consignación"],
            "Estado": ["Disponible", "En Reparación", "Disponible", "Disponible", "En Reparación"],
            "Mercado Libre": ["Sí", "Sí", "No", "Sí", "No"],
            "Pautado": ["Sí", "No", "No", "Sí", "Sí"],
            "Precio de Venta": [120000000, 85000000, 190000000, 110000000, 150000000]
        }
        df = pd.DataFrame(data)[COLUMNAS_ORDEN]
        df.to_json(ARCHIVO_JSON, orient="records", indent=4)

    df.index = range(1, len(df) + 1)
    df.index.name = "Nº"
    return df


def guardar_datos(df):
    df.to_json(ARCHIVO_JSON, orient="records", indent=4)


# 4. Inicializar base de datos
if "inventario" not in st.session_state:
    st.session_state.inventario = cargar_datos()

# 5. Encabezado y Logo Automático
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=150)
    else:
        st.info("Guarda 'logo.png' en esta carpeta")
with col_titulo:
    st.title("Inventario")

# 6. Formulario para agregar
with st.expander("➕ Agregar Nuevo Vehículo al Inventario"):
    with st.form("form_nuevo_vehiculo", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        marca = c1.selectbox("Marca", OPCIONES_MARCA)
        linea = c2.text_input("Línea (Ej: NHR, Hilux)")
        modelo = c3.selectbox("Modelo", OPCIONES_MODELO)

        c4, c5, c6 = st.columns(3)
        color = c4.selectbox("Color", OPCIONES_COLOR)
        condicion = c5.selectbox("Condición", OPCIONES_CONDICION)
        propietario = c6.selectbox("Propietario", OPCIONES_PROPIETARIO)

        c7, c8, c9 = st.columns(3)
        estado = c7.selectbox("Estado", OPCIONES_ESTADO)
        ml = c8.selectbox("Publicado en Mercado Libre", OPCIONES_SINO)
        pautado = c9.selectbox("Pautado", OPCIONES_SINO)

        c10, c11, c12 = st.columns([1, 2, 1])
        precio = c11.number_input("Precio de Venta ($)", min_value=0, step=1000000)

        enviado = st.form_submit_button("Guardar Vehículo", type="primary")

        if enviado and linea:
            nuevo_dato = pd.DataFrame([{
                "Marca": marca, "Línea": linea, "Modelo": modelo, "Color": color,
                "Condición": condicion, "Propietario": propietario, "Estado": estado,
                "Mercado Libre": ml, "Pautado": pautado, "Precio de Venta": precio
            }])
            nuevo_dato = nuevo_dato[COLUMNAS_ORDEN]
            st.session_state.inventario = pd.concat([st.session_state.inventario, nuevo_dato], ignore_index=True)
            st.session_state.inventario.index = range(1, len(st.session_state.inventario) + 1)
            st.session_state.inventario.index.name = "Nº"

            guardar_datos(st.session_state.inventario)
            st.success(f"¡{marca} {linea} guardado en la base de datos!")
            st.rerun()

df = st.session_state.inventario

# 7. Filtros
st.sidebar.header("Filtros de Búsqueda")
filtro_estado = st.sidebar.multiselect("Estado", df["Estado"].unique(), default=df["Estado"].unique())
filtro_condicion = st.sidebar.multiselect("Condición", df["Condición"].unique(), default=df["Condición"].unique())
filtro_ml = st.sidebar.multiselect("Mercado Libre", df["Mercado Libre"].unique(), default=df["Mercado Libre"].unique())

df_filtrado = df[
    (df["Estado"].isin(filtro_estado)) &
    (df["Condición"].isin(filtro_condicion)) &
    (df["Mercado Libre"].isin(filtro_ml))
    ]

# 8. KPIs
df_propios = df_filtrado[df_filtrado["Propietario"] == "Autocamiones"]
df_consignacion = df_filtrado[df_filtrado["Propietario"] == "Consignación"]

st.markdown("### 📊 Resumen de Unidades")
col_u1, col_u2, col_u3 = st.columns(3)
col_u1.metric("🚗 Vehículos Propios", len(df_propios))
col_u2.metric("🤝 Vehículos en Consignación", len(df_consignacion))
col_u3.metric("📈 Gran Total de Unidades", len(df_filtrado))

st.markdown("### 💰 Resumen Financiero")
col_v1, col_v2, col_v3 = st.columns(3)
col_v1.metric("Capital Propio", f"${df_propios['Precio de Venta'].sum():,.0f}".replace(",", "."))
col_v2.metric("Capital en Consignación", f"${df_consignacion['Precio de Venta'].sum():,.0f}".replace(",", "."))
col_v3.metric("Gran Total del Inventario", f"${df_filtrado['Precio de Venta'].sum():,.0f}".replace(",", "."))

st.write("---")

# 9. Gráficos
col_graf1, col_graf2 = st.columns(2)
with col_graf1:
    st.subheader("Distribución por Marca")
    if not df_filtrado.empty:
        fig_marca = px.pie(df_filtrado, names="Marca", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_marca.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#1E88E5"))
        st.plotly_chart(fig_marca, width="stretch")
with col_graf2:
    st.subheader("Estado Físico del Inventario")
    if not df_filtrado.empty:
        fig_estado = px.histogram(df_filtrado, x="Estado", color="Estado",
                                  color_discrete_sequence=["#1E88E5", "#FFB300"])
        fig_estado.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                 font=dict(color="#1E88E5"))
        st.plotly_chart(fig_estado, width="stretch")

# 10. Tabla Editable Interactiva con Ordenamiento Activado
st.subheader("📝 Gestión del Inventario")
st.markdown(
    "Da doble clic en las celdas para modificar datos. Clic en los encabezados para **ordenar**. Para **eliminar**, marca la casilla **🗑️ Eliminar**.")

df_mostrar = df_filtrado.copy()
df_mostrar["🗑️ Eliminar"] = False

# Configuración completa de columnas
column_config = {
    "Marca": st.column_config.SelectboxColumn("Marca", options=OPCIONES_MARCA, required=True),
    "Modelo": st.column_config.SelectboxColumn("Modelo", options=OPCIONES_MODELO, required=True),
    "Color": st.column_config.SelectboxColumn("Color", options=OPCIONES_COLOR, required=True),
    "Condición": st.column_config.SelectboxColumn("Condición", options=OPCIONES_CONDICION, required=True),
    "Propietario": st.column_config.SelectboxColumn("Propietario", options=OPCIONES_PROPIETARIO, required=True),
    "Estado": st.column_config.SelectboxColumn("Estado", options=OPCIONES_ESTADO, required=True),
    "Mercado Libre": st.column_config.SelectboxColumn("Mercado Libre", options=OPCIONES_SINO, required=True),
    "Pautado": st.column_config.SelectboxColumn("Pautado", options=OPCIONES_SINO, required=True),
    "Precio de Venta": st.column_config.NumberColumn("Precio de Venta", help="Pesos colombianos", min_value=0,
                                                     step=1000000, format="$ %d"),
    "🗑️ Eliminar": st.column_config.CheckboxColumn("🗑️ Eliminar", help="Marca esta casilla para borrar el vehículo")
}

# Al quitar num_rows="dynamic", se reactiva automáticamente el ordenamiento en las columnas
df_editado = st.data_editor(
    df_mostrar,
    column_config=column_config,
    width="stretch",
    hide_index=False
)

# Lógica de actualización y borrado con Checkbox
filas_a_eliminar = df_editado[df_editado["🗑️ Eliminar"] == True].index

if len(filas_a_eliminar) > 0:
    st.session_state.inventario = st.session_state.inventario.drop(index=filas_a_eliminar)

    # Reorganizar la numeración limpiamente
    st.session_state.inventario.index = range(1, len(st.session_state.inventario) + 1)
    st.session_state.inventario.index.name = "Nº"

    guardar_datos(st.session_state.inventario)
    st.rerun()
else:
    df_editado_limpio = df_editado.drop(columns=["🗑️ Eliminar"])
    df_mostrar_limpio = df_mostrar.drop(columns=["🗑️ Eliminar"])

    if not df_editado_limpio.equals(df_mostrar_limpio):
        st.session_state.inventario.update(df_editado_limpio)
        guardar_datos(st.session_state.inventario)
        st.rerun()