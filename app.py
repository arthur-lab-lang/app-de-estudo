import streamlit as st
import json
import os
import hashlib
import pdfplumber
import google.generativeai as genai

# ── Config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="StudyQuiz", page_icon="📚", layout="wide")
DB_FILE = "studyquiz_db.json"

# ── DB helpers ────────────────────────────────────────────────────────────
def load_db():
    if not os.path.exists(DB_FILE):
        db = {"users": {}, "questions": {}}
        db["users"]["admin"] = {"nome": "Administrador", "senha": _hash("admin123"), "role": "admin"}
        save_db(db)
        return db
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def _hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

# ── Session state ─────────────────────────────────────────────────────────
for k, v in [("usuario", None), ("quiz_qs", []), ("quiz_idx", 0),
              ("quiz_acertos", 0), ("quiz_erros", 0),
              ("quiz_respondida", False), ("quiz_escolha", None),
              ("quiz_ativo", False), ("quiz_finalizado", False),
              ("qs_geradas", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Auth ──────────────────────────────────────────────────────────────────
def login(username, senha, role_esperado=None):
    db = load_db()
    u = username.strip().lower()
    if u not in db["users"]:
        return False, "Usuário não encontrado."
    user = db["users"][u]
    if user["senha"] != _hash(senha):
        return False, "Senha incorreta."
    if role_esperado and user["role"] != role_esperado:
        return False, "Acesso não autorizado."
    st.session_state.usuario = {"username": u, "nome": user["nome"], "role": user["role"]}
    return True, ""

def logout():
    st.session_state.usuario = None
    st.rerun()

def registrar(nome, username, senha):
    db = load_db()
    u = username.strip().lower().replace(" ", "")
    if len(u) < 3: return False, "Usuário muito curto (mín. 3)."
    if len(senha) < 4: return False, "Senha muito curta (mín. 4)."
    if u in db["users"]: return False, "Usuário já existe."
    db["users"][u] = {"nome": nome.strip(), "senha": _hash(senha), "role": "prof"}
    db["questions"][u] = {}
    save_db(db)
    st.session_state.usuario = {"username": u, "nome": nome.strip(), "role": "prof"}
    return True, ""

# ── PDF helpers ───────────────────────────────────────────────────────────
def extrair_texto_pdf(arquivo):
    texto = ""
    with pdfplumber.open(arquivo) as pdf:
        for pg in pdf.pages:
            t = pg.extract_text()
            if t:
                texto += t + "\n"
    return texto.strip()

def gerar_questoes_ia(texto, quantidade, materia, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""Você é um professor criando questões de múltipla escolha para um cursinho preparatório.

A partir do texto abaixo, crie exatamente {quantidade} questões de múltipla escolha sobre o tema "{materia}".

REGRAS OBRIGATÓRIAS:
- Cada questão deve ter 4 alternativas (A, B, C, D)
- Apenas uma alternativa deve ser correta
- As questões devem testar compreensão, não apenas memorização
- Inclua uma explicação breve para o gabarito

Responda SOMENTE com um JSON válido, sem texto antes ou depois, neste formato exato:
[
  {{
    "enunciado": "texto da questão",
    "alternativa_a": "texto",
    "alternativa_b": "texto",
    "alternativa_c": "texto",
    "alternativa_d": "texto",
    "gabarito": "a",
    "explicacao": "por que essa é a resposta certa"
  }}
]

TEXTO DO PDF:
{texto[:12000]}
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)

# ── Tela de login ─────────────────────────────────────────────────────────
def tela_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("## 📚 StudyQuiz")
        st.markdown("Sistema de questões para cursinhos")
        st.divider()
        tipo = st.radio("Entrar como:", ["👨‍🏫 Professor", "👤 Aluno", "⚙️ Admin"], horizontal=True)

        if tipo == "👨‍🏫 Professor":
            aba = st.tabs(["Entrar", "Criar conta"])
            with aba[0]:
                u = st.text_input("Usuário", key="l_user")
                p = st.text_input("Senha", type="password", key="l_pass")
                if st.button("Entrar", use_container_width=True, type="primary"):
                    ok, msg = login(u, p, "prof")
                    if ok: st.rerun()
                    else: st.error(msg)
            with aba[1]:
                nome = st.text_input("Nome completo", key="r_nome")
                u2 = st.text_input("Usuário", key="r_user", placeholder="ex: prof.ana")
                p2 = st.text_input("Senha", type="password", key="r_pass")
                if st.button("Criar conta", use_container_width=True, type="primary"):
                    ok, msg = registrar(nome, u2, p2)
                    if ok: st.rerun()
                    else: st.error(msg)

        elif tipo == "👤 Aluno":
            st.info("Modo aluno: acesse questões de todos os professores sem precisar de conta.")
            if st.button("Entrar como aluno", use_container_width=True, type="primary"):
                st.session_state.usuario = {"username": "__aluno__", "nome": "Aluno", "role": "aluno"}
                st.rerun()

        else:
            p = st.text_input("Senha admin", type="password", key="a_pass")
            if st.button("Entrar como admin", use_container_width=True):
                ok, msg = login("admin", p, "admin")
                if ok: st.rerun()
                else: st.error(msg)

# ── Sidebar ───────────────────────────────────────────────────────────────
def sidebar():
    u = st.session_state.usuario
    db = load_db()
    with st.sidebar:
        st.markdown("### 📚 StudyQuiz")
        role_label = {"prof": "Professor", "aluno": "Aluno", "admin": "Admin"}.get(u["role"], "")
        st.markdown(f"**{u['nome']}** `{role_label}`")
        st.divider()

        paginas = ["📖 Estudar"]
        if u["role"] == "prof":
            paginas += ["➕ Adicionar questão", "🤖 Gerar do PDF", "📋 Banco de questões"]
        elif u["role"] == "admin":
            paginas += ["📋 Banco de questões", "⚙️ Admin"]

        pg = st.radio("Navegação", paginas, label_visibility="collapsed")
        st.divider()

        total_profs = len([x for x in db["users"].values() if x["role"] == "prof"])
        total_qs = sum(len(qs) for prof in db["questions"].values() for qs in prof.values())
        st.caption(f"👨‍🏫 {total_profs} professor(es)")
        st.caption(f"📝 {total_qs} questão(ões)")
        st.divider()
        if st.button("🚪 Sair", use_container_width=True):
            logout()
    return pg

# ── Página: Estudar ───────────────────────────────────────────────────────
def pg_estudar():
    st.header("📖 Estudar")
    db = load_db()

    def get_all():
        all_qs = []
        for prof_u, mats in db["questions"].items():
            prof_nome = db["users"].get(prof_u, {}).get("nome", prof_u)
            for mat, qs in mats.items():
                for q in qs:
                    all_qs.append({**q, "materia": mat, "prof_nome": prof_nome})
        return all_qs

    todas = get_all()
    materias = sorted(set(q["materia"] for q in todas))

    if not st.session_state.quiz_ativo and not st.session_state.quiz_finalizado:
        with st.container(border=True):
            mat_sel = st.selectbox("Matéria", ["🔀 Todas as matérias"] + materias)
            col1, col2 = st.columns(2)
            with col1:
                qtd = st.number_input("Quantidade de questões", min_value=1, max_value=500, value=10)
            with col2:
                shuffle = st.checkbox("Embaralhar", value=True)
            if st.button("▶ Iniciar sessão", type="primary"):
                import random
                pool = todas if mat_sel.startswith("🔀") else [q for q in todas if q["materia"] == mat_sel]
                if not pool:
                    st.error("Nenhuma questão nessa matéria.")
                else:
                    if shuffle: random.shuffle(pool)
                    pool = pool[:int(qtd)]
                    st.session_state.quiz_qs = pool
                    st.session_state.quiz_idx = 0
                    st.session_state.quiz_acertos = 0
                    st.session_state.quiz_erros = 0
                    st.session_state.quiz_respondida = False
                    st.session_state.quiz_escolha = None
                    st.session_state.quiz_ativo = True
                    st.session_state.quiz_finalizado = False
                    st.rerun()

    elif st.session_state.quiz_finalizado:
        ac = st.session_state.quiz_acertos
        er = st.session_state.quiz_erros
        tot = ac + er
        pct = round(ac / tot * 100) if tot else 0
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Acertos", ac)
        col2.metric("❌ Erros", er)
        col3.metric("📊 Aproveitamento", f"{pct}%")
        if pct >= 70: st.success("🎉 Ótimo desempenho! Continue assim.")
        elif pct >= 50: st.warning("📚 Resultado razoável. Revise os temas.")
        else: st.error("💪 Precisa estudar mais. Não desista!")
        if st.button("↺ Nova sessão", type="primary"):
            st.session_state.quiz_ativo = False
            st.session_state.quiz_finalizado = False
            st.rerun()

    else:
        qs = st.session_state.quiz_qs
        idx = st.session_state.quiz_idx
        if idx >= len(qs):
            st.session_state.quiz_ativo = False
            st.session_state.quiz_finalizado = True
            st.rerun()
            return

        q = qs[idx]
        st.progress(idx / len(qs), text=f"Questão {idx+1} de {len(qs)}  —  ✅ {st.session_state.quiz_acertos}  ❌ {st.session_state.quiz_erros}")

        with st.container(border=True):
            st.caption(f"📚 {q['materia']}  ·  {q['prof_nome']}")
            st.markdown(f"**{q['enunciado']}**")
            st.write("")
            letras = ["a", "b", "c", "d"]
            labels = [f"{l.upper()}) {q[f'alternativa_{l}']}" for l in letras]
            respondida = st.session_state.quiz_respondida
            escolha = st.session_state.quiz_escolha

            if not respondida:
                resp = st.radio("Escolha:", labels, index=None, key=f"radio_{idx}")
                if st.button("Confirmar →", type="primary", disabled=(resp is None)):
                    letra = letras[labels.index(resp)]
                    st.session_state.quiz_escolha = letra
                    st.session_state.quiz_respondida = True
                    if letra == q["gabarito"]: st.session_state.quiz_acertos += 1
                    else: st.session_state.quiz_erros += 1
                    st.rerun()
            else:
                acertou = escolha == q["gabarito"]
                for i, l in enumerate(letras):
                    if l == q["gabarito"]: st.success(f"✅ {labels[i]}")
                    elif l == escolha and not acertou: st.error(f"❌ {labels[i]}")
                    else: st.write(labels[i])
                if acertou: st.success("**Correto!**")
                else: st.error(f"**Errado!** Resposta certa: **{q['gabarito'].upper()}**")
                if q.get("explicacao"):
                    with st.expander("💡 Ver explicação"):
                        st.write(q["explicacao"])
                if st.button("Próxima →", type="primary"):
                    st.session_state.quiz_idx += 1
                    st.session_state.quiz_respondida = False
                    st.session_state.quiz_escolha = None
                    st.rerun()

# ── Página: Adicionar manual ──────────────────────────────────────────────
def pg_adicionar():
    st.header("➕ Adicionar questão")
    u = st.session_state.usuario
    db = load_db()
    minhas_mats = sorted(db["questions"].get(u["username"], {}).keys())

    with st.form("form_questao"):
        tipo_mat = st.radio("Matéria", ["Selecionar existente", "Criar nova"], horizontal=True)
        if tipo_mat == "Selecionar existente" and minhas_mats:
            mat = st.selectbox("Matéria", minhas_mats)
        else:
            mat = st.text_input("Nome da nova matéria", placeholder="Ex: Física, História...")
        enunc = st.text_area("Enunciado")
        col1, col2 = st.columns(2)
        with col1:
            alt_a = st.text_input("A)")
            alt_c = st.text_input("C)")
        with col2:
            alt_b = st.text_input("B)")
            alt_d = st.text_input("D)")
        gabarito = st.selectbox("Gabarito", ["A", "B", "C", "D"])
        explicacao = st.text_area("Explicação (opcional)", height=80)
        salvar = st.form_submit_button("✓ Salvar questão", type="primary", use_container_width=True)

    if salvar:
        if not all([mat, enunc, alt_a, alt_b, alt_c, alt_d]):
            st.error("Preencha todos os campos.")
        else:
            db = load_db()
            if u["username"] not in db["questions"]: db["questions"][u["username"]] = {}
            if mat not in db["questions"][u["username"]]: db["questions"][u["username"]][mat] = []
            db["questions"][u["username"]][mat].append({
                "enunciado": enunc, "alternativa_a": alt_a, "alternativa_b": alt_b,
                "alternativa_c": alt_c, "alternativa_d": alt_d,
                "gabarito": gabarito.lower(), "explicacao": explicacao, "materia": mat
            })
            save_db(db)
            st.success(f"✅ Questão salva em **{mat}**!")
            st.rerun()

# ── Página: Gerar do PDF ──────────────────────────────────────────────────
def pg_gerar_pdf():
    st.header("🤖 Gerar questões do PDF")
    u = st.session_state.usuario

    st.info("Faça upload de um PDF (apostila, prova, resumo) e a IA vai gerar questões automaticamente.")

    # API Key
    api_key = st.text_input(
        "🔑 Chave da API Google Gemini",
        type="password",
        placeholder="AIza...",
        help="Obtenha gratuitamente em aistudio.google.com"
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        pdf_file = st.file_uploader("📄 Upload do PDF", type="pdf")
    with col2:
        db = load_db()
        minhas_mats = sorted(db["questions"].get(u["username"], {}).keys())
        tipo_mat = st.radio("Matéria", ["Criar nova", "Selecionar existente"], horizontal=True)
        if tipo_mat == "Selecionar existente" and minhas_mats:
            materia = st.selectbox("Matéria existente", minhas_mats)
        else:
            materia = st.text_input("Nome da matéria", placeholder="Ex: Biologia, Química...")
        quantidade = st.slider("Quantidade de questões a gerar", 1, 20, 5)

    if pdf_file and materia and api_key:
        if st.button("✨ Gerar questões com IA", type="primary", use_container_width=True):
            with st.spinner("📖 Lendo o PDF..."):
                try:
                    texto = extrair_texto_pdf(pdf_file)
                    if not texto:
                        st.error("Não foi possível extrair texto deste PDF.")
                        st.stop()
                    st.caption(f"✅ {len(texto)} caracteres extraídos do PDF.")
                except Exception as e:
                    st.error(f"Erro ao ler PDF: {e}")
                    st.stop()

            with st.spinner(f"🤖 Gerando {quantidade} questões com IA..."):
                try:
                    qs = gerar_questoes_ia(texto, quantidade, materia, api_key)
                    st.session_state.qs_geradas = qs
                    st.success(f"✅ {len(qs)} questões geradas! Revise abaixo e salve as que quiser.")
                except Exception as e:
                    st.error(f"Erro na IA: {e}")
                    st.stop()

    # Mostrar questões geradas para revisão
    if st.session_state.qs_geradas:
        st.divider()
        st.subheader(f"📝 Questões geradas — revise e salve")

        salvar_todas = st.button("💾 Salvar todas no banco", type="primary")
        qs_para_salvar = []

        for i, q in enumerate(st.session_state.qs_geradas):
            with st.expander(f"Questão {i+1}: {q['enunciado'][:80]}...", expanded=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    enunc = st.text_area("Enunciado", q["enunciado"], key=f"enunc_{i}")
                    c1, c2 = st.columns(2)
                    with c1:
                        a = st.text_input("A)", q["alternativa_a"], key=f"a_{i}")
                        c = st.text_input("C)", q["alternativa_c"], key=f"c_{i}")
                    with c2:
                        b = st.text_input("B)", q["alternativa_b"], key=f"b_{i}")
                        d = st.text_input("D)", q["alternativa_d"], key=f"d_{i}")
                    gab_opcoes = ["a", "b", "c", "d"]
                    gab_idx = gab_opcoes.index(q["gabarito"]) if q["gabarito"] in gab_opcoes else 0
                    gab = st.selectbox("Gabarito", ["A", "B", "C", "D"], index=gab_idx, key=f"gab_{i}")
                    explic = st.text_input("Explicação", q.get("explicacao", ""), key=f"explic_{i}")
                with col2:
                    incluir = st.checkbox("Incluir", value=True, key=f"inc_{i}")

                if incluir:
                    qs_para_salvar.append({
                        "enunciado": enunc, "alternativa_a": a, "alternativa_b": b,
                        "alternativa_c": c, "alternativa_d": d,
                        "gabarito": gab.lower(), "explicacao": explic, "materia": materia
                    })

        if salvar_todas and qs_para_salvar:
            db2 = load_db()
            if u["username"] not in db2["questions"]: db2["questions"][u["username"]] = {}
            if materia not in db2["questions"][u["username"]]: db2["questions"][u["username"]][materia] = []
            db2["questions"][u["username"]][materia].extend(qs_para_salvar)
            save_db(db2)
            st.session_state.qs_geradas = []
            st.success(f"✅ {len(qs_para_salvar)} questões salvas em **{materia}**!")
            st.rerun()

# ── Página: Banco ─────────────────────────────────────────────────────────
def pg_banco():
    st.header("📋 Banco de questões")
    u = st.session_state.usuario
    db = load_db()

    if u["role"] == "prof":
        fonte = {mat: (qs, u["nome"], u["username"], mat)
                 for mat, qs in db["questions"].get(u["username"], {}).items()}
    else:
        fonte = {}
        for prof_u, mats in db["questions"].items():
            prof_nome = db["users"].get(prof_u, {}).get("nome", prof_u)
            for mat, qs in mats.items():
                fonte[f"{mat} ({prof_nome})"] = (qs, prof_nome, prof_u, mat)

    if not fonte:
        st.info("Nenhuma questão cadastrada ainda.")
        return

    for key, val in sorted(fonte.items()):
        qs, _, prof_u, mat_real = val
        with st.expander(f"📚 {key} — {len(qs)} questão(ões)"):
            for i, q in enumerate(qs):
                st.markdown(f"**{i+1}.** {q['enunciado']}")
                st.caption(f"A) {q['alternativa_a']}  ·  B) {q['alternativa_b']}  ·  C) {q['alternativa_c']}  ·  D) {q['alternativa_d']}")
                st.caption(f"✅ **{q['gabarito'].upper()}**" + (f"  —  {q['explicacao']}" if q.get("explicacao") else ""))
                st.divider()
            if st.button(f"🗑️ Apagar matéria", key=f"del_{key}"):
                db2 = load_db()
                if prof_u in db2["questions"] and mat_real in db2["questions"][prof_u]:
                    del db2["questions"][prof_u][mat_real]
                save_db(db2)
                st.success("Matéria apagada.")
                st.rerun()

# ── Página: Admin ─────────────────────────────────────────────────────────
def pg_admin():
    st.header("⚙️ Administração")
    db = load_db()
    profs = [(u, d) for u, d in db["users"].items() if d["role"] == "prof"]

    st.subheader("👨‍🏫 Professores")
    if not profs:
        st.info("Nenhum professor cadastrado.")
    else:
        for u, d in profs:
            total = sum(len(qs) for qs in db["questions"].get(u, {}).values())
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{d['nome']}** `@{u}` — {total} questões")
            with col2:
                if st.button("Remover", key=f"rm_{u}"):
                    db2 = load_db()
                    del db2["users"][u]
                    db2["questions"].pop(u, None)
                    save_db(db2)
                    st.rerun()
            st.divider()

    st.subheader("💾 Backup")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇️ Exportar tudo", json.dumps(db, ensure_ascii=False, indent=2),
                           "studyquiz_backup.json", "application/json", use_container_width=True)
    with col2:
        arq = st.file_uploader("⬆️ Importar backup", type="json")
        if arq:
            try:
                imp = json.load(arq)
                if "users" not in imp or "questions" not in imp: raise ValueError
                db2 = load_db()
                db2["users"].update(imp["users"])
                for u, mats in imp["questions"].items():
                    if u not in db2["questions"]: db2["questions"][u] = {}
                    for mat, qs in mats.items():
                        if mat not in db2["questions"][u]: db2["questions"][u][mat] = []
                        existentes = {q["enunciado"] for q in db2["questions"][u][mat]}
                        for q in qs:
                            if q["enunciado"] not in existentes:
                                db2["questions"][u][mat].append(q)
                save_db(db2)
                st.success("Importado!")
            except:
                st.error("Arquivo inválido.")

    st.subheader("⚠️ Zona de perigo")
    if st.button("🗑️ Apagar TODOS os dados"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        logout()

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.usuario:
        tela_login()
        return

    pg = sidebar()
    if pg == "📖 Estudar": pg_estudar()
    elif pg == "➕ Adicionar questão": pg_adicionar()
    elif pg == "🤖 Gerar do PDF": pg_gerar_pdf()
    elif pg == "📋 Banco de questões": pg_banco()
    elif pg == "⚙️ Admin": pg_admin()

main()
