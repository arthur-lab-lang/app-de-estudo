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
        json={"model":"openrouter/auto","messages":[{"role":"user","content":prompt}]}
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
                    st.session_state.ultima_resposta="correct" if acertou else "wrong"
                    st.session_state.quiz_respostas.append({"q":q,"escolha":letra}); st.rerun()
            else:
                escolha=st.session_state.quiz_escolha; acertou=escolha==q["gabarito"]
                for i,l in enumerate(letras):
                    if l==q["gabarito"]: st.success(f"✅ {labels[i]}")
                    elif l==escolha and not acertou: st.error(f"❌ {labels[i]}")
                    else: st.write(labels[i])
                if acertou: st.success("**Correto! Você aprendeu essa!**")
                else: st.error(f"**Errado de novo!** Resposta: **{q['gabarito'].upper()}**")
                if q.get("explicacao"):
                    with st.expander("💡 Explicação"): st.write(q["explicacao"])
                with st.expander("💬 Comentários"):
                    pg_comentarios_questao(q_id(q),q["enunciado"])
                if st.button("Próxima →",type="primary"):
                    st.session_state.quiz_idx+=1; st.session_state.quiz_respondida=False
                    st.session_state.quiz_escolha=None; st.session_state.ultima_resposta=None; st.rerun()

# ── RANKING ───────────────────────────────────────────────────────────────
def pg_ranking():
    st.header("🏆 Ranking")
    u=st.session_state.usuario; db=load_db()
    col1,col2=st.columns(2)
    with col1: tipo=st.selectbox("Ranking por",["📊 Aproveitamento médio","📝 Total de questões","🔥 Sessões"])
    with col2:
        turmas=get_minhas_turmas(u["username"],u["role"])
        turma_opts={"_geral":"🌐 Geral (todos)"}
        turma_opts.update({tid:t["nome"] for tid,t in turmas.items()})
        filtro_turma=st.selectbox("Turma",list(turma_opts.keys()),format_func=lambda x:turma_opts[x])
    st.divider()
    alunos=[(uid,d) for uid,d in db["users"].items() if d["role"] in ["aluno","prof"]]
    if filtro_turma!="_geral":
        turma_alunos=db["turmas"].get(filtro_turma,{}).get("alunos",[])
        alunos=[(uid,d) for uid,d in alunos if uid in turma_alunos]
    ranking=[]
    for uid,d in alunos:
        udata=db.get("user_data",{}).get(uid,{}); hist=udata.get("historico",[])
        if not hist: continue
        total_qs=sum(h["total"] for h in hist); media=round(sum(h["pct"] for h in hist)/len(hist))
        ranking.append({"username":uid,"nome":d["nome"],"media":media,"total_qs":total_qs,"sessoes":len(hist)})
    if not ranking: st.info("Nenhum dado ainda."); return
    if tipo.startswith("📊"): ranking.sort(key=lambda x:x["media"],reverse=True); chave,label="media","%"
    elif tipo.startswith("📝"): ranking.sort(key=lambda x:x["total_qs"],reverse=True); chave,label="total_qs"," questões"
    else: ranking.sort(key=lambda x:x["sessoes"],reverse=True); chave,label="sessoes"," sessões"
    medalhas=["🥇","🥈","🥉"]; meu_pos=None
    for i,r in enumerate(ranking):
        pos=i+1; medalha=medalhas[i] if i<3 else f"#{pos}"
        sou_eu=r["username"]==u["username"]
        if sou_eu: meu_pos=pos
        with st.container(border=True):
            col1,col2,col3=st.columns([1,4,2])
            with col1: st.markdown(f"### {medalha}")
            with col2:
                destaque=" **(você)**" if sou_eu else ""
                row=st.columns([1,4])
                with row[0]: render_avatar(r["nome"],r["username"],32)
                with row[1]:
                    st.markdown(f"**{r['nome']}**{destaque}")
                    st.caption(f"@{r['username']}  ·  {r['sessoes']} sessões")
            with col3:
                valor=r[chave]; cor="🟢" if (chave=="media" and valor>=70) else "🟡" if (chave=="media" and valor>=50) else "🔵"
                st.metric("",f"{cor} {valor}{label}")
    if meu_pos: st.divider(); st.caption(f"Sua posição: **#{meu_pos}** de {len(ranking)}")

# ── FAVORITOS ─────────────────────────────────────────────────────────────
def pg_favoritos():
    st.header("⭐ Favoritos")
    u=st.session_state.usuario; udata=get_user_data(u["username"])
    favs=udata.get("favoritos",[])
    if not favs: st.info("Nenhuma questão favoritada."); return
    todas=get_all_questions(); fav_qs=[q for q in todas if q_id(q) in favs]
    st.caption(f"{len(fav_qs)} questão(ões) favoritada(s)")
    for q in fav_qs:
        with st.container(border=True):
            col1,col2=st.columns([5,1])
            with col1:
                dif=q.get("dificuldade","—"); cor_dif={"Fácil":"🟢","Médio":"🟡","Difícil":"🔴"}.get(dif,"⚪")
                st.caption(f"📚 {q['materia']}  ·  {q['prof_nome']}  ·  {cor_dif} {dif}")
                render_tags(q)
                st.markdown(f"**{q['enunciado']}**")
                st.caption(f"A) {q['alternativa_a']}  ·  B) {q['alternativa_b']}  ·  C) {q['alternativa_c']}  ·  D) {q['alternativa_d']}")
                st.caption(f"✅ Gabarito: **{q['gabarito'].upper()}**")
                with st.expander("💬 Comentários"):
                    pg_comentarios_questao(q_id(q),q["enunciado"])
            with col2:
                if st.button("🗑️",key=f"rmfav_{q_id(q)}"):
                    udata["favoritos"].remove(q_id(q)); save_user_data(u["username"],udata); st.rerun()

