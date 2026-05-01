import streamlit as st
import json
import os
import random

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyQuiz",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)

QUESTOES_FILE = "questoes.json"

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

/* fundo escuro */
.stApp {
    background: #0d0f14;
    color: #e8e8f0;
}

/* sidebar */
[data-testid="stSidebar"] {
    background: #13161e;
    border-right: 1px solid #1f2333;
}

/* título principal */
h1 { font-family: 'Syne', sans-serif; font-weight: 800; color: #7ee8a2; letter-spacing: -1px; }
h2, h3 { font-family: 'Syne', sans-serif; font-weight: 600; color: #c8d6ff; }

/* card de questão */
.card {
    background: #161922;
    border: 1px solid #252a3a;
    border-radius: 12px;
    padding: 28px 32px;
    margin: 16px 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}

.enunciado {
    font-size: 1.1rem;
    line-height: 1.7;
    color: #dde4ff;
    margin-bottom: 20px;
    font-family: 'Syne', sans-serif;
}

/* badge de matéria */
.badge {
    display: inline-block;
    background: #1a2540;
    color: #7eb8f7;
    border: 1px solid #2a3d6b;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.78rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.04em;
    margin-bottom: 14px;
}

/* resultado correto/errado */
.resultado-certo {
    background: #0d2b1a;
    border: 1px solid #1e7a45;
    border-radius: 10px;
    padding: 14px 20px;
    color: #5ddb8a;
    font-weight: 600;
    margin-top: 12px;
}
.resultado-errado {
    background: #2b0d0d;
    border: 1px solid #7a1e1e;
    border-radius: 10px;
    padding: 14px 20px;
    color: #e06060;
    font-weight: 600;
    margin-top: 12px;
}

/* placar */
.placar {
    background: #13161e;
    border: 1px solid #1f2333;
    border-radius: 12px;
    padding: 20px 28px;
    text-align: center;
    margin: 20px 0;
}

.placar-num {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    color: #7ee8a2;
    font-weight: 700;
}

/* inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #1a1d27 !important;
    border: 1px solid #2a2f45 !important;
    color: #e8e8f0 !important;
    border-radius: 8px !important;
}

/* botões */
.stButton > button {
    background: #1e3a5f;
    color: #7eb8f7;
    border: 1px solid #2a5490;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    padding: 10px 24px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #2a4f80;
    border-color: #4a7fbe;
    color: #aed4ff;
}

/* radio buttons */
.stRadio > div {
    gap: 10px;
}
.stRadio label {
    background: #161922;
    border: 1px solid #252a3a;
    border-radius: 8px;
    padding: 10px 16px;
    cursor: pointer;
    transition: border-color 0.2s;
    color: #c8d6ff !important;
}
.stRadio label:hover {
    border-color: #4a6fa5;
}

/* divider */
hr { border-color: #1f2333; }

/* progress bar */
.stProgress > div > div > div {
    background: #7ee8a2;
}

/* metric */
[data-testid="metric-container"] {
    background: #161922;
    border: 1px solid #252a3a;
    border-radius: 10px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Funções de dados ─────────────────────────────────────────────────────────
def carregar_questoes():
    if os.path.exists(QUESTOES_FILE):
        with open(QUESTOES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_questoes(dados):
    with open(QUESTOES_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def listar_materias(dados):
    return sorted(dados.keys())

# ── Init session state ───────────────────────────────────────────────────────
if "dados" not in st.session_state:
    st.session_state.dados = carregar_questoes()
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "acertos" not in st.session_state:
    st.session_state.acertos = 0
if "erros" not in st.session_state:
    st.session_state.erros = 0
if "respondida" not in st.session_state:
    st.session_state.respondida = False
if "escolha" not in st.session_state:
    st.session_state.escolha = None
if "questoes_sessao" not in st.session_state:
    st.session_state.questoes_sessao = []
if "modo" not in st.session_state:
    st.session_state.modo = "estudar"

dados = st.session_state.dados

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 📚 StudyQuiz")
    st.markdown("---")
    modo = st.radio(
        "Navegação",
        ["📝 Estudar", "➕ Adicionar Questão", "📋 Ver Banco de Questões"],
        key="nav"
    )
    st.markdown("---")
    materias = listar_materias(dados)
    total = sum(len(qs) for qs in dados.values())
    st.markdown(f"**Matérias cadastradas:** {len(materias)}")
    st.markdown(f"**Total de questões:** {total}")

# ═══════════════════════════════════════════════════════════════════════════
# MODO: ESTUDAR
# ═══════════════════════════════════════════════════════════════════════════
if modo == "📝 Estudar":
    st.markdown("## 📝 Modo Estudo")

    if not dados:
        st.info("Nenhuma questão cadastrada ainda. Vá em **➕ Adicionar Questão** para começar!")
    else:
        materias = listar_materias(dados)
        materia_sel = st.selectbox("Selecione a matéria", ["🔀 Todas as matérias"] + materias)

        col1, col2 = st.columns(2)
        with col1:
            embaralhar = st.checkbox("Embaralhar questões", value=True)
        with col2:
            limite = st.number_input("Qtd. de questões", min_value=1, max_value=100, value=10)

        if st.button("▶  Iniciar Sessão de Estudo"):
            if materia_sel == "🔀 Todas as matérias":
                pool = []
                for qs in dados.values():
                    pool.extend(qs)
            else:
                pool = dados.get(materia_sel, [])

            if not pool:
                st.warning("Nenhuma questão nessa matéria.")
            else:
                if embaralhar:
                    random.shuffle(pool)
                st.session_state.questoes_sessao = pool[:limite]
                st.session_state.idx = 0
                st.session_state.acertos = 0
                st.session_state.erros = 0
                st.session_state.respondida = False
                st.session_state.escolha = None
                st.session_state.modo = "quiz"
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# MODO: QUIZ ATIVO
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.modo == "quiz" and modo == "📝 Estudar":
    qs = st.session_state.questoes_sessao
    idx = st.session_state.idx

    if idx >= len(qs):
        # Resultado final
        st.markdown("## 🏁 Sessão Concluída!")
        total_respondidas = st.session_state.acertos + st.session_state.erros
        pct = int((st.session_state.acertos / total_respondidas) * 100) if total_respondidas else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Acertos", st.session_state.acertos)
        col2.metric("❌ Erros", st.session_state.erros)
        col3.metric("🎯 Aproveitamento", f"{pct}%")

        st.progress(pct / 100)

        if pct >= 70:
            st.markdown('<div class="resultado-certo">🎉 Ótimo desempenho! Continue assim.</div>', unsafe_allow_html=True)
        elif pct >= 50:
            st.markdown('<div class="resultado-errado">📖 Resultado razoável. Revise os temas com mais atenção.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="resultado-errado">💪 Precisa estudar mais. Não desista!</div>', unsafe_allow_html=True)

        if st.button("🔄 Nova Sessão"):
            st.session_state.modo = "estudar"
            st.rerun()
    else:
        questao = qs[idx]
        progresso = idx / len(qs)

        st.markdown(f"**Questão {idx+1} de {len(qs)}**")
        st.progress(progresso)

        st.markdown(f'<div class="badge">{questao.get("materia", "Geral")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><div class="enunciado">{questao["enunciado"]}</div></div>', unsafe_allow_html=True)

        alternativas = {
            "A": questao["alternativa_a"],
            "B": questao["alternativa_b"],
            "C": questao["alternativa_c"],
            "D": questao["alternativa_d"],
        }

        opcoes = [f"{k}) {v}" for k, v in alternativas.items()]

        if not st.session_state.respondida:
            escolha = st.radio("Escolha sua resposta:", opcoes, key=f"radio_{idx}")
            letra = escolha[0]

            if st.button("✔  Confirmar Resposta"):
                st.session_state.escolha = letra
                st.session_state.respondida = True
                if letra == questao["gabarito"]:
                    st.session_state.acertos += 1
                else:
                    st.session_state.erros += 1
                st.rerun()
        else:
            letra = st.session_state.escolha
            gabarito = questao["gabarito"]

            # mostra as alternativas sem interação
            for k, v in alternativas.items():
                st.write(f"**{k})** {v}")

            if letra == gabarito:
                st.markdown(f'<div class="resultado-certo">✅ Correto! A resposta é <b>{gabarito}</b>.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="resultado-errado">❌ Errado! Você escolheu <b>{letra}</b>. A resposta certa é <b>{gabarito}</b>.</div>', unsafe_allow_html=True)

            if questao.get("explicacao"):
                with st.expander("💡 Ver explicação"):
                    st.write(questao["explicacao"])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("✅ Acertos", st.session_state.acertos)
            with col2:
                st.metric("❌ Erros", st.session_state.erros)

            if st.button("➡  Próxima Questão"):
                st.session_state.idx += 1
                st.session_state.respondida = False
                st.session_state.escolha = None
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# MODO: ADICIONAR QUESTÃO
# ═══════════════════════════════════════════════════════════════════════════
elif modo == "➕ Adicionar Questão":
    st.markdown("## ➕ Cadastrar Nova Questão")

    materias_existentes = listar_materias(dados)

    opcao_materia = st.radio(
        "Matéria",
        ["Selecionar existente", "Criar nova matéria"],
        horizontal=True
    )

    if opcao_materia == "Criar nova matéria":
        materia = st.text_input("Nome da nova matéria (ex: Redes, Python, Hardware)")
    else:
        if materias_existentes:
            materia = st.selectbox("Selecione a matéria", materias_existentes)
        else:
            st.info("Nenhuma matéria cadastrada. Crie uma nova.")
            materia = st.text_input("Nome da nova matéria")

    st.markdown("---")
    enunciado = st.text_area("📄 Enunciado da questão", height=100, placeholder="Digite o enunciado completo aqui...")

    col1, col2 = st.columns(2)
    with col1:
        alt_a = st.text_input("A)", placeholder="Alternativa A")
        alt_b = st.text_input("B)", placeholder="Alternativa B")
    with col2:
        alt_c = st.text_input("C)", placeholder="Alternativa C")
        alt_d = st.text_input("D)", placeholder="Alternativa D")

    gabarito = st.selectbox("✅ Gabarito (resposta correta)", ["A", "B", "C", "D"])
    explicacao = st.text_area("💡 Explicação (opcional)", height=80, placeholder="Explique por que essa é a resposta correta...")

    if st.button("💾  Salvar Questão"):
        if not materia or not enunciado or not alt_a or not alt_b or not alt_c or not alt_d:
            st.error("Preencha todos os campos obrigatórios.")
        else:
            nova = {
                "enunciado": enunciado,
                "alternativa_a": alt_a,
                "alternativa_b": alt_b,
                "alternativa_c": alt_c,
                "alternativa_d": alt_d,
                "gabarito": gabarito,
                "explicacao": explicacao,
                "materia": materia,
            }
            if materia not in dados:
                dados[materia] = []
            dados[materia].append(nova)
            salvar_questoes(dados)
            st.session_state.dados = dados
            st.success(f"✅ Questão salva em **{materia}**! Total nessa matéria: {len(dados[materia])}")

# ═══════════════════════════════════════════════════════════════════════════
# MODO: VER BANCO
# ═══════════════════════════════════════════════════════════════════════════
elif modo == "📋 Ver Banco de Questões":
    st.markdown("## 📋 Banco de Questões")

    if not dados:
        st.info("Nenhuma questão cadastrada ainda.")
    else:
        for materia, questoes in sorted(dados.items()):
            with st.expander(f"📂 {materia}  —  {len(questoes)} questão(ões)"):
                for i, q in enumerate(questoes, 1):
                    st.markdown(f"**{i}.** {q['enunciado']}")
                    st.markdown(f"- A) {q['alternativa_a']}")
                    st.markdown(f"- B) {q['alternativa_b']}")
                    st.markdown(f"- C) {q['alternativa_c']}")
                    st.markdown(f"- D) {q['alternativa_d']}")
                    st.markdown(f"✅ **Gabarito:** {q['gabarito']}")
                    if q.get("explicacao"):
                        st.markdown(f"💡 *{q['explicacao']}*")
                    if i < len(questoes):
                        st.markdown("---")

                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button(f"🗑 Apagar matéria", key=f"del_{materia}"):
                        del dados[materia]
                        salvar_questoes(dados)
                        st.session_state.dados = dados
                        st.rerun()
