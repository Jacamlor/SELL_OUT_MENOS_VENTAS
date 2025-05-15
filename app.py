import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Comparar Columnas", layout="centered")

st.title("🔍 Comparador de Códigos (Columna A vs Columna F)")

uploaded_file = st.file_uploader("📤 Sube tu archivo Excel o CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Verificamos si existen las columnas A y F por posición
        if df.shape[1] < 6:
            st.error("❌ El archivo debe tener al menos 6 columnas (A hasta F).")
        else:
            # Forzar columnas A y F a texto sin espacios
            col_a = df.iloc[:, 0].astype(str).str.strip()
            col_f = df.iloc[:, 5].astype(str).str.strip()

            # Comprobar coincidencias
            df["Coincide"] = col_a.isin(col_f)
            df["Coincide"] = df["Coincide"].map({True: "Sí", False: "No"})

            st.success("✅ Coincidencias analizadas correctamente.")
            st.dataframe(df)

            # Descargar como Excel
            def convertir_a_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                return output.getvalue()

            excel_data = convertir_a_excel(df)
            st.download_button(
                label="⬇️ Descargar resultado en Excel",
                data=excel_data,
                file_name="resultado_con_coincidencias.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
