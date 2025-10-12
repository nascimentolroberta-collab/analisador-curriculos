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
        st.session_state.uploaded_files_bytes = [file.read() for file in uploaded_files]
        st.success(f"✅ {len(uploaded_files)} currículos carregados com sucesso!")

    st.subheader("🎯 Requisitos obrigatórios")

    # Curso de graduação (livre)
    st.text_input("Curso de Graduação (ex: Engenharia Civil)", key="requisitos_grad")

    # Status do curso (dropdown)
    status_curso = ["Concluído", "Em andamento"]
    st.selectbox("Status do curso", options=status_curso, key="requisitos_status")

    # Estado desejado
    estados = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    st.selectbox("Estado do candidato", options=estados, key="estado_desejado")

    # Habilidades técnicas
    st.text_area("Habilidades técnicas desejadas (uma por linha)", height=120, key="requisitos_multiplos")

    if st.button("🔎 Analisar Currículos"):
        if not st.session_state.uploaded_files_bytes or not st.session_state.requisitos_grad.strip():
            st.warning("Por favor, envie os currículos e preencha todos os campos obrigatórios.")
        else:
            st.session_state.run_analysis = True

if st.session_state.run_analysis:
    if st.session_state.uploaded_files_bytes:
        curso_desejado = st.session_state.requisitos_grad.strip().lower()
        status_aceito = st.session_state.requisitos_status.strip().lower()
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
            palavras_no_texto = texto_pdf.split()

            # FILTROS ELIMINATÓRIOS
            motivo_desclassificado = None

            curso_encontrado = difflib.get_close_matches(curso_desejado, palavras_no_texto, n=1, cutoff=0.8)
            if not curso_encontrado:
                motivo_desclassificado = "Curso não encontrado ou diferente do exigido."
            elif status_aceito and status_aceito not in texto_pdf:
                motivo_desclassificado = "Status do curso não atende (ex: não está concluído ou em andamento)."
            elif estado_desejado and estado_desejado not in texto_pdf:
                motivo_desclassificado = "Estado do candidato diferente do desejado."

            if motivo_desclassificado:
                resultados.append({
                    "indice": idx,
                    "pontuacao": 0,
                    "habilidades": [],
                    "motivo": motivo_desclassificado
                })
                continue

            # SE PASSOU NOS FILTROS, CALCULA PONTUAÇÃO POR HABILIDADES
            habilidades_encontradas = []
            score = 0
            for habilidade in habilidades_desejadas:
                if habilidade:
                    similar = difflib.get_close_matches(habilidade, palavras_no_texto, n=1, cutoff=0.8)
                    if similar:
                        score += 1
                        habilidades_encontradas.append(habilidade)

            resultados.append({
                "indice": idx,
                "pontuacao": score,
                "habilidades": habilidades_encontradas,
                "motivo": None
            })

        # Exibição dos resultados
        st.subheader("✅ Currículos aprovados:")

        aprovados = [r for r in resultados if r["motivo"] is None]
        reprovados = [r for r in resultados if r["motivo"]]

        if aprovados:
            aprovados_ordenados = sorted(aprovados, key=lambda x: x["pontuacao"], reverse=True)
            for r in aprovados_ordenados:
                nome_arquivo = f"Currículo {r['indice']+1}"
                st.success(f"{nome_arquivo} — Pontuação: {r['pontuacao']} — Habilidades: {', '.join(r['habilidades']) if r['habilidades'] else 'Nenhuma'}")
        else:
            st.info("Nenhum currículo passou na triagem.")

        st.subheader("❌ Currículos desclassificados:")
        if reprovados:
            for r in reprovados:
                nome_arquivo = f"Currículo {r['indice']+1}"
                st.error(f"{nome_arquivo} — {r['motivo']}")
        else:
            st.info("Nenhum currículo foi desclassificado.")
    else:
        st.info("Nenhum currículo carregado para análise.")

    st.markdown("---")
    if st.button("🔄 Nova análise"):
        reset_app()
        st.experimental_rerun()
