# 🏎️ F1 Analytics Secure Lab

Laboratório de engenharia de dados e IA sobre Fórmula 1. Coleta telemetria oficial
via **FastF1**, armazena em **PostgreSQL** isolado e disponibiliza um chat analítico
em **Streamlit** com respostas geradas pela **API da Groq**.

O assistente responde exclusivamente sobre Fórmula 1 e baseia as análises nos dados
carregados no banco.

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Interface | Streamlit 1.60 |
| Banco | PostgreSQL 16 (rede interna, sem porta exposta) |
| Dados | FastF1 3.8 |
| IA | Groq API (`llama-3.3-70b-versatile`) |
| Runtime | Docker + Docker Compose |

---

## 📋 Pré-requisitos

- **Docker Engine 20.10+** com o plugin **Compose v2** (`docker compose`, sem hífen)
- **4 GB de RAM** livres e ~3 GB de disco
- **Conta gratuita na Groq** para a chave de API (veja a seção abaixo)
- **Acesso à internet** no host — o FastF1 baixa os dados direto da F1

Verifique o ambiente:

```bash
docker --version && docker compose version
```

---

## 🔑 Chave da API Groq (gratuita)

A geração das respostas usa a API da Groq. A conta é gratuita e **não pede cartão
de crédito**.

1. Acesse **https://console.groq.com**
2. Crie a conta com e-mail, Google ou GitHub
3. No menu lateral, clique em **API Keys**
4. Clique em **Create API Key** e dê um nome (ex.: `f1-analytics`)
5. **Copie a chave imediatamente** — ela começa com `gsk_` e só é exibida uma vez
6. Cole no arquivo `.env`, no campo `GROQ_API_KEY`

Se perder a chave, não há como recuperá-la: apague a antiga no console e gere outra.

### Limites do plano gratuito

Os limites são por requisições e por tokens, aplicados **por organização** — criar
várias chaves não aumenta a cota. Para o modelo padrão do projeto, a ordem de
grandeza é de dezenas de requisições por minuto, suficiente para uso pessoal.

Os valores mudam com o tempo. Consulte os limites vigentes da sua conta em
**Settings → Limits**, no console da Groq.

Ao estourar o limite, a API responde com HTTP 429 e a aplicação mostra uma mensagem
genérica de falha. O motivo real aparece no log:

```bash
docker compose logs app | tail -20
```

### Trocar de modelo

Qualquer modelo disponível na sua conta funciona. Basta ajustar o `.env`:

Modelo utilizado GROQ_MODEL=llama-3.3-70b-versatile

Modelos menores respondem mais rápido e consomem menos cota, com respostas menos
elaboradas. A lista atual fica em **Models**, no console.

> A chave dá acesso à sua cota. Nunca a coloque em commit, print ou issue.
> Se vazar, revogue no console e gere outra — é gratuito e leva segundos.

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/Snake-arch57/F1-Analytics-Secure-Lab.git
cd F1-Analytics-Secure-Lab
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

**Edite o `.env` antes de continuar.** Copiar o exemplo não basta: ele contém
valores de placeholder que fazem a aplicação falhar.

```bash
nano .env
```

Preencha obrigatoriamente:

| Variável | O que colocar |
|---|---|
| `GROQ_API_KEY` | Sua chave da Groq (começa com `gsk_`) |
| `POSTGRES_PASSWORD` | Uma senha forte que você escolher |
| `APP_PORT` | Porta de acesso (padrão `8501`) |
| `GROQ_MODEL` | Modelo da Groq (padrão `llama-3.3-70b-versatile`) |

Para gerar uma senha aleatória:

```bash
openssl rand -base64 24
```

> O `.env` está no `.gitignore` e nunca deve ser versionado.

### 3. Suba os containers

```bash
docker compose up -d --build
```

A primeira construção leva alguns minutos. Confira se os dois serviços subiram:

```bash
docker compose ps
```

Espere ver `app` e `postgres` com status `Up`, o postgres marcado como `healthy`.

### 4. Crie o schema analítico

O container do Postgres executa o `database/init.sql` automaticamente na primeira
subida. Os demais objetos precisam ser aplicados manualmente:

```bash
docker compose exec -T postgres psql -U f1_app -d f1_analytics < database/f1_schema.sql
docker compose exec -T postgres psql -U f1_app -d f1_analytics < database/ai_context_view.sql
```

Confirme:

```bash
docker compose exec postgres psql -U f1_app -d f1_analytics -c "\dt" -c "\dv"
```

### 5. Carregue os dados da F1

Sem esta etapa o chat funciona, mas responde que não possui dados.

```bash
# uma temporada
docker compose exec app python load_seasons.py 2024

# várias
docker compose exec app python load_seasons.py 2024 2025 2026
```

