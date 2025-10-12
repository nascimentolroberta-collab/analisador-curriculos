import streamlit as st
import fitz  # PyMuPDF
import difflib

st.set_page_config(page_title="Candidata - Triagem de Currículos", layout="centered")

def reset_app():
    st.session_state.run_analysis = False
    st.session_state.requisitos_grad = ""
    st.session_state.requisitos_status = ""
    st.session_state.requisitos_multiplos = ""
    st.session_state.uploaded_files_bytes = []
    st.session_state.escolaridade_minima = ""
    st.session_state.estado_desejado = ""

if "run_analysis" not in st.session_state:
    reset_app()

st.title("🔍 Candidata - Triagem de Currículos")

if not st.session_state.run_analysis:
    uploaded_files = st.file_uploader(
        "📄 Faça upload de currículos em PDF",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Salva os bytes para ler sempre do zero
        st.session_state.uploaded_files_bytes = [file.read() for file in uploaded_files]
        st.success(f"✅ {len(uploaded_files)} currículos carregados com sucesso!")

    # Campo graduação (ex: Engenharia Civil)
    st.subheader("🎯 Requisitos obrigatórios")
    st.text_input("Curso de Graduação (ex: Engenharia Civil)", key="requisitos_grad")
    st.text_input("Status do curso (ex: Concluído, Em andamento)", key="requisitos_status")

    # Escolaridade (lista padrão)
    escolaridades = [
        "Ensino Médio completo",
        "Curso Técnico completo",
        "Superior cursando",
        "Superior completo",
        "Pós-graduação ou superior"
    ]
    st.selectbox("Escolaridade mínima", options=escolaridades, key="escolaridade_minima")

    # Estados
    estados = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    st.selectbox("Estado do candidato", options=estados, key="estado_desejado")

    # Habilidades (multilinha)
    st.text_area("Habilidades técnicas desejadas (uma por linha)", height=120, key="requisitos_multiplos")

    if st.button("🔎 Analisar Currículos"):
        if not st.session_state.uploaded_files_bytes or not st.session_state.requisitos_grad.strip():
            st.warning("Por favor, envie os currículos e preencha todos os campos obrigatórios.")
        else:
            st.session_state.run_analysis = True

if st.session_state.run_analysis:
    curso_desejado = st.session_state.requisitos_grad.strip().lower()
    status_desejado = st.session_state.requisitos_status.strip().lower()
    escolaridade_minima = st.session_state.escolaridade_minima.strip().lower()
    estado_desejado = st.session_state.estado_desejado.strip().lower()
    habilidades_desejadas = [
        h.strip().lower() for h in st.session_state.requisitos_multiplos.splitlines() if h.strip()
    ]

    resultados = []

    for idx, file_bytes in enumerate(st.session_state.uploaded_files_bytes):
        texto_pdf = ""
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                texto_pdf += page.get_text()
        texto_pdf = texto_pdf.lower()

        score = 0

        # Pontuar graduação
        if curso_desejado in texto_pdf:
            score += 5
        
        # Pontuar status (concluído, em andamento etc)
        if status_desejado and status_desejado in texto_pdf:
            score += 5

        # Pontuar estado
        if estado_desejado and estado_desejado in texto_pdf:
            score += 5

        # Pontuar escolaridade (se aparecer no texto)
        if escolaridade_minima and escolaridade_minima in texto_pdf:
            score += 5

        # Pontuar habilidades por similaridade
        palavras_no_texto = texto_pdf.split()
        habilidades_encontradas = []
        for habilidade in habilidades_desejadas:
            if habilidade:
                similar = difflib.get_close_matches(habilidade, palavras_no_texto, n=1, cutoff=0.8)
                if similar:
                    score += 1
                    habilidades_encontradas.append(habilidade)

        resultados.append({
            "indice": idx,
            "pontuacao": score,
            "habilidades": habilidades_encontradas
        })

    # Ordena do maior para o menor score
    resultados_ordenados = sorted(resultados, key=lambda x: x["pontuacao"], reverse=True)

    st.subheader("📄 Resultados ordenados por pontuação:")
    for r in resultados_ordenados:
        nome_arquivo = f"Currículo {r['indice']+1}"
        st.success(f"{nome_arquivo} — Pontuação: {r['pontuacao']} — Habilidades: {', '.join(r['habilidades']) if r['habilidades'] else 'Nenhuma'}")

    st.markdown("---")
    if st.button("🔄 Nova análise"):
        reset_app()
        st.experimental_rerun()
