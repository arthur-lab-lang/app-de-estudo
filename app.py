<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StudyQuiz</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0b0d12;--bg2:#111419;--bg3:#161a22;
  --border:#1e2330;--border2:#2a3148;
  --accent:#4af0a0;--accent2:#4a9ff0;--accent3:#f0a04a;
  --text:#dde4f5;--text2:#7a88aa;--text3:#3d4a63;
  --danger:#f04a4a;--mono:'Space Mono',monospace;--sans:'Syne',sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh}
/* HEADER */
header{background:var(--bg2);border-bottom:1px solid var(--border);padding:0 24px;height:56px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}
.logo{font-family:var(--mono);font-size:15px;color:var(--accent);letter-spacing:.08em}
.logo span{color:var(--text2)}
.user-pill{display:flex;align-items:center;gap:8px;background:var(--bg3);border:1px solid var(--border2);border-radius:20px;padding:5px 14px 5px 10px;font-size:12px;font-family:var(--mono);color:var(--text2)}
.user-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);display:inline-block}
.user-dot.aluno{background:var(--accent2)}
.hbtn{background:none;border:1px solid var(--border2);color:var(--text2);font-family:var(--mono);font-size:11px;padding:5px 12px;border-radius:6px;cursor:pointer;transition:all .15s}
.hbtn:hover{border-color:var(--danger);color:var(--danger)}
/* MODAL OVERLAY */
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:200;display:flex;align-items:center;justify-content:center}
.modal{background:var(--bg2);border:1px solid var(--border2);border-radius:16px;padding:32px;width:100%;max-width:400px}
.modal-title{font-size:18px;font-weight:800;color:var(--text);margin-bottom:6px}
.modal-sub{font-size:12px;color:var(--text2);font-family:var(--mono);margin-bottom:24px}
.tabs{display:flex;gap:0;border:1px solid var(--border2);border-radius:8px;overflow:hidden;margin-bottom:20px}
.tab{flex:1;padding:9px;text-align:center;font-size:12px;font-family:var(--mono);cursor:pointer;color:var(--text2);background:var(--bg3);border:none;transition:all .15s}
.tab.active{background:rgba(74,159,240,.15);color:var(--accent2)}
/* FORMS */
.fg{margin-bottom:14px}
.fg label{display:block;font-size:11px;color:var(--text2);margin-bottom:5px;font-family:var(--mono);letter-spacing:.04em;text-transform:uppercase}
input[type=text],input[type=password]{width:100%;background:var(--bg3);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--sans);font-size:13px;padding:10px 13px;outline:none;transition:border-color .15s}
input:focus{border-color:var(--accent2)}
.err-msg{font-size:11px;font-family:var(--mono);color:var(--danger);margin-top:6px;min-height:16px}
/* BUTTONS */
.btn{padding:9px 20px;border-radius:8px;border:1px solid var(--border2);background:var(--bg3);color:var(--text);font-family:var(--mono);font-size:12px;cursor:pointer;transition:all .15s}
.btn-primary{background:rgba(74,159,240,.15);border-color:var(--accent2);color:var(--accent2)}
.btn-primary:hover{background:rgba(74,159,240,.25)}
.btn-success{background:rgba(74,240,160,.12);border-color:var(--accent);color:var(--accent)}
.btn-success:hover{background:rgba(74,240,160,.22)}
.btn-danger{background:rgba(240,74,74,.1);border-color:var(--danger);color:var(--danger);font-size:11px;padding:5px 12px}
.btn-danger:hover{background:rgba(240,74,74,.2)}
.btn-block{width:100%;padding:11px;font-size:13px}
.btn-row{display:flex;gap:8px;align-items:center;margin-top:6px}
.btn-ghost{background:none;border:none;color:var(--text2);font-family:var(--mono);font-size:12px;cursor:pointer;padding:8px 0;width:100%;text-align:center}
.btn-ghost:hover{color:var(--accent2)}
/* LAYOUT */
.app{display:flex}
nav{width:200px;background:var(--bg2);border-right:1px solid var(--border);padding:20px 12px;display:flex;flex-direction:column;gap:4px;position:sticky;top:56px;height:calc(100vh - 56px)}
.nav-item{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:8px;border:1px solid transparent;cursor:pointer;font-size:13px;color:var(--text2);transition:all .15s;background:none;width:100%;text-align:left;font-family:var(--sans)}
.nav-item:hover{background:var(--bg3);color:var(--text)}
.nav-item.active{background:var(--bg3);border-color:var(--border2);color:var(--accent)}
.nav-icon{font-size:15px}
.nav-divider{height:1px;background:var(--border);margin:8px 0}
.nav-stats{margin-top:auto;padding:12px;background:var(--bg3);border:1px solid var(--border);border-radius:8px;font-family:var(--mono);font-size:11px;color:var(--text2);line-height:2}
.nav-stats b{color:var(--accent)}
main{flex:1;padding:28px 32px;max-width:760px}
.page{display:none}
.page.active{display:block}
.page-title{font-size:22px;font-weight:800;color:var(--text);margin-bottom:24px;display:flex;align-items:center;gap:10px}
.page-title::after{content:'';flex:1;height:1px;background:var(--border);margin-left:8px}
/* CARDS */
.card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px 24px;margin-bottom:16px}
.card-title{font-size:13px;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px;font-family:var(--mono)}
/* ESTUDO */
.sel-card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:16px}
.sel-label{font-size:12px;font-family:var(--mono);color:var(--text2);margin-bottom:8px;text-transform:uppercase;letter-spacing:.06em}
select{width:100%;background:var(--bg3);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--sans);font-size:13px;padding:9px 12px;outline:none}
input[type=number]{width:80px;background:var(--bg3);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--mono);font-size:13px;padding:9px 12px;outline:none}
textarea{width:100%;background:var(--bg3);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--sans);font-size:13px;padding:9px 12px;outline:none;resize:vertical;height:80px}
/* QUIZ */
.progress-wrap{margin-bottom:18px}
.progress-info{display:flex;justify-content:space-between;font-size:11px;font-family:var(--mono);color:var(--text2);margin-bottom:6px}
.progress-bar{height:3px;background:var(--border);border-radius:2px;overflow:hidden}
.progress-fill{height:100%;background:var(--accent2);border-radius:2px;transition:width .4s}
.q-text{font-size:15px;line-height:1.7;color:var(--text);margin-bottom:18px}
.alt{display:flex;align-items:flex-start;gap:12px;padding:11px 14px;border-radius:8px;border:1px solid var(--border);margin-bottom:8px;cursor:pointer;font-size:13px;transition:all .15s;color:var(--text);background:var(--bg3)}
.alt:hover{border-color:var(--border2)}
.alt.sel{border-color:var(--accent2);background:rgba(74,159,240,.08)}
.alt.certo{border-color:var(--accent);background:rgba(74,240,160,.08);color:var(--accent)}
.alt.errado{border-color:var(--danger);background:rgba(240,74,74,.08);color:var(--danger)}
.alt-letra{font-family:var(--mono);font-weight:700;font-size:12px;min-width:20px;margin-top:1px}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-family:var(--mono);background:rgba(74,159,240,.12);border:1px solid rgba(74,159,240,.3);color:var(--accent2);margin-bottom:10px}
.badge.prof{background:rgba(74,240,160,.1);border-color:rgba(74,240,160,.3);color:var(--accent)}
.feedback-box{padding:12px 16px;border-radius:8px;font-size:13px;font-family:var(--mono);margin:14px 0}
.feedback-box.ok{background:rgba(74,240,160,.08);border:1px solid rgba(74,240,160,.3);color:var(--accent)}
.feedback-box.no{background:rgba(240,74,74,.08);border:1px solid rgba(240,74,74,.3);color:var(--danger)}
.explic{font-size:12px;color:var(--text2);padding:10px 14px;background:var(--bg3);border-left:2px solid var(--border2);border-radius:0 6px 6px 0;margin-top:8px;line-height:1.6}
/* RESULTADO */
.result-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
.result-card{background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center}
.result-num{font-family:var(--mono);font-size:28px;font-weight:700;margin-bottom:4px}
.result-lbl{font-size:11px;color:var(--text2);text-transform:uppercase;letter-spacing:.06em;font-family:var(--mono)}
/* BANCO */
.mat-block{background:var(--bg2);border:1px solid var(--border);border-radius:12px;margin-bottom:12px;overflow:hidden}
.mat-header{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;cursor:pointer;border-bottom:1px solid transparent;transition:background .15s}
.mat-header:hover{background:var(--bg3)}
.mat-header.open{border-bottom-color:var(--border)}
.mat-name{font-size:14px;font-weight:600;color:var(--text)}
.mat-count{font-size:11px;font-family:var(--mono);color:var(--text2);margin-left:10px}
.mat-body{display:none;padding:14px 18px}
.mat-body.open{display:block}
.q-item{padding:12px 0;border-bottom:1px solid var(--border);font-size:13px}
.q-item:last-child{border-bottom:none}
.q-enunc{color:var(--text);margin-bottom:6px;line-height:1.5}
.q-alts{color:var(--text2);font-size:12px;line-height:1.8}
.q-gabarito{color:var(--accent);font-family:var(--mono);font-size:12px;margin-top:4px}
/* FORM */
.form-group{margin-bottom:14px}
.form-group label{display:block;font-size:12px;color:var(--text2);margin-bottom:5px;font-family:var(--mono);letter-spacing:.04em}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.pill-group{display:flex;gap:6px;flex-wrap:wrap}
.pill{padding:6px 14px;border-radius:20px;border:1px solid var(--border2);font-size:12px;cursor:pointer;color:var(--text2);background:var(--bg3);font-family:var(--mono);transition:all .15s}
.pill.active-green{background:rgba(74,240,160,.12);border-color:var(--accent);color:var(--accent)}
.pill.active{background:rgba(74,159,240,.12);border-color:var(--accent2);color:var(--accent2)}
.msg{font-size:12px;font-family:var(--mono);padding:8px 12px;border-radius:6px;display:inline-block;margin-left:10px}
.msg.ok{background:rgba(74,240,160,.1);color:var(--accent)}
.msg.err{background:rgba(240,74,74,.1);color:var(--danger)}
.empty{text-align:center;padding:48px;color:var(--text3);font-size:13px;font-family:var(--mono)}
/* ADMIN */
.prof-list{display:flex;flex-direction:column;gap:8px}
.prof-row{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:var(--bg3);border:1px solid var(--border);border-radius:8px}
.prof-info{font-size:13px}
.prof-name{color:var(--text);font-weight:600}
.prof-user{color:var(--text2);font-size:11px;font-family:var(--mono);margin-top:2px}
.prof-qs{font-size:11px;font-family:var(--mono);color:var(--accent);margin-top:2px}
/* SWITCH ALUNO */
.switch-area{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px 24px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between}
.switch-txt{font-size:13px;color:var(--text2)}
.switch-txt b{color:var(--text);display:block;font-size:15px;margin-bottom:2px}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px}
</style>
</head>
<body>