A primeira carga é demorada: o FastF1 baixa cada Grande Prêmio da API oficial.
Os downloads ficam em cache no volume `fastf1_cache`, então cargas seguintes
são rápidas.

Opções via variável de ambiente:

```bash
# testar com apenas 2 corridas
docker compose exec -e LIMIT_EVENTS=2 app python load_seasons.py 2024

# incluir classificação e treinos além da corrida
docker compose exec -e SESSION_TYPES=R,Q,FP1 app python load_seasons.py 2024
```

Corridas que ainda não aconteceram são puladas automaticamente.

### 6. Acesse
http://localhost:8501

Em servidor remoto, troque `localhost` pelo IP da máquina.

---

## 💬 Uso

| Ação | Como |
|---|---|
| Perguntar | Digite na caixa inferior e pressione Enter |
| Nova conversa | Botão **➕ Nova Conversa** no menu lateral |
| Retomar conversa | Clique no título no histórico |
| Apagar conversa | Ícone 🗑️ ao lado do título, depois confirme |
| Trocar tema | Menu **⋮** no canto superior direito |

As conversas ficam salvas no PostgreSQL e sobrevivem a reinícios do container.

---

## ⚙️ Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_NAME` | `f1-analytics-secure-lab` | Identificação da aplicação |
| `APP_ENV` | `development` | Ambiente de execução |
| `APP_PORT` | `8501` | Porta publicada no host |
| `POSTGRES_DB` | `f1_analytics` | Nome do banco |
| `POSTGRES_USER` | `f1_app` | Usuário do banco |
| `POSTGRES_PASSWORD` | — | **Obrigatório.** Senha do banco |
| `GROQ_API_KEY` | — | **Obrigatório.** Chave da API Groq |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Modelo usado nas respostas |

---

## 🗂️ Estrutura

├── app.py # aplicação Streamlit (entrypoint)
├── chat_controller.py # persistência do chat e integração com a IA
├── chat_view.py # renderização das mensagens
├── sidebar.py # histórico e ações de conversa
├── callbacks.py # handlers de interação
├── state.py # estado da sessão
├── load_seasons.py # carga de dados via FastF1
├── database/
│ ├── init.sql # executado na primeira subida do Postgres
│ ├── f1_schema.sql # schema analítico
│ └── ai_context_view.sql # view de contexto da IA
├── app/services/ # camada de acesso a dados
├── assets/ # logo e estilos
└── docker-compose.yml

---

## 🩺 Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `port is already allocated` | Porta 8501 em uso | Troque `APP_PORT` no `.env` e suba de novo |
| "Não consegui gerar a resposta agora" | Chave Groq ausente, inválida ou sem cota | `docker compose logs app` mostra o erro real |
| IA diz que não tem dados | Banco vazio | Rode a etapa 5 (carga de dados) |
| Carga falha em uma corrida específica | Sessão indisponível no FastF1 | Normal; o script segue para a próxima |
| Postgres não fica `healthy` | Senha ausente no `.env` | Preencha `POSTGRES_PASSWORD` e recrie: `docker compose down -v && docker compose up -d` |
| Página não abre remotamente | Firewall bloqueando | `sudo firewall-cmd --add-port=8501/tcp --permanent && sudo firewall-cmd --reload` |
| Permissão negada nos volumes (RHEL/Rocky/Fedora) | SELinux | Adicione `:z` aos bind mounts no compose |

Logs em tempo real:

```bash
docker compose logs -f app
```

> `docker compose down -v` apaga o volume do banco, incluindo conversas e dados carregados.

---

## 🛡️ Postura de segurança

* **Execução não-root** — o container roda como `appuser`, usuário de sistema sem
  shell, reduzindo o impacto de um eventual container breakout.
* **Banco isolado** — o PostgreSQL vive na rede `backend` marcada como
  `internal: true` e não publica nenhuma porta. É inalcançável a partir do host
  ou da rede externa.
* **Segredos fora do versionamento** — `.env`, ambientes virtuais, caches e logs
  estão no `.gitignore`. Apenas o `.env.example`, sem valores reais, é publicado.
* **Consultas parametrizadas** — as operações do chat usam placeholders (`%s`) em
  vez de interpolação de strings.
* **Credenciais fora do contexto da IA** — chaves e senhas vivem apenas em
  variáveis de ambiente e nunca são enviadas ao modelo de linguagem.
* **Escopo restrito** — o prompt de sistema limita as respostas a Fórmula 1 e
  proíbe divulgação de detalhes de infraestrutura. Vale notar que isso é uma
  medida de produto, não uma fronteira de segurança.

---

## 📄 Licença e créditos

Projeto de estudo. Dados de telemetria via [FastF1](https://github.com/theOehrly/Fast-F1).
Interface construída com [Streamlit](https://streamlit.io).
Não afiliado à Formula One World Championship Limited.
