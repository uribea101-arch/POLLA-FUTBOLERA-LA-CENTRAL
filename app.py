import streamlit as st
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

st.title("⚽ Polla Futbolera")
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

st.divider()
st.subheader("🔐 Panel Admin")

admin_pass = st.text_input("Clave admin", type="password")
if admin_pass == "1469":  # puedes cambiar esta clave
    if st.button("🎡 Elegir ganador"):
        
        # Filtrar ganadores
        df_ganadores = df[
            (df["equipo1"] == resultado1) &
            (df["equipo2"] == resultado2)
        ]

        if df_ganadores.empty:
            st.error("Nadie acertó el marcador 😢")
        else:
            import random
            
            fila_ganadora = df_ganadores.sample().iloc[0]

            nombre_ganador = fila_ganadora["nombre"]
            cedula_ganador = fila_ganadora["usuario"]
            
            st.success(f"🏆 Ganador: {nombre_ganador}")
            st.write(f"🪪 Cédula: {cedula_ganador}")

if st.button("Enviar"):
    if not usuario or not nombre:
        st.error("Debes completar todos los campos")
    
    elif not df.empty and usuario in df["usuario"].values:
        st.warning("Ya registraste un marcador ❌")
    
    else:
        sheet.append_row([
            usuario,
            nombre,
            goles1,
            goles2,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        st.success("Marcador registrado ✅")