<!-- HEADER -->
<header>
  <div class="logo">STUDY<span>/</span>QUIZ</div>
  <div style="display:flex;gap:10px;align-items:center">
    <div class="user-pill" id="user-pill" style="display:none">
      <span class="user-dot" id="user-dot"></span>
      <span id="user-label">—</span>
    </div>
    <button class="hbtn" id="btn-logout" style="display:none" onclick="logout()">Sair</button>
  </div>
</header>

<!-- OVERLAY LOGIN (PROFESSOR) -->
<div class="overlay" id="overlay-login">
  <div class="modal">
    <div class="modal-title">Bem-vindo ao StudyQuiz</div>
    <div class="modal-sub">Escolha como deseja entrar</div>
    <div class="tabs">
      <button class="tab active" id="tab-prof" onclick="setTab('prof')">Professor</button>
      <button class="tab" id="tab-aluno" onclick="setTab('aluno')">Aluno</button>
      <button class="tab" id="tab-admin" onclick="setTab('admin')">Admin</button>
    </div>

    <!-- LOGIN PROFESSOR -->
    <div id="form-prof">
      <div class="tabs" style="margin-bottom:16px">
        <button class="tab active" id="tab-entrar" onclick="setSubTab('entrar')">Entrar</button>
        <button class="tab" id="tab-cadastrar" onclick="setSubTab('cadastrar')">Criar conta</button>
      </div>
      <div id="form-entrar">
        <div class="fg"><label>Usuário</label><input type="text" id="l-user" placeholder="seu.usuario"></div>
        <div class="fg"><label>Senha</label><input type="password" id="l-pass" placeholder="••••••"></div>
        <div class="err-msg" id="l-err"></div>
        <button class="btn btn-primary btn-block" style="margin-top:8px" onclick="loginProf()">Entrar como professor</button>
      </div>
      <div id="form-cadastrar" style="display:none">
        <div class="fg"><label>Nome completo</label><input type="text" id="r-nome" placeholder="Ex: Prof. Ana Lima"></div>
        <div class="fg"><label>Usuário</label><input type="text" id="r-user" placeholder="ana.lima"></div>
        <div class="fg"><label>Senha</label><input type="password" id="r-pass" placeholder="••••••"></div>
        <div class="err-msg" id="r-err"></div>
        <button class="btn btn-success btn-block" style="margin-top:8px" onclick="cadastrarProf()">Criar conta</button>
      </div>
    </div>

    <!-- LOGIN ALUNO -->
    <div id="form-aluno" style="display:none">
      <p style="font-size:13px;color:var(--text2);margin-bottom:16px;line-height:1.6">Modo aluno: veja questões de todos os professores, estude à vontade. Sem senha necessária.</p>
      <button class="btn btn-primary btn-block" onclick="loginAluno()">Entrar como aluno</button>
    </div>

    <!-- LOGIN ADMIN -->
    <div id="form-admin" style="display:none">
      <div class="fg"><label>Senha admin</label><input type="password" id="a-pass" placeholder="••••••"></div>
      <div class="err-msg" id="a-err"></div>
      <button class="btn btn-block" style="background:rgba(240,160,74,.1);border-color:var(--accent3);color:var(--accent3);margin-top:8px" onclick="loginAdmin()">Entrar como admin</button>
    </div>
  </div>
