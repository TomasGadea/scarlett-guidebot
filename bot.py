import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import guide
import osmnx as ox
import os
import traceback

bcn_map = None


def init_bcn_map():
    """ Descarrega i guarda el mapa de Barcelona, si ja existeix simplement el carrega. """
    global bcn_map
    try:
        bcn_map = guide.load_graph("bcn_map")
    except FileNotFoundError:
        bcn_map = guide.download_graph("Barcelona, Spain")
        guide.save_graph(bcn_map, "bcn_map")


init_bcn_map()


def start(update, context):
    """ inicia la conversa. """
    user = update.effective_chat.first_name
    salute = "Hola %s! Sóc Scarlett, el teu bot guia.\nSi no coneixes el meu funcioanemnt et recomano la comanda /help.\nSi ja em coneixes, a on anem avui?" % (
        user)
    context.bot.send_message(chat_id=update.effective_chat.id, text=salute)


def help(update, context):
    """ ofereix ajuda sobre les comandes disponibles. """
    user = update.effective_chat.first_name
    help_message = "D'acord %s, t'explico el meu funcionament.\nPrimer de tot necessito que comparteixis la teva ubicació en directe amb mi per a poder funcionar correctament.🗺\nUn cop fet això t'explico tot el que em pots demanar que faci:\n" % (
        user)
    for key in COMMANDS.keys():  # PROVAR JOINT
        help_message += '\n 🚩 /' + key + ' ➡️ ' + COMMANDS[key]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_message)


def language(update, context):
    """ ... """
    user = update.effective_chat.first_name

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
    user = update.effective_chat.first_name

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
    info = '''
Els meus creadors són:
- *Tomás Gadea Alcaide* 🧑🏼‍💻
    mail: 01tomas.gadea@gmail.com
- *Pau Matas Albiol* 🧑🏼‍💻
    mail: paumatasalbi@gmail.com
'''

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=info,
        parse_mode=telegram.ParseMode.MARKDOWN)


def go(update, context):
    """ comença a guiar l'usuari per arrivar de la seva posició actual fins al punt de destí escollit. Per exemple; /go Campus Nord. """
# Suposem que només ens movem per Barcelona.
    global bcn_map
    user = update.effective_chat.first_name
    nick = str(update.effective_chat.username)

    try:
        location = context.user_data['location']  # KeyError if not shared

        message = ''  # ' '.join(str(context.args))
        for i in range(len(context.args)):
            message += str(context.args[i] + ' ')

        destination = guide.address_coord(message)  # (lat, long)
        directions = guide.get_directions(bcn_map, location, destination)  # dict

        # Save vars in user dictionary
        context.user_data['destination'] = destination
        context.user_data['directions'] = directions
        context.user_data['checkpoint'] = 0  # Create pair {'checkpoint' : int}

        send_message(update, context)  # És el que hi havia aqui

        # Send journey starting message:
        info = "Estàs a " + str(directions[0]['src']) + "\nComença al Checkpoint #1:    " + str(
            directions[0]['mid']) + '\n(' + directions[0]['next_name'] + ')'
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=info)

    except KeyError:  # any location has been shared
        print('KeyError')

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Necessito saber la teva ubicació en directe, potser t'hauries de repassar les meves opcions amb /help...")

    except Exception as e:
        print(traceback.format_exc())

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No em dones prou informacio! No sé on vols anar🤷🏼‍♂️\nProva l'estructura Lloc, País")


def zoom(update, context):
    try:
        check = context.user_data['checkpoint']
        directions = context.user_data['directions']

        n = len(directions)

        end = check+3 if check+3 < n else n-1

        zoom_dir = directions[check:end] # zoomed/chopped directions

        send_photo(update, context, zoom_dir)

    except Exception:
        print(traceback.format_exc())
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No has iniciat cap trajecte! Utilitza la comanda [/go 'destinació'] per començar la ruta.")


def where(update, context):
    """ Dóna la localització actual de l'usuari. Aquesta funció no pot ser cridada per l'usuari, es crida automàticament quan es comparteix la ubicació """

    if 'location' not in context.user_data or not context.user_data['test']:
        message = update.edited_message if update.edited_message else update.message
        loc = context.user_data['location'] = (
            message.location.latitude, message.location.longitude)

    else:
        loc = context.user_data['location']

    check = context.user_data['checkpoint']
    directions = context.user_data['directions']
    mid = directions[check]['mid']

    if guide.dist(loc, mid) <= 20:  # user near next checkpoint
        check += 1

        info = 'Molt bé: has arribat al Checkpoint  # %d!\n \
        Estàs a % s\n \
        Ves al Chekpoint  # %d: %s(%s) longitud:\n \
        angle: \n' \
        % (
            check,
            str(directions[check]['src']),
            check+1,
            str(directions[check]['mid']),
            str(directions[check]['next_name'])
        )

        context.user_data['checkpoint'] += 1

        send_message(update, context)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=info)


def cancel(update, context):
    """ Finalitza la ruta actual de l'usuari. """
    nick = str(update.effective_chat.username)
    print("canceled by", nick)

    # Reset initial conditions:
    del context.user_data['directions']
    del context.user_data['destination']
    context.user_data['checkpoint'] = 0


def send_message(update, context):
    """ ... """
    check = context.user_data['checkpoint']
    directions = context.user_data['directions']

    send_photo(update, context, directions[check:])
    #send_text(update, context)


def send_photo(update, context, directions):
    """ Generates, saves, sends, and deletes an image of journey """

    global bcn_map
    nick = str(update.effective_chat.username)

    location = context.user_data['location']
    destination = context.user_data['destination']

    guide.plot_directions(bcn_map, location, destination, directions, nick)

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(str(nick) + '.png', 'rb'))

    os.remove(nick + '.png')


def send_text(update, context):
    """ ... """
    pass


def next(update, context):
    """Debugging command"""
    check = context.user_data['checkpoint']
    mid = context.user_data['directions'][check]['mid']
    next = (mid[0] - 0.0001, mid[1] - 0.0001)
    context.user_data['location'] = next

    context.user_data['test'] = True  # bool to know if we are testing
    where(update, context)


TOKEN = open('token.txt').read().strip()

COMMANDS = {
    'start': "inicia la conversa amb mi.",
    'help': "et torno a oferir aquesta ajuda sobre les meves comandes disponibles els cops que necessitis.",
    'language llengua': "canvia la l'idioma amb el que t'atenc al que m'hagis especificat.",
    'conveyance trasport': "canvia les rutes que et proporciono per les adeqüades del transport que m'hagis especificat.",
    'author': "si ets curiós et puc dir qui m'ha creat.",
    'go destí': "et començo a guiar per a arrivar de la teva posició actual fins al punt de destí que m'hagis especificat.🧭\nT'anire enviant indicacions al teu dispositiu de les direccions que has de prendre.📲",
    'cancel': "cancel·la el sistema de guia actiu.",
    'zoom': "Envia una foto ampliada amb els 3 pròxims checkpoints."
}

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
dispatcher.add_handler(CommandHandler('next', next))
dispatcher.add_handler(CommandHandler('zoom', zoom))
dispatcher.add_handler(MessageHandler(Filters.location, where))

# engega el bot
updater.start_polling()
