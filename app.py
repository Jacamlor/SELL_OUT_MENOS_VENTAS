import streamlit as st
import pandas as pd
from io import BytesIO
import re

# Configuración de la página
st.set_page_config(page_title="Verificar menos vendido está en sell out", layout="centered")
st.title("🔄 Verificar menos vendido está en sell out")


# Función de normalización robusta (elimina caracteres no alfanuméricos y espacios)
def normalizar(valor):
    if pd.isna(valor):
        return ""
    return re.sub(r"\W+", "", str(valor)).strip()

# Subida del archivo
uploaded_file = st.file_uploader("📤 Sube tu archivo Excel o CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Detectar tipo de archivo y leer contenido
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str)
            sheet_name = "csv_file"
        else:
            excel = pd.ExcelFile(uploaded_file)
            sheet_name = excel.sheet_names[0]
            df = pd.read_excel(excel, sheet_name=sheet_name, dtype=str)

        # Validar número de columnas
        if df.shape[1] < 6:
            st.error("❌ El archivo debe tener al menos 6 columnas (A hasta F).")
        else:
            # Limpieza de datos en columnas A (1ª) y F (6ª)
            col_a_raw = df.iloc[0:200, 0].fillna("")
            col_f_raw = df.iloc[:, 5].fillna("")

            col_a = col_a_raw.apply(normalizar)
            col_f = col_f_raw.apply(normalizar)
            col_a_set = set(col_a)

            # Comparación F vs A1:A200
            resultados = []
            fila_en_a = []

            for valor in col_f:
                if valor in col_a_set:
                    resultados.append("Sí")
                    fila = col_a[col_a == valor].index[0] + 2  # +2 por base 0 + encabezado
                    fila_en_a.append(fila)
                else:
                    resultados.append("No")
                    fila_en_a.append("")

            # Agregar resultados al dataframe original
            df["Valor comprobado (col F)"] = col_f_raw
            df["Existe en A1:A200"] = resultados
            df["Fila en A"] = fila_en_a

            st.success("✅ Verificación completada.")
            st.dataframe(df)

            # Crear segunda hoja con columnas A, C, D, E si Existe en A1:A200 = "Sí"
            columnas_acde = [df.columns[0], df.columns[2], df.columns[3], df.columns[4]]
            df_coincidentes = df[df["Existe en A1:A200"] == "Sí"][columnas_acde]

            # Exportar a Excel con dos hojas
            def convertir_a_excel(df, hoja1, hoja2, df_extra):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name=hoja1)
                    df_extra.to_excel(writer, index=False, sheet_name=hoja2)
                return output.getvalue()

            excel_data = convertir_a_excel(df, hoja1=sheet_name, hoja2="Coincidencias", df_extra=df_coincidentes)
            file_name = f"resultado_{sheet_name}.xlsx"

            # Botón de descarga
            st.download_button(
                label="⬇️ Descargar resultado en Excel",
                data=excel_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Error procesando el archivo: {e}")
