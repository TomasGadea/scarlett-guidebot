import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import guide
import os
import traceback
import numpy as np


# Constants:
city = "Barcelona"
distance = 20  # max distance from user to checkpoint to consider him near it.
#-------------------------------------------------------------------------------

# Global variables:
map = None   # variable to store the map/graph of the city

TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
#-------------------------------------------------------------------------------


def init_map(city):
    """ Descarrega i guarda el mapa de city, si ja existeix simplement el carrega. """
    global map
    try:
        map = guide.load_graph(city + "_map")
    except FileNotFoundError:
        print("downloading...")
        map = guide.download_graph(city)
        guide.save_graph(map, city + "_map")
        print("downloaded!")


init_map(city)

# guide.print_graph(map)

def start(update, context):
    """ inicia la conversa. """

    user = update.effective_chat.first_name
    salute = '''
Hola %s! Sóc _Scarlett_, el teu bot guia.
Si no coneixes el meu funcioanemnt et recomano la comanda */help*.
Si ja em coneixes, a on anem avui?
''' % (user)

    send_markdown(update, context, salute)


def help(update, context):
    """ ofereix ajuda sobre les comandes disponibles. """

    user = update.effective_chat.first_name
    help_message = '''
D'acord %s, t'explico el meu funcionament:

Primer de tot necessito que comparteixis la teva *ubicació en directe* amb mi per a poder funcionar correctament.🗺

Un cop fet això t'explico tot el que em pots demanar que faci:

''' % (user)

    for key in COMMANDS.keys():  # PROVAR JOINT
        help_message += ''' 🚩 */''' + key + '''* ➡️ ''' + COMMANDS[key] + '''\n'''

    send_markdown(update, context, help_message)


def author(update, context):
    """ Mostra el nom dels autors del projecte. """
    info = '''
Els meus creadors són:
- *Tomás Gadea Alcaide* 🧑🏼‍💻
    mail: 01tomas.gadea@gmail.com
- *Pau Matas Albiol* 🧑🏼‍💻
    mail: paumatasalbi@gmail.com
'''

    send_markdown(update, context, info)


def go(update, context):
    """ comença a guiar l'usuari per arrivar de la seva posició actual fins al punt de destí escollit. Per exemple; /go Campus Nord. """
# Suposem que només ens movem per Barcelona.
    global map

    try:
        location = context.user_data['location']  # KeyError if not shared

        message = str(' '.join(context.args))

        destination = guide.address_coord(message)  # (lat, long)
        directions = guide.get_directions(map, location, destination)  # dict

        # Save vars in user dictionary
        store(context, message, destination, directions)


        send_photo(update, context, directions)
        send_first_text(update, context, directions)

    except KeyError:  # any location has been shared
        print(traceback.format_exc())
        locErr(update, context)

    except Exception:
        print(traceback.format_exc())
        dstErr(update, context)

def store(context, message, destination, directions):
    context.user_data['address'] = message
    context.user_data['destination'] = destination
    context.user_data['directions'] = directions
    context.user_data['checkpoint'] = 0  # Create pair {'checkpoint' : int}

def locErr(update, context):
    locErr = '''
Necessito saber la teva *ubicació en directe*!

Potser t'hauries de repassar les meves opcions amb */help*...
'''
    send_markdown(update, context, locErr)

def dstErr(update, context):
    dstErr = '''
No em dones prou informacio! No sé on vols anar🤷🏼‍♂️

Prova l'estructura */go* _Lloc, País_
'''
    send_markdown(update, context, dstErr)


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
        zoomErr(update, context)


def zoomErr(update, context):
    zoomErr = '''
No has iniciat cap trajecte!

Utilitza la comanda */go* _destinació_ per començar la ruta.
'''
    send_markdown(update, context, zoomErr)


def where(update, context):
    """ Dóna la localització actual de l'usuari. Aquesta funció no pot ser cridada per l'usuari, es crida automàticament quan es comparteix la ubicació """

    if 'location' not in context.user_data or not context.user_data['test']:
        regular_where(update, context)

    else:
        testing_where(update, context)

def regular_where(update, context):
    message = update.edited_message if update.edited_message else update.message
    loc = context.user_data['location'] = (
        message.location.latitude, message.location.longitude)

    common_where(update, context, loc)

def testing_where(update, context):
    loc = context.user_data['location']
    common_where(update, context, loc)

def common_where(update, context, loc):
    check = context.user_data['checkpoint']
    directions = context.user_data['directions']

    dist_list = [guide.dist(loc, section['src']) for section in directions[check:]]
    nearest_check = check + np.argmin(dist_list)
    nearest_dist = dist_list[nearest_check - check]

    global distance

    if nearest_dist <= distance:  # user near next checkpoint
        next_checkpoint(update, context, nearest_check, directions)