</div>

<!-- APP -->
<div class="app" id="app" style="display:none">
  <nav id="nav-sidebar">
    <button class="nav-item active" onclick="irPara('estudar')"><span class="nav-icon">▶</span> Estudar</button>
    <button class="nav-item" id="nav-adicionar" onclick="irPara('adicionar')"><span class="nav-icon">+</span> Adicionar</button>
    <button class="nav-item" id="nav-banco" onclick="irPara('banco')"><span class="nav-icon">≡</span> Banco</button>
    <button class="nav-item" id="nav-admin" onclick="irPara('admin')" style="display:none"><span class="nav-icon">⚙</span> Admin</button>
    <div class="nav-divider"></div>
    <div class="nav-stats" id="nav-stats"></div>
  </nav>

  <main>
    <!-- ESTUDAR -->
    <div id="page-estudar" class="page active">
      <div class="page-title">Estudar</div>
      <div id="config-area">
        <div class="sel-card">
          <div class="sel-label">Matéria</div>
          <select id="sel-materia" style="margin-bottom:14px"></select>
          <div class="form-row" style="align-items:end">
            <div><div class="sel-label">Quantidade</div><input type="number" id="qtd-qs" value="10" min="1"></div>
            <div><label style="display:flex;align-items:center;gap:8px;font-size:13px;color:var(--text2);cursor:pointer;margin-top:10px">
              <input type="checkbox" id="chk-shuffle" checked style="accent-color:var(--accent2)"> Embaralhar
            </label></div>
          </div>
          <div class="btn-row" style="margin-top:18px">
            <button class="btn btn-success" onclick="iniciarSessao()">▶ Iniciar sessão</button>
          </div>
        </div>
      </div>
      <div id="quiz-area" style="display:none">
        <div class="progress-wrap">
          <div class="progress-info"><span id="prog-texto"></span><span id="prog-placar"></span></div>
          <div class="progress-bar"><div class="progress-fill" id="prog-fill"></div></div>
        </div>
        <div class="card" id="quiz-card">
          <div id="q-badge" class="badge"></div>
          <div id="q-texto" class="q-text"></div>
          <div id="q-alts"></div>
          <div id="q-feedback"></div>
          <div id="q-explic"></div>
          <div class="btn-row" id="q-acoes" style="margin-top:14px"></div>
        </div>
      </div>
      <div id="result-area" style="display:none">
        <div class="result-grid">
          <div class="result-card"><div class="result-num" style="color:var(--accent)" id="r-acertos">0</div><div class="result-lbl">Acertos</div></div>
          <div class="result-card"><div class="result-num" style="color:var(--danger)" id="r-erros">0</div><div class="result-lbl">Erros</div></div>
          <div class="result-card"><div class="result-num" style="color:var(--accent3)" id="r-pct">0%</div><div class="result-lbl">Aproveit.</div></div>
        </div>
        <div class="feedback-box" id="r-msg"></div>
        <div class="btn-row"><button class="btn btn-primary" onclick="novaSessao()">↺ Nova sessão</button></div>
      </div>
    </div>

    <!-- ADICIONAR (só prof) -->
    <div id="page-adicionar" class="page">
      <div class="page-title">Adicionar questão</div>
      <div class="card">
        <div class="form-group">
          <label>TIPO DE MATÉRIA</label>
          <div class="pill-group">
            <div class="pill active" id="pill-exist" onclick="setTipoMat('existente')">Selecionar existente</div>
            <div class="pill" id="pill-nova" onclick="setTipoMat('nova')">Criar nova</div>
          </div>
        </div>
        <div class="form-group" id="fg-matsel">
          <label>MATÉRIA</label><select id="f-matsel"></select>
        </div>
        <div class="form-group" id="fg-matnova" style="display:none">
          <label>NOME DA NOVA MATÉRIA</label><input type="text" id="f-matnova" placeholder="Ex: Física, Matemática...">
        </div>
        <div class="form-group"><label>ENUNCIADO</label><textarea id="f-enunc" placeholder="Enunciado completo..."></textarea></div>
        <div class="form-row">
          <div class="form-group"><label>A)</label><input type="text" id="f-a"></div>
          <div class="form-group"><label>B)</label><input type="text" id="f-b"></div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>C)</label><input type="text" id="f-c"></div>
          <div class="form-group"><label>D)</label><input type="text" id="f-d"></div>
        </div>
        <div class="form-group">
          <label>GABARITO</label>
          <div class="pill-group">
            <div class="pill active-green" id="gab-a" onclick="setGab('a')">A</div>
            <div class="pill" id="gab-b" onclick="setGab('b')">B</div>
            <div class="pill" id="gab-c" onclick="setGab('c')">C</div>
            <div class="pill" id="gab-d" onclick="setGab('d')">D</div>
          </div>
        </div>
        <div class="form-group"><label>EXPLICAÇÃO (OPCIONAL)</label><textarea id="f-explic" style="height:60px" placeholder="Por que essa é a resposta correta?"></textarea></div>
        <div class="btn-row"><button class="btn btn-success" onclick="salvarQuestao()">✓ Salvar questão</button><span id="msg-salvar"></span></div>
      </div>
    </div>

    <!-- BANCO -->
    <div id="page-banco" class="page">
      <div class="page-title">Banco de questões</div>
      <div id="banco-conteudo"></div>
    </div>

    <!-- ADMIN -->
    <div id="page-admin" class="page">
      <div class="page-title">Administração</div>
      <div class="card">
        <div class="card-title">Professores cadastrados</div>
        <div class="prof-list" id="prof-list"></div>
      </div>
      <div class="card" style="margin-top:16px">
        <div class="card-title">Exportar / Importar banco completo</div>
        <div class="btn-row">
          <button class="btn btn-primary" onclick="exportarDados()">⬇ Exportar tudo</button>
          <button class="btn" onclick="document.getElementById('importInput').click()">⬆ Importar</button>
          <input type="file" id="importInput" accept=".json" style="display:none" onchange="importarDados(event)">
          <span id="msg-admin"></span>
        </div>
      </div>
      <div class="card" style="margin-top:16px;border-color:rgba(240,74,74,.25)">
        <div class="card-title" style="color:var(--danger)">Zona de perigo</div>
        <p style="font-size:13px;color:var(--text2);margin-bottom:14px">Apagar todos os dados do sistema (professores, questões, tudo).</p>
        <button class="btn btn-danger" onclick="apagarTudo()">Apagar tudo</button>
      </div>
    </div>
  </main>
