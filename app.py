import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from io import BytesIO
from datetime import datetime
import random
import time

# =========================
# 🔐 SESSION
# =========================
if "admin_visible" not in st.session_state:
    st.session_state.admin_visible = False

# =========================
# 🔥 FIRESTORE
# =========================
@st.cache_resource
def conectar_firestore():

    if not firebase_admin._apps:

        cred = credentials.Certificate(
            dict(st.secrets["gcp_service_account"])
        )

        firebase_admin.initialize_app(cred)

    return firestore.client()

db = conectar_firestore()

# =========================
# ⚙️ CONFIG
# =========================
@st.cache_data(ttl=10)
def cargar_config():

    doc = db.collection("config").document("partido_actual").get()

    if doc.exists:
        return doc.to_dict()

    return {}

config = cargar_config()

equipo1 = config.get("equipo1", "Equipo 1")
equipo2 = config.get("equipo2", "Equipo 2")
hora = config.get("hora", "")
descripcion = config.get("descripcion", "")
activo = config.get("activo", False)
resultado1 = config.get("resultado1", 0)
resultado2 = config.get("resultado2", 0)

bandera1 = config.get(
    "bandera1",
    "https://flagcdn.com/w80/uz.png"
)

bandera2 = config.get(
    "bandera2",
    "https://flagcdn.com/w80/co.png"
)

# =========================
# 📊 APUESTAS
# =========================
@st.cache_data(ttl=10)
def cargar_apuestas():

    docs = db.collection("apuestas").stream()

    data = []

    for doc in docs:
        data.append(doc.to_dict())

    return pd.DataFrame(data)

df = cargar_apuestas()

# =========================
# 🎨 HEADER
# =========================
st.markdown(
    "<h1 style='text-align: center;'>⚽ ¡En La Central, el Mundial se vive mejor!</h1>",
    unsafe_allow_html=True
)

# 🔒 Botón oculto admin
st.markdown("""
<div style="position: relative; height: 0px;">
    <a href="?admin=true"
       style="
       position: absolute;
       top: -10px;
       right: 0;
       width: min(200px, 40vw);
       height: 60px;
       display: block;
       text-decoration: none;
       ">
    </a>
</div>
""", unsafe_allow_html=True)

if "admin" in st.query_params:
    st.session_state.admin_visible = True

# =========================
# ⚽ EQUIPOS
# =========================
colA, colB, colC = st.columns([2,1,2])

