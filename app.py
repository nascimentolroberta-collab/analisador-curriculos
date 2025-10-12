import streamlit as st
import fitz  # PyMuPDF

st.set_page_config(page_title="Candidata - Triagem de Currículos", layout="centered")

# Função para resetar o estado
def reset_app():
    st.session_state.run_analysis = False
    st.session_state.requisitos_1 = ""
    st.session_state.requisitos_multiplos = ""
    st.session_state.uploaded_files = []

# Inicializa o estado
if "run_analysis" not in st.session_state:
    reset_app()

st.title("🔍 Candidata - Triagem de Currículos")

if not st.session_state.run_analysis:
    uploaded_files = st.file_uploader(
        "Faça upload de currículos em PDF",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.success(f"✅ {len(uploaded_files)} currículos carregados com sucesso!")

    st.subheader("Requisitos")
    st.text_input("Graduação obrigatória (ex: Engenharia Civil)", key="requisitos_1")
    st.text_area("Habilidades técnicas desejadas (uma por linha)", height=120, key="requisitos_multiplos")

    if st.button("🔎 Analisar Currículos"):
        if not st.session_state.uploaded_files or not st.session_state.requisitos_1.strip():
            st.warning("Por favor, envie currículos e preencha o campo de graduação.")
        else:
            st.session_state.run_analysis = True

# Análise dos currículos
if st.session_state.run_analysis:
    resultados = []
    requisito_graduacao = st.session_state.requisitos_1.strip().lower()
    habilidades_desejadas = [
        h.strip().lower() for h in st.session_state.requisitos_multiplos.splitlines() if h.strip()
    ]

    termos_conclusao = ["concluído", "completo", "formado", "formação", "bacharel", "graduado"]
    termos_nao_concluido = ["em andamento", "cursando", "incompleto", "estudando"]

    for file in st.session_state.uploaded_files:
        texto_pdf = ""
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                texto_pdf += page.get_text()

        texto_pdf = texto_pdf.lower()

        possui_graduacao = requisito_graduacao in texto_pdf
        tem_conclusao = any(t in texto_pdf for t in termos_conclusao)
        em_andamento = any(t in texto_pdf for t in termos_nao_concluido)

        if possui_graduacao and tem_conclusao and not em_andamento:
            pontuacao = 10  # peso da graduação
            habilidades_encontradas = []

            for habilidade in habilidades_desejadas:
                if habilidade in texto_pdf:
                    pontuacao += 1
                    habilidades_encontradas.append(habilidade)

            resultados.append({
                "nome": file.name,
                "pontuacao": pontuacao,
                "habilidades": habilidades_encontradas
            })

    st.subheader("📄 Currículos aprovados (ordenados por pontuação):")
    if resultados:
        resultados_ordenados = sorted(resultados, key=lambda x: x["pontuacao"], reverse=True)
        for r in resultados_ordenados:
            st.success(f"✅ {r['nome']} — Pontuação: {r['pontuacao']} — Habilidades: {', '.join(r['habilidades']) if r['habilidades'] else 'Nenhuma'}")
    else:
        st.error("❌ Nenhum currículo corresponde aos critérios de graduação e habilidades.")

    st.markdown("---")
    if st.button("🔄 Nova análise"):
        reset_app()
