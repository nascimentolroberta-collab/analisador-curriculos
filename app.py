import streamlit as st
import fitz  # PyMuPDF
import difflib  # Para comparação de similaridade

st.set_page_config(page_title="Candidata - Triagem de Currículos", layout="centered")

# Resetar estado da aplicação
def reset_app():
    st.session_state.run_analysis = False
    st.session_state.requisitos_1 = ""
    st.session_state.requisitos_multiplos = ""
    st.session_state.uploaded_files = []
    st.session_state.escolaridade_minima = ""
    st.session_state.estado_desejado = ""

# Inicialização
if "run_analysis" not in st.session_state:
    reset_app()

st.title("🔍 Candidata - Triagem de Currículos")

# Página inicial
if not st.session_state.run_analysis:
    uploaded_files = st.file_uploader(
        "📄 Faça upload de currículos em PDF",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        st.success(f"✅ {len(uploaded_files)} currículos carregados com sucesso!")

    st.subheader("🎯 Requisitos obrigatórios")
    st.text_input("Curso de Graduação (ex: Engenharia Civil)", key="requisitos_1")

    st.selectbox(
        "Escolaridade mínima",
        options=[
            "Ensino Médio completo",
            "Curso Técnico completo",
            "Superior cursando",
            "Superior completo",
            "Pós-graduação ou superior"
        ],
        key="escolaridade_minima"
    )

    estados = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    st.selectbox("Estado do candidato", options=estados, key="estado_desejado")

    st.text_area("Habilidades técnicas desejadas (uma por linha)", height=120, key="requisitos_multiplos")

    if st.button("🔎 Analisar Currículos"):
        if not st.session_state.uploaded_files or not st.session_state.requisitos_1.strip():
            st.warning("Por favor, envie os currículos e preencha todos os campos obrigatórios.")
        else:
            st.session_state.run_analysis = True

# Página de análise
if st.session_state.run_analysis:
    resultados = []

    curso_desejado = st.session_state.requisitos_1.strip().lower()
    escolaridade_minima = st.session_state.escolaridade_minima.strip().lower()
    estado_desejado = st.session_state.estado_desejado.strip().lower()
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

        # ✅ Regras de exclusão
        possui_curso = curso_desejado in texto_pdf
        conclusao_curso = any(t in texto_pdf for t in termos_conclusao)
        curso_em_andamento = any(t in texto_pdf for t in termos_nao_concluido)
        possui_escolaridade = escolaridade_minima in texto_pdf
        estado_ok = estado_desejado in texto_pdf

        if possui_curso and conclusao_curso and not curso_em_andamento and possui_escolaridade and estado_ok:
            pontuacao = 10  # peso para graduação
            habilidades_encontradas = []

            for habilidade in habilidades_desejadas:
                palavras_no_texto = texto_pdf.split()
                match_similar = difflib.get_close_matches(habilidade, palavras_no_texto, n=1, cutoff=0.8)
                if match_similar:
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
        st.error("❌ Nenhum currículo corresponde aos critérios obrigatórios.")

    st.markdown("---")
        if st.button("🔄 Nova análise"):
        reset_app()
        st.experimental_rerun()

