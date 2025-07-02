import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from textblob import TextBlob
import os

st.title("🔍 Análisis Avanzado de Comentarios en TikTok")

# SUBIDA DE MÚLTIPLES ARCHIVOS
archivos = st.file_uploader("Sube uno o varios archivos CSV de comentarios", type="csv", accept_multiple_files=True)

if archivos:
    df_total = pd.concat([pd.read_csv(archivo, encoding='latin-1') for archivo in archivos], ignore_index=True)

    if 'text' not in df_total.columns:
        st.error("No se encontró la columna 'text'. Verifica los archivos.")
    else:
        # LIMPIEZA
        def limpiar_texto(texto):
            texto = str(texto).lower()
            texto = re.sub(r"http\S+|www\S+|https\S+", '', texto)
            texto = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]", '', texto)
            return texto

        df_total['texto_limpio'] = df_total['text'].apply(limpiar_texto)

        # DETECCIÓN DE OFENSAS
        palabras_ofensivas = ["feo", "marrón", "negro"]
        def es_ofensivo(texto):
            return any(p in texto for p in palabras_ofensivas)

        df_total['discriminatorio'] = df_total['texto_limpio'].apply(es_ofensivo)

        # ANÁLISIS DE SENTIMIENTO
        def sentimiento(texto):
            analisis = TextBlob(texto)
            if analisis.sentiment.polarity > 0.1:
                return "Positivo"
            elif analisis.sentiment.polarity < -0.1:
                return "Negativo"
            else:
                return "Neutro"

        df_total['sentimiento'] = df_total['texto_limpio'].apply(sentimiento)

        # RESULTADOS
        st.subheader("📊 Resultados Generales")

        st.markdown("**Distribución de comentarios ofensivos:**")
        conteo_discriminatorio = df_total['discriminatorio'].value_counts()
        st.bar_chart(conteo_discriminatorio.rename({True: "Discriminatorio", False: "No Discriminatorio"}))

        st.markdown("**Distribución de sentimientos:**")
        st.bar_chart(df_total['sentimiento'].value_counts())

        # NUBE DE PALABRAS
        st.subheader("☁️ Palabras más comunes")
        todo_el_texto = ' '.join(df_total['texto_limpio'])
        nube = WordCloud(width=800, height=300, background_color='white').generate(todo_el_texto)
        st.image(nube.to_array())

        # COMENTARIOS DESTACADOS
        st.subheader("🧾 Ejemplos de comentarios ofensivos:")
        st.write(df_total[df_total["discriminatorio"] == True]["text"].head(10))

        st.subheader("🧾 Ejemplos de comentarios negativos:")
        st.write(df_total[df_total["sentimiento"] == "Negativo"]["text"].head(10))