# ── MINHA CONTA ───────────────────────────────────────────────────────────
def pg_minha_conta():
    st.header("🔒 Minha conta")
    u=st.session_state.usuario; udata=get_user_data(u["username"])

    col1,col2=st.columns([1,4])
    with col1: render_avatar(u["nome"],u["username"],64)
    with col2:
        db=load_db(); user=db["users"][u["username"]]
        st.markdown(f"### {user['nome']}")
        st.caption(f"@{u['username']}  ·  {u['role']}")

    st.divider()
    with st.expander("🔑 Trocar senha",expanded=True):
        with st.form("form_senha"):
            atual=st.text_input("Senha atual",type="password")
            nova=st.text_input("Nova senha",type="password")
            nova2=st.text_input("Confirmar",type="password")
            if st.form_submit_button("Salvar",type="primary"):
                if nova!=nova2: st.error("As senhas não coincidem.")
                else:
                    ok,msg=alterar_senha(u["username"],atual,nova)
                    if ok: st.success("✅ Senha alterada!")
                    else: st.error(msg)

    if u["role"]=="prof":
        st.divider()
        with st.expander("🤖 Chave API OpenRouter"):
            api_key_salva=udata.get("api_key","")
            nova_key=st.text_input("Chave",value=api_key_salva,type="password",placeholder="sk-or-...")
            if st.button("💾 Salvar chave"):
                udata["api_key"]=nova_key; save_user_data(u["username"],udata); st.success("✅ Chave salva!")

    if u["role"]=="aluno":
        st.divider()
        minhas_turmas=get_minhas_turmas(u["username"],"aluno")
        with st.expander("👥 Minhas turmas"):
            if not minhas_turmas: st.info("Você não está em nenhuma turma.")
            else:
                for tid,t in minhas_turmas.items(): st.write(f"📚 **{t['nome']}** `código: {tid}`")
            pg_entrar_turma()

# ── ADICIONAR ─────────────────────────────────────────────────────────────
def pg_adicionar():
    st.header("➕ Adicionar questão")
    u=st.session_state.usuario; db=load_db()
    minhas_mats=sorted(db["questions"].get(u["username"],{}).keys())
    with st.form("form_questao"):
        tipo_mat=st.radio("Matéria",["Selecionar existente","Criar nova"],horizontal=True)
        mat=st.selectbox("Matéria",minhas_mats) if (tipo_mat=="Selecionar existente" and minhas_mats) else st.text_input("Nova matéria")
        tags=st.text_input("🏷️ Tags / Subtópicos",placeholder="Ex: frações, álgebra, equações (separe por vírgula)")
        dificuldade=st.select_slider("Dificuldade",DIFICULDADES,value="Médio")
        enunc=st.text_area("Enunciado")
        img_upload=st.file_uploader("🖼️ Imagem (opcional)",type=["png","jpg","jpeg","gif","webp"])
        col1,col2=st.columns(2)
        with col1: alt_a=st.text_input("A)"); alt_c=st.text_input("C)")
        with col2: alt_b=st.text_input("B)"); alt_d=st.text_input("D)")
        gabarito=st.selectbox("Gabarito",["A","B","C","D"])
        explicacao=st.text_area("Explicação (opcional)",height=80)
        if st.form_submit_button("✓ Salvar",type="primary",use_container_width=True):
            if not all([mat,enunc,alt_a,alt_b,alt_c,alt_d]): st.error("Preencha todos os campos.")
            else:
                db2=load_db()
                if u["username"] not in db2["questions"]: db2["questions"][u["username"]]={}
                if mat not in db2["questions"][u["username"]]: db2["questions"][u["username"]][mat]=[]
                q_novo={"enunciado":enunc,"alternativa_a":alt_a,"alternativa_b":alt_b,
                        "alternativa_c":alt_c,"alternativa_d":alt_d,"gabarito":gabarito.lower(),
                        "explicacao":explicacao,"materia":mat,"dificuldade":dificuldade,
                        "tags":tags,"imagem":None}
                if img_upload: q_novo["imagem"]=img_to_base64(img_upload)
                db2["questions"][u["username"]][mat].append(q_novo)
                save_db(db2); st.success(f"✅ Salvo em **{mat}** ({dificuldade})!"); st.rerun()