with colA:
    st.markdown(f"""
    <div style='text-align:center;'>
        <img src='{bandera1}' width='80'><br>
        <b>{equipo1}</b>
    </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown(
        "<h2 style='text-align:center;'>VS</h2>",
        unsafe_allow_html=True
    )

with colC:
    st.markdown(f"""
    <div style='text-align:center;'>
        <img src='{bandera2}' width='80'><br>
        <b>{equipo2}</b>
    </div>
    """, unsafe_allow_html=True)

st.write(f"🕒 {hora}")
st.caption(descripcion)
st.write(f"👥 Participantes: {len(df)}")


# =========================
# 🔒 BLOQUEO
# =========================
apuestas_cerradas = False

if not activo:

    apuestas_cerradas = True

    st.warning("Las apuestas están cerradas ❌")

# =========================
# 🧾 FORMULARIO
# =========================
usuario = st.text_input("🪪 Cédula")
nombre = st.text_input("✍️ Nombre completo (como en la cédula)")

col1, col2 = st.columns(2, gap="small")

# 🟡 Equipo 1
with col1:

    st.markdown(f"""
    <div style='text-align:center;'>
        <img src='{bandera1}' width='40'><br>
        <b>{equipo1}</b>
    </div>
    """, unsafe_allow_html=True)

    goles1 = st.number_input(
        "",
        min_value=0,
        max_value=10,
        key="g1",
        label_visibility="collapsed"
    )

# 🔵 Equipo 2
with col2:

    st.markdown(f"""
    <div style='text-align:center;'>
        <img src='{bandera2}' width='40'><br>
        <b>{equipo2}</b>
    </div>
    """, unsafe_allow_html=True)

    goles2 = st.number_input(
        "",
        min_value=0,
        max_value=10,
        key="g2",
        label_visibility="collapsed"
    )

# =========================
# 🔐 PANEL ADMIN
# =========================
if st.session_state.admin_visible:

    st.divider()
    st.subheader("🔐 Panel Admin")

    admin_pass = st.text_input("Clave admin", type="password")
    admin_secret = st.secrets.get("admin_password", "1469")

    if admin_pass == admin_secret:

        st.divider()
        st.subheader("⚙️ Configuración Evento")

        nuevo_equipo1 = st.text_input(
            "Equipo 1",
            value=equipo1
        )

        nuevo_equipo2 = st.text_input(
            "Equipo 2",
            value=equipo2
        )

        nueva_bandera1 = st.text_input(
            "URL bandera/escudo equipo 1",
            value=bandera1
        )

        nueva_bandera2 = st.text_input(
            "URL bandera/escudo equipo 2",
            value=bandera2
        )

        nueva_hora = st.text_input(
            "Hora",
            value=hora
        )

        nueva_descripcion = st.text_area(
            "Descripción",
            value=descripcion
        )

        nuevo_resultado1 = st.number_input(
            "Resultado equipo 1",
            min_value=0,
            max_value=20,
            value=int(resultado1)
        )

        nuevo_resultado2 = st.number_input(
            "Resultado equipo 2",
            min_value=0,
            max_value=20,
            value=int(resultado2)
        )

        nuevo_estado = st.toggle(
            "🟢 Apuestas activas",
            value=activo
        )

        # 💾 guardar configuración
        if st.button("💾 Guardar configuración"):

            try:

                db.collection("config").document("partido_actual").set({

                    "equipo1": nuevo_equipo1,
                    "equipo2": nuevo_equipo2,

                    "bandera1": nueva_bandera1,
                    "bandera2": nueva_bandera2,

                    "hora": nueva_hora,
                    "descripcion": nueva_descripcion,

                    "resultado1": int(nuevo_resultado1),
                    "resultado2": int(nuevo_resultado2),

                    "activo": nuevo_estado
                })

                cargar_config.clear()

                st.success("✅ Configuración actualizada")

            except Exception as e:

                st.error(e)


        # 📥 EXPORTAR EXCEL
        if not df.empty:

            excel_buffer = BytesIO()

            # 🧹 convertir fechas a texto
            df_export = df.copy()

            if "fecha" in df_export.columns:

                df_export["fecha"] = (
                    df_export["fecha"]
                    .astype(str)
                )

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                df_export.to_excel(
                    writer,
                    index=False,
                    sheet_name="Participantes"
                )

            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="📥 Descargar participantes Excel",
                data=excel_data,
                file_name="participantes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # 🗑️ reiniciar participantes
        if st.button("🗑️ Reiniciar participantes"):

            try:

                docs = db.collection("apuestas").stream()

                for doc in docs:

                    doc.reference.delete()

                cargar_apuestas.clear()

                st.success("✅ Participantes eliminados")

            except Exception as e:

                st.error(e)

        if st.button("🎡 Elegir ganador"):

            # 🚫 validar resultados
            if str(resultado1).strip() == "" or str(resultado2).strip() == "":
                st.warning("⏳ Aún no se ha definido el resultado")
                st.stop()

            resultado1_int = int(resultado1)
            resultado2_int = int(resultado2)

            # 🚫 si no hay apuestas
            if df.empty:
                st.error("No hay participantes")
                st.stop()

            # 🧠 asegurar enteros
            df["equipo1"] = df["equipo1"].astype(int)
            df["equipo2"] = df["equipo2"].astype(int)

            # 🎯 filtrar ganadores
            df_ganadores = df[
                (df["equipo1"] == resultado1_int) &
                (df["equipo2"] == resultado2_int)
            ]

            # 🚫 nadie acertó
            if df_ganadores.empty:

                st.error("Nadie acertó el marcador 😢")

            else:

                st.success(f"🎯 {len(df_ganadores)} personas acertaron")

                nombres = df_ganadores["nombre"].tolist()

                placeholder = st.empty()

                # 🎡 RULETA
                for i in range(20):

                    nombre_random = random.choice(nombres)

                    placeholder.markdown(
                        f"""
                        <h2 style='text-align:center;'>
                        🎡 {nombre_random}
                        </h2>
                        """,
                        unsafe_allow_html=True
                    )

                    time.sleep(0.05 + i * 0.01)

                # 🏆 ganador
                fila_ganadora = df_ganadores.sample().iloc[0]

                nombre_ganador = fila_ganadora["nombre"]
                cedula_ganador = fila_ganadora["usuario"]

                placeholder.markdown(
                    f"""
                    <h1 style='text-align:center; color:green;'>
                    🏆 GANADOR 🏆
                    </h1>

                    <h2 style='text-align:center;'>
                    {nombre_ganador}
                    </h2>

                    <h3 style='text-align:center;'>
                    🪪 Cédula: {cedula_ganador}
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

                st.balloons()

# =========================
# 📩 ENVIAR
# =========================

if st.button(
    "Enviar",
    use_container_width=True,
    disabled=apuestas_cerradas
):


    usuario_original = str(usuario)
    nombre_original = str(nombre)

    usuario_limpio = ''.join(filter(str.isdigit, usuario_original))
    nombre_limpio = nombre_original.strip().title()

    # 🚫 validar campos
    if usuario_limpio == "" or nombre_limpio == "":

        st.error("Debes completar todos los campos")

    else:

        try:

            # 🔄 refrescar apuestas
            cargar_apuestas.clear()

            df = cargar_apuestas()

            # 🧠 usuarios existentes
            if not df.empty and "usuario" in df.columns:

                usuarios_registrados = (
                    df["usuario"]
                    .astype(str)
                    .str.strip()
                    .tolist()
                )

            else:
                usuarios_registrados = []

            # 🚫 duplicado
            if usuario_limpio in usuarios_registrados:

                st.warning("Ya registraste un marcador ❌")

            else:

                # 🔥 guardar en Firestore
                db.collection("apuestas").add({
                    "usuario": usuario_limpio,
                    "nombre": nombre_limpio,
                    "equipo1": int(goles1),
                    "equipo2": int(goles2),
                    "fecha": datetime.now()
                })

                # 🔄 limpiar cache
                cargar_apuestas.clear()

                st.success("Marcador registrado ✅")
                st.balloons()

        except Exception as e:

            st.error(e)