</div>

<script>
// ── Storage helpers ───────────────────────────────────────────────────────
const KEY = 'studyquiz_v2';
function carregarDB(){
  try{ return JSON.parse(localStorage.getItem(KEY))||{users:{},questions:{}}; }
  catch(e){ return {users:{},questions:{}}; }
}
function salvarDB(db){ localStorage.setItem(KEY,JSON.stringify(db)); }

// estrutura: db.users = { username: {nome, senha, role:'prof'|'admin'} }
// db.questions = { username: { materia: [ {...} ] } }
// admin padrão: usuario 'admin', senha 'admin123'

function getDB(){
  let db = carregarDB();
  // garantir admin padrão
  if(!db.users['admin']){
    db.users['admin']={nome:'Administrador',senha:'admin123',role:'admin'};
    salvarDB(db);
  }
  return db;
}

// ── Estado sessão ─────────────────────────────────────────────────────────
let sessaoUsuario = null; // {username, nome, role}
let tipoMat='existente', gabSel='a';
let quiz = {qs:[],idx:0,acertos:0,erros:0,respondida:false,escolha:null};

// ── LOGIN / LOGOUT ────────────────────────────────────────────────────────
let tabAtual='prof', subTabAtual='entrar';
function setTab(t){
  tabAtual=t;
  ['prof','aluno','admin'].forEach(x=>{
    document.getElementById('tab-'+x).classList.toggle('active',x===t);
    document.getElementById('form-'+x).style.display=x===t?'block':'none';
  });
}
function setSubTab(t){
  subTabAtual=t;
  ['entrar','cadastrar'].forEach(x=>{
    document.getElementById('tab-'+x).classList.toggle('active',x===t);
    document.getElementById('form-'+x).style.display=x===t?'block':'none';
  });
}