# ── GERAR PDF ─────────────────────────────────────────────────────────────
def pg_gerar_pdf():
    st.header("🤖 Gerar do PDF")
    u=st.session_state.usuario; udata=get_user_data(u["username"])
    api_key_salva=udata.get("api_key","")
    if api_key_salva:
        st.success("✅ Usando chave salva.")
        api_key=api_key_salva
        if st.button("🔄 Usar outra chave"):
            udata["api_key"]=""; save_user_data(u["username"],udata); st.rerun()
    else:
        api_key=st.text_input("🔑 Chave OpenRouter",type="password",placeholder="sk-or-...")
    st.divider()
    col1,col2=st.columns(2)
    with col1: pdf_file=st.file_uploader("📄 Upload do PDF",type="pdf")
    with col2:
        db=load_db(); minhas_mats=sorted(db["questions"].get(u["username"],{}).keys())
        tipo_mat=st.radio("Matéria",["Criar nova","Selecionar existente"],horizontal=True)
        materia=st.selectbox("Existente",minhas_mats) if (tipo_mat=="Selecionar existente" and minhas_mats) else st.text_input("Nova matéria")
        tags_ia=st.text_input("🏷️ Subtópicos para focar",placeholder="Ex: mitose, fotossíntese")
        dificuldade=st.select_slider("Dificuldade",DIFICULDADES,value="Médio")
        quantidade=st.slider("Quantidade",1,20,5)
    if pdf_file and materia and api_key:
        if st.button("✨ Gerar com IA",type="primary",use_container_width=True):
            with st.spinner("📖 Lendo PDF..."):
                try:
                    texto=extrair_texto_pdf(pdf_file)
                    if not texto: st.error("Sem texto."); st.stop()
                except Exception as e: st.error(f"Erro: {e}"); st.stop()
            with st.spinner("🤖 Gerando questões..."):
                try:
                    qs=gerar_questoes_ia(texto,quantidade,materia,dificuldade,api_key,tags_ia)
                    st.session_state.qs_geradas=qs; st.success(f"✅ {len(qs)} questões geradas!")
                except Exception as e: st.error(f"Erro na IA: {e}"); st.stop()
    if st.session_state.qs_geradas:
        st.divider(); st.subheader("📝 Revise e salve")
        salvar=st.button("💾 Salvar todas",type="primary"); qs_salvar=[]
        for i,q in enumerate(st.session_state.qs_geradas):
            with st.expander(f"Q{i+1}: {q['enunciado'][:80]}...",expanded=False):
                enunc=st.text_area("Enunciado",q["enunciado"],key=f"enunc_{i}")
                tags_q=st.text_input("🏷️ Tags",q.get("tags",""),key=f"tags_{i}")
                c1,c2=st.columns(2)
                with c1: a=st.text_input("A)",q["alternativa_a"],key=f"a_{i}"); c=st.text_input("C)",q["alternativa_c"],key=f"c_{i}")
                with c2: b=st.text_input("B)",q["alternativa_b"],key=f"b_{i}"); d=st.text_input("D)",q["alternativa_d"],key=f"d_{i}")
                gab_idx=["a","b","c","d"].index(q["gabarito"]) if q["gabarito"] in ["a","b","c","d"] else 0
                gab=st.selectbox("Gabarito",["A","B","C","D"],index=gab_idx,key=f"gab_{i}")
                explic=st.text_input("Explicação",q.get("explicacao",""),key=f"explic_{i}")
                dif_q=st.select_slider("Dificuldade",DIFICULDADES,value=q.get("dificuldade","Médio"),key=f"dif_{i}")
                if st.checkbox("Incluir",value=True,key=f"inc_{i}"):
                    qs_salvar.append({"enunciado":enunc,"alternativa_a":a,"alternativa_b":b,
                                      "alternativa_c":c,"alternativa_d":d,"gabarito":gab.lower(),
                                      "explicacao":explic,"materia":materia,"dificuldade":dif_q,"tags":tags_q,"imagem":None})
        if salvar and qs_salvar:
            db2=load_db()
            if u["username"] not in db2["questions"]: db2["questions"][u["username"]]={}
            if materia not in db2["questions"][u["username"]]: db2["questions"][u["username"]][materia]=[]
            db2["questions"][u["username"]][materia].extend(qs_salvar)
            save_db(db2); st.session_state.qs_geradas=[]; st.success(f"✅ {len(qs_salvar)} questões salvas!"); st.rerun()

