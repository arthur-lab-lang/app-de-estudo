<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StudyQuiz</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0b0d12;
    --bg2: #111419;
    --bg3: #161a22;
    --border: #1e2330;
    --border2: #2a3148;
    --accent: #4af0a0;
    --accent2: #4a9ff0;
    --accent3: #f0a04a;
    --text: #dde4f5;
    --text2: #7a88aa;
    --text3: #3d4a63;
    --danger: #f04a4a;
    --success: #4af0a0;
    --mono: 'Space Mono', monospace;
    --sans: 'Syne', sans-serif;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* HEADER */
  header {
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    padding: 0 24px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .logo {
    font-family: var(--mono);
    font-size: 15px;
    color: var(--accent);
    letter-spacing: 0.08em;
  }
  .logo span { color: var(--text2); }
  .header-actions { display: flex; gap: 8px; }
  .hbtn {
    background: none;
    border: 1px solid var(--border2);
    color: var(--text2);
    font-family: var(--mono);
    font-size: 11px;
    padding: 5px 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .hbtn:hover { border-color: var(--accent2); color: var(--accent2); }

  /* LAYOUT */
  .app { display: flex; flex: 1; }
  nav {
    width: 200px;
    background: var(--bg2);
    border-right: 1px solid var(--border);
    padding: 20px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    position: sticky;
    top: 56px;
    height: calc(100vh - 56px);
  }
  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: 8px;
    border: 1px solid transparent;
    cursor: pointer;
    font-size: 13px;
    color: var(--text2);
    transition: all 0.15s;
    background: none;
    width: 100%;
    text-align: left;
    font-family: var(--sans);
  }
  .nav-item:hover { background: var(--bg3); color: var(--text); }
  .nav-item.active {
    background: var(--bg3);
    border-color: var(--border2);
    color: var(--accent);
  }
  .nav-icon { font-size: 15px; }
  .nav-divider { height: 1px; background: var(--border); margin: 8px 0; }
  .nav-stats {
    margin-top: auto;
    padding: 12px;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 8px;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text2);
    line-height: 2;
  }
  .nav-stats b { color: var(--accent); }

  /* MAIN */
  main { flex: 1; padding: 28px 32px; max-width: 760px; }
  .page { display: none; }
  .page.active { display: block; }
  .page-title {
    font-size: 22px;
    font-weight: 800;
    color: var(--text);
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .page-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    margin-left: 8px;
  }

  /* CARDS */
  .card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
  }
  .card-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text2);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 14px;
    font-family: var(--mono);
  }

  /* FORM */
  .form-group { margin-bottom: 14px; }
  .form-group label {
    display: block;
    font-size: 12px;
    color: var(--text2);
    margin-bottom: 5px;
    font-family: var(--mono);
    letter-spacing: 0.04em;
  }
  input[type=text], textarea, select {
    width: 100%;
    background: var(--bg3);
    border: 1px solid var(--border2);
    border-radius: 7px;
    color: var(--text);
    font-family: var(--sans);
    font-size: 13px;
    padding: 9px 12px;
    outline: none;
    transition: border-color 0.15s;
  }
  input[type=text]:focus, textarea:focus, select:focus {
    border-color: var(--accent2);
  }
  textarea { height: 80px; resize: vertical; }
  select option { background: var(--bg3); }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

  /* RADIO PILLS */
  .pill-group { display: flex; gap: 6px; flex-wrap: wrap; }
  .pill {
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid var(--border2);
    font-size: 12px;
    cursor: pointer;
    color: var(--text2);
    background: var(--bg3);
    font-family: var(--mono);
    transition: all 0.15s;
  }
  .pill:hover { border-color: var(--accent2); color: var(--accent2); }
  .pill.active { background: rgba(74,159,240,0.12); border-color: var(--accent2); color: var(--accent2); }
  .pill.active-green { background: rgba(74,240,160,0.12); border-color: var(--accent); color: var(--accent); }

  /* BUTTONS */
  .btn {
    padding: 9px 20px;
    border-radius: 8px;
    border: 1px solid var(--border2);
    background: var(--bg3);
    color: var(--text);
    font-family: var(--mono);
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
    letter-spacing: 0.03em;
  }
  .btn:hover { border-color: var(--text2); }
  .btn-primary {
    background: rgba(74,159,240,0.15);
    border-color: var(--accent2);
    color: var(--accent2);
  }
  .btn-primary:hover { background: rgba(74,159,240,0.25); }
  .btn-success {
    background: rgba(74,240,160,0.12);
    border-color: var(--accent);
    color: var(--accent);
  }
  .btn-success:hover { background: rgba(74,240,160,0.22); }
  .btn-danger {
    background: rgba(240,74,74,0.1);
    border-color: var(--danger);
    color: var(--danger);
    font-size: 11px;
    padding: 5px 12px;
  }
  .btn-danger:hover { background: rgba(240,74,74,0.2); }
  .btn-row { display: flex; gap: 8px; align-items: center; margin-top: 6px; }

  /* BADGE */
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: var(--mono);
    background: rgba(74,159,240,0.12);
    border: 1px solid rgba(74,159,240,0.3);
    color: var(--accent2);
    margin-bottom: 10px;
  }

  /* STUDY PAGE */
  .sel-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
  }
  .sel-label {
    font-size: 12px;
    font-family: var(--mono);
    color: var(--text2);
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  /* QUIZ */
  #quiz-area { display: none; }
  .progress-wrap { margin-bottom: 18px; }
  .progress-info {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    font-family: var(--mono);
    color: var(--text2);
    margin-bottom: 6px;
  }
  .progress-bar {
    height: 3px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    background: var(--accent2);
    border-radius: 2px;
    transition: width 0.4s ease;
  }
  .q-text {
    font-size: 15px;
    line-height: 1.7;
    color: var(--text);
    margin-bottom: 18px;
  }
  .alt {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 11px 14px;
    border-radius: 8px;
    border: 1px solid var(--border);
    margin-bottom: 8px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.15s;
    color: var(--text);
    background: var(--bg3);
  }
  .alt:hover { border-color: var(--border2); }
  .alt.sel { border-color: var(--accent2); background: rgba(74,159,240,0.08); }
  .alt.certo { border-color: var(--accent); background: rgba(74,240,160,0.08); color: var(--accent); }
  .alt.errado { border-color: var(--danger); background: rgba(240,74,74,0.08); color: var(--danger); }
  .alt-letra {
    font-family: var(--mono);
    font-weight: 700;
    font-size: 12px;
    min-width: 20px;
    margin-top: 1px;
  }
  .feedback-box {
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-family: var(--mono);
    margin: 14px 0;
  }
  .feedback-box.ok {
    background: rgba(74,240,160,0.08);
    border: 1px solid rgba(74,240,160,0.3);
    color: var(--accent);
  }
  .feedback-box.no {
    background: rgba(240,74,74,0.08);
    border: 1px solid rgba(240,74,74,0.3);
    color: var(--danger);
  }
  .explic {
    font-size: 12px;
    color: var(--text2);
    padding: 10px 14px;
    background: var(--bg3);
    border-left: 2px solid var(--border2);
    border-radius: 0 6px 6px 0;
    margin-top: 8px;
    line-height: 1.6;
  }

  /* RESULT */
  #result-area { display: none; }
  .result-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
  .result-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
  }
  .result-num {
    font-family: var(--mono);
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 4px;
  }
  .result-lbl { font-size: 11px; color: var(--text2); text-transform: uppercase; letter-spacing: 0.06em; font-family: var(--mono); }

  /* BANCO */
  .mat-block {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 12px;
    overflow: hidden;
  }
  .mat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 18px;
    cursor: pointer;
    border-bottom: 1px solid transparent;
    transition: background 0.15s;
  }
  .mat-header:hover { background: var(--bg3); }
  .mat-header.open { border-bottom-color: var(--border); }
  .mat-name { font-size: 14px; font-weight: 600; color: var(--text); }
  .mat-count { font-size: 11px; font-family: var(--mono); color: var(--text2); margin-left: 10px; }
  .mat-body { display: none; padding: 14px 18px; }
  .mat-body.open { display: block; }
  .q-item {
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
  }
  .q-item:last-child { border-bottom: none; }
  .q-enunc { color: var(--text); margin-bottom: 6px; line-height: 1.5; }
  .q-alts { color: var(--text2); font-size: 12px; line-height: 1.8; }
  .q-gabarito { color: var(--accent); font-family: var(--mono); font-size: 12px; margin-top: 4px; }

  /* MENSAGEM */
  .msg {
    font-size: 12px;
    font-family: var(--mono);
    padding: 8px 12px;
    border-radius: 6px;
    display: inline-block;
    margin-left: 10px;
  }
  .msg.ok { background: rgba(74,240,160,0.1); color: var(--accent); }
  .msg.err { background: rgba(240,74,74,0.1); color: var(--danger); }

  /* EMPTY */
  .empty {
    text-align: center;
    padding: 48px;
    color: var(--text3);
    font-size: 13px;
    font-family: var(--mono);
  }

  /* CHECKBOX */
  .check-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--text2);
    cursor: pointer;
    margin-top: 10px;
  }
  input[type=checkbox] { accent-color: var(--accent2); width: 14px; height: 14px; cursor: pointer; }
  input[type=number] {
    width: 80px;
    background: var(--bg3);
    border: 1px solid var(--border2);
    border-radius: 7px;
    color: var(--text);
    font-family: var(--mono);
    font-size: 13px;
    padding: 9px 12px;
    outline: none;
  }
  input[type=number]:focus { border-color: var(--accent2); }

  /* SCROLLBAR */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