function loginProf(){
  const u=(document.getElementById('l-user').value||'').trim().toLowerCase();
  const p=(document.getElementById('l-pass').value||'');
  const db=getDB();
  if(!db.users[u]||db.users[u].role==='admin'){document.getElementById('l-err').textContent='Usuário não encontrado.';return;}
  if(db.users[u].senha!==p){document.getElementById('l-err').textContent='Senha incorreta.';return;}
  entrar({username:u,nome:db.users[u].nome,role:'prof'});
}

function cadastrarProf(){
  const nome=(document.getElementById('r-nome').value||'').trim();
  const u=(document.getElementById('r-user').value||'').trim().toLowerCase().replace(/\s/g,'');
  const p=(document.getElementById('r-pass').value||'');
  if(!nome||!u||!p){document.getElementById('r-err').textContent='Preencha todos os campos.';return;}
  if(u.length<3){document.getElementById('r-err').textContent='Usuário muito curto.';return;}
  if(p.length<4){document.getElementById('r-err').textContent='Senha muito curta (min. 4).';return;}
  const db=getDB();
  if(db.users[u]){document.getElementById('r-err').textContent='Usuário já existe.';return;}
  db.users[u]={nome,senha:p,role:'prof'};
  if(!db.questions[u]) db.questions[u]={};
  salvarDB(db);
  entrar({username:u,nome,role:'prof'});
}

function loginAluno(){
  entrar({username:'__aluno__',nome:'Aluno',role:'aluno'});
}

function loginAdmin(){
  const p=(document.getElementById('a-pass').value||'');
  const db=getDB();
  if(db.users['admin'].senha!==p){document.getElementById('a-err').textContent='Senha incorreta.';return;}
  entrar({username:'admin',nome:'Administrador',role:'admin'});
}

function entrar(u){
  sessaoUsuario=u;
  document.getElementById('overlay-login').style.display='none';
  document.getElementById('app').style.display='flex';
  // header
  document.getElementById('user-pill').style.display='flex';
  document.getElementById('user-dot').className='user-dot'+(u.role==='aluno'?' aluno':'');
  document.getElementById('user-label').textContent=u.nome+' ['+u.role+']';
  document.getElementById('btn-logout').style.display='block';
  // nav
  const isProf=u.role==='prof';
  const isAdmin=u.role==='admin';
  document.getElementById('nav-adicionar').style.display=isProf?'flex':'none';
  document.getElementById('nav-banco').style.display=isProf||isAdmin?'flex':'none';
  document.getElementById('nav-admin').style.display=isAdmin?'flex':'none';
  irPara('estudar');
}

