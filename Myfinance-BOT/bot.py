import os
import logging
import tempfile
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ========================
# CONFIGURAÇÃO
# ========================

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ========================
# FUNÇÃO AUXILIAR API
# ========================

async def call_api(method: str, endpoint: str, params=None, json_data=None):
    async with httpx.AsyncClient(timeout=60) as client:
        url = f"{API_URL}{endpoint}"

        if method == "GET":
            return await client.get(url, params=params)

        if method == "POST":
            return await client.post(url, json=json_data, params=params)

        if method == "DELETE":
            return await client.delete(url, params=params)

# ========================
# START
# ========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📊 *MyFinance BOT Ativo!*\n\n"
        "*Registrar transações:*\n"
        "`+100 salario, renda`\n"
        "`-50 pizza, lazer`\n\n"
        "*Consultas:*\n"
        "/resumo [monthly|annual]\n"
        "/buscar <termo>\n"
        "/categorias\n\n"
        "*Relatórios (PDF):*\n"
        "/relatorio mensal\n"
        "/relatorio anual\n"
        "/relatorio categorias\n\n"
        "*Gerenciar:*\n"
        "/desfazer\n"
        "/addcategoria <nome>\n"
        "/rmvcategoria <nome>"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ========================
# TRANSAÇÕES
# ========================

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.startswith(("+", "-")):
        return

    payload = {
        "telegram_id": update.effective_user.id,
        "message": text
    }

    response = await call_api("POST", "/transactions/", json_data=payload)

    if response.status_code == 200:
        res = response.json()
        await update.message.reply_text(
            f"✅ *Registrado com sucesso!*\n"
            f"📝 {res['description']}\n"
            f"💰 R$ {res['amount']:.2f}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ Formato inválido!\n"
            "Use: `+/-valor descrição, categoria`",
            parse_mode="Markdown"
        )

async def desfazer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    response = await call_api(
        "DELETE",
        "/transactions/last",
        params={"telegram_id": user_id}
    )

    if response.status_code == 200:
        tx = response.json()["deleted_transaction"]
        await update.message.reply_text(
            f"🗑 *Transação desfeita:*\n"
            f"{tx['description']} - R$ {tx['amount']}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("⚠️ Nenhuma transação encontrada.")

# ========================
# CONSULTAS
# ========================

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    period = context.args[0] if context.args else "monthly"

    response = await call_api(
        "GET",
        "/summary/",
        params={"telegram_id": user_id, "period": period}
    )

    if response.status_code != 200:
        await update.message.reply_text("❌ Erro ao buscar resumo.")
        return

    d = response.json()
    msg = (
        f"💰 *Resumo {period.capitalize()}*\n"
        f"──────────────────\n"
        f"🟢 Receitas: R$ {d['incomes']:.2f}\n"
        f"🔴 Despesas: R$ {d['expenses']:.2f}\n"
        f"──────────────────\n"
        f"⚖️ Saldo: *R$ {d['balance']:.2f}*"
    )

    await update.message.reply_markdown(msg)

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: `/buscar <descrição>`", parse_mode="Markdown")
        return

    user_id = update.effective_user.id
    query = " ".join(context.args)

    response = await call_api(
        "GET",
        "/search/",
        params={"telegram_id": user_id, "description": query}
    )

    if response.status_code != 200:
        await update.message.reply_text("❌ Erro na busca.")
        return

    data = response.json()

    if not data:
        await update.message.reply_text("🔎 Nenhuma transação encontrada.")
        return

    texto = f"🔍 *Resultados para '{query}':*\n\n"

    for item in data[:10]:
        emoji = "🟢" if item["type"] == "income" else "🔴"
        texto += f"{emoji} {item['transaction_date']} - {item['description']} • R$ {item['amount']}\n"

    await update.message.reply_markdown(texto)

# ========================
# CATEGORIAS
# ========================

async def listar_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    response = await call_api(
        "GET",
        "/categories/",
        params={"telegram_id": user_id}
    )

    if response.status_code != 200:
        await update.message.reply_text("❌ Erro ao listar categorias.")
        return

    cats = response.json()
    texto = "📂 *Suas Categorias:*\n" + "\n".join(f"• {c}" for c in cats)
    await update.message.reply_markdown(texto)

async def add_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: `/addcategoria <nome>`")
        return

    user_id = update.effective_user.id
    name = context.args[0]

    response = await call_api(
        "POST",
        "/categories/add",
        params={"telegram_id": user_id, "name": name}
    )

    if response.status_code == 200:
        await update.message.reply_text(f"✅ Categoria *{name}* adicionada!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Categoria já existe ou erro.")

async def rmv_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: `/rmvcategoria <nome>`")
        return

    user_id = update.effective_user.id
    name = context.args[0]

    response = await call_api(
        "DELETE",
        "/categories/remove",
        params={"telegram_id": user_id, "name": name}
    )

    if response.status_code == 200:
        await update.message.reply_text(f"🗑 Categoria *{name}* removida!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Categoria não encontrada.")

# ========================
# RELATÓRIOS PDF 
# ========================

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📄 Use:\n"
            "/relatorio mensal\n"
            "/relatorio anual\n"
            "/relatorio categorias"
        )
        return

    tipo = context.args[0].lower()
    user_id = update.effective_user.id

    
    endpoints = {
        "mensal": "/reports/monthly",
        "anual": "/reports/annual",
        "categorias": "/reports/categories"
    }

    if tipo not in endpoints:
        await update.message.reply_text("❌ Tipo inválido. Use: mensal, anual ou categorias.")
        return

    await update.message.reply_text("⏳ Gerando relatório... Isso pode levar alguns segundos.")

    try:
        #  Enviando o telegram_id como query parameter
        response = await call_api(
            "GET", 
            endpoints[tipo], 
            params={"telegram_id": user_id}
        )

        if response.status_code == 200:
            # Usando contexto para garantir que o arquivo seja fechado
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

            # Envia o documento
            with open(tmp_path, "rb") as pdf:
                await update.message.reply_document(
                    document=pdf,
                    filename=f"relatorio_{tipo}.pdf",
                    caption=f"📊 Aqui está seu relatório {tipo}!"
                )
            
            # Limpeza opcional do arquivo temporário local
            os.remove(tmp_path)
        
        elif response.status_code == 404:
            await update.message.reply_text("❌ Erro: Rota não encontrada na API (404).")
        else:
            await update.message.reply_text(f"❌ Erro na API (Status {response.status_code}).")

    except Exception as e:
        logging.error(f"Erro ao gerar PDF: {e}")
        await update.message.reply_text("❌ Ocorreu um erro interno ao processar o PDF.")

# ========================
# EXECUÇÃO
# ========================

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resumo", resumo))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(CommandHandler("desfazer", desfazer))
    app.add_handler(CommandHandler("buscar", buscar))
    app.add_handler(CommandHandler("categorias", listar_categorias))
    app.add_handler(CommandHandler("addcategoria", add_categoria))
    app.add_handler(CommandHandler("rmvcategoria", rmv_categoria))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction))

    print("🚀 Bot Financeiro rodando com sucesso!")
    app.run_polling()