</style>
</head>
<body>

<header>
  <div class="logo">STUDY<span>/</span>QUIZ</div>
  <div class="header-actions">
    <button class="hbtn" onclick="exportarDados()">⬇ Exportar</button>
    <button class="hbtn" onclick="document.getElementById('importInput').click()">⬆ Importar</button>
    <input type="file" id="importInput" accept=".json" style="display:none" onchange="importarDados(event)">
  </div>
</header>

<div class="app">
  <nav>
    <button class="nav-item active" onclick="irPara('estudar')">
      <span class="nav-icon">▶</span> Estudar
    </button>
    <button class="nav-item" onclick="irPara('adicionar')">
      <span class="nav-icon">+</span> Adicionar
    </button>
    <button class="nav-item" onclick="irPara('banco')">
      <span class="nav-icon">≡</span> Banco
    </button>
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
            <div>
              <div class="sel-label">Quantidade de questões</div>
              <input type="number" id="qtd-qs" value="10" min="1" max="999">
            </div>
            <div>
              <label class="check-row">
                <input type="checkbox" id="chk-shuffle" checked>
                Embaralhar questões
              </label>
            </div>
          </div>

          <div class="btn-row" style="margin-top:18px">
            <button class="btn btn-success" onclick="iniciarSessao()">▶ Iniciar sessão</button>
          </div>
        </div>
      </div>

      <div id="quiz-area">
        <div class="progress-wrap">
          <div class="progress-info">
            <span id="prog-texto"></span>
            <span id="prog-placar"></span>
          </div>
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

      <div id="result-area">
        <div class="result-grid">
          <div class="result-card">
            <div class="result-num" style="color:var(--accent)" id="r-acertos">0</div>
            <div class="result-lbl">Acertos</div>
          </div>
          <div class="result-card">
            <div class="result-num" style="color:var(--danger)" id="r-erros">0</div>
            <div class="result-lbl">Erros</div>
          </div>
          <div class="result-card">
            <div class="result-num" style="color:var(--accent3)" id="r-pct">0%</div>
            <div class="result-lbl">Aproveit.</div>
          </div>
        </div>
        <div class="feedback-box" id="r-msg"></div>
        <div class="btn-row">
          <button class="btn btn-primary" onclick="novaSessao()">↺ Nova sessão</button>
        </div>
      </div>
    </div>

    <!-- ADICIONAR -->
    <div id="page-adicionar" class="page">
      <div class="page-title">Adicionar questão</div>
      <div class="card">

        <div class="form-group">
          <label>TIPO DE MATÉRIA</label>
          <div class="pill-group">
            <div class="pill active" id="pill-exist" onclick="setTipoMat('existente')">Selecionar existente</div>
            <div class="pill" id="pill-nova" onclick="setTipoMat('nova')">Criar nova matéria</div>
          </div>
        </div>

        <div class="form-group" id="fg-matsel">
          <label>MATÉRIA</label>
          <select id="f-matsel"></select>
        </div>
        <div class="form-group" id="fg-matnova" style="display:none">
          <label>NOME DA NOVA MATÉRIA</label>
          <input type="text" id="f-matnova" placeholder="Ex: Redes, Python, Hardware...">
        </div>

        <div class="form-group">
          <label>ENUNCIADO</label>
          <textarea id="f-enunc" placeholder="Digite o enunciado completo da questão..."></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>A)</label>
            <input type="text" id="f-a" placeholder="Alternativa A">
          </div>
          <div class="form-group">
            <label>B)</label>
            <input type="text" id="f-b" placeholder="Alternativa B">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>C)</label>
            <input type="text" id="f-c" placeholder="Alternativa C">
          </div>
          <div class="form-group">
            <label>D)</label>
            <input type="text" id="f-d" placeholder="Alternativa D">
          </div>
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

        <div class="form-group">
          <label>EXPLICAÇÃO (OPCIONAL)</label>
          <textarea id="f-explic" placeholder="Explique por que essa é a resposta correta..." style="height:60px"></textarea>
        </div>

        <div class="btn-row">
          <button class="btn btn-success" onclick="salvarQuestao()">✓ Salvar questão</button>
          <span id="msg-salvar"></span>
        </div>
      </div>
    </div>

    <!-- BANCO -->
    <div id="page-banco" class="page">
      <div class="page-title">Banco de questões</div>
      <div id="banco-conteudo"></div>
    </div>

  </main>