function logout(){
  sessaoUsuario=null;
  document.getElementById('app').style.display='none';
  document.getElementById('user-pill').style.display='none';
  document.getElementById('btn-logout').style.display='none';
  document.getElementById('overlay-login').style.display='flex';
  // limpar inputs
  ['l-user','l-pass','r-nome','r-user','r-pass','a-pass'].forEach(id=>{
    const el=document.getElementById(id); if(el) el.value='';
  });
  ['l-err','r-err','a-err'].forEach(id=>{ document.getElementById(id).textContent=''; });
  setTab('prof'); setSubTab('entrar');
}

// ── Navegação ─────────────────────────────────────────────────────────────
function irPara(pg){
  document.querySelectorAll('.nav-item').forEach(b=>b.classList.remove('active'));
  const navMap={estudar:0,adicionar:1,banco:2,admin:3};
  const items=document.querySelectorAll('.nav-item');
  // ativa o correto
  items.forEach(b=>{ if(b.textContent.trim().toLowerCase().includes(pg.substring(0,5))) b.classList.add('active'); });
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  const el=document.getElementById('page-'+pg);
  if(el) el.classList.add('active');
  if(pg==='estudar') renderConfigEstudar();
  if(pg==='adicionar') renderFormAdicionar();
  if(pg==='banco') renderBanco();
  if(pg==='admin') renderAdmin();
  atualizarStats();
}

function atualizarStats(){
  const db=getDB();
  let total=0;
  Object.values(db.questions).forEach(prof=>Object.values(prof).forEach(qs=>total+=qs.length));
  document.getElementById('nav-stats').innerHTML=`<div><b>${Object.keys(db.users).filter(u=>db.users[u].role==='prof').length}</b> professores</div><div><b>${total}</b> questões</div>`;
}

// ── ESTUDAR ───────────────────────────────────────────────────────────────
function getAllQuestions(){
  const db=getDB();
  let all=[];
  Object.entries(db.questions).forEach(([prof,mats])=>{
    Object.entries(mats).forEach(([mat,qs])=>{
      qs.forEach(q=>all.push({...q,materia:mat,profUsername:prof,profNome:db.users[prof]?.nome||prof}));
    });
  });
  return all;
}

function getMateriasList(){
  const db=getDB();
  const mats=new Set();
  Object.values(db.questions).forEach(prof=>Object.keys(prof).forEach(m=>mats.add(m)));
  return [...mats].sort();
}

function renderConfigEstudar(){
  document.getElementById('quiz-area').style.display='none';
  document.getElementById('result-area').style.display='none';
  document.getElementById('config-area').style.display='block';
  const sel=document.getElementById('sel-materia');
  sel.innerHTML='<option value="_todas">🔀 Todas as matérias</option>'+
    getMateriasList().map(m=>`<option value="${m}">${m}</option>`).join('');
}

function iniciarSessao(){
  const mat=document.getElementById('sel-materia').value;
  const qtd=parseInt(document.getElementById('qtd-qs').value)||10;
  const shuffle=document.getElementById('chk-shuffle').checked;
  let pool=getAllQuestions();
  if(mat!=='_todas') pool=pool.filter(q=>q.materia===mat);
  if(!pool.length){alert('Nenhuma questão nessa matéria.');return;}
  if(shuffle) pool.sort(()=>Math.random()-.5);
  quiz={qs:pool.slice(0,qtd),idx:0,acertos:0,erros:0,respondida:false,escolha:null};
  document.getElementById('config-area').style.display='none';
  document.getElementById('quiz-area').style.display='block';
  renderQuestao();
}

function renderQuestao(){
  const {qs,idx,acertos,erros,respondida,escolha}=quiz;
  if(idx>=qs.length){mostrarResultado();return;}
  const q=qs[idx];
  const pct=Math.round(idx/qs.length*100);
  document.getElementById('prog-texto').textContent=`Questão ${idx+1} de ${qs.length}`;
  document.getElementById('prog-placar').textContent=`✓ ${acertos}  ✗ ${erros}`;
  document.getElementById('prog-fill').style.width=pct+'%';
  const badge=document.getElementById('q-badge');
  badge.textContent=`${q.materia} · ${q.profNome}`;
  badge.className='badge';
  const alts=['a','b','c','d'];
  document.getElementById('q-texto').textContent=q.enunciado;
  document.getElementById('q-alts').innerHTML=alts.map(l=>{
    let cls='alt';
    if(respondida){ if(l===q.gabarito) cls='alt certo'; else if(l===escolha) cls='alt errado'; }
    else if(l===escolha) cls='alt sel';
    return`<div class="${cls}" onclick="selecionarAlt('${l}')"><span class="alt-letra">${l.toUpperCase()}</span><span>${q['alternativa_'+l]}</span></div>`;
  }).join('');
  if(!respondida){
    document.getElementById('q-feedback').innerHTML='';
    document.getElementById('q-explic').innerHTML='';
    document.getElementById('q-acoes').innerHTML=`<button class="btn btn-primary" onclick="confirmar()" ${!escolha?'disabled':''}>Confirmar →</button>`;
  } else {
    const ok=escolha===q.gabarito;
    document.getElementById('q-feedback').innerHTML=`<div class="feedback-box ${ok?'ok':'no'}">${ok?'✓ Correto!':'✗ Errado! Resposta: '+q.gabarito.toUpperCase()}</div>`;
    document.getElementById('q-explic').innerHTML=q.explicacao?`<div class="explic">💡 ${q.explicacao}</div>`:'';
    document.getElementById('q-acoes').innerHTML=`<button class="btn btn-primary" onclick="proxima()">Próxima →</button>`;
  }
}

