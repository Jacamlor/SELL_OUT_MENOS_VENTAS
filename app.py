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

        if df.shape[1] < 6:
            st.error("❌ El archivo debe tener al menos 6 columnas (A hasta F).")
        else:
            col_a = df.iloc[:, 0].astype(str).str.strip()
            col_f = df.iloc[:, 5].astype(str).str.strip()

            # Buscar coincidencias y la primera fila donde aparece el valor
            coincidencias = []
            fila_en_f = []

            for valor in col_a:
                if valor in col_f.values:
                    coincidencias.append("Sí")
                    # obtener índice +1 (para mostrar número de fila humano)
                    fila = col_f[col_f == valor].index[0] + 2  # +2 para compensar encabezado y base 0
                    fila_en_f.append(fila)
                else:
                    coincidencias.append("No")
                    fila_en_f.append("")

            df["Coincide"] = coincidencias
            df["Fila en F"] = fila_en_f

            st.success("✅ Análisis completado.")
            st.dataframe(df)

            def convertir_a_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                return output.getvalue()

            excel_data = convertir_a_excel(df)
            st.download_button(
                label="⬇️ Descargar resultado en Excel",
                data=excel_data,
                file_name="resultado_con_coincidencias_y_fila.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
