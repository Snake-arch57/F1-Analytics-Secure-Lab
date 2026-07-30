# 🏎️ F1 Analytics & AI Local Lab (Secure Blue Team Edition)

Um laboratório de engenharia de dados e Inteligência Artificial que consome dados da Fórmula 1 (via **FastF1**), armazena em um banco **PostgreSQL** isolado e permite interagir através de um chat construído em **Streamlit** e integrado à API da **Groq**.

---

## 🛠️ Tecnologias
- **Python / Streamlit** (Interface Visual)
- **PostgreSQL 16** (Banco Relacional)
- **FastF1** (Telemetria Oficial)
- **Groq API** (LLM llama-3.3-70b-versatile)
- **Docker & Docker Compose** (Containerização)

---

## 🚀 Como Executar o Projeto

1. **Clone o repositório:**
   git clone https://github.com/SEU-USUARIO/f1-analytics-ai.git
   cd f1-analytics-ai

2. **Configure o arquivo de ambiente:**
   cp .env.example .env

3. **Suba a aplicação com Docker:**
   docker compose up --build -d

4. **Acesse no navegador:**
   http://localhost:8501

---

## 🛡️ Postura de Segurança e Hardening (Blue Team Lab)

Este repositório adota práticas de segurança defensiva (*Security by Design*) para operar como um ambiente controlado e seguro.

### Medidas Aplicadas:

* **Execução Não-Root no Container (Dockerfile):**
  A aplicação Python/Streamlit roda sob a conta de menor privilégio (appuser), impedindo potenciais ataques de Container Breakout e escalação de privilégios no host.

* **Isolamento de Rede Interna (docker-compose.yml):**
  O banco de dados PostgreSQL roda exclusivamente na rede restrita backend (internal: true). Nenhuma porta (ex: 5432) é exposta para o ambiente externo ou para o host físico, prevenindo varreduras de porta e ataques diretos.

* **Prevenção de Vazamento de Segredos (.gitignore):**
  Credenciais, logs sensíveis, dumps de banco de dados (*.sql, *.dump) e backups temporários estão explicitamente bloqueados de versionamento via Git.