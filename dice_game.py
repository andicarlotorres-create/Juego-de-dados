import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import config

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados del juego
PLAYERS = {}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""
🎲 *Bienvenido {user.first_name}!* 🎲

*COMANDOS:*
/play - Jugar ahora 🎯
/stats - Mis estadísticas 📊
/ranking - Top 10 🏆
/rules - Reglas 📜
/help - Ayuda ❓

¡Usa /play para empezar a jugar! El bot tira su dado automáticamente.
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# Comando /play
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Inicializar si es nuevo
    if user_id not in PLAYERS:
        PLAYERS[user_id] = {"wins": 0, "losses": 0, "draws": 0, "score": 0.0, "name": user.first_name}
    
    keyboard = [
        [InlineKeyboardButton("🎯 TIRAR DADO", callback_data="roll")],
        [InlineKeyboardButton("📊 MIS ESTADÍSTICAS", callback_data="mystats")],
        [InlineKeyboardButton("🏆 RANKING", callback_data="showrank")]
    ]
    
    await update.message.reply_text(
        f"🎲 *¡Hola {user.first_name}!* 🎲\n\nPresiona 🎯 para tirar el dado y jugar contra el bot.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Comando /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id in PLAYERS:
        stats = PLAYERS[user_id]
        total = stats['wins'] + stats['losses'] + stats['draws']
        win_rate = (stats['wins'] / total * 100) if total > 0 else 0
        
        message = f"""
📊 *ESTADÍSTICAS DE {user.first_name}*

🏆 Victorias: {stats['wins']}
😢 Derrotas: {stats['losses']}
🤝 Empates: {stats['draws']}
🎯 Total jugadas: {total}
⭐ Puntuación: {stats['score']:.1f}
📈 % Victorias: {win_rate:.1f}%
"""
    else:
        message = "📊 Aún no has jugado. ¡Usa /play para empezar!"
    
    await update.message.reply_text(message, parse_mode='Markdown')

# Comando /ranking
async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PLAYERS:
        await update.message.reply_text("🏆 No hay jugadores aún. ¡Usa /play para ser el primero!")
        return
    
    sorted_players = sorted(PLAYERS.items(), key=lambda x: x[1]['score'], reverse=True)[:10]
    
    message = "🏆 *TOP 10 JUGADORES* 🏆\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, (pid, pstats) in enumerate(sorted_players):
        if i < 3:
            message += f"{medals[i]} *{pstats['name']}*\n"
        else:
            message += f"{medals[i]} {pstats['name']}\n"
        message += f"   ⭐ {pstats['score']:.1f} pts | 🏆{pstats['wins']} | 🎯{pstats['wins']+pstats['losses']+pstats['draws']}\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

# Comando /rules
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """
📜 *REGLAS DEL JUEGO*

1. 🎯 Tiras un dado (1-6)
2. 🤖 El bot tira su dado (1-6)
3. 🏆 Gana el número más alto
4. ⚖️ Empate si son iguales

*PUNTUACIÓN:*
✅ Victoria = +1 punto
❌ Derrota = 0 puntos
🤝 Empate = +0.5 puntos

¡Es así de simple! Usa /play para empezar.
"""
    await update.message.reply_text(message, parse_mode='Markdown')

# Comando /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """
❓ *AYUDA Y COMANDOS*

*COMANDOS DISPONIBLES:*
/start - Inicia el bot
/play - Jugar una partida
/stats - Ver tus estadísticas
/ranking - Ver top 10 jugadores
/rules - Ver reglas del juego
/help - Esta ayuda

*CÓMO JUGAR:*
1. Usa /play o el botón "🎯 TIRAR DADO"
2. El bot tira automáticamente
3. Compara resultados
4. ¡Gana puntos!

El bot funciona 24/7. ¡Diviértete! 🎲
"""
    await update.message.reply_text(message, parse_mode='Markdown')

# Handler de botones
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = user.id
    data = query.data
    
    if data == "roll":
        # Tirar dados
        user_dice = random.randint(1, 6)
        bot_dice = random.randint(1, 6)
        
        # Inicializar si es nuevo
        if user_id not in PLAYERS:
            PLAYERS[user_id] = {"wins": 0, "losses": 0, "draws": 0, "score": 0.0, "name": user.first_name}
        
        # Determinar resultado
        if user_dice > bot_dice:
            result = "🎉 *¡GANASTE!* 🎉"
            points = 1
            PLAYERS[user_id]["wins"] += 1
        elif user_dice < bot_dice:
            result = "😢 *Perdiste...*"
            points = 0
            PLAYERS[user_id]["losses"] += 1
        else:
            result = "🤝 *¡EMPATE!*"
            points = 0.5
            PLAYERS[user_id]["draws"] += 1
        
        PLAYERS[user_id]["score"] += points
        
        # Mensaje con resultados
        message = f"""
🎲 *RESULTADO* 🎲

🎯 Tu dado: *{user_dice}*
🤖 Bot dado: *{bot_dice}*

{result}
⭐ Puntos ganados: *{points}*

*Tu puntuación total: {PLAYERS[user_id]['score']:.1f}*
"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 TIRAR OTRA VEZ", callback_data="roll")],
            [InlineKeyboardButton("📊 VER MIS ESTADÍSTICAS", callback_data="mystats")],
            [InlineKeyboardButton("🏆 VER RANKING", callback_data="showrank")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "mystats":
        if user_id in PLAYERS:
            stats = PLAYERS[user_id]
            total = stats['wins'] + stats['losses'] + stats['draws']
            win_rate = (stats['wins'] / total * 100) if total > 0 else 0
            
            message = f"""
📊 *TUS ESTADÍSTICAS*

👤 Jugador: {user.first_name}
🏆 Victorias: {stats['wins']}
😢 Derrotas: {stats['losses']}
🤝 Empates: {stats['draws']}
🎯 Total: {total} partidas
⭐ Puntuación: {stats['score']:.1f}
📈 % Victorias: {win_rate:.1f}%
"""
        else:
            message = "📊 Aún no has jugado. ¡Presiona 🎯 para empezar!"
        
        keyboard = [
            [InlineKeyboardButton("🎯 JUGAR AHORA", callback_data="roll")],
            [InlineKeyboardButton("🏆 VER RANKING", callback_data="showrank")],
            [InlineKeyboardButton("🔙 VOLVER", callback_data="back")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "showrank":
        if not PLAYERS:
            message = "🏆 No hay jugadores aún. ¡Sé el primero en jugar!"
        else:
            sorted_players = sorted(PLAYERS.items(), key=lambda x: x[1]['score'], reverse=True)[:5]
            message = "🏆 *TOP 5 JUGADORES* 🏆\n\n"
            
            for i, (pid, pstats) in enumerate(sorted_players):
                medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                message += f"{medal} {pstats['name']}\n"
                message += f"   ⭐ {pstats['score']:.1f} pts | 🏆{pstats['wins']}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🎯 JUGAR YO", callback_data="roll")],
            [InlineKeyboardButton("📊 MIS ESTADÍSTICAS", callback_data="mystats")],
            [InlineKeyboardButton("🔙 VOLVER", callback_data="back")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("🎯 TIRAR DADO", callback_data="roll")],
            [InlineKeyboardButton("📊 MIS ESTADÍSTICAS", callback_data="mystats")],
            [InlineKeyboardButton("🏆 RANKING", callback_data="showrank")]
        ]
        
        await query.edit_message_text(
            f"🎲 *MENÚ PRINCIPAL* 🎲\n\n¡Hola {user.first_name}! Elige una opción:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# Función principal
def main():
    print("=" * 50)
    print("🎲 INICIANDO BOT DE DADOS DE TELEGRAM")
    print(f"🤖 Token: {config.BOT_TOKEN[:15]}...")
    print(f"👑 Admin ID: {config.ADMIN_ID}")
    print("=" * 50)
    
    # Crear aplicación
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("ranking", ranking))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("help", help_cmd))
    
    # Botones
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Iniciar
    print("✅ Bot listo. Presiona Ctrl+C para detener.")
    print("📱 Busca tu bot en Telegram y usa /start")
    app.run_polling()

if __name__ == "__main__":
    main()
