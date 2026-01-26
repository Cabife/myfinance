# 📊 MyFinance – API & Bot de Controle Financeiro

O **MyFinance** é um projeto completo de controle financeiro pessoal composto por **duas aplicações**:

* **MyFinance-API** → uma API REST desenvolvida em **FastAPI** responsável por toda a lógica de negócio, acesso ao banco de dados, geração de relatórios, gráficos e estatísticas.
* **MyFinance-BOT** → um **bot do Telegram** que consome a API e permite ao usuário gerenciar suas finanças diretamente pelo chat.

O objetivo do projeto é oferecer uma solução simples, extensível e automatizada para **controle de receitas, despesas, categorias, metas e relatórios em PDF**.

---

## 🧱 Arquitetura do Projeto

O projeto é dividido em dois repositórios/pastas principais:

```
MyFinance-API/
MyFinance-BOT/
```

Cada parte tem responsabilidades bem definidas, seguindo boas práticas de separação de responsabilidades.

---

## 🚀 MyFinance-API

API responsável por:

* Gerenciar transações financeiras
* Categorias
* Metas
* Resumos financeiros
* Gráficos
* Relatórios em PDF
* Comunicação com o banco de dados

### 📂 Estrutura de Pastas

```
MyFinance-API
├── app
│   ├── core
│   │   ├── config.py        # Configurações do projeto (.env)
│   │   └── database.py      # Conexão com o banco de dados
│   ├── routers
│   │   ├── categories.py    # Rotas de categorias
│   │   ├── charts.py        # Rotas de gráficos
│   │   ├── goals.py         # Rotas de metas
│   │   ├── health.py        # Health check da API
│   │   ├── reports.py       # Rotas de relatórios em PDF
│   │   ├── search.py        # Busca de transações
│   │   ├── summary.py       # Resumos financeiros
│   │   └── transactions.py # Transações financeiras
│   ├── services
│   │   ├── charts_service.py # Lógica de geração de gráficos
│   │   └── pdf_service.py    # Geração de relatórios em PDF
│   ├── main.py               # Inicialização da aplicação
│   └── __init__.py
├── .env                      # Variáveis de ambiente (NÃO versionar)
├── requirements.txt          # Dependências do projeto
└── README.md
```

---

### 🛠️ Tecnologias Utilizadas (API)

* **Python 3.10+**
* **FastAPI** – Framework web
* **Uvicorn** – Servidor ASGI
* **SQLAlchemy** – ORM
* **Supabase / PostgreSQL** – Banco de dados
* **ReportLab** – Geração de PDFs
* **Matplotlib** – Geração de gráficos
* **Python-dotenv** – Gerenciamento de variáveis de ambiente

---

### 🔐 Variáveis de Ambiente (.env)

⚠️ **Nunca suba suas chaves para o GitHub**.

Exemplo de `.env`:

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/banco
API_TOKEN=sua_chave_de_api
```

Cada pessoa que for rodar o projeto deve **configurar seu próprio banco de dados**.

---

### ▶️ Como Rodar a API

```bash
# criar ambiente virtual
python -m venv venv

# ativar (Windows)
venv\Scripts\activate

# instalar dependências
pip install -r requirements.txt

# rodar a aplicação
uvicorn app.main:app --reload
```

A API ficará disponível em:

```
http://localhost:8000
```

Documentação automática:

```
http://localhost:8000/docs
```

---

## 🤖 MyFinance-BOT

Bot do Telegram que permite:

* Registrar receitas e despesas
* Consultar saldo
* Gerar relatórios
* Visualizar resumos
* Interagir com a API de forma simples

### 📂 Estrutura

```
MyFinance-BOT
├── bot.py            # Código principal do bot
├── .env              # Token do bot e URL da API
├── requirements.txt  # Dependências
└── README.md
```

---

### 🛠️ Tecnologias Utilizadas (Bot)

* **Python**
* **python-telegram-bot**
* **Requests / HTTPX** – Comunicação com a API
* **Python-dotenv**

---

### 🔐 Variáveis de Ambiente do Bot

Exemplo de `.env`:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
API_BASE_URL=http://localhost:8000
```

⚠️ **Você precisa criar seu próprio bot no BotFather** para obter o token.

---

### ▶️ Como Rodar o Bot

```bash
# criar ambiente virtual
python -m venv venv

# ativar
venv\Scripts\activate

# instalar dependências
pip install -r requirements.txt

# iniciar o bot
python bot.py
```

---

## 📄 Relatórios em PDF

O sistema gera automaticamente:

* 📅 Relatório mensal
* 📆 Relatório anual
* 🗂️ Relatório por categorias

Os PDFs são gerados dinamicamente pela API usando **ReportLab** e gráficos gerados via **Matplotlib**.

---

## 📊 Gráficos

Os gráficos são processados no backend e utilizados:

* Nos relatórios em PDF
* Em endpoints específicos para visualização futura

---

## 🧪 Testes e Debug

* Endpoint de health check: `/health`
* Endpoint de teste de banco: `db_test.py`
* Tratamento de erros com `try/except` e `HTTPException`

---

## 📌 Observações Importantes

* Este projeto **não inclui chaves de banco ou token de bot**.
* Cada usuário deve:

  * Criar seu banco de dados
  * Configurar o `.env`
  * Criar seu próprio bot no Telegram
* O projeto foi estruturado para facilitar manutenção e expansão.

---

## 🧠 Próximos Passos (Ideias)

* Dashboard web
* Autenticação JWT
* Exportação para Excel
* Notificações automáticas
* IA para análise financeira

---

## 📄 Licença

Projeto desenvolvido para fins educacionais e uso pessoal.

Sinta-se livre para estudar, adaptar e evoluir 🚀
