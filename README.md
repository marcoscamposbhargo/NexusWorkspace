# 🚀 Nexus Workspace

Painel *full-stack* de gerenciamento de tarefas e produtividade desenvolvido para demonstrar a integração eficiente e moderna entre **Python (Flask)**, **HTML5**, **CSS3** e **JavaScript (Vanilla)**.

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Framework-black?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/JavaScript-ES6+-yellow?style=for-the-badge&logo=javascript&logoColor=white" alt="JavaScript">
  <img src="https://img.shields.io/badge/CSS3-Modern-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3">
</div>

---

## ✨ Funcionalidades

* **Cadastro Dinâmico (Sem Refresh):** Adicione novas tarefas informando título e categoria sem recarregar a página através de requisições assíncronas (*Fetch API*).
* **Filtro em Tempo Real:** Campo de busca interativo que filtra instantaneamente os registros por título ou categoria conforme você digita.
* **Exclusão de Registros:** Remova tarefas da lista com atualização imediata do DOM e sincronização com o backend.
* **Arquitetura RESTful:** O backend em Flask atua como uma API leve processando rotas `GET`, `POST` e `JSON`.
* **Design Moderno & Responsivo:** Interface limpa inspirada em painéis corporativos, utilizando variáveis CSS e modo escuro nativo (*Dark Mode*).

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python / Flask
* **Frontend Estrutural:** HTML5 Semântico
* **Estilização:** CSS3 Customizado (Flexbox, Variáveis, Transições)
* **Interatividade:** JavaScript moderno (DOM Manipulation, Async/Await)

---

## 📂 Estrutura do Projeto

O projeto foi consolidado em arquivo único para facilitar a execução local e portabilidade:

```text
NexusWorkspace/
│
└── app.py    # Contém rotas Flask, HTML, CSS e Lógica JS integradas


Plaintext/
├── app.py               # Código principal (Flask + Pywebview + SQLite)
├── icone.ico            # Ícone do aplicativo
├── nexus_workspace.db   # Banco de dados SQLite gerado automaticamente
└── README.md            # Documentação do projeto