# ── BANCO ─────────────────────────────────────────────────────────────────
def pg_banco():
    st.header("📋 Banco de questões")
    u=st.session_state.usuario; db=load_db()
    if u["role"]=="prof":
        fonte={mat:(qs,u["nome"],u["username"],mat) for mat,qs in db["questions"].get(u["username"],{}).items()}
    else:
        fonte={}
        for prof_u,mats in db["questions"].items():
            prof_nome=db["users"].get(prof_u,{}).get("nome",prof_u)
            for mat,qs in mats.items():
                fonte[f"{mat} ({prof_nome})"]=(qs,prof_nome,prof_u,mat)
    if not fonte: st.info("Nenhuma questão."); return

    col1,col2=st.columns(2)
    with col1: filtro_dif=st.selectbox("Filtrar por dificuldade",["Todas"]+DIFICULDADES)
    with col2:
        todas_tags=sorted(set(t.strip() for qs_list,_,_,_ in fonte.values() for q in qs_list for t in q.get("tags","").split(",") if t.strip()))
        filtro_tag=st.multiselect("Filtrar por tag",todas_tags)

    for key,val in sorted(fonte.items()):
        qs,_,prof_u,mat_real=val
        qs_f=qs
        if filtro_dif!="Todas": qs_f=[q for q in qs_f if q.get("dificuldade")==filtro_dif]
        if filtro_tag: qs_f=[q for q in qs_f if any(t in q.get("tags","") for t in filtro_tag)]
        if not qs_f: continue
        with st.expander(f"📚 {key} — {len(qs_f)} questão(ões)"):
            for i,q in enumerate(qs_f):
                dif=q.get("dificuldade","—"); cor_dif={"Fácil":"🟢","Médio":"🟡","Difícil":"🔴"}.get(dif,"⚪")
                idx_real=qs.index(q)
                col1,col2,col3=st.columns([5,1,1])
                with col1:
                    st.markdown(f"**{i+1}.** {q['enunciado']}  {cor_dif} `{dif}`")
                    render_tags(q); mostrar_imagem_questao(q)
                    st.caption(f"A) {q['alternativa_a']}  ·  B) {q['alternativa_b']}  ·  C) {q['alternativa_c']}  ·  D) {q['alternativa_d']}")
                    st.caption(f"✅ **{q['gabarito'].upper()}**"+(f"  —  {q['explicacao']}" if q.get("explicacao") else ""))
                    db2=load_db(); total_com=len(db2.get("comentarios",{}).get(q_id(q),[]))
                    with st.expander(f"💬 {total_com} comentário(s)"):
                        pg_comentarios_questao(q_id(q),q["enunciado"])
                with col2:
                    if st.button("✏️",key=f"edit_{key}_{i}"):
                        st.session_state.editando_q={"prof_u":prof_u,"mat":mat_real,"idx":idx_real,"q":q}; st.rerun()
                with col3:
                    if st.button("🗑️",key=f"delq_{key}_{i}"):
                        db2=load_db(); db2["questions"][prof_u][mat_real].pop(idx_real); save_db(db2); st.rerun()
                st.divider()
            if st.button("🗑️ Apagar matéria",key=f"delmat_{key}"):
                db2=load_db()
                if prof_u in db2["questions"] and mat_real in db2["questions"][prof_u]:
                    del db2["questions"][prof_u][mat_real]
                save_db(db2); st.rerun()

    if st.session_state.editando_q:
        eq=st.session_state.editando_q; q=eq["q"]
        st.divider(); st.subheader("✏️ Editar questão")
        with st.form("form_editar"):
            enunc=st.text_area("Enunciado",q["enunciado"])
            tags_e=st.text_input("🏷️ Tags",q.get("tags",""))
            col1,col2=st.columns(2)
            with col1: alt_a=st.text_input("A)",q["alternativa_a"]); alt_c=st.text_input("C)",q["alternativa_c"])
            with col2: alt_b=st.text_input("B)",q["alternativa_b"]); alt_d=st.text_input("D)",q["alternativa_d"])
            gab_idx=["a","b","c","d"].index(q["gabarito"]) if q["gabarito"] in ["a","b","c","d"] else 0
            gabarito=st.selectbox("Gabarito",["A","B","C","D"],index=gab_idx)
            dif=st.select_slider("Dificuldade",DIFICULDADES,value=q.get("dificuldade","Médio"))
            explicacao=st.text_area("Explicação",q.get("explicacao",""),height=80)
            if q.get("imagem"):
                st.caption("📷 Imagem atual:"); mostrar_imagem_questao(q)
                remover_img=st.checkbox("Remover imagem")
            else: remover_img=False
            nova_img=st.file_uploader("🖼️ Nova imagem",type=["png","jpg","jpeg","gif","webp"])
            c1,c2=st.columns(2)
            with c1: salvar=st.form_submit_button("💾 Salvar",type="primary",use_container_width=True)
            with c2: cancelar=st.form_submit_button("Cancelar",use_container_width=True)
        if salvar:
            db2=load_db(); img_val=eq["q"].get("imagem")
            if nova_img: img_val=img_to_base64(nova_img)
            elif remover_img: img_val=None
            db2["questions"][eq["prof_u"]][eq["mat"]][eq["idx"]]={
                "enunciado":enunc,"alternativa_a":alt_a,"alternativa_b":alt_b,
                "alternativa_c":alt_c,"alternativa_d":alt_d,"gabarito":gabarito.lower(),
                "explicacao":explicacao,"materia":eq["mat"],"dificuldade":dif,"tags":tags_e,"imagem":img_val
            }
            save_db(db2); st.session_state.editando_q=None; st.success("✅ Atualizada!"); st.rerun()
        if cancelar: st.session_state.editando_q=None; st.rerun()

# ── TURMAS ────────────────────────────────────────────────────────────────
def pg_turmas():
    st.header("👥 Turmas")
    u=st.session_state.usuario; db=load_db(); minhas=get_minhas_turmas(u["username"],u["role"])
    with st.expander("➕ Criar nova turma",expanded=not minhas):
        with st.form("form_turma"):
            nome_t=st.text_input("Nome da turma",placeholder="Ex: Turma A — Manhã")
            descricao=st.text_input("Descrição (opcional)")
            if st.form_submit_button("Criar turma",type="primary"):
                if not nome_t: st.error("Digite um nome.")
                else:
                    tid=str(uuid.uuid4())[:8]
                    db["turmas"][tid]={"nome":nome_t,"descricao":descricao,"prof_u":u["username"],"alunos":[],"codigo":tid,"criada_em":datetime.now().strftime("%d/%m/%Y")}
                    save_db(db); st.success(f"✅ Turma **{nome_t}** criada! Código: `{tid}`"); st.rerun()
    st.divider()
    if not minhas: st.info("Nenhuma turma ainda."); return
    for tid,t in minhas.items():
        alunos=t.get("alunos",[])
        with st.expander(f"👥 {t['nome']} — {len(alunos)} aluno(s)  `código: {tid}`"):
            if t.get("descricao"): st.caption(t["descricao"])
            st.info(f"🔗 Código: **`{tid}`**")
            st.subheader("Alunos")
            if not alunos: st.caption("Nenhum aluno ainda.")
            else:
                for au in alunos:
                    nome_al=db["users"].get(au,{}).get("nome",au)
                    col1,col2=st.columns([4,1])
                    with col1:
                        row=st.columns([1,5])
                        with row[0]: render_avatar(nome_al,au,28)
                        with row[1]: st.write(f"**{nome_al}** `@{au}`")
                    with col2:
                        if st.button("Remover",key=f"rm_al_{tid}_{au}"):
                            db2=load_db(); db2["turmas"][tid]["alunos"].remove(au); save_db(db2); st.rerun()
            with st.form(f"form_add_al_{tid}"):
                user_al=st.text_input("Adicionar aluno pelo usuário")
                if st.form_submit_button("Adicionar"):
                    db2=load_db(); au=user_al.strip().lower()
                    if au not in db2["users"]: st.error("Usuário não encontrado.")
                    elif db2["users"][au]["role"]!="aluno": st.error("Não é um aluno.")
                    elif au in db2["turmas"][tid]["alunos"]: st.error("Já está na turma.")
                    else:
                        db2["turmas"][tid]["alunos"].append(au); save_db(db2)
                        st.success(f"✅ {db2['users'][au]['nome']} adicionado!"); st.rerun()
            if st.button("🗑️ Apagar turma",key=f"del_turma_{tid}"):
                db2=load_db(); del db2["turmas"][tid]; save_db(db2); st.rerun()

