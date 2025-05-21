from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import asyncio
import os
import json
from pathlib import Path

# Dados de autenticação do Telegram
api_id = 21605802
api_hash = "dd73ec1fe415b7eaff759ede430fdaa8"
bot_token = "7172455057:AAHkuDX_i0htXiKmoP_SZNm_JMuXjq9U8PI"

# Inicializa o bot
app = Client("botmary", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Links de imagens
avaliacao_image = "https://i.imgur.com/a/3JSq0hu.jpg"
pack_images = {
    "curiosinho": "https://imgur.com/a/qkybFFU.jpg",  # Bronze -> Curiosinho
    "essencia": "https://imgur.com/4kGemfd.jpg",     # Prata -> Essência
    "luxuoso": "https://imgur.com/tk3524S.jpg",      # Ouro -> Luxuoso
    "intimo": "https://imgur.com/a/I3nazm5.jpg",       # Diamante -> Íntimo
}
tabela_precos_image = "https://imgur.com/a/HBLygil.jpg"

# Links de pagamento
pagamento_links = {
    "curiosinho": "https://pay.cakto.com.br/y5vox4y",    # Bronze
    "essencia": "https://pay.cakto.com.br/fjb4tr4",      # Prata
    "luxuoso": "https://pay.cakto.com.br/5aa6uss",       # Ouro
    "intimo": "https://pay.cakto.com.br/3c4as48",        # Diamante
    "avaliacao_pica": "https://pay.cakto.com.br/hyxohkw"
}

# Mapeamento de nomes
nomes_pacotes = {
    "curiosinho": "Curiosinho",
    "essencia": "Essência",
    "luxuoso": "Luxuoso",
    "intimo": "Íntimo"
}

# Variáveis para controlar mensagens e bloqueios
last_bot_message_id = {}
last_bot_image_message_id = {}
user_lock = {}

# Variáveis para rastreamento de usuários
user_ids = set()  # Armazena todos os IDs
user_join_dates = {}  # Dicionário: {user_id: datetime}

# Arquivo para salvar os dados
DATA_FILE = "user_data.json"

# ID do administrador
ADMIN_ID = 7497831123

def save_user_data():
    """Salva user_ids e user_join_dates em um arquivo JSON."""
    data = {
        "user_ids": list(user_ids),
        "user_join_dates": {str(k): v.isoformat() for k, v in user_join_dates.items()}
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_user_data():
    """Carrega os dados do arquivo JSON (se existir)."""
    if not Path(DATA_FILE).exists():
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        user_ids.update(set(data["user_ids"]))
        user_join_dates.update({
            int(k): datetime.fromisoformat(v) for k, v in data["user_join_dates"].items()
        })

# Carrega os dados ao iniciar o bot
load_user_data()

# Função para apagar mensagens anteriores
async def delete_previous_message(chat_id, client):
    if chat_id in last_bot_message_id:
        try:
            await client.delete_messages(chat_id, [last_bot_message_id[chat_id]])
        except Exception as e:
            print(f"Erro ao apagar mensagem anterior: {e}")
    if chat_id in last_bot_image_message_id:
        try:
            await client.delete_messages(chat_id, [last_bot_image_message_id[chat_id]])
        except Exception as e:
            print(f"Erro ao apagar imagem anterior: {e}")

# Mensagem inicial
@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    user_id = message.chat.id
    if user_id not in user_ids:
        user_ids.add(user_id)
        user_join_dates[user_id] = datetime.now()
        save_user_data()

    file_id = "CgACAgEAAxkBAAICkGc6E5TRIVKa4wwUBzKagpfQBqFTAALfBAACH0HRReKbif4M5CE6NgQ"

    msg = await message.reply_animation(
        animation=file_id,
        caption="Eae, taradão. Sou a botmary😈 \n\nTô aqui pra te deixar duro. \nEscolhe aí embaixo e não enrola, senão teu pau esfria...\n\nEscolha uma das opções abaixo, gostoso👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🤫Tabela do Prazer🔥", callback_data="tabela_precos")],
            [InlineKeyboardButton("⁉️Dúvidas Frequentes. LEIA❗", callback_data="duvidas_frequentes")]
        ])
    )
    last_bot_message_id[message.chat.id] = msg.id

