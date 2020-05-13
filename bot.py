from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import guide


def start(update, context):
    """ inicia la conversa. """
    global user
    user = update.effective_chat.first_name
    salute = "Hola %s! Sóc Scarlett, el teu bot guia.\nSi no coneixes el meu funcioanemnt et recomano la comanda /help.\nSi ja em coneixes, a on anem avui?" % (
        user)
    context.bot.send_message(chat_id=update.effective_chat.id, text=salute)


def help(update, context):
    """ ofereix ajuda sobre les comandes disponibles. """
    global user
    help_message = "D'acord %s, t'explico el meu funcionament.\nPrimer de tot necessito que comparteixis la teva ubicació en directe amb mi per a poder funcionar correctament.🗺\nUn cop fet això t'explico tot el que em pots demanar que faci:\n" % (
        user)
    for key in COMMANDS.keys():  # PROVAR JOINT
        help_message += '\n 🚩 /' + key + ' ➡️ ' + COMMANDS[key]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_message)


def language(update, context):
    """ ... """
    global user
    language = str(context.args[0])
    try:
        pass
    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Em sap greu %s, encara no estic preparada per parlar en %s\nSegueixo en desenvolupament⚙️" % (user, language))


def conveyance(update, context):
    """ ... """
    global user
    conveyance = str(context.args[0])
    try:
        if conveyance == 'cotxe':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Perfecte anem en cotxe!🚗')
        elif conveyance == 'caminant':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Perfecte anem en caminant!🚶‍♂️')
        else:
            raise Exception

    except Exception as e:
        print(e)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Em sap greu %s, encara no estic preparada per a ajudar-te a desplaçarte en %s\nSegueixo en desenvolupament⚙️" % (user, conveyance))


def author(update, context):
    """ Mostra el nom dels autors del projecte. """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Els meus creadors són:\n" +
        "    -Tomás Gadea Alcaide🧑🏼‍💻\n" +
        "        mail: 01tomas.gadea@gmail.com\n\n" +
        "    -Pau Matas Albiol🧑🏼‍💻\n" +
        "        mail: paumatasalbi@gmail.com\n")


def go(update, context):
    """ comença a guiar l'usuari per arrivar de la seva posició actual fins al punt de destí escollit. Per exemple; /go Campus Nord. """
# Suposem que només ens movem per Barcelona.
    global bcn_map
    global location

    try:
        destination = str(context.args)
        # insertem la destinacio al diccionari particular de l'usuari:
        context.user_data['destination'] = destination
# -----
        where()  # podem prescindir d'això (?). crec que s'actualitza sol, no cal cridar where()

        directions = guide.get_directions(graph, location, destination)
        plot_directions(graph, location, destination_coords,
                        directions, destination)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(destination + '.png', 'rb'))
    except Exception as e:
        print(e)
        if location == (None, None):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Necessito saber la teva ubicació en directe, potser t'hauries de repassar les meves opcions amb /help...")
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="No em dones prou informacio! No sé on vols anar🤷🏼‍♂️\nProva l'estructura Lloc, País")


def where(update, context):
    """ Dóna la localització actual de l'usuari. Aquesta funció no pot ser cridada per l'usuari, es crida automàticament quan es comparteix la ubicació """

    message = update.edited_message if update.edited_message else update.message
    global location
    location = (message.location.latitude, message.location.longitude)


def cancel(update, context):
    """ """


def init_bcn_map():
    """ Descarrega i guarda el mapa de Barcelona, si ja existeix simplement el carrega. """
    global bcn_map
    try:
        bcn_map = guide.load_graph("bcn_graph")
    except FileNotFoundError:
        bcn_map = guide.download_graph("Barcelona, Spain")
        guide.save_graph(bcn_map, "bcn_graph")


init_bcn_map()

TOKEN = open('token.txt').read().strip()

COMMANDS = {
    'start': "inicia la conversa amb mi.",
    'help': "et torno a oferir aquesta ajuda sobre les meves comandes disponibles els cops que necessitis.",
    'language llengua': "canvia la l'idioma amb el que t'atenc al que m'hagis especificat.",
    'conveyance trasport': "canvia les rutes que et proporciono per les adeqüades del transport que m'hagis especificat.",
    'author': "si ets curiós et puc dir qui m'ha creat.",
    'go destí': "et començo a guiar per a arrivar de la teva posició actual fins al punt de destí que m'hagis especificat.🧭\nT'anire enviant indicacions al teu dispositiu de les direccions que has de prendre.📲",
    'cancel': "cancel·la el sistema de guia actiu.",
}

location = (None, None)
destination = (None, None)
user = None
bcn_map = None
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('cancel', cancel))
dispatcher.add_handler(CommandHandler('language', language))
dispatcher.add_handler(CommandHandler('conveyance', conveyance))
dispatcher.add_handler(MessageHandler(Filters.location, where))

# engega el bot
updater.start_polling()


# commit petit
