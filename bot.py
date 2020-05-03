from telegram.ext import Updater, CommandHandler

def start(update, context):
    """ Inicia la conversa. """
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hola! Sóc Scarlett el teu bot guia.")

def help(update, context):
    """ Ofereix ajuda sobre les comandes disponibles. """
    help_message = 'Tinc les funcions següents:\n'
    for key in COMMANDS.keys():
        help_message += '\n 🚩 ' '/' + key + ' ➡️ ' + COMMANDS[key]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_message)

def author(update, context):
    """ Mostra el nom dels autors del projecte. """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Els meus autors són:\n" +
        "    -Tomàs Gadea Alcaide🧑🏼‍💻\n" +
        "    -Pau Matas Albiol👨🏼‍💻")

def go(update, context):
    """ Comença a guiar l'usuari per arrivar de la seva posició actual fins al punt de destí escollit. Per exemple; /go Campus Nord. """
    
def where(update, context):
    """ Dóna la localització actual de l'usuari. """

def cancel(update, context):
    """ """

TOKEN = open('token.txt').read().strip()

COMMANDS = {
    'start': "inicia la conversa.",
    'help': "ofereix ajuda sobre les comandes disponibles.",
    'author': "mostra el nom dels autors del projecte.",
    'go destí': "comença a guiar l'usuari per arrivar de la seva posició actual fins al punt de destí escollit. Per exemple: /go Campus Nord.",
    'where': "dóna la localització actual de l'usuari.",
    'cancel': "cancel·la el sistema de guia actiu.",
}

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('where', where))
dispatcher.add_handler(CommandHandler('cancel', cancel))

# engega el bot
updater.start_polling()
