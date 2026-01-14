import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Funções de Apoio ---
async def call_api(method: str, endpoint: str, params=None, json_data=None):
    async with httpx.AsyncClient() as client:
        url = f"{API_URL}{endpoint}"
        if method == "GET":
            return await client.get(url, params=params)
        elif method == "POST":
            return await client.post(url, json=json_data)
        elif method == "DELETE":
            return await client.delete(url, params=params)

# --- Handlers de Transações ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📊 *MyFinance BOT Ativo!*\n\n"
        " *Registrar:*\n"
        "'+100 salario, renda' ou `-50 pizza, lazer`\n"
        " *Consultas:* /resumo, /buscar <termo>, /categorias\n"
        " *Gerenciar:* /desfazer, /addcategoria <nome>, /rmvcategoria <nome>"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith(("+", "-")):
        payload = {"telegram_id": update.effective_user.id, "message": text}
        response = await call_api("POST", "/transactions/", json_data=payload)
        
        if response.status_code == 200:
            res = response.json()
            await update.message.reply_text(f"✅ Registrado: *{res['description']}*\n💰 Valor: R$ {res['amount']:.2f}", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Formato inválido! Use: `+/-valor descrição, categoria`", parse_mode="Markdown")

async def desfazer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    response = await call_api("DELETE", "/transactions/last", params={"telegram_id": user_id})
    
    if response.status_code == 200:
        data = response.json()
        tx = data['deleted_transaction']
        await update.message.reply_text(f"🗑 *Desfeito:* {tx['description']} (R$ {tx['amount']})", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Nenhuma transação encontrada para desfazer.")

# --- Handlers de Consulta ---

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    period = context.args[0] if context.args else "monthly"
    
    response = await call_api("GET", "/summary/", params={"telegram_id": user_id, "period": period})
    
    if response.status_code == 200:
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
    else:
        await update.message.reply_text("❌ Erro ao buscar resumo.")

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: `/buscar <descrição>`", parse_mode="Markdown")
        return

    user_id = update.effective_user.id
    query = " ".join(context.args)
    response = await call_api("GET", "/search/", params={"telegram_id": user_id, "description": query})

    if response.status_code == 200:
        data = response.json()
        if not data:
            await update.message.reply_text("🔎 Nenhuma transação encontrada.")
            return
        
        texto = f"🔍 *Resultados para '{query}':*\n\n"
        for item in data[:10]: # Limita aos 10 últimos
            emoji = "🟢" if item['type'] == 'income' else "🔴"
            texto += f"{emoji} {item['transaction_date']}: {item['description']} - *R$ {item['amount']}*\n"
        
        await update.message.reply_markdown(texto)

# --- Handlers de Categorias ---

async def listar_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    response = await call_api("GET", "/categories/", params={"telegram_id": user_id})
    
    if response.status_code == 200:
        cats = response.json()
        texto = "📂 *Suas Categorias:*\n" + "\n".join([f"• {c}" for c in cats])
        await update.message.reply_markdown(texto)

async def add_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: `/addcategoria <nome>`")
        return
    
    user_id = update.effective_user.id
    cat_name = context.args[0]
    response = await call_api("POST", "/categories/add", params={"telegram_id": user_id, "name": cat_name})
    
    if response.status_code == 200:
        await update.message.reply_text(f"✅ Categoria *{cat_name}* adicionada!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Erro: Categoria já existe ou falha na API.")

async def rmv_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: `/rmvcategoria <nome>`")
        return
    
    user_id = update.effective_user.id
    cat_name = context.args[0]
    response = await call_api("DELETE", "/categories/remove", params={"telegram_id": user_id, "name": cat_name})
    
    if response.status_code == 200:
        await update.message.reply_text(f"🗑 Categoria *{cat_name}* removida!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Categoria não encontrada.")

# --- Execução ---

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Registro de Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resumo", resumo))
    app.add_handler(CommandHandler("desfazer", desfazer))
    app.add_handler(CommandHandler("buscar", buscar))
    app.add_handler(CommandHandler("categorias", listar_categorias))
    app.add_handler(CommandHandler("addcategoria", add_categoria))
    app.add_handler(CommandHandler("rmvcategoria", rmv_categoria))
    
    # Registro de Mensagem de Texto (+/-)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction))
    
    print("🚀 Bot Financeiro rodando com todas as funções!")
    app.run_polling()