import streamlit as st
import pandas as pd
from io import BytesIO
import re

# Configuración de la página
st.set_page_config(page_title="Verificar menos vendido está en sell out", layout="centered")
st.title("🔄 Verificar menos vendido está en sell out")



# Función de limpieza
def normalizar(valor):
    if pd.isna(valor):
        return ""
    return re.sub(r"\W+", "", str(valor)).strip()

# Selector de rango
limite_filas = st.number_input(
    "📌 Comparar con valores de A1 hasta A:", min_value=1, max_value=10000, value=200
)

# Subida del archivo
uploaded_file = st.file_uploader("📤 Sube tu archivo Excel o CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Leer archivo
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str)
            sheet_name = "csv_file"
        else:
            excel = pd.ExcelFile(uploaded_file)
            sheet_name = excel.sheet_names[0]
            df = pd.read_excel(excel, sheet_name=sheet_name, dtype=str)

        # Validación
        if df.shape[1] < 6:
            st.error("❌ El archivo debe tener al menos 6 columnas (A hasta F).")
        else:
            # Seleccionar columnas A y F
            col_a_raw = df.iloc[0:int(limite_filas), 0].fillna("")
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

            columna_resultado = f"Existe en A1:A{limite_filas}"
            df["Valor comprobado (col F)"] = col_f_raw
            df[columna_resultado] = resultados
            df["Fila en A"] = fila_en_a

            # Mostrar tabla
            st.success("✅ Verificación completada.")
            st.dataframe(df)

            # Exportar resultado completo
            def convertir_a_excel(df_exportar):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_exportar.to_excel(writer, index=False)
                return output.getvalue()

            excel_data = convertir_a_excel(df)
            st.download_button(
                label="⬇️ Descargar resultado en Excel",
                data=excel_data,
                file_name=f"resultado_{sheet_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