</div>

<script>
// ── Dados ────────────────────────────────────────────────────────────────
let dados = JSON.parse(localStorage.getItem('studyquiz') || '{}');
let tipoMat = 'existente';
let gabSel = 'a';
let sessao = { qs:[], idx:0, acertos:0, erros:0, respondida:false, escolha:null };

function salvar() { localStorage.setItem('studyquiz', JSON.stringify(dados)); }
function getMaterias() { return Object.keys(dados).sort(); }
function totalQs() { return Object.values(dados).reduce((a,b)=>a+b.length,0); }

// ── Nav ──────────────────────────────────────────────────────────────────
function irPara(pg) {
  document.querySelectorAll('.nav-item').forEach((b,i)=>{
    b.classList.toggle('active', ['estudar','adicionar','banco'][i]===pg);
  });
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.getElementById('page-'+pg).classList.add('active');
  if(pg==='estudar') renderConfigEstudar();
  if(pg==='adicionar') renderFormAdicionar();
  if(pg==='banco') renderBanco();
  atualizarStats();
}

function atualizarStats() {
  document.getElementById('nav-stats').innerHTML =
    `<div><b>${getMaterias().length}</b> matérias</div><div><b>${totalQs()}</b> questões</div>`;
}

// ── Estudar ──────────────────────────────────────────────────────────────
function renderConfigEstudar() {
  document.getElementById('quiz-area').style.display = 'none';
  document.getElementById('result-area').style.display = 'none';
  document.getElementById('config-area').style.display = 'block';
  const sel = document.getElementById('sel-materia');
  sel.innerHTML = '<option value="_todas">🔀 Todas as matérias</option>' +
    getMaterias().map(m=>`<option value="${m}">${m}</option>`).join('');
}

