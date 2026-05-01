import streamlit as st
import PyPDF2
import re
import time
import json
import os

st.set_page_config(page_title="StudyQuiz PRO", layout="centered")

st.title("📄🧠 StudyQuiz PRO")

# -----------------------------
# FUNÇÕES
# -----------------------------

def extrair_texto(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() + "\n"
    return texto

def transformar_em_questoes(texto):
    padrao = r'(\d+\).*?(?=\n\d+\)|$)'
    blocos = re.findall(padrao, texto, re.DOTALL)

    questoes = []

    for bloco in blocos:
        partes = re.split(r'[A-D]\)', bloco)
        alternativas = re.findall(r'([A-D]\)\s.*)', bloco)

        if len(alternativas) >= 2:
            pergunta = partes[0].strip()
            opcoes = [alt[3:].strip() for alt in alternativas]

            questoes.append({
                "pergunta": pergunta,
                "opcoes": opcoes,
                "dificuldade": detectar_dificuldade(pergunta)
            })

    return questoes

def detectar_dificuldade(pergunta):
    tamanho = len(pergunta)

    if tamanho < 80:
        return "Fácil"
    elif tamanho < 150:
        return "Médio"
    else:
        return "Difícil"

def salvar_progresso(respostas, acertos, tempo):
    dados = {
        "respostas": respostas,
        "acertos": acertos,
        "tempo": tempo
    }

    with open("progresso.json", "w") as f:
        json.dump(dados, f)

def carregar_progresso():
    if os.path.exists("progresso.json"):
        with open("progresso.json", "r") as f:
            return json.load(f)
    return None

# -----------------------------
# UPLOAD PDF
# -----------------------------

pdf = st.file_uploader("📄 Envie seu PDF de questões", type="pdf")

if pdf:
    texto = extrair_texto(pdf)
    questoes = transformar_em_questoes(texto)

    if not questoes:
        st.error("Não consegui identificar questões 😢")
    else:
        st.success(f"{len(questoes)} questões encontradas!")

        # iniciar tempo
        if "start_time" not in st.session_state:
            st.session_state.start_time = time.time()

        respostas_usuario = []

        # -----------------------------
        # QUIZ
        # -----------------------------
        for i, q in enumerate(questoes):
            st.markdown(f"### Questão {i+1}")
            st.caption(f"Dificuldade: {q['dificuldade']}")

            resposta = st.radio(
                q["pergunta"],
                q["opcoes"],
                key=f"q_{i}"
            )

            respostas_usuario.append(resposta)

        # -----------------------------
        # FINALIZAR
        # -----------------------------
        if st.button("🚀 Finalizar"):
            tempo_total = time.time() - st.session_state.start_time

            acertos = 0
            for i, q in enumerate(questoes):
                # aqui ainda não temos gabarito automático
                # então só conta se existir "correta"
                if "correta" in q and respostas_usuario[i] == q["correta"]:
                    acertos += 1

            total = len(questoes)
            porcentagem = (acertos / total) * 100 if total > 0 else 0

            salvar_progresso(respostas_usuario, acertos, tempo_total)

            st.success("💾 Progresso salvo!")

            # -----------------------------
            # DASHBOARD
            # -----------------------------
            st.subheader("📊 Resultado")

            st.write(f"Acertos: {acertos}/{total}")
            st.write(f"Porcentagem: {porcentagem:.1f}%")
            st.write(f"Tempo gasto: {int(tempo_total)} segundos")

# -----------------------------
# CARREGAR PROGRESSO
# -----------------------------

st.divider()
st.subheader("📂 Progresso anterior")

dados = carregar_progresso()

if dados:
    st.write(f"Acertos: {dados['acertos']}")
    st.write(f"Tempo: {int(dados['tempo'])} segundos")
else:
    st.info("Nenhum progresso salvo ainda.")
