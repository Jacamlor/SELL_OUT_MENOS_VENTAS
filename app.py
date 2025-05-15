import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Verificar si F está en A1:A68", layout="centered")

st.title("🔄 Comparar valores de la columna F contra A1:A68")

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
            col_a = df.iloc[0:68, 0].astype(str).fillna("").str.strip()
            col_f = df.iloc[:, 5].astype(str).fillna("").str.strip()

            resultados = []
            fila_en_a = []

            for valor in col_f:
                if valor in col_a.values:
                    resultados.append("Sí")
                    fila = col_a[col_a == valor].index[0] + 2  # +2 para compensar encabezado y base 0
                    fila_en_a.append(fila)
                else:
                    resultados.append("No")
                    fila_en_a.append("")

            df["Valor comprobado (col F)"] = df.iloc[:, 5].astype(str).fillna("").str.strip()
            df["Existe en A1:A68"] = resultados
            df["Fila en A"] = fila_en_a

            st.success("✅ Verificación completada.")
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
                file_name="resultado_f_en_a.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
