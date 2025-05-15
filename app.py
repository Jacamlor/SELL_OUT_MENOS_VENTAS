import streamlit as st
import pandas as pd
from io import BytesIO
import re

# Configuración de la página
st.set_page_config(page_title="Verificar menos vendido está en sell out", layout="centered")
st.title("🔄 Verificar menos vendido está en sell out")


# Función para limpiar y normalizar texto
def normalizar(valor):
    if pd.isna(valor):
        return ""
    return re.sub(r"\W+", "", str(valor)).strip()

# Subida del archivo
uploaded_file = st.file_uploader("📤 Sube tu archivo Excel o CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Leer archivo según extensión
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str)
            sheet_name = "csv_file"
        else:
            excel = pd.ExcelFile(uploaded_file)
            sheet_name = excel.sheet_names[0]
            df = pd.read_excel(excel, sheet_name=sheet_name, dtype=str)

        # Validación de estructura
        if df.shape[1] < 6:
            st.error("❌ El archivo debe tener al menos 6 columnas (A hasta F).")
        else:
            # Normalizar valores de columna A (A1:A200) y F
            col_a_raw = df.iloc[0:200, 0].fillna("")
            col_f_raw = df.iloc[:, 5].fillna("")

            col_a = col_a_raw.apply(normalizar)
            col_f = col_f_raw.apply(normalizar)
            col_a_set = set(col_a)

            # Comparación
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

            # Guardar resultados en el DataFrame
            columna_resultado = "Existe en A1:A200"
            df["Valor comprobado (col F)"] = col_f_raw
            df[columna_resultado] = resultados
            df["Fila en A"] = fila_en_a

            # Mostrar resultados principales
            st.success("✅ Verificación completada.")
            st.dataframe(df)

             # Filtrar filas que tienen "Sí" como coincidencia
            df_coincidentes = df[df[columna_resultado].str.strip().str.upper() == "SÍ"]

            # Seleccionar columnas por nombre explícito
            # Ajusta estos nombres si los tuyos son distintos
            columnas_a_mostrar = ["CODIGO", "DESCRIPCION", "S01", "V01"]
            df_coincidentes = df_coincidentes[[col for col in columnas_a_mostrar if col in df_coincidentes.columns]]


            # Mostrar coincidencias en pantalla
            if not df_coincidentes.empty:
                st.markdown("### ✅ Coincidencias encontradas (A, C, D, E)")
                st.dataframe(df_coincidentes)
            else:
                st.info("ℹ️ No se encontraron coincidencias para mostrar.")

            # Función para convertir un DataFrame a Excel
            def convertir_a_excel_individual(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                return output.getvalue()

            # Descargar archivo principal
            excel_data_1 = convertir_a_excel_individual(df)
            st.download_button(
                label="⬇️ Descargar Excel completo",
                data=excel_data_1,
                file_name=f"resultado_{sheet_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Descargar archivo de coincidencias
            if not df_coincidentes.empty:
                excel_data_2 = convertir_a_excel_individual(df_coincidentes)
                st.download_button(
                    label="⬇️ Descargar solo Coincidencias (A,C,D,E)",
                    data=excel_data_2,
                    file_name=f"coincidencias_{sheet_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