def pg_entrar_turma():
    u=st.session_state.usuario
    with st.form("form_entrar_turma"):
        codigo=st.text_input("Código da turma",placeholder="ex: a1b2c3d4")
        if st.form_submit_button("Entrar na turma",type="primary"):
            db=load_db(); codigo=codigo.strip()
            if codigo not in db["turmas"]: st.error("Código inválido.")
            elif u["username"] in db["turmas"][codigo]["alunos"]: st.error("Já está nessa turma.")
            else:
                db["turmas"][codigo]["alunos"].append(u["username"]); save_db(db)
                st.success(f"✅ Entrou na turma **{db['turmas'][codigo]['nome']}**!"); st.rerun()

# ── CRIAR PROVA ───────────────────────────────────────────────────────────
def pg_criar_prova():
    st.header("📋 Criar prova")
    u=st.session_state.usuario; db=load_db()
    todas=get_all_questions(); minhas_turmas=get_minhas_turmas(u["username"],"prof")
    with st.form("form_prova"):
        nome_p=st.text_input("Nome da prova",placeholder="Ex: Simulado Março")
        turma_opts={tid:t["nome"] for tid,t in minhas_turmas.items()}
        turma_opts["_todas"]="🔀 Todas as turmas"
        turma_id=st.selectbox("Turma",list(turma_opts.keys()),format_func=lambda x:turma_opts[x])
        col1,col2=st.columns(2)
        with col1: abertura=st.date_input("Data de abertura",value=date.today()); hora_ab=st.time_input("Hora de abertura",value=datetime.now().time())
        with col2: fechamento=st.date_input("Data de fechamento"); hora_fe=st.time_input("Hora de fechamento")
        tempo_total=st.number_input("Tempo limite em minutos (0 = sem limite)",min_value=0,value=0)
        st.divider(); st.markdown("**Selecione as questões:**")
        mat_filtro=st.selectbox("Filtrar por matéria",["Todas"]+sorted(set(q["materia"] for q in todas)))
        dif_filtro=st.selectbox("Filtrar por dificuldade",["Todas"]+DIFICULDADES)
        todas_tags=sorted(set(t.strip() for q in todas for t in q.get("tags","").split(",") if t.strip()))
        tag_filtro=st.multiselect("Filtrar por tag",todas_tags)
        qs_f=todas
        if mat_filtro!="Todas": qs_f=[q for q in qs_f if q["materia"]==mat_filtro]
        if dif_filtro!="Todas": qs_f=[q for q in qs_f if q.get("dificuldade")==dif_filtro]
        if tag_filtro: qs_f=[q for q in qs_f if any(t in q.get("tags","") for t in tag_filtro)]
        selecionadas=[]
        for i,q in enumerate(qs_f[:50]):
            dif=q.get("dificuldade","—"); cor={"Fácil":"🟢","Médio":"🟡","Difícil":"🔴"}.get(dif,"⚪")
            tags_str=f" [{q.get('tags','')}]" if q.get("tags") else ""
            if st.checkbox(f"{cor} [{q['materia']}]{tags_str} {q['enunciado'][:80]}...",key=f"sel_q_{i}"): selecionadas.append(q)
        if st.form_submit_button("✅ Criar prova",type="primary",use_container_width=True):
            if not nome_p: st.error("Digite um nome.")
            elif not selecionadas: st.error("Selecione pelo menos uma questão.")
            else:
                pid=str(uuid.uuid4())[:8]
                ab=datetime.combine(abertura,hora_ab).isoformat()
                fe=datetime.combine(fechamento,hora_fe).isoformat()
                db2=load_db()
                db2["provas"][pid]={
                    "nome":nome_p,"prof_u":u["username"],
                    "turma_id":None if turma_id=="_todas" else turma_id,
                    "abertura":ab,"fechamento":fe,"tempo_total":int(tempo_total),
                    "questoes":[{k:v for k,v in q.items() if not k.startswith("_")} for q in selecionadas],
                    "criada_em":datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                save_db(db2); st.success(f"✅ Prova **{nome_p}** criada com {len(selecionadas)} questões!"); st.rerun()

# ── PROVAS ────────────────────────────────────────────────────────────────
def pg_provas():
    st.header("📝 Provas")
    u=st.session_state.usuario; db=load_db()
    if u["role"]=="aluno":
        minhas_turmas=get_minhas_turmas(u["username"],"aluno")
        with st.expander("🔗 Entrar em uma turma pelo código"): pg_entrar_turma()
        if minhas_turmas: st.caption("Suas turmas: "+", ".join(f"**{t['nome']}**" for t in minhas_turmas.values()))
        st.divider()
    provas=get_provas_disponiveis(u["username"],u["role"])
    if st.session_state.prova_ativa and not st.session_state.prova_finalizada: _resolver_prova(); return
    if st.session_state.prova_finalizada: _resultado_prova(); return
    if not provas:
        st.info("Nenhuma prova disponível." if u["role"]=="aluno" else "Nenhuma prova criada ainda."); return
    st.subheader("Provas disponíveis" if u["role"]=="aluno" else "Suas provas")
    now=datetime.now(); udata=get_user_data(u["username"])
    for pid,p in provas.items():
        ab=datetime.fromisoformat(p["abertura"]) if p.get("abertura") else None
        fe=datetime.fromisoformat(p["fechamento"]) if p.get("fechamento") else None
        turma_nome=db["turmas"].get(p.get("turma_id",""),{}).get("nome","Todas as turmas")
        ja_fez=pid in udata.get("respostas_provas",{}); aberta=(not ab or now>=ab) and (not fe or now<=fe)
        with st.container(border=True):
            col1,col2=st.columns([4,1])
            with col1:
                st.markdown(f"### {p['nome']}")
                st.caption(f"👥 {turma_nome}  ·  📝 {len(p['questoes'])} questões  ·  {p.get('criada_em','—')}")
                if ab: st.caption(f"🟢 Abre: {ab.strftime('%d/%m/%Y %H:%M')}")
                if fe: st.caption(f"🔴 Fecha: {fe.strftime('%d/%m/%Y %H:%M')}")
                if p.get("tempo_total"): st.caption(f"⏱️ Tempo: {p['tempo_total']} min")
                if ja_fez:
                    res=udata["respostas_provas"][pid]
                    st.success(f"✅ Já realizada — {res['acertos']}/{res['total']} ({res['pct']}%)")
            with col2:
                if u["role"]=="aluno":
                    if ja_fez: st.button("Ver resultado",key=f"ver_{pid}",on_click=lambda pid=pid:_ver_resultado_prova(pid))
                    elif aberta:
                        if st.button("▶ Fazer prova",key=f"start_{pid}",type="primary"):
                            st.session_state.prova_ativa=pid; st.session_state.prova_idx=0
                            st.session_state.prova_respondida=False; st.session_state.prova_escolha=None
                            st.session_state.prova_respostas=[]; st.session_state.prova_finalizada=False
                            st.session_state.quiz_tempo_inicio=time.time(); st.rerun()
                    else: st.caption("⏳ Não disponível")
                else:
                    if st.button("🗑️ Apagar",key=f"del_p_{pid}"):
                        db2=load_db(); del db2["provas"][pid]; save_db(db2); st.rerun()

def _ver_resultado_prova(pid):
    st.session_state.prova_ativa=pid; st.session_state.prova_finalizada=True

def _resolver_prova():
    pid=st.session_state.prova_ativa; db=load_db(); p=db["provas"].get(pid)
    if not p: st.error("Prova não encontrada."); return
    qs=p["questoes"]; idx=st.session_state.prova_idx
    if idx>=len(qs): _finalizar_prova(); return
    if p.get("tempo_total"):
        elapsed=(time.time()-st.session_state.quiz_tempo_inicio)/60
        restante=max(0,p["tempo_total"]-elapsed); pct_t=restante/p["tempo_total"]
        cor="🟢" if pct_t>0.5 else "🟡" if pct_t>0.25 else "🔴"
        st.progress(pct_t,text=f"{cor} Tempo: {int(restante)}min {int((restante%1)*60)}s")
        if restante<=0: _finalizar_prova(); return
    st.markdown(f"### 📝 {p['nome']}")
    st.progress(idx/len(qs),text=f"Questão {idx+1} de {len(qs)}")
    q=qs[idx]
    with st.container(border=True):
        dif=q.get("dificuldade","—"); cor_dif={"Fácil":"🟢","Médio":"🟡","Difícil":"🔴"}.get(dif,"⚪")
        st.caption(f"📚 {q.get('materia','—')}  ·  {cor_dif} {dif}")
        render_tags(q); st.markdown(f"**{q['enunciado']}**"); mostrar_imagem_questao(q); st.write("")
        letras=["a","b","c","d"]; labels=[f"{l.upper()}) {q[f'alternativa_{l}']}" for l in letras]
        if not st.session_state.prova_respondida:
            resp=st.radio("Escolha:",labels,index=None,key=f"prova_radio_{idx}")
            col1,col2=st.columns([1,3])
            with col1:
                if st.button("Confirmar →",type="primary",disabled=(resp is None)):
                    letra=letras[labels.index(resp)]; st.session_state.prova_escolha=letra
                    st.session_state.prova_respondida=True
                    st.session_state.prova_respostas.append({"q":q,"escolha":letra}); st.rerun()
            with col2:
                if st.button("Pular →"):
                    st.session_state.prova_respostas.append({"q":q,"escolha":"—"})
                    st.session_state.prova_idx+=1; st.session_state.prova_respondida=False; st.rerun()
        else:
            escolha=st.session_state.prova_escolha; acertou=escolha==q["gabarito"]
            for i,l in enumerate(letras):
                if l==q["gabarito"]: st.success(f"✅ {labels[i]}")
                elif l==escolha and not acertou: st.error(f"❌ {labels[i]}")
                else: st.write(labels[i])
            if acertou: st.success("**Correto!**")
            else: st.error(f"**Errado!** Resposta: **{q['gabarito'].upper()}**")
            if q.get("explicacao"):
                with st.expander("💡 Explicação"): st.write(q["explicacao"])
            if st.button("Próxima →",type="primary"):
                st.session_state.prova_idx+=1; st.session_state.prova_respondida=False; st.session_state.prova_escolha=None; st.rerun()
    if p.get("tempo_total"): time.sleep(1); st.rerun()

def _finalizar_prova():
    u=st.session_state.usuario; pid=st.session_state.prova_ativa
    respostas=st.session_state.prova_respostas
    acertos=sum(1 for r in respostas if r["escolha"]==r["q"]["gabarito"])
    total=len(respostas); pct=round(acertos/total*100) if total else 0
    udata=get_user_data(u["username"])
    udata["respostas_provas"][pid]={"acertos":acertos,"total":total,"pct":pct,
        "data":datetime.now().strftime("%d/%m/%Y %H:%M"),
        "respostas":[{"enunciado":r["q"]["enunciado"],"escolha":r["escolha"],"gabarito":r["q"]["gabarito"],"acertou":r["escolha"]==r["q"]["gabarito"]} for r in respostas]}
    udata["historico"].append({"data":datetime.now().strftime("%d/%m/%Y %H:%M"),"materia":"Prova","dificuldade":"—","total":total,"acertos":acertos,"pct":pct})
    save_user_data(u["username"],udata); st.session_state.prova_finalizada=True; st.rerun()

def _resultado_prova():
    u=st.session_state.usuario; pid=st.session_state.prova_ativa
    udata=get_user_data(u["username"]); res=udata["respostas_provas"].get(pid,{})
    db=load_db(); p=db["provas"].get(pid,{})
    st.markdown(f"## 📝 {p.get('nome','Prova')} — Resultado")
    col1,col2,col3=st.columns(3)
    col1.metric("✅ Acertos",res.get("acertos",0)); col2.metric("❌ Erros",res.get("total",0)-res.get("acertos",0))
    col3.metric("📊 Aproveitamento",f"{res.get('pct',0)}%")
    pct=res.get("pct",0)
    if pct>=70: st.success("🎉 Ótimo!")
    elif pct>=50: st.warning("📚 Razoável.")
    else: st.error("💪 Não desista!")
    with st.expander("📋 Revisão"):
        for r in res.get("respostas",[]):
            ok=r["acertou"]; st.markdown(f"{'✅' if ok else '❌'} **{r['enunciado']}**")
            st.caption(f"Sua: **{r['escolha'].upper()}** | Gabarito: **{r['gabarito'].upper()}**"); st.divider()
    if st.button("← Voltar",type="primary"):
        st.session_state.prova_ativa=None; st.session_state.prova_finalizada=False; st.rerun()

# ── RELATÓRIO ─────────────────────────────────────────────────────────────
def pg_relatorio():
    st.header("📊 Relatório de turma")
    u=st.session_state.usuario; db=load_db(); minhas_turmas=get_minhas_turmas(u["username"],"prof")
    if not minhas_turmas: st.info("Nenhuma turma ainda."); return
    turma_id=st.selectbox("Turma",list(minhas_turmas.keys()),format_func=lambda x:minhas_turmas[x]["nome"])
    turma=minhas_turmas[turma_id]; alunos=turma.get("alunos",[])
    if not alunos: st.info("Nenhum aluno nessa turma."); return
    st.divider()
    provas_turma={pid:p for pid,p in db["provas"].items() if p.get("turma_id")==turma_id and p["prof_u"]==u["username"]}
    st.subheader("👤 Desempenho dos alunos")
    dados_alunos=[]
    for au in alunos:
        nome_al=db["users"].get(au,{}).get("nome",au); udata=db.get("user_data",{}).get(au,{})
        hist=udata.get("historico",[]); respostas_provas=udata.get("respostas_provas",{})
        media_geral=round(sum(h["pct"] for h in hist)/len(hist)) if hist else 0
        provas_feitas=sum(1 for pid in provas_turma if pid in respostas_provas)
        media_provas=round(sum(respostas_provas[pid]["pct"] for pid in provas_turma if pid in respostas_provas)/provas_feitas) if provas_feitas else 0
        dados_alunos.append({"nome":nome_al,"username":au,"sessoes":len(hist),"media_estudo":media_geral,"provas_feitas":provas_feitas,"media_provas":media_provas})
    for d in sorted(dados_alunos,key=lambda x:x["media_provas"],reverse=True):
        cor="🟢" if d["media_provas"]>=70 else "🟡" if d["media_provas"]>=50 else "🔴"
        with st.container(border=True):
            row=st.columns([1,3,2,2,2])
            with row[0]: render_avatar(d["nome"],d["username"],32)
            with row[1]: st.markdown(f"**{d['nome']}**"); st.caption(f"@{d['username']}")
            with row[2]: st.metric("Sessões",d["sessoes"])
            with row[3]: st.metric("Média estudo",f"{d['media_estudo']}%")
            with row[4]: st.metric(f"{cor} Média provas",f"{d['media_provas']}%")
    st.divider()
    if provas_turma:
        st.subheader("📝 Resultado por prova")
        prova_sel=st.selectbox("Prova",list(provas_turma.keys()),format_func=lambda x:provas_turma[x]["nome"])
        p=provas_turma[prova_sel]; st.caption(f"{len(p['questoes'])} questões  ·  {p.get('criada_em','—')}")
        for au in alunos:
            nome_al=db["users"].get(au,{}).get("nome",au); udata=db.get("user_data",{}).get(au,{})
            res=udata.get("respostas_provas",{}).get(prova_sel)
            if res:
                cor="🟢" if res["pct"]>=70 else "🟡" if res["pct"]>=50 else "🔴"
                st.caption(f"{cor} **{nome_al}** — {res['acertos']}/{res['total']} ({res['pct']}%)  ·  {res['data']}")
            else: st.caption(f"⚪ **{nome_al}** — Não realizou")

# ── ADMIN ─────────────────────────────────────────────────────────────────
def pg_admin():
    st.header("⚙️ Admin"); db=load_db()
    def render_usuarios(role,label):
        users=[(u,d) for u,d in db["users"].items() if d["role"]==role]
        st.subheader(label)
        if not users: st.info(f"Nenhum {role}."); return
        for u,d in users:
            total=sum(len(qs) for qs in db["questions"].get(u,{}).values()) if role=="prof" else 0
            sessoes=len(db.get("user_data",{}).get(u,{}).get("historico",[])) if role=="aluno" else 0
            info=f"{total} questões" if role=="prof" else f"{sessoes} sessões"
            with st.container(border=True):
                col1,col2,col3=st.columns([3,1,1])
                with col1:
                    row=st.columns([1,5])
                    with row[0]: render_avatar(d["nome"],u,32)
                    with row[1]: st.markdown(f"**{d['nome']}** `@{u}` — {info}")
                with col2:
                    if st.button("🔑",key=f"pwd_{u}",help="Redefinir senha"): st.session_state[f"redef_{u}"]=True
                with col3:
                    if st.button("🗑️",key=f"rm_{u}",help="Remover"):
                        db2=load_db(); del db2["users"][u]; db2["questions"].pop(u,None); db2.get("user_data",{}).pop(u,None); save_db(db2); st.rerun()
                if st.session_state.get(f"redef_{u}"):
                    with st.form(f"redef_{u}_form"):
                        nova=st.text_input(f"Nova senha para @{u}",type="password")
                        c1,c2=st.columns(2)
                        with c1: ok_btn=st.form_submit_button("Redefinir",type="primary")
                        with c2: cancel_btn=st.form_submit_button("Cancelar")
                    if ok_btn:
                        ok,msg=redefinir_senha_admin(u,nova)
                        if ok: st.success("✅ Redefinida!"); st.session_state[f"redef_{u}"]=False; st.rerun()
                        else: st.error(msg)
                    if cancel_btn: st.session_state[f"redef_{u}"]=False; st.rerun()
    render_usuarios("prof","👨‍🏫 Professores"); st.divider()
    render_usuarios("aluno","👤 Alunos"); st.divider()
    st.subheader("💾 Backup")
    col1,col2=st.columns(2)
    with col1:
        st.download_button("⬇️ Exportar",json.dumps(db,ensure_ascii=False,indent=2),"studyquiz_backup.json","application/json",use_container_width=True)
    with col2:
        arq=st.file_uploader("⬆️ Importar",type="json")
        if arq:
            try:
                imp=json.load(arq)
                if "users" not in imp or "questions" not in imp: raise ValueError
                db2=load_db(); db2["users"].update(imp["users"])
                for u,mats in imp["questions"].items():
                    if u not in db2["questions"]: db2["questions"][u]={}
                    for mat,qs in mats.items():
                        if mat not in db2["questions"][u]: db2["questions"][u][mat]=[]
                        ex={q["enunciado"] for q in db2["questions"][u][mat]}
                        for q in qs:
                            if q["enunciado"] not in ex: db2["questions"][u][mat].append(q)
                save_db(db2); st.success("Importado!")
            except: st.error("Arquivo inválido.")
    st.divider(); st.subheader("⚠️ Zona de perigo")
    if st.button("🗑️ Apagar TUDO"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        logout()

# ── MAIN ──────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.usuario: tela_login(); return
    pg=sidebar()
    if pg=="📖 Estudar": pg_estudar()
    elif pg=="📝 Provas": pg_provas()
    elif pg=="🔁 Modo revisão": pg_revisao()
    elif pg=="⭐ Favoritos": pg_favoritos()
    elif pg=="📊 Meu desempenho": pg_desempenho()
    elif pg=="🏆 Ranking": pg_ranking()
    elif pg=="🔒 Minha conta": pg_minha_conta()
    elif pg=="➕ Adicionar questão": pg_adicionar()
    elif pg=="🤖 Gerar do PDF": pg_gerar_pdf()
    elif pg=="📋 Banco de questões": pg_banco()
    elif pg=="👥 Turmas": pg_turmas()
    elif pg=="📋 Criar prova": pg_criar_prova()
    elif pg=="📊 Relatório de turma": pg_relatorio()
    elif pg=="⚙️ Admin": pg_admin()

main()