function selecionarAlt(l){ if(quiz.respondida)return; quiz.escolha=l; renderQuestao(); }
function confirmar(){ if(!quiz.escolha)return; quiz.respondida=true; if(quiz.escolha===quiz.qs[quiz.idx].gabarito) quiz.acertos++; else quiz.erros++; renderQuestao(); }
function proxima(){ quiz.idx++; quiz.respondida=false; quiz.escolha=null; renderQuestao(); }

function mostrarResultado(){
  document.getElementById('quiz-area').style.display='none';
  document.getElementById('result-area').style.display='block';
  const tot=quiz.acertos+quiz.erros;
  const pct=tot?Math.round(quiz.acertos/tot*100):0;
  document.getElementById('r-acertos').textContent=quiz.acertos;
  document.getElementById('r-erros').textContent=quiz.erros;
  document.getElementById('r-pct').textContent=pct+'%';
  const m=document.getElementById('r-msg');
  if(pct>=70){m.className='feedback-box ok';m.textContent='Ótimo desempenho! Continue assim.';}
  else if(pct>=50){m.className='feedback-box no';m.textContent='Resultado razoável. Revise os temas.';}
  else{m.className='feedback-box no';m.textContent='Precisa estudar mais. Não desista!';}
}
function novaSessao(){ document.getElementById('result-area').style.display='none'; renderConfigEstudar(); }

// ── ADICIONAR ─────────────────────────────────────────────────────────────
function renderFormAdicionar(){
  if(!sessaoUsuario||sessaoUsuario.role!=='prof') return;
  const db=getDB();
  const minhas=Object.keys(db.questions[sessaoUsuario.username]||{}).sort();
  const sel=document.getElementById('f-matsel');
  sel.innerHTML=minhas.length?minhas.map(m=>`<option value="${m}">${m}</option>`).join(''):'<option value="">Nenhuma matéria ainda</option>';
  if(!minhas.length) setTipoMat('nova');
}

function setTipoMat(t){
  tipoMat=t;
  document.getElementById('pill-exist').classList.toggle('active',t==='existente');
  document.getElementById('pill-nova').classList.toggle('active',t==='nova');
  document.getElementById('fg-matsel').style.display=t==='existente'?'block':'none';
  document.getElementById('fg-matnova').style.display=t==='nova'?'block':'none';
}

function setGab(l){
  gabSel=l;
  ['a','b','c','d'].forEach(x=>document.getElementById('gab-'+x).className='pill'+(x===l?' active-green':''));
}

function salvarQuestao(){
  if(!sessaoUsuario||sessaoUsuario.role!=='prof') return;
  let mat=tipoMat==='nova'?(document.getElementById('f-matnova').value||'').trim():document.getElementById('f-matsel').value;
  const enunc=(document.getElementById('f-enunc').value||'').trim();
  const a=(document.getElementById('f-a').value||'').trim();
  const b=(document.getElementById('f-b').value||'').trim();
  const c=(document.getElementById('f-c').value||'').trim();
  const d=(document.getElementById('f-d').value||'').trim();
  const explic=(document.getElementById('f-explic').value||'').trim();
  if(!mat||!enunc||!a||!b||!c||!d){mostrarMsg('msg-salvar','Preencha todos os campos!','err');return;}
  const db=getDB();
  if(!db.questions[sessaoUsuario.username]) db.questions[sessaoUsuario.username]={};
  if(!db.questions[sessaoUsuario.username][mat]) db.questions[sessaoUsuario.username][mat]=[];
  db.questions[sessaoUsuario.username][mat].push({enunciado:enunc,alternativa_a:a,alternativa_b:b,alternativa_c:c,alternativa_d:d,gabarito:gabSel,explicacao:explic,materia:mat});
  salvarDB(db);
  ['f-enunc','f-a','f-b','f-c','f-d','f-explic','f-matnova'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});
  gabSel='a'; setGab('a');
  renderFormAdicionar(); atualizarStats();
  mostrarMsg('msg-salvar',`Salvo em "${mat}"!`,'ok');
}

