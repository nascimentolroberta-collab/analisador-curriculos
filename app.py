import streamlit as st
import fitz  # PyMuPDF

st.set_page_config(page_title="Candidata - Triagem de Currículos", layout="centered")

# Função para resetar o estado
def reset_app():
    st.session_state.run_analysis = False
    st.session_state.uploaded_files = []
    st.session_state.requisitos_1 = ""
    st.session_state.requisitos_multiplos = ""

# Inicializa o estado da análise
if "run_analysis" not in st.session_state:
    reset_app()

# Título
st.title("🔍 Candidata - Triagem de Currículos")

# Upload de arquivos
if not st.session_state.run_analysis:
    uploaded_files = st.file_uploader(
        "Faça upload de currículos em PDF",
        type=["pdf"],
        accept_multiple_files=True,
        key="uploaded_files"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} currículos carregados com sucesso!")

    # Campo para requisitos
    st.subheader("Requisitos")
    st.text_input("Graduação (ex: Engenharia Civil)", key="requisitos_1")
    st.text_area("Habilidades técnicas (ex: Autocad, Excel)", height=120, key="requisitos_multiplos")

    # Botão para rodar análise
    if st.button("🔎 Analisar Currículos"):
        if not uploaded_files or not st.session_state.requisitos_1.strip():
            st.warning("Por favor, envie currículos e preencha pelo menos o requisito principal.")
        else:
            st.session_state.run_analysis = True

# Análise dos currículos
if st.session_state.run_analysis:
    resultados = []
    requisito_1 = st.session_state.requisitos_1.strip().lower()
    outros_requisitos = [linha.strip().lower() for linha in st.session_state.requisitos_multiplos.splitlines() if linha.strip()]

    for file in st.session_state.uploaded_files:
        texto_pdf = ""
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                texto_pdf += page.get_text()

        texto_pdf = texto_pdf.lower()

        # Verifica se todos os requisitos estão no texto
        if requisito_1 in texto_pdf and all(r in texto_pdf for r in outros_requisitos):
            resultados.append(file.name)

    st.subheader("📄 Currículos que atendem aos requisitos:")
    if resultados:
        for nome in resultados:
            st.success(f"✅ {nome}")
    else:
        st.error("❌ Nenhum currículo corresponde aos requisitos informados.")

    st.markdown("---")
    if st.button("🔄 Nova análise"):
        reset_app()
        st.experimental_rerun()