function iniciarSessao() {
  const mat = document.getElementById('sel-materia').value;
  const qtd = parseInt(document.getElementById('qtd-qs').value)||10;
  const shuffle = document.getElementById('chk-shuffle').checked;
  let pool = [];
  if(mat==='_todas') Object.values(dados).forEach(qs=>pool.push(...qs));
  else pool = [...(dados[mat]||[])];
  if(!pool.length) { alert('Nenhuma questão nessa matéria.'); return; }
  if(shuffle) pool.sort(()=>Math.random()-0.5);
  sessao = { qs:pool.slice(0,qtd), idx:0, acertos:0, erros:0, respondida:false, escolha:null };
  document.getElementById('config-area').style.display = 'none';
  document.getElementById('quiz-area').style.display = 'block';
  renderQuestao();
}

function renderQuestao() {
  const {qs,idx,acertos,erros,respondida,escolha} = sessao;
  if(idx>=qs.length) { mostrarResultado(); return; }
  const q = qs[idx];
  const pct = Math.round(idx/qs.length*100);

  document.getElementById('prog-texto').textContent = `Questão ${idx+1} de ${qs.length}`;
  document.getElementById('prog-placar').textContent = `✓ ${acertos}  ✗ ${erros}`;
  document.getElementById('prog-fill').style.width = pct+'%';
  document.getElementById('q-badge').textContent = q.materia||'Geral';
  document.getElementById('q-texto').textContent = q.enunciado;

  const alts = ['a','b','c','d'];
  document.getElementById('q-alts').innerHTML = alts.map(l=>{
    let cls = 'alt';
    if(respondida) {
      if(l===q.gabarito) cls='alt certo';
      else if(l===escolha) cls='alt errado';
    } else if(l===escolha) cls='alt sel';
    const letra = l.toUpperCase();
    return `<div class="${cls}" onclick="selecionarAlt('${l}')" id="alt-${l}">
      <span class="alt-letra">${letra}</span>
      <span>${q['alternativa_'+l]}</span>
    </div>`;
  }).join('');

  if(!respondida) {
    document.getElementById('q-feedback').innerHTML = '';
    document.getElementById('q-explic').innerHTML = '';
    document.getElementById('q-acoes').innerHTML =
      `<button class="btn btn-primary" onclick="confirmar()" id="btn-conf" ${!escolha?'disabled':''}>Confirmar →</button>`;
  } else {
    const ok = escolha===q.gabarito;
    document.getElementById('q-feedback').innerHTML =
      `<div class="feedback-box ${ok?'ok':'no'}">${ok?'✓ Correto!':'✗ Errado! Resposta: '+q.gabarito.toUpperCase()}</div>`;
    document.getElementById('q-explic').innerHTML = q.explicacao
      ? `<div class="explic">💡 ${q.explicacao}</div>` : '';
    document.getElementById('q-acoes').innerHTML =
      `<button class="btn btn-primary" onclick="proxima()">Próxima →</button>`;
  }
}

