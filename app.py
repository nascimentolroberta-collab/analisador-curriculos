import streamlit as st
import fitz  # PyMuPDF

st.set_page_config(page_title="Candidata: Triagem de Currículos", layout="centered")

st.title("🔍 Candidata: Triagem de Currículos")

# 1. Upload de arquivos
uploaded_files = st.file_uploader("Faça upload de currículos em PDF", type=["pdf"], accept_multiple_files=True)

# 2. Campos para requisitos
st.subheader("Requisitos Técnicos")
requisito_1 = st.text_input("Graduação (ex: Engenharia Civil)").strip().lower()
requisito_2 = st.text_input("Habilidades Técnicas (ex: Excel; Autocad)").strip().lower()

# 3. Botão para analisar
if st.button("🔎 Analisar Currículos"):

    if not uploaded_files or not requisito_1 or not requisito_2:
        st.warning("Por favor, envie os currículos e preencha os dois requisitos.")
    else:
        resultados = []

        for file in uploaded_files:
            # Ler o conteúdo do PDF
            texto_pdf = ""
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                for page in doc:
                    texto_pdf += page.get_text()

            texto_pdf = texto_pdf.lower()  # Deixa tudo em minúsculas para facilitar a busca

            # Verifica se os dois requisitos estão no texto
            if requisito_1 in texto_pdf and requisito_2 in texto_pdf:
                resultados.append(file.name)

        # Mostrar resultados
        st.subheader("📄 Currículos que atendem aos requisitos:")
        if resultados:
            for nome in resultados:
                st.success(f"✅ {nome}")
        else:
            st.error("Nenhum currículo corresponde aos dois requisitos.")