def next_checkpoint(update, context, nearest_check, directions):
    nc = nearest_check
    last = len(directions) - 1

    if nc == last: # last node
        end_route(update, context)

    else:
        context.user_data['checkpoint'] = nc
        send_photo(update, context, directions[nc:])
        send_mid_text(update, context, nc)

def end_route(update, context):
    user = update.effective_chat.first_name
    address = context.user_data['address']
    info = '''
Felicitats %s! 🥳
Has arribat a %s.
Ha estat un plaer guiar-te fins aquí. Que passis un bon dia 😁

(Pots continuar desplaçan-te amb la comanda */go*)
''' %(user, str(address))

    send_markdown(update, context, info)
    cancel(update, context)






def cancel(update, context):
    """ Finalitza la ruta actual de l'usuari. """
    user = update.effective_chat.first_name
    print("canceled by", user)

    # Reset initial conditions:
    del context.user_data['directions']
    del context.user_data['destination']
    context.user_data['checkpoint'] = 0


def send_photo(update, context, chopped_dir):
    """ Generates, saves, sends, and deletes an image of journey """
    global map
    location = context.user_data['location']
    destination = context.user_data['destination']
    user_id = str(update.message.from_user.id)

    guide.plot_directions(map, location, destination, chopped_dir, user_id)

    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(str(user_id) + '.png', 'rb'))

    os.remove(user_id + '.png')


def send_first_text(update, context, directions):

    info = '''
Estàs a %s
Comença al *Checkpoint #1*:
    %s
    %s
''' % (
    str(directions[0]['src']),
    str(directions[0]['mid']),
    directions[0]['next_name'])

    send_markdown(update, context, info)


def send_mid_text(update, context, check):
    """ Sends text from middle checkpoints. """

    directions = context.user_data['directions']
    info = '''
Molt bé: has arribat al *Checkpoint # %d*!

Estàs a % s
Ves al *Chekpoint # %d*:
    %s
''' % (
    check,
    str(directions[check]['src']),
    check+1,
    str(directions[check]['mid']) + '''\n'''
    )

    info = add_angle(directions, check, info)
    info = add_meters(directions, check, info)


    if directions[check]['next_name'] is not None:
        info += ''' per ''' + directions[check]['next_name'] + '''\n'''

    send_markdown(update, context, info)


def add_angle(directions, check, info):

    n = len(directions)
    if check <= 1 or check >= n:
        a = 0   # Assume first and last angle is 0
    else:
        a = directions[check]['angle']

    if 22.5 <= a <= 67.5 or -337.5 <= a <= -292.5:
        info += '''Gira lleugerament a la dreta '''
    elif 67.5 <= a <= 112.5 or -292.5 <= a <= -247.5:
        info += '''Gira a la dreta '''
    elif 112.5 <= a <= 157.5 or -202.5 <= a <= -157.5:
        info += '''Gira pronunciadament a la dreta '''


    elif 202.5 <= a <= 247.5 or -67.5 <= a <= -22.5:
        info += '''Gira lleugerament a l'esquerra '''
    elif 247.5 <= a <= 292.5 or -112.5 <= a <= -67.5:
        info += '''Gira a l'esquerra '''
    elif 292.5 <= a <= 337.5 or -157.5 <= a <= -112.5:
        info += '''Gira pronunciadament a l'esquerra '''

    else:
        info += '''Segueix recte '''

    return info


def add_meters(directions, check, info_angles):

    try:
        if 'lenght' not in directions[check] or directions[check]['lenght'] != None:
            info_angles += '''i avança ''' + str(round(directions[check]['length'])) + ''' metres'''
        else:
            print("no lenght")

        return info_angles

    except Exception:
        print(traceback.format_exc())


def next(update, context):
    """Debugging command"""
    check = context.user_data['checkpoint']
    mid = context.user_data['directions'][check]['mid']
    next = (mid[0] - 0.0001, mid[1] - 0.0001)
    context.user_data['location'] = next

    context.user_data['test'] = True  # bool to know if we are testing

    where(update, context)


def next4(update, context):
    """ updates location 4 checkpoints forward """
    check = context.user_data['checkpoint']
    src = context.user_data['directions'][check+4]['src']
    next = (src[0] - 0.0001, src[1] - 0.0001)
    context.user_data['location'] = next

    context.user_data['test'] = True  # bool to know if we are testing
    where(update, context)


def send_markdown(update, context, info):

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=info,
        parse_mode=telegram.ParseMode.MARKDOWN)


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



# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('cancel', cancel))
dispatcher.add_handler(CommandHandler('next', next))
dispatcher.add_handler(CommandHandler('next4', next4))
dispatcher.add_handler(CommandHandler('zoom', zoom))
dispatcher.add_handler(MessageHandler(Filters.location, where))

# engega el bot
updater.start_polling()