function selecionarAlt(l) {
  if(sessao.respondida) return;
  sessao.escolha = l;
  renderQuestao();
}

function confirmar() {
  if(!sessao.escolha) return;
  sessao.respondida = true;
  if(sessao.escolha===sessao.qs[sessao.idx].gabarito) sessao.acertos++;
  else sessao.erros++;
  renderQuestao();
}

function proxima() {
  sessao.idx++;
  sessao.respondida = false;
  sessao.escolha = null;
  renderQuestao();
}

function mostrarResultado() {
  document.getElementById('quiz-area').style.display = 'none';
  document.getElementById('result-area').style.display = 'block';
  const tot = sessao.acertos+sessao.erros;
  const pct = tot ? Math.round(sessao.acertos/tot*100) : 0;
  document.getElementById('r-acertos').textContent = sessao.acertos;
  document.getElementById('r-erros').textContent = sessao.erros;
  document.getElementById('r-pct').textContent = pct+'%';
  const msg = document.getElementById('r-msg');
  if(pct>=70) { msg.className='feedback-box ok'; msg.textContent='Ótimo desempenho! Continue assim.'; }
  else if(pct>=50) { msg.className='feedback-box no'; msg.textContent='Resultado razoável. Revise os temas com mais atenção.'; }
  else { msg.className='feedback-box no'; msg.textContent='Precisa estudar mais. Não desista!'; }
}

function novaSessao() {
  document.getElementById('result-area').style.display = 'none';
  renderConfigEstudar();
}

// ── Adicionar ─────────────────────────────────────────────────────────────
function renderFormAdicionar() {
  const mats = getMaterias();
  const sel = document.getElementById('f-matsel');
  sel.innerHTML = mats.length
    ? mats.map(m=>`<option value="${m}">${m}</option>`).join('')
    : '<option value="">Nenhuma matéria ainda</option>';
  if(!mats.length) setTipoMat('nova');
}

function setTipoMat(t) {
  tipoMat = t;
  document.getElementById('pill-exist').classList.toggle('active', t==='existente');
  document.getElementById('pill-nova').classList.toggle('active', t==='nova');
  document.getElementById('fg-matsel').style.display = t==='existente' ? 'block':'none';
  document.getElementById('fg-matnova').style.display = t==='nova' ? 'block':'none';
}

function setGab(l) {
  gabSel = l;
  ['a','b','c','d'].forEach(x=>{
    document.getElementById('gab-'+x).className = 'pill'+(x===l?' active-green':'');
  });
}