# Callback geral
@app.on_callback_query()
async def callback_handler(client, callback_query):
    chat_id = callback_query.message.chat.id

    if user_lock.get(chat_id, False):
        await callback_query.answer()
        return

    user_lock[chat_id] = True
    await callback_query.answer()
    data = callback_query.data

    try:
        await delete_previous_message(chat_id, client)

        if data == "tabela_precos":
            msg = await callback_query.message.reply_photo(
                photo=tabela_precos_image,
                caption="Aqui a tabela, escolha com carinho🥺",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Íntimo - R$ 96👄", callback_data="pack_intimo")],
                    [InlineKeyboardButton("Luxuoso - R$ 50 ❤️‍🔥", callback_data="pack_luxuoso")],
                    [InlineKeyboardButton("Essência - R$ 36 🤤", callback_data="pack_essencia")],
                    [InlineKeyboardButton("Curiosinho - R$ 20 👀", callback_data="pack_curiosinho")],
                    [InlineKeyboardButton("Avaliação - R$ 19 🍆", callback_data="avaliacao_pica")],
                    [InlineKeyboardButton("VOLTAR ◀️", callback_data="voltar_menu")]
                ])
            )
            last_bot_message_id[chat_id] = msg.id

        elif data in ["pack_intimo", "pack_luxuoso", "pack_essencia", "pack_curiosinho"]:
            pacote_tipo = data.split("_")[1]  # Pega o tipo do pacote
            pacote_nome = nomes_pacotes[pacote_tipo]
            imagem = pack_images[pacote_tipo]
            link_pagamento = pagamento_links[pacote_tipo]

            mensagem = (
                f"Hmmm... Então você gosta de uma provocaçãozinha né safado? O {pacote_nome} tá aqui te esperando🥵\n\n"
                f"Link de pagamento:\n👉 {link_pagamento} 👈\n\n"
                "Quer pix direto, ou não consegue acesso ao conteúdo? Me mande uma mensagem no zap que respondo ligeirinho😋\n\n"
                "Seja direto, diga sua dúvida para resolver rapidamente.\n"
                "💕 WhatsApp: wa.me/82999872865 💕\n\n"
            )

            msg = await callback_query.message.reply_photo(
                photo=imagem,
                caption=mensagem,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("VOLTAR ◀️", callback_data="voltar_menu")]
                ])
            )
            last_bot_message_id[chat_id] = msg.id

        elif data == "duvidas_frequentes":
            msg = await callback_query.message.reply(
                "PERGUNTAS❤️\n"
                "RESPOSTAS💙\n\n"
                "❤️- Faz programa / atende presencial?\n💙- Não, amor. Só vendo conteúdo. Meu prazer é virtual e exclusivo pra quem merece.\n\n"
                "❤️- Não consigo/quero pagar pelo link\n💙- Me chama no WhatsApp que te mando a chave Pix direto… jeitinho mais íntimo.\n\n"
                "❤️- Tem interação ao vivo? Por exemplo, vídeo chamada?\n💙- Ainda não… mas tô preparando algo bem quente pra quando isso acontecer.\n\n"
                "❤️- Formas de pagamento aceitas?\n💙- Só Pix por enquanto. Simples, rápido e seguro.\n\n"
                "❤️- É seguro pagar por ali?\n💙- Super. Ninguém vai saber de nada, é só entre a gente.\n\n"
                "❤️- O que tem nos pacotes?\n💙- Vídeos meus me explorando, provocando e te deixando maluco. No 'Íntimo' a coisa pega fogo de verdade.\n\n"
                "❤️- Aceita pedidos personalizados?\n💙- Por enquanto não… mas quem sabe mais pra frente, se você for um bom menino.\n\n"
                "❤️- Como é a entrega de conteúdo?\n💙- No seu e-mail vem tudo certinho, com link pro Drive. Se tiver dificuldade, só me chamar.\n\n"
                "❤️- Isso é uma assinatura?\n💙- Nada disso. Você compra só o que quiser, quando quiser. Sem enrolação.\n\n"
                "❤️- Tem grupo VIP?\n💙- Ainda não, mas vem aí… e quem for esperto já garante o lugar comigo desde agora.\n\n"
                "❤️- Minha mulher irá saber que estou pagando por isso?\n💙- Claro que não. É tudo discreto. O segredo mais gostoso que você vai guardar.\n\n"
                "❤️- Posso te mandar uma mensagem no WhatsApp para conversar?\n💙- Só dou atenção VIP pra quem investe em mim. Comprou, aí sim a gente conversa à vontade.\n\n"
                "❤️- Se eu não gostar do conteúdo, o que faço?\n💙- Me fala. Tô aprendendo e melhorando sempre. Quem sabe você me ensina do seu jeitinho…\n\n",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("VOLTAR ◀️", callback_data="voltar_menu")]
                ])
            )
            last_bot_message_id[chat_id] = msg.id

        elif data == "avaliacao_pica":
            msg1 = await callback_query.message.reply_photo(
                photo=avaliacao_image,
                caption="Só de pensar na tua pica já fico molhadinha assim oh👆😳"
            )
            last_bot_image_message_id[chat_id] = msg1.id

            msg2 = await callback_query.message.reply(
                f"Você escolheu **Avaliação Pica**, isso é pros macho que nao tem medo de mostrar o brinquedo 😈\n\n"
                f"Link de pagamento:\n👉 {pagamento_links['avaliacao_pica']} 👈\n\n"
                "Não sabe pagar ou prefere pix direto? Chama no zap que te passo a chave pix rapidinho!😘\n\n"
                "Depois do pagamento ja manda o comprovante pedindo a avaliação mais gostosa da tua vida 💦\n"
                "💕 WhatsApp: wa.me/82999872865 💕\n\n",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("VOLTAR ◀️", callback_data="voltar_menu")]
                ])
            )
            last_bot_message_id[chat_id] = msg2.id

        elif data in ["pack_bronze", "pack_prata", "pack_ouro", "pack_diamante"]:
            pacote_nome = data.replace("_", " ").title()
            imagem = pack_images[data.split("_")[1]]
            link_pagamento = pagamento_links[data.split("_")[1]]
            mensagem = (
                f"hmmm... Então você gosta de uma provocaçãozinha ne safado o {pacote_nome}Ta aqui te esperando🥵\n\n"
                f"Link de pagamento:\n👉 {link_pagamento} 👈\n\n"
                "Quer pix direto, ou não consegue acesso ao conteúdo, me mande uma mensagem no zap que respondo ligeirinho😋\n\n"
                "Seja direto, diga sua dúvida para resolver rapidamente.\n"
                "💕 WhatsApp: wa.me/82999872865 💕\n\n"
            )

            msg = await callback_query.message.reply_photo(
                photo=imagem,
                caption=mensagem,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("VOLTAR ◀️", callback_data="voltar_menu")]
                ])
            )
            last_bot_message_id[chat_id] = msg.id

        elif data == "voltar_menu":
            await delete_previous_message(chat_id, client)
            await start(client, callback_query.message)

    except Exception as e:
        print(f"Erro no callback: {e}")

    user_lock[chat_id] = False

