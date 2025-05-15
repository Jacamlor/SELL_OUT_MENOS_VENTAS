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
        # Leer archivo según tipo
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str)
            sheet_name = "csv_file"
        else:
            excel = pd.ExcelFile(uploaded_file)
            sheet_name = excel.sheet_names[0]
            df = pd.read_excel(excel, sheet_name=sheet_name, dtype=str)

        # Validación básica
        if df.shape[1] < 6:
            st.error("❌ El archivo debe tener al menos 6 columnas (A hasta F).")
        else:
            # Selección y normalización de datos
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

            columna_resultado = "Existe en A1:A200"
            df["Valor comprobado (col F)"] = col_f_raw
            df[columna_resultado] = resultados
            df["Fila en A"] = fila_en_a

            st.success("✅ Verificación completada.")
            st.dataframe(df)

            # 🔍 Detectar coincidencias de forma robusta
            # Mostrar nombres de columnas disponibles
            st.write("🧾 Columnas disponibles:", list(df.columns))

            # Verificar que la columna de resultado exista y filtrar por "Sí"
            columna_real = [col for col in df.columns if "existe en a1:a200" in col.lower()]
            if columna_real:
                columna_real = columna_real[0]
            else:
                st.error("❌ No se encontró la columna de coincidencias.")
                st.stop()

            df_coincidentes = df[df[columna_real].astype(str).str.strip().str.upper() == "SÍ"]

            # Mostrar coincidencias en pantalla usando columnas por posición
            if not df_coincidentes.empty:
                st.markdown("### ✅ Coincidencias encontradas (A, C, D, E)")
                st.dataframe(df_coincidentes[[df.columns[0], df.columns[2], df.columns[3], df.columns[4]]])
            else:
                st.warning("⚠️ No se detectaron coincidencias, aunque se esperaba que sí.")

            # Exportar archivo Excel completo
            def convertir_a_excel_individual(df_exportar):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_exportar.to_excel(writer, index=False)
                return output.getvalue()

            excel_data_1 = convertir_a_excel_individual(df)
            st.download_button(
                label="⬇️ Descargar Excel completo",
                data=excel_data_1,
                file_name=f"resultado_{sheet_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Exportar coincidencias como archivo independiente
            if not df_coincidentes.empty:
                df_export = df_coincidentes[[df.columns[0], df.columns[2], df.columns[3], df.columns[4]]]
                excel_data_2 = convertir_a_excel_individual(df_export)
                st.download_button(
                    label="⬇️ Descargar solo Coincidencias (A,C,D,E)",
                    data=excel_data_2,
                    file_name=f"coincidencias_{sheet_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