function salvarQuestao() {
  let mat = tipoMat==='nova'
    ? (document.getElementById('f-matnova').value||'').trim()
    : document.getElementById('f-matsel').value;
  const enunc = (document.getElementById('f-enunc').value||'').trim();
  const a = (document.getElementById('f-a').value||'').trim();
  const b = (document.getElementById('f-b').value||'').trim();
  const c = (document.getElementById('f-c').value||'').trim();
  const d = (document.getElementById('f-d').value||'').trim();
  const explic = (document.getElementById('f-explic').value||'').trim();
  if(!mat||!enunc||!a||!b||!c||!d) {
    mostrarMsg('msg-salvar','Preencha todos os campos!','err'); return;
  }
  if(!dados[mat]) dados[mat]=[];
  dados[mat].push({enunciado:enunc,alternativa_a:a,alternativa_b:b,alternativa_c:c,alternativa_d:d,gabarito:gabSel,explicacao:explic,materia:mat});
  salvar();
  // limpar campos
  ['f-enunc','f-a','f-b','f-c','f-d','f-explic','f-matnova'].forEach(id=>{
    const el=document.getElementById(id); if(el) el.value='';
  });
  gabSel='a'; setGab('a');
  renderFormAdicionar();
  atualizarStats();
  mostrarMsg('msg-salvar',`Salvo em "${mat}"!`,'ok');
}

function mostrarMsg(id,txt,tipo) {
  const el=document.getElementById(id);
  el.className='msg '+tipo; el.textContent=txt;
  setTimeout(()=>el.textContent='',2800);
}

// ── Banco ─────────────────────────────────────────────────────────────────
function renderBanco() {
  const mats = getMaterias();
  const c = document.getElementById('banco-conteudo');
  if(!mats.length) { c.innerHTML='<div class="empty">Nenhuma questão cadastrada ainda.</div>'; return; }
  c.innerHTML = mats.map(m=>`
    <div class="mat-block">
      <div class="mat-header" onclick="toggleMat(this)">
        <div>
          <span class="mat-name">${m}</span>
          <span class="mat-count">${dados[m].length} questão(ões)</span>
        </div>
        <button class="btn btn-danger" onclick="event.stopPropagation();apagarMat('${m}')">Apagar matéria</button>
      </div>
      <div class="mat-body">
        ${dados[m].map((q,i)=>`
          <div class="q-item">
            <div class="q-enunc"><b>${i+1}.</b> ${q.enunciado}</div>
            <div class="q-alts">
              A) ${q.alternativa_a} &nbsp;·&nbsp;
              B) ${q.alternativa_b} &nbsp;·&nbsp;
              C) ${q.alternativa_c} &nbsp;·&nbsp;
              D) ${q.alternativa_d}
            </div>
            <div class="q-gabarito">Gabarito: ${q.gabarito.toUpperCase()}${q.explicacao?' — '+q.explicacao:''}</div>
          </div>`).join('')}
      </div>
    </div>`).join('');
}

function toggleMat(header) {
  header.classList.toggle('open');
  header.nextElementSibling.classList.toggle('open');
}

function apagarMat(m) {
  if(!confirm(`Apagar a matéria "${m}" e todas as suas questões?`)) return;
  delete dados[m]; salvar(); renderBanco(); atualizarStats();
}

// ── Export / Import ────────────────────────────────────────────────────────
function exportarDados() {
  if(!totalQs()) { alert('Nenhuma questão para exportar.'); return; }
  const blob = new Blob([JSON.stringify(dados,null,2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'studyquiz_backup.json';
  a.click();
}

function importarDados(e) {
  const file = e.target.files[0];
  if(!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    try {
      const importado = JSON.parse(ev.target.result);
      if(typeof importado!=='object') throw new Error();
      // merge
      for(const mat in importado) {
        if(!dados[mat]) dados[mat]=[];
        importado[mat].forEach(q=>{ if(!dados[mat].find(x=>x.enunciado===q.enunciado)) dados[mat].push(q); });
      }
      salvar(); atualizarStats();
      alert(`Importado com sucesso! Total: ${totalQs()} questões.`);
    } catch{ alert('Arquivo inválido.'); }
  };
  reader.readAsText(file);
  e.target.value='';
}

// ── Init ───────────────────────────────────────────────────────────────────
renderConfigEstudar();
atualizarStats();
</script>
</body>
</html>