// ── BANCO ─────────────────────────────────────────────────────────────────
function renderBanco(){
  if(!sessaoUsuario) return;
  const db=getDB();
  const c=document.getElementById('banco-conteudo');
  let html='';
  let mats={};
  // prof vê só as suas, admin vê todas
  if(sessaoUsuario.role==='prof'){
    const minhas=db.questions[sessaoUsuario.username]||{};
    Object.entries(minhas).forEach(([m,qs])=>mats[m]={qs,prof:sessaoUsuario.nome});
  } else {
    Object.entries(db.questions).forEach(([u,profMats])=>{
      Object.entries(profMats).forEach(([m,qs])=>{
        const key=`${m} (${db.users[u]?.nome||u})`;
        mats[key]={qs,prof:db.users[u]?.nome||u,username:u,materia:m};
      });
    });
  }
  const keys=Object.keys(mats).sort();
  if(!keys.length){c.innerHTML='<div class="empty">Nenhuma questão cadastrada ainda.</div>';return;}
  html=keys.map(k=>{
    const {qs,prof,username,materia}=mats[k];
    const delBtn=sessaoUsuario.role==='prof'?
      `<button class="btn btn-danger" onclick="event.stopPropagation();apagarMateria('${materia}')">Apagar matéria</button>`:
      `<button class="btn btn-danger" onclick="event.stopPropagation();apagarMateriaAdmin('${username}','${materia}')">Apagar</button>`;
    return`<div class="mat-block">
      <div class="mat-header" onclick="toggleMat(this)">
        <div><span class="mat-name">${k}</span><span class="mat-count">${qs.length} questão(ões)</span></div>
        ${delBtn}
      </div>
      <div class="mat-body">
        ${qs.map((q,i)=>`<div class="q-item">
          <div class="q-enunc"><b>${i+1}.</b> ${q.enunciado}</div>
          <div class="q-alts">A) ${q.alternativa_a} · B) ${q.alternativa_b} · C) ${q.alternativa_c} · D) ${q.alternativa_d}</div>
          <div class="q-gabarito">Gabarito: ${q.gabarito.toUpperCase()}${q.explicacao?' — '+q.explicacao:''}</div>
        </div>`).join('')}
      </div>
    </div>`;
  }).join('');
  c.innerHTML=html;
}

function toggleMat(h){ h.classList.toggle('open'); h.nextElementSibling.classList.toggle('open'); }

function apagarMateria(m){
  if(!confirm(`Apagar a matéria "${m}" e todas as suas questões?`)) return;
  const db=getDB();
  delete db.questions[sessaoUsuario.username][m];
  salvarDB(db); renderBanco(); atualizarStats();
}

function apagarMateriaAdmin(u,m){
  if(!confirm(`Apagar "${m}" do professor?`)) return;
  const db=getDB();
  if(db.questions[u]) delete db.questions[u][m];
  salvarDB(db); renderBanco(); atualizarStats();
}

// ── ADMIN ─────────────────────────────────────────────────────────────────
function renderAdmin(){
  const db=getDB();
  const profs=Object.entries(db.users).filter(([u,d])=>d.role==='prof');
  const el=document.getElementById('prof-list');
  if(!profs.length){el.innerHTML='<div class="empty">Nenhum professor cadastrado.</div>';return;}
  el.innerHTML=profs.map(([u,d])=>{
    const total=Object.values(db.questions[u]||{}).reduce((a,b)=>a+b.length,0);
    return`<div class="prof-row">
      <div class="prof-info">
        <div class="prof-name">${d.nome}</div>
        <div class="prof-user">@${u}</div>
        <div class="prof-qs">${total} questões cadastradas</div>
      </div>
      <button class="btn btn-danger" onclick="apagarProf('${u}')">Remover</button>
    </div>`;
  }).join('');
}

function apagarProf(u){
  if(!confirm(`Remover o professor @${u} e todas as questões dele?`)) return;
  const db=getDB();
  delete db.users[u];
  delete db.questions[u];
  salvarDB(db); renderAdmin(); atualizarStats();
}

function exportarDados(){
  const db=getDB();
  const blob=new Blob([JSON.stringify(db,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download='studyquiz_backup.json'; a.click();
}

function importarDados(e){
  const file=e.target.files[0]; if(!file) return;
  const reader=new FileReader();
  reader.onload=ev=>{
    try{
      const imp=JSON.parse(ev.target.result);
      if(!imp.users||!imp.questions) throw new Error();
      const db=getDB();
      // merge users e questions
      Object.assign(db.users,imp.users);
      Object.entries(imp.questions).forEach(([u,mats])=>{
        if(!db.questions[u]) db.questions[u]={};
        Object.entries(mats).forEach(([m,qs])=>{
          if(!db.questions[u][m]) db.questions[u][m]=[];
          qs.forEach(q=>{ if(!db.questions[u][m].find(x=>x.enunciado===q.enunciado)) db.questions[u][m].push(q); });
        });
      });
      salvarDB(db); atualizarStats(); renderAdmin();
      mostrarMsg('msg-admin','Importado!','ok');
    }catch{ mostrarMsg('msg-admin','Arquivo inválido.','err'); }
  };
  reader.readAsText(file); e.target.value='';
}

function apagarTudo(){
  if(!confirm('Apagar TUDO? Isso não pode ser desfeito.')) return;
  localStorage.removeItem(KEY); logout();
}

// ── Helpers ───────────────────────────────────────────────────────────────
function mostrarMsg(id,txt,tipo){
  const el=document.getElementById(id);
  el.className='msg '+tipo; el.textContent=txt;
  setTimeout(()=>el.textContent='',2800);
}

// init
getDB();
</script>
</body>
</html>