@app.on_message(filters.command("💕") & filters.private)
async def broadcast(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ **Acesso negado!** Apenas o admin pode usar este comando.")
        return

    if not (message.text or message.photo or message.video or message.document):
        await message.reply(
            "⚠️ **Formato incorreto!**\n\n"
            "🔹 **Para texto:** `/💕 sua_mensagem`\n"
            "🔹 **Para mídia:** Envie uma foto/vídeo com legenda (opcional)\n\n"
            "Exemplo:\n`/💕 Olá, novos packs disponíveis! 🔥`"
        )
        return

    broadcast_text = ""
    if message.text:
        broadcast_text = message.text.split("/💕", 1)[-1].strip()
    elif message.caption:
        broadcast_text = message.caption

    media = None
    if message.photo:
        media = ("photo", message.photo.file_id)
    elif message.video:
        media = ("video", message.video.file_id)

    if not broadcast_text.strip() and not media:
        await message.reply("❌ **Erro:** A mensagem está vazia!")
        return

    success = 0
    fails = 0
    for user_id in user_ids:
        try:
            if media:
                if media[0] == "photo":
                    await client.send_photo(
                        user_id,
                        photo=media[1],
                        caption=broadcast_text if broadcast_text else None
                    )
                else:
                    await client.send_video(
                        user_id,
                        video=media[1],
                        caption=broadcast_text if broadcast_text else None
                    )
            else:
                await client.send_message(user_id, broadcast_text)

            success += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Erro ao enviar para {user_id}: {e}")
            fails += 1

    await message.reply(
        f"📢 **Broadcast concluído!**\n\n"
        f"✅ **Enviados:** {success}\n"
        f"❌ **Falhas:** {fails}\n\n"
        f"🔹 **Mensagem:**\n{broadcast_text if broadcast_text else '(Mídia sem legenda)'}"
    )

@app.on_message(filters.command("users") & filters.private)
async def cmd_users(client, message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Apenas o admin pode usar este comando.")
        return

    hoje = datetime.now()
    contagens = {
        "hoje": 0,
        "ontem": 0,
        "7_dias": 0,
        "total": len(user_ids)
    }

    for user_id, join_date in user_join_dates.items():
        delta = hoje - join_date
        if delta.days == 0:
            contagens["hoje"] += 1
        elif delta.days == 1:
            contagens["ontem"] += 1
        if delta.days <= 7:
            contagens["7_dias"] += 1

    resposta = (
        "📊 **Estatísticas de Usuários**\n\n"
        f"👥 **Total:** `{contagens['total']}`\n"
        f"🟢 **Hoje:** `{contagens['hoje']}`\n"
        f"🟡 **Ontem:** `{contagens['ontem']}`\n"
        f"🔵 **Últimos 7 dias:** `{contagens['7_dias']}`"
    )
    await message.reply(resposta)

# Inicialização do bot
print("✅ Bot Mary ta ligado, Xico!")
import atexit
atexit.register(save_user_data)
app.run()
