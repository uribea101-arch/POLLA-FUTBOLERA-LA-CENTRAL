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
goles1 = st.number_input(equipo1, min_value=0, max_value=20)
goles2 = st.number_input(equipo2, min_value=0, max_value=20)

if st.button("Enviar"):
    if not activo:
        st.error("Las apuestas están cerradas ❌")
    
    elif not usuario:
        st.error("Debes ingresar un dato válido")
    
    else:
        if not df.empty and usuario in df["usuario"].values:
            st.warning("Ya registraste un marcador ❌")
        else:
            sheet.append_row([
                usuario,
                goles1,
                goles2,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            st.success("Marcador registrado ✅")
