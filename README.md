# 📚 StudyQuiz — App de Questões para Estudo

## Como rodar

### 1. Instale o Streamlit
Abra o terminal e rode:
```
pip install streamlit
```

### 2. Execute o app
Na pasta onde está o arquivo `app.py`, rode:
```
streamlit run app.py
```

O navegador vai abrir automaticamente em `http://localhost:8501`

---

## Funcionalidades

- **➕ Adicionar Questão** — Cadastre questões com 4 alternativas, gabarito e explicação opcional, organizadas por matéria
- **📝 Estudar** — Selecione uma matéria (ou todas), defina quantas questões quer responder, embaralhe e estude
- **📋 Ver Banco** — Visualize todas as questões cadastradas por matéria

## Onde ficam salvas as questões?
No arquivo `questoes.json`, criado automaticamente na mesma pasta do `app.py`.
