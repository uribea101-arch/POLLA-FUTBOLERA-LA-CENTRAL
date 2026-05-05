import streamlit as st
if "admin_visible" not in st.session_state:
    st.session_state.admin_visible = False
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime


# 🔐 Conexión con Google Sheets
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("Polla Futbolera").sheet1

# 📊 Leer datos actuales
data = sheet.get_all_records()
df = pd.DataFrame(data)

# 📊 Leer configuración
config_sheet = client.open("Polla Futbolera").worksheet("config")
config_data = config_sheet.get_all_records()

config = config_data[0]

equipo1 = config["equipo1"]
equipo2 = config["equipo2"]
hora = config["hora"]
descripcion = config["descripcion"]
activo = config["activo"]
resultado1 = config["resultado1"]
resultado2 = config["resultado2"]

st.markdown(
    "<h1 style='text-align: center;'>⚽ ¡En La Central, el Mundial se vive mejor!</h1>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([10,1,1])

with col3:
    if st.button(" ", help=""):
        st.session_state.admin_visible = True
        
st.subheader(f"{equipo1} vs {equipo2}")
st.write(f"🕒 {hora}")
st.caption(descripcion)
st.write(f"👥 Participantes: {len(df)}")

# 🔒 BLOQUEO TOTAL
if not activo:
    st.warning("Las apuestas están cerradas ❌")
    st.stop()

# 🧾 Formulario
usuario = st.text_input("Cédula")
nombre = st.text_input("Nombre Completo (como en la cédula)")
goles1 = st.number_input(equipo1, min_value=0, max_value=20)
goles2 = st.number_input(equipo2, min_value=0, max_value=20)

if st.session_state.admin_visible:
    
    st.divider()
    st.subheader("🔐 Panel Admin")

    admin_pass = st.text_input("Clave admin", type="password")
    admin_secret = st.secrets.get("admin_password", "1469")

    if admin_pass == admin_secret:

        if st.button("🎡 Elegir ganador"):
            
            import random
            import time

            df["equipo1"] = df["equipo1"].astype(int)
            df["equipo2"] = df["equipo2"].astype(int)

            resultado1_int = int(resultado1)
            resultado2_int = int(resultado2)

            df_ganadores = df[
                (df["equipo1"] == resultado1_int) &
                (df["equipo2"] == resultado2_int)
            ]

            if df_ganadores.empty:
                st.error("Nadie acertó el marcador 😢")
            else:
                st.success(f"🎯 {len(df_ganadores)} personas acertaron!")

                nombres = df_ganadores["nombre"].tolist()
                placeholder = st.empty()

                for i in range(20):
                    nombre_random = random.choice(nombres)
                    placeholder.markdown(
                        f"<h2 style='text-align:center;'>🎡 {nombre_random}</h2>",
                        unsafe_allow_html=True
                    )
                    time.sleep(0.1 + i * 0.02)

                fila_ganadora = df_ganadores.sample().iloc[0]

                nombre_ganador = fila_ganadora["nombre"]
                cedula_ganador = fila_ganadora["usuario"]

                placeholder.markdown(
                    f"""
                    <h1 style='text-align:center; color:green;'>🏆 GANADOR 🏆</h1>
                    <h2 style='text-align:center;'>{nombre_ganador}</h2>
                    <h3 style='text-align:center;'>🪪Cédula: {cedula_ganador}</h3>
                    """,
                    unsafe_allow_html=True
                )

                st.balloons()

if st.button("Enviar", use_container_width=True):

    # 🧹 limpiar datos
    usuario_original = str(usuario)
    nombre_original = str(nombre)

    usuario_limpio = ''.join(filter(str.isdigit, usuario_original))
    nombre_limpio = nombre_original.strip()

    # 🔍 debug visual (puedes quitarlo luego)
    # st.write(f"DEBUG usuario: '{usuario_limpio}'")
    # st.write(f"DEBUG nombre: '{nombre_limpio}'")

    if usuario_limpio == "" or nombre_limpio == "":
        st.error("Debes completar todos los campos")

    else:
        nombre_limpio = nombre_limpio.title()

        # 🔄 refrescar datos
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        if not df.empty:
            usuarios_registrados = (
                df["usuario"]
                .astype(str)
                .str.replace(".0", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.strip()
                .tolist()
            )
        else:
            usuarios_registrados = []

        if usuario_limpio in usuarios_registrados:
            st.warning("Ya registraste un marcador ❌")

        else:
            sheet.append_row([
                usuario_limpio,
                nombre_limpio,
                goles1,
                goles2,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            st.success("Marcador registrado ✅")
