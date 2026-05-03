import streamlit as st
import json
import os
import hashlib
import time
import requests
import pdfplumber
from datetime import datetime, date
import uuid
import base64

st.set_page_config(page_title="StudyQuiz", page_icon="favicon-removebg-preview.png", layout="wide")

def set_favicon(image_path):
    if not os.path.exists(image_path): return
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    ext = image_path.split(".")[-1]
    st.markdown(f'<head><link rel="shortcut icon" href="data:image/{ext};base64,{img}"></head>', unsafe_allow_html=True)

set_favicon("favicon-removebg-preview.png")

def img_to_base64(img_file):
    return base64.b64encode(img_file.read()).decode()

def mostrar_imagem_questao(q):
    if q.get("imagem"):
        try:
            st.image(base64.b64decode(q["imagem"]), use_container_width=True)
        except: pass

# ── CSS global ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes correctPop {
  0%{transform:scale(1);background:transparent}
  30%{transform:scale(1.03);background:rgba(74,240,160,0.15)}
  100%{transform:scale(1);background:rgba(74,240,160,0.08)}
}
@keyframes wrongShake {
  0%,100%{transform:translateX(0);background:transparent}
  15%{transform:translateX(-8px);background:rgba(240,74,74,0.12)}
  30%{transform:translateX(8px)}
  45%{transform:translateX(-5px)}
  60%{transform:translateX(5px)}
  75%{transform:translateX(-3px)}
}
@keyframes confettiFall {
  0%{transform:translateY(-20px) rotate(0deg);opacity:1}
  100%{transform:translateY(200px) rotate(720deg);opacity:0}
}
@keyframes progShine {
  0%{opacity:1}50%{opacity:0.7}100%{opacity:1}
}
.correct-anim{animation:correctPop 0.5s ease forwards;border-color:#4af0a0!important;color:#4af0a0!important}
.wrong-anim{animation:wrongShake 0.5s ease forwards;border-color:#f04a4a!important;color:#f04a4a!important}
.confetti-wrap{position:fixed;top:30%;left:50%;transform:translateX(-50%);pointer-events:none;z-index:9999}
.confetti-piece{position:absolute;width:10px;height:10px;border-radius:2px;animation:confettiFall linear forwards}
.prog-anim{animation:progShine 1.5s ease infinite}
.avatar-circle{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;color:white;flex-shrink:0}
.notif-badge{display:inline-block;background:rgba(240,74,74,0.15);border:1px solid rgba(240,74,74,0.4);color:#f04a4a;border-radius:20px;padding:2px 10px;font-size:11px;font-family:monospace}
.tag-pill{display:inline-block;background:rgba(74,159,240,0.1);border:1px solid rgba(74,159,240,0.3);color:#4a9ff0;border-radius:20px;padding:2px 10px;font-size:11px;margin:2px}
</style>
""", unsafe_allow_html=True)

DB_FILE = "studyquiz_db.json"
DIFICULDADES = ["Fácil", "Médio", "Difícil"]
AVATAR_CORES = ["#4a9ff0","#f04a4a","#4af0a0","#f0a04a","#a78bfa","#f04a9f","#4af0f0","#f0f04a"]

# ── DB ────────────────────────────────────────────────────────────────────
def load_db():
    if not os.path.exists(DB_FILE):
        db = {"users":{},"questions":{},"user_data":{},"turmas":{},"provas":{},"comentarios":{}}
        db["users"]["admin"] = {"nome":"Administrador","senha":_hash("admin123"),"role":"admin"}
        save_db(db); return db
    with open(DB_FILE,"r",encoding="utf-8") as f:
        db = json.load(f)
    for k in ["users","questions","user_data","turmas","provas","comentarios"]:
        if k not in db: db[k] = {}
    return db

def save_db(db):
    with open(DB_FILE,"w",encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def _hash(s): return hashlib.sha256(s.encode()).hexdigest()

def get_user_data(username):
    db = load_db()
    if username not in db["user_data"]:
        db["user_data"][username] = {"historico":[],"favoritos":[],"api_key":"","respostas_provas":{}}
        save_db(db)
    ud = db["user_data"][username]
    if "respostas_provas" not in ud:
        ud["respostas_provas"] = {}; db["user_data"][username]=ud; save_db(db)
    return ud

def save_user_data(username, data):
    db = load_db(); db["user_data"][username] = data; save_db(db)

def get_avatar_color(username):
    return AVATAR_CORES[sum(ord(c) for c in username) % len(AVATAR_CORES)]

def render_avatar(nome, username, size=48):
    iniciais = "".join([p[0].upper() for p in nome.split()[:2]])
    cor = get_avatar_color(username)
    st.markdown(f'<div class="avatar-circle" style="width:{size}px;height:{size}px;font-size:{size//3}px;background:{cor}">{iniciais}</div>', unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────
defaults = {
    "usuario":None,"quiz_qs":[],"quiz_idx":0,"quiz_acertos":0,"quiz_erros":0,
    "quiz_respondida":False,"quiz_escolha":None,"quiz_ativo":False,"quiz_finalizado":False,
    "quiz_mat":None,"quiz_dif":None,"quiz_tempo_inicio":None,"quiz_tempo_limit":None,
    "quiz_respostas":[],"qs_geradas":[],"editando_q":None,"revisao_ativa":False,
    "prova_ativa":None,"prova_idx":0,"prova_respondida":False,"prova_escolha":None,
    "prova_respostas":[],"prova_finalizada":False,"ultima_resposta":None,
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

# ── Auth ──────────────────────────────────────────────────────────────────
def login(username, senha, role_esperado=None):
    db=load_db(); u=username.strip().lower()
    if u not in db["users"]: return False,"Usuário não encontrado."
    user=db["users"][u]
    if user["senha"]!=_hash(senha): return False,"Senha incorreta."
    if role_esperado and user["role"]!=role_esperado: return False,"Acesso não autorizado."
    st.session_state.usuario={"username":u,"nome":user["nome"],"role":user["role"]}
    return True,""

def logout():
    for k,v in defaults.items(): st.session_state[k]=v
    st.rerun()

def registrar(nome, username, senha, role="prof"):
    db=load_db(); u=username.strip().lower().replace(" ","")
    if len(u)<3: return False,"Usuário muito curto (mín. 3)."
    if len(senha)<4: return False,"Senha muito curta (mín. 4)."
    if u in db["users"]: return False,"Usuário já existe."
    db["users"][u]={"nome":nome.strip(),"senha":_hash(senha),"role":role}
    if role=="prof" and u not in db["questions"]: db["questions"][u]={}
    save_db(db)
    st.session_state.usuario={"username":u,"nome":nome.strip(),"role":role}
    return True,""

def alterar_senha(username, senha_atual, senha_nova):
    db=load_db()
    if db["users"][username]["senha"]!=_hash(senha_atual): return False,"Senha atual incorreta."
    if len(senha_nova)<4: return False,"Nova senha muito curta (mín. 4)."
    db["users"][username]["senha"]=_hash(senha_nova); save_db(db); return True,""

def redefinir_senha_admin(username, senha_nova):
    if len(senha_nova)<4: return False,"Senha muito curta."
    db=load_db()
    if username not in db["users"]: return False,"Usuário não encontrado."
    db["users"][username]["senha"]=_hash(senha_nova); save_db(db); return True,""

# ── PDF/IA ────────────────────────────────────────────────────────────────
def extrair_texto_pdf(arquivo):
    texto=""
    with pdfplumber.open(arquivo) as pdf:
        for pg in pdf.pages:
            t=pg.extract_text()
            if t: texto+=t+"\n"
    return texto.strip()

def gerar_questoes_ia(texto, quantidade, materia, dificuldade, api_key, tags=""):
    tag_info = f' com foco nos subtópicos: {tags}' if tags else ''
    prompt=f"""Você é um professor criando questões de múltipla escolha de nível {dificuldade} para um cursinho.
Crie exatamente {quantidade} questões sobre "{materia}"{tag_info} a partir do texto abaixo.
REGRAS:
- 4 alternativas (A, B, C, D), apenas uma correta
- Nível {dificuldade}: {"objetivas" if dificuldade=="Fácil" else "interpretação" if dificuldade=="Médio" else "análise aprofundada"}
- Inclua explicação breve do gabarito
- Inclua um campo "tags" com 1-3 subtópicos relevantes separados por vírgula
Responda SOMENTE com JSON válido:
[{{"enunciado":"...","alternativa_a":"...","alternativa_b":"...","alternativa_c":"...","alternativa_d":"...","gabarito":"a","explicacao":"...","dificuldade":"{dificuldade}","tags":"subtópico1, subtópico2"}}]
TEXTO: {texto[:12000]}"""
    response=requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization":f"Bearer {api_key}"},
        json={"model":"meta-llama/llama-3.3-70b-instruct:free","messages":[{"role":"user","content":prompt}]}
    )
    response.raise_for_status()
    raw=response.json()["choices"][0]["message"]["content"].strip()
    if raw.startswith("```"):
        raw=raw.split("```")[1]
        if raw.startswith("json"): raw=raw[4:]
    return json.loads(raw.strip())

# ── Helpers ───────────────────────────────────────────────────────────────
def get_all_questions():
    db=load_db(); all_qs=[]
    for prof_u,mats in db["questions"].items():
        prof_nome=db["users"].get(prof_u,{}).get("nome",prof_u)
        for mat,qs in mats.items():
            for idx,q in enumerate(qs):
                all_qs.append({**q,"materia":mat,"prof_nome":prof_nome,"prof_u":prof_u,"_idx":idx})
    return all_qs

def q_id(q): return _hash(q["enunciado"])[:16]

def get_minhas_turmas(username, role):
    db=load_db(); result={}
    for tid,t in db["turmas"].items():
        if role=="prof" and t["prof_u"]==username: result[tid]=t
        elif role=="aluno" and username in t.get("alunos",[]): result[tid]=t
    return result

def get_provas_disponiveis(username, role):
    db=load_db(); now=datetime.now(); result={}
    minhas_turmas=get_minhas_turmas(username,role)
    for pid,p in db["provas"].items():
        if role=="prof" and p["prof_u"]==username: result[pid]=p
        elif role=="aluno":
            if p.get("turma_id") in minhas_turmas or p.get("turma_id") is None:
                ab=datetime.fromisoformat(p["abertura"]) if p.get("abertura") else None
                fe=datetime.fromisoformat(p["fechamento"]) if p.get("fechamento") else None
                if ab and now<ab: continue
                if fe and now>fe: continue
                result[pid]=p
    return result

def render_tags(q):
    tags = q.get("tags","")
    if tags:
        pills = "".join([f'<span class="tag-pill">{t.strip()}</span>' for t in tags.split(",") if t.strip()])
        st.markdown(pills, unsafe_allow_html=True)

def mostrar_animacao(acertou):
    if acertou:
        cols = ["#4af0a0","#4a9ff0","#f0a04a","#a78bfa","#f04a9f"]
        pieces = ""
        for i in range(25):
            import random
            x = random.randint(-120,120)
            cor = cols[i%len(cols)]
            dur = 0.6+random.random()*0.6
            delay = random.random()*0.3
            pieces += f'<div class="confetti-piece" style="left:{x}px;background:{cor};animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"></div>'
        st.markdown(f'<div class="confetti-wrap">{pieces}</div>', unsafe_allow_html=True)

# ── Comentários ───────────────────────────────────────────────────────────
def pg_comentarios_questao(qid, q_enunc):
    db = load_db()
    comentarios = db.get("comentarios",{}).get(qid,[])
    u = st.session_state.usuario

    st.markdown(f"**💬 Comentários** — {len(comentarios)} comentário(s)")

    for c in comentarios:
        with st.container(border=True):
            col1, col2 = st.columns([1,6])
            with col1:
                render_avatar(c["nome"], c["username"], 32)
            with col2:
                st.markdown(f"**{c['nome']}** `{c['data']}`")
                st.write(c["texto"])
                if c["username"] == u["username"]:
                    if st.button("🗑️", key=f"delcom_{qid}_{c['id']}"):
                        db2=load_db()
                        db2["comentarios"][qid]=[x for x in db2["comentarios"].get(qid,[]) if x["id"]!=c["id"]]
                        save_db(db2); st.rerun()

    with st.form(f"form_com_{qid}"):
        texto = st.text_area("Adicionar comentário", placeholder="Dúvida, observação ou dica...", height=70)
        if st.form_submit_button("Comentar", type="primary"):
            if texto.strip():
                db2=load_db()
                if qid not in db2["comentarios"]: db2["comentarios"][qid]=[]
                db2["comentarios"][qid].append({
                    "id": str(uuid.uuid4())[:8],
                    "username": u["username"],
                    "nome": u["nome"],
                    "texto": texto.strip(),
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                save_db(db2); st.rerun()

# ── Notificações ──────────────────────────────────────────────────────────
def get_notificacoes(username, role):
    db=load_db(); now=datetime.now(); notifs=[]
    turmas=get_minhas_turmas(username, role)
    for pid,p in db["provas"].items():
        if role=="aluno":
            if p.get("turma_id") in turmas or p.get("turma_id") is None:
                ab=datetime.fromisoformat(p["abertura"]) if p.get("abertura") else None
                fe=datetime.fromisoformat(p["fechamento"]) if p.get("fechamento") else None
                udata=get_user_data(username)
                ja_fez=pid in udata.get("respostas_provas",{})
                if ab and not ja_fez:
                    diff=(ab-now).total_seconds()/3600
                    if 0<=diff<=24:
                        notifs.append(f"⏰ Prova **{p['nome']}** abre em {int(diff)}h!")
                    elif diff<0 and fe and now<fe and not ja_fez:
                        notifs.append(f"📝 Prova **{p['nome']}** disponível! Não perca.")
        elif role=="prof" and p["prof_u"]==username:
            fe=datetime.fromisoformat(p["fechamento"]) if p.get("fechamento") else None
            if fe:
                diff=(fe-now).total_seconds()/3600
                if 0<=diff<=2:
                    notifs.append(f"⏳ Prova **{p['nome']}** fecha em {int(diff*60)}min!")
    return notifs

# ── LOGIN ─────────────────────────────────────────────────────────────────
def tela_login():
    col1,col2,col3=st.columns([1,1.2,1])
    with col2:
        st.markdown("## 📚 StudyQuiz")
        st.markdown("Sistema de questões para cursinhos")
        st.divider()
        tipo=st.radio("Entrar como:",["👨‍🏫 Professor","👤 Aluno","⚙️ Admin"],horizontal=True)
        if tipo=="👨‍🏫 Professor":
            aba=st.tabs(["Entrar","Criar conta"])
            with aba[0]:
                u=st.text_input("Usuário",key="l_user")
                p=st.text_input("Senha",type="password",key="l_pass")
                if st.button("Entrar",use_container_width=True,type="primary"):
                    ok,msg=login(u,p,"prof")
                    if ok: st.rerun()
                    else: st.error(msg)
            with aba[1]:
                nome=st.text_input("Nome completo",key="r_nome")
                u2=st.text_input("Usuário",key="r_user")
                p2=st.text_input("Senha",type="password",key="r_pass")
                if st.button("Criar conta",use_container_width=True,type="primary"):
                    ok,msg=registrar(nome,u2,p2,"prof")
                    if ok: st.rerun()
                    else: st.error(msg)
        elif tipo=="👤 Aluno":
            aba=st.tabs(["Entrar","Criar conta"])
            with aba[0]:
                u=st.text_input("Usuário",key="al_user")
                p=st.text_input("Senha",type="password",key="al_pass")
                if st.button("Entrar",use_container_width=True,type="primary"):
                    ok,msg=login(u,p,"aluno")
                    if ok: st.rerun()
                    else: st.error(msg)
            with aba[1]:
                nome=st.text_input("Nome completo",key="ar_nome")
                u2=st.text_input("Usuário",key="ar_user")
                p2=st.text_input("Senha",type="password",key="ar_pass")
                if st.button("Criar conta",use_container_width=True,type="primary"):
                    ok,msg=registrar(nome,u2,p2,"aluno")
                    if ok: st.rerun()
                    else: st.error(msg)
        else:
            p=st.text_input("Senha admin",type="password",key="a_pass")
            if st.button("Entrar como admin",use_container_width=True):
                ok,msg=login("admin",p,"admin")
                if ok: st.rerun()
                else: st.error(msg)

# ── SIDEBAR ───────────────────────────────────────────────────────────────
def sidebar():
    u=st.session_state.usuario; db=load_db()
    with st.sidebar:
        col1,col2=st.columns([1,3])
        with col1: render_avatar(u["nome"],u["username"],40)
        with col2:
            role_label={"prof":"Professor","aluno":"Aluno","admin":"Admin"}.get(u["role"],"")
            st.markdown(f"**{u['nome']}**")
            st.caption(f"`{role_label}`")

        notifs=get_notificacoes(u["username"],u["role"])
        if notifs:
            st.divider()
            for n in notifs:
                st.markdown(f'<span class="notif-badge">{n}</span>', unsafe_allow_html=True)

        st.divider()
        paginas=["📖 Estudar","📝 Provas","🔁 Modo revisão","⭐ Favoritos","📊 Meu desempenho","🏆 Ranking","🔒 Minha conta"]
        if u["role"]=="prof":
            paginas+=["➕ Adicionar questão","🤖 Gerar do PDF","📋 Banco de questões","👥 Turmas","📋 Criar prova","📊 Relatório de turma"]
        elif u["role"]=="admin":
            paginas+=["📋 Banco de questões","⚙️ Admin"]
        pg=st.radio("Navegação",paginas,label_visibility="collapsed")
        st.divider()
        total_profs=len([x for x in db["users"].values() if x["role"]=="prof"])
        total_qs=sum(len(qs) for prof in db["questions"].values() for qs in prof.values())
        total_turmas=len(db.get("turmas",{}))
        st.caption(f"👨‍🏫 {total_profs} professor(es)")
        st.caption(f"📝 {total_qs} questão(ões)")
        st.caption(f"👥 {total_turmas} turma(s)")
        st.divider()
        if st.button("🚪 Sair",use_container_width=True): logout()
    return pg

# ── ESTUDAR ───────────────────────────────────────────────────────────────
def pg_estudar():
    st.header("📖 Estudar")
    u=st.session_state.usuario
    todas=get_all_questions()
    materias=sorted(set(q["materia"] for q in todas))

    if not st.session_state.quiz_ativo and not st.session_state.quiz_finalizado:
        with st.container(border=True):
            col1,col2=st.columns(2)
            with col1: mat_sel=st.selectbox("Matéria",["🔀 Todas"]+materias)
            with col2: dif_sel=st.selectbox("Dificuldade",["🔀 Todas"]+DIFICULDADES)

            # Filtro por tag
            todas_tags=sorted(set(t.strip() for q in todas for t in q.get("tags","").split(",") if t.strip()))
            tag_sel=st.multiselect("Filtrar por subtópico (tags)",todas_tags)

            col3,col4,col5=st.columns(3)
            with col3: qtd=st.number_input("Quantidade",min_value=1,max_value=500,value=10)
            with col4: shuffle=st.checkbox("Embaralhar",value=True)
            with col5: usar_tempo=st.checkbox("Temporizador")
            tempo_limit=None
            if usar_tempo: tempo_limit=st.slider("Segundos por questão",10,120,30)

            if st.button("▶ Iniciar sessão",type="primary",use_container_width=True):
                import random
                pool=todas
                if not mat_sel.startswith("🔀"): pool=[q for q in pool if q["materia"]==mat_sel]
                if not dif_sel.startswith("🔀"): pool=[q for q in pool if q.get("dificuldade")==dif_sel]
                if tag_sel: pool=[q for q in pool if any(t in q.get("tags","") for t in tag_sel)]
                if not pool: st.error("Nenhuma questão com esses filtros."); return
                if shuffle: random.shuffle(pool)
                pool=pool[:int(qtd)]
                st.session_state.quiz_qs=pool; st.session_state.quiz_idx=0
                st.session_state.quiz_acertos=0; st.session_state.quiz_erros=0
                st.session_state.quiz_respondida=False; st.session_state.quiz_escolha=None
                st.session_state.quiz_ativo=True; st.session_state.quiz_finalizado=False
                st.session_state.quiz_mat=mat_sel; st.session_state.quiz_dif=dif_sel
                st.session_state.quiz_tempo_limit=tempo_limit
                st.session_state.quiz_tempo_inicio=time.time()
                st.session_state.quiz_respostas=[]; st.session_state.ultima_resposta=None
                st.rerun()

    elif st.session_state.quiz_finalizado and not st.session_state.revisao_ativa:
        ac=st.session_state.quiz_acertos; er=st.session_state.quiz_erros
        tot=ac+er; pct=round(ac/tot*100) if tot else 0
        col1,col2,col3=st.columns(3)
        col1.metric("✅ Acertos",ac); col2.metric("❌ Erros",er)
        col3.metric("📊 Aproveitamento",f"{pct}%")
        if pct>=70: st.success("🎉 Ótimo desempenho!")
        elif pct>=50: st.warning("📚 Resultado razoável.")
        else: st.error("💪 Não desista!")
        if u["role"]!="admin":
            udata=get_user_data(u["username"])
            udata["historico"].append({
                "data":datetime.now().strftime("%d/%m/%Y %H:%M"),
                "materia":st.session_state.quiz_mat,"dificuldade":st.session_state.quiz_dif,
                "total":tot,"acertos":ac,"pct":pct,
                "respostas":[{"enunciado":r["q"]["enunciado"],"acertou":r["escolha"]==r["q"]["gabarito"]} for r in st.session_state.quiz_respostas]
            })
            save_user_data(u["username"],udata)
        with st.expander("📋 Revisão"):
            for r in st.session_state.quiz_respostas:
                q=r["q"]; ok=r["escolha"]==q["gabarito"]
                st.markdown(f"{'✅' if ok else '❌'} **{q['enunciado']}**")
                render_tags(q)
                st.caption(f"Sua: **{r['escolha'].upper()}** | Gabarito: **{q['gabarito'].upper()}**")
                if q.get("explicacao"): st.caption(f"💡 {q['explicacao']}")
                with st.expander(f"💬 Comentários",expanded=False):
                    pg_comentarios_questao(q_id(q),q["enunciado"])
                st.divider()
        if st.button("↺ Nova sessão",type="primary"):
            st.session_state.quiz_ativo=False; st.session_state.quiz_finalizado=False; st.rerun()

    else:
        qs=st.session_state.quiz_qs; idx=st.session_state.quiz_idx
        if idx>=len(qs):
            st.session_state.quiz_ativo=False; st.session_state.quiz_finalizado=True; st.rerun(); return
        q=qs[idx]
        tempo_limit=st.session_state.quiz_tempo_limit
        if tempo_limit and not st.session_state.quiz_respondida:
            elapsed=time.time()-st.session_state.quiz_tempo_inicio
            restante=max(0,tempo_limit-elapsed); pct_t=restante/tempo_limit
            cor="🟢" if pct_t>0.5 else "🟡" if pct_t>0.25 else "🔴"
            st.progress(pct_t,text=f"{cor} Tempo: {int(restante)}s")
            if restante<=0:
                st.session_state.quiz_respondida=True; st.session_state.quiz_escolha="—"
                st.session_state.quiz_erros+=1
                st.session_state.quiz_respostas.append({"q":q,"escolha":"—"})
                st.session_state.ultima_resposta="wrong"; st.rerun()

        st.progress(idx/len(qs),text=f"Questão {idx+1} de {len(qs)}  —  ✅ {st.session_state.quiz_acertos}  ❌ {st.session_state.quiz_erros}")

        # Animação de resultado
        if st.session_state.ultima_resposta=="correct":
            mostrar_animacao(True)
        elif st.session_state.ultima_resposta=="wrong":
            mostrar_animacao(False)

        with st.container(border=True):
            col1,col2,col3=st.columns([3,1,1])
            with col1:
                st.caption(f"📚 {q['materia']}  ·  {q['prof_nome']}")
                render_tags(q)
            with col2:
                dif=q.get("dificuldade","—")
                cor_dif={"Fácil":"🟢","Médio":"🟡","Difícil":"🔴"}.get(dif,"⚪")
                st.caption(f"{cor_dif} {dif}")
            with col3:
                if u["role"]!="admin":
                    udata=get_user_data(u["username"]); qid=q_id(q)
                    ja_fav=qid in udata["favoritos"]
                    if st.button("⭐" if ja_fav else "☆",key=f"fav_{idx}"):
                        if ja_fav: udata["favoritos"].remove(qid)
                        else: udata["favoritos"].append(qid)
                        save_user_data(u["username"],udata); st.rerun()
            st.markdown(f"**{q['enunciado']}**")
            mostrar_imagem_questao(q)
            letras=["a","b","c","d"]
            labels=[f"{l.upper()}) {q[f'alternativa_{l}']}" for l in letras]
            if not st.session_state.quiz_respondida:
                resp=st.radio("Escolha:",labels,index=None,key=f"radio_{idx}")
                if st.button("Confirmar →",type="primary",disabled=(resp is None)):
                    letra=letras[labels.index(resp)]
                    st.session_state.quiz_escolha=letra; st.session_state.quiz_respondida=True
                    st.session_state.quiz_tempo_inicio=time.time()
                    acertou=letra==q["gabarito"]
                    if acertou: st.session_state.quiz_acertos+=1
                    else: st.session_state.quiz_erros+=1
                    st.session_state.ultima_resposta="correct" if acertou else "wrong"
                    st.session_state.quiz_respostas.append({"q":q,"escolha":letra}); st.rerun()
            else:
                escolha=st.session_state.quiz_escolha; acertou=escolha==q["gabarito"]
                for i,l in enumerate(letras):
                    if l==q["gabarito"]: st.success(f"✅ {labels[i]}")
                    elif l==escolha and not acertou: st.error(f"❌ {labels[i]}")
                    else: st.write(labels[i])
                if acertou: st.success("**Correto!**")
                else: st.error(f"**Errado!** Resposta: **{q['gabarito'].upper()}**")
                if q.get("explicacao"):
                    with st.expander("💡 Explicação"): st.write(q["explicacao"])
                with st.expander("💬 Comentários desta questão"):
                    pg_comentarios_questao(q_id(q),q["enunciado"])
                if st.button("Próxima →",type="primary"):
                    st.session_state.quiz_idx+=1; st.session_state.quiz_respondida=False
                    st.session_state.quiz_escolha=None; st.session_state.ultima_resposta=None
                    st.session_state.quiz_tempo_inicio=time.time(); st.rerun()

        if tempo_limit and not st.session_state.quiz_respondida:
            time.sleep(1); st.rerun()

# ── DASHBOARD VISUAL ──────────────────────────────────────────────────────
def pg_desempenho():
    st.header("📊 Meu desempenho")
    u=st.session_state.usuario; udata=get_user_data(u["username"])
    hist=udata.get("historico",[])
    if not hist: st.info("Nenhuma sessão concluída ainda."); return

    total_sessoes=len(hist); total_qs=sum(h["total"] for h in hist)
    total_ac=sum(h["acertos"] for h in hist); media_pct=round(sum(h["pct"] for h in hist)/total_sessoes)

    col1,col2,col3,col4=st.columns(4)
    col1.metric("📅 Sessões",total_sessoes); col2.metric("📝 Respondidas",total_qs)
    col3.metric("✅ Acertos",total_ac); col4.metric("📊 Média",f"{media_pct}%")
    st.divider()

    # Gráfico de barras por matéria (HTML/CSS)
    st.subheader("📊 Por matéria")
    por_mat={}
    for h in hist:
        mat=h["materia"] if not h["materia"].startswith("🔀") else "Mistas"
        if mat not in por_mat: por_mat[mat]={"total":0,"acertos":0}
        por_mat[mat]["total"]+=h["total"]; por_mat[mat]["acertos"]+=h["acertos"]

    if por_mat:
        bars_html=""
        cores=["#4a9ff0","#4af0a0","#f0a04a","#a78bfa","#f04a9f","#4af0f0"]
        for i,(mat,d) in enumerate(sorted(por_mat.items())):
            pct=round(d["acertos"]/d["total"]*100) if d["total"] else 0
            cor=cores[i%len(cores)]
            bars_html+=f"""
            <div style="margin-bottom:12px">
              <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
                <span style="color:var(--text-color,#dde4f5)">{mat}</span>
                <span style="color:{cor};font-family:monospace;font-weight:700">{pct}% ({d['acertos']}/{d['total']})</span>
              </div>
              <div style="height:10px;background:rgba(255,255,255,0.08);border-radius:5px;overflow:hidden">
                <div style="height:100%;width:{pct}%;background:{cor};border-radius:5px;transition:width 1s ease;animation:progShine 2s infinite"></div>
              </div>
            </div>"""
        st.markdown(f'<div style="padding:16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px">{bars_html}</div>', unsafe_allow_html=True)

    st.divider()

    # Gráfico de pizza (SVG)
    st.subheader("🍕 Acertos vs Erros")
    erros_total=total_qs-total_ac
    pct_ac=round(total_ac/total_qs*100) if total_qs else 0
    circunf=2*3.14159*45
    dash_ac=round(circunf*pct_ac/100,1)
    dash_er=round(circunf-dash_ac,1)
    svg=f"""<svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:300px">
      <circle cx="60" cy="60" r="45" fill="none" stroke="#1e2535" stroke-width="18"/>
      <circle cx="60" cy="60" r="45" fill="none" stroke="#4af0a0" stroke-width="18"
        stroke-dasharray="{dash_ac} {dash_er}" stroke-dashoffset="0"
        style="transform:rotate(-90deg);transform-origin:60px 60px"/>
      <circle cx="60" cy="60" r="45" fill="none" stroke="#f04a4a" stroke-width="18"
        stroke-dasharray="{dash_er} {dash_ac}" stroke-dashoffset="-{dash_ac}"
        style="transform:rotate(-90deg);transform-origin:60px 60px"/>
      <text x="60" y="55" text-anchor="middle" font-size="16" font-weight="700" fill="#dde4f5">{pct_ac}%</text>
      <text x="60" y="70" text-anchor="middle" font-size="9" fill="#7a88aa">acertos</text>
      <rect x="120" y="30" width="12" height="12" rx="3" fill="#4af0a0"/>
      <text x="138" y="41" font-size="11" fill="#dde4f5">Acertos ({total_ac})</text>
      <rect x="120" y="55" width="12" height="12" rx="3" fill="#f04a4a"/>
      <text x="138" y="66" font-size="11" fill="#dde4f5">Erros ({erros_total})</text>
    </svg>"""
    st.markdown(svg, unsafe_allow_html=True)

    st.divider()
    st.subheader("Por dificuldade")
    por_dif={}
    for h in hist:
        dif=h.get("dificuldade","—") if not h.get("dificuldade","").startswith("🔀") else "Mistas"
        if dif not in por_dif: por_dif[dif]={"total":0,"acertos":0}
        por_dif[dif]["total"]+=h["total"]; por_dif[dif]["acertos"]+=h["acertos"]
    for dif,d in sorted(por_dif.items()):
        pct=round(d["acertos"]/d["total"]*100) if d["total"] else 0
        cor={"Fácil":"🟢","Médio":"🟡","Difícil":"🔴"}.get(dif,"⚪")
        st.progress(pct/100,text=f"{cor} {dif}: {pct}% ({d['acertos']}/{d['total']})")

    st.divider()
    st.subheader("Histórico")
    for h in reversed(hist):
        cor="🟢" if h["pct"]>=70 else "🟡" if h["pct"]>=50 else "🔴"
        st.caption(f"{cor} **{h['data']}** — {h['materia']} | {h.get('dificuldade','—')} | {h['acertos']}/{h['total']} ({h['pct']}%)")
    if st.button("🗑️ Limpar histórico"):
        udata["historico"]=[]; save_user_data(u["username"],udata); st.rerun()

# ── MODO REVISÃO ──────────────────────────────────────────────────────────
def pg_revisao():
    st.header("🔁 Modo revisão")
    u=st.session_state.usuario; udata=get_user_data(u["username"]); hist=udata.get("historico",[])
    todas=get_all_questions(); todas_por_enunc={q["enunciado"]:q for q in todas}
    erradas=[]
    for h in hist:
        for r in h.get("respostas",[]):
            if not r.get("acertou",True):
                enunc=r.get("enunciado","")
                if enunc in todas_por_enunc: erradas.append(todas_por_enunc[enunc])
    vistas=set(); erradas_unicas=[]
    for q in erradas:
        qid=q_id(q)
        if qid not in vistas: vistas.add(qid); erradas_unicas.append(q)
    if not erradas_unicas:
        st.info("Nenhuma questão errada encontrada. Complete sessões de estudo primeiro!"); return
    st.caption(f"📋 {len(erradas_unicas)} questão(ões) que você já errou")
    if not st.session_state.quiz_ativo and not st.session_state.revisao_ativa and not st.session_state.quiz_finalizado:
        col1,col2=st.columns(2)
        with col1: qtd=st.number_input("Quantidade",min_value=1,max_value=len(erradas_unicas),value=min(10,len(erradas_unicas)))
        with col2: shuffle=st.checkbox("Embaralhar",value=True)
        if st.button("🔁 Iniciar revisão",type="primary",use_container_width=True):
            import random
            pool=erradas_unicas.copy()
            if shuffle: random.shuffle(pool)
            pool=pool[:int(qtd)]
            st.session_state.quiz_qs=pool; st.session_state.quiz_idx=0
            st.session_state.quiz_acertos=0; st.session_state.quiz_erros=0
            st.session_state.quiz_respondida=False; st.session_state.quiz_escolha=None
            st.session_state.quiz_ativo=True; st.session_state.revisao_ativa=True
            st.session_state.quiz_finalizado=False; st.session_state.quiz_mat="Revisão"
            st.session_state.quiz_dif="—"; st.session_state.quiz_tempo_limit=None
            st.session_state.quiz_tempo_inicio=time.time(); st.session_state.quiz_respostas=[]
            st.session_state.ultima_resposta=None; st.rerun()
    elif st.session_state.quiz_finalizado and st.session_state.revisao_ativa:
        ac=st.session_state.quiz_acertos; er=st.session_state.quiz_erros
        tot=ac+er; pct=round(ac/tot*100) if tot else 0
        col1,col2,col3=st.columns(3)
        col1.metric("✅ Acertos",ac); col2.metric("❌ Erros",er); col3.metric("📊 Aproveitamento",f"{pct}%")
        if pct>=70: st.success("🎉 Você dominou essas questões!")
        elif pct>=50: st.warning("📚 Melhorando! Continue.")
        else: st.error("💪 Continue praticando.")
        udata2=get_user_data(u["username"])
        udata2["historico"].append({
            "data":datetime.now().strftime("%d/%m/%Y %H:%M"),"materia":"Revisão","dificuldade":"—",
            "total":tot,"acertos":ac,"pct":pct,
            "respostas":[{"enunciado":r["q"]["enunciado"],"acertou":r["escolha"]==r["q"]["gabarito"]} for r in st.session_state.quiz_respostas]
        })
        save_user_data(u["username"],udata2)
        if st.button("↺ Revisar novamente",type="primary"):
            st.session_state.quiz_ativo=False; st.session_state.quiz_finalizado=False
            st.session_state.revisao_ativa=False; st.rerun()
    elif st.session_state.quiz_ativo and st.session_state.revisao_ativa:
        qs=st.session_state.quiz_qs; idx=st.session_state.quiz_idx
        if idx>=len(qs):
            st.session_state.quiz_ativo=False; st.session_state.quiz_finalizado=True; st.rerun(); return
        q=qs[idx]
        if st.session_state.ultima_resposta=="correct": mostrar_animacao(True)
        elif st.session_state.ultima_resposta=="wrong": mostrar_animacao(False)
        st.progress(idx/len(qs),text=f"Questão {idx+1} de {len(qs)}  —  ✅ {st.session_state.quiz_acertos}  ❌ {st.session_state.quiz_erros}")
        with st.container(border=True):
            col1,col2=st.columns([4,1])
            with col1:
                dif=q.get("dificuldade","—"); cor_dif={"Fácil":"🟢","Médio":"🟡","Difícil":"🔴"}.get(dif,"⚪")
                st.caption(f"📚 {q['materia']}  ·  {cor_dif} {dif}  ·  {q['prof_nome']}")
                render_tags(q)
            with col2:
                udata3=get_user_data(u["username"]); qid=q_id(q); ja_fav=qid in udata3["favoritos"]
                if st.button("⭐" if ja_fav else "☆",key=f"rev_fav_{idx}"):
                    if ja_fav: udata3["favoritos"].remove(qid)
                    else: udata3["favoritos"].append(qid)
                    save_user_data(u["username"],udata3); st.rerun()
            st.markdown(f"**{q['enunciado']}**"); mostrar_imagem_questao(q)
            letras=["a","b","c","d"]; labels=[f"{l.upper()}) {q[f'alternativa_{l}']}" for l in letras]
            if not st.session_state.quiz_respondida:
                resp=st.radio("Escolha:",labels,index=None,key=f"rev_radio_{idx}")
                if st.button("Confirmar →",type="primary",disabled=(resp is None)):
                    letra=letras[labels.index(resp)]; st.session_state.quiz_escolha=letra
                    st.session_state.quiz_respondida=True; acertou=letra==q["gabarito"]
                    if acertou: st.session_state.quiz_acertos+=1
                    else: st.session_state.quiz_erros+=1
                    st.session_state.ultima_resposta="correct" if acertou else "wrong
