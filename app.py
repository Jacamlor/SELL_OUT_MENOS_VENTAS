import streamlit as st
import pandas as pd
from io import BytesIO
import re

st.set_page_config(page_title="Verificar si menos vendido está en sell out", layout="centered")

st.title("🔄 Comparar códigos menos vendidos con sell out (versión robusta)")

def normalizar(valor):
    if pd.isna(valor):
        return ""
    return re.sub(r"\W+", "", str(valor)).strip()

uploaded_file = st.file_uploader("📤 Sube tu archivo Excel o CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str)
        else:
            df = pd.read_excel(uploaded_file, dtype=str)

        if df.shape[1] < 6:
            st.error("❌ El archivo debe tener al menos 6 columnas (A hasta F).")
        else:
            # Limpiar A1:A200 y toda F con función de normalización
            col_a_raw = df.iloc[0:200, 0].fillna("")
            col_f_raw = df.iloc[:, 5].fillna("")

            col_a = col_a_raw.apply(normalizar)
            col_f = col_f_raw.apply(normalizar)

            col_a_set = set(col_a)

            resultados = []
            fila_en_a = []

            for valor in col_f:
                if valor in col_a_set:
                    resultados.append("Sí")
                    fila = col_a[col_a == valor].index[0] + 2
                    fila_en_a.append(fila)
                else:
                    resultados.append("No")
                    fila_en_a.append("")

            df["Valor comprobado (col F)"] = col_f_raw
            df["Existe en A1:A200"] = resultados
            df["Fila en A"] = fila_en_a

            st.success("✅ Verificación completada.")
            st.dataframe(df)

              def convertir_a_excel(df, hoja):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name=hoja)
                return output.getvalue()

            excel_data = convertir_a_excel(df, hoja=sheet_name)
            file_name = f"resultado_{sheet_name}.xlsx"

            st.download_button(
                label="⬇️ Descargar resultado en Excel",
                data=excel_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
