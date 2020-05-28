############################## SCARLETT-GUIDEBOT ###############################

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import guide
import os
import traceback
import numpy as np

# ----------------------------- Initialization ----------------------------------

""" This bot works in Barcelona and her language is catalan. """

# Constants:
city = "Barcelona"
distance = 20  # max distance from user to checkpoint to consider him near it.

# Global variables:
map = None   # variable to store the map/graph of the city

TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

updater.start_polling()

# -------------------------------------------------------------------------------

# ------------------------------- Commands --------------------------------------


def start(update, context):
    """ Carries out the preparations and starts the conversation. """

    init_map(city)

    user = update.effective_chat.first_name
    salute = '''
Hola %s! Sóc _Scarlett_, el teu bot guia.
Si no coneixes el meu funcioanemnt et recomano la comanda */help*.
Si ja em coneixes, a on anem avui?
''' % (user)

    send_markdown(update, context, salute)


def help(update, context):
    """ Sends the user a markdown text explaining the commands aviable. """

    user = update.effective_chat.first_name
    help_message = '''
D'acord %s, t'explico el meu funcionament:

Primer de tot necessito que comparteixis la teva *ubicació en directe* amb mi per a poder funcionar correctament.🗺

Un cop fet això t'explico tot el que em pots demanar que faci:

''' % (user)

    # COMMANDS is a dict of {command : instructions} (See line 405)
    for key in COMMANDS.keys():
        help_message += ''' 🚩 */''' + key + \
            '''* ➡️ ''' + COMMANDS[key] + '''\n'''

    send_markdown(update, context, help_message)


def author(update, context):
    """ Sends the user a markdown txt with the authors names and info. """

    info = '''
Els meus creadors són:
- *Tomás Gadea Alcaide* 🧑🏼‍💻
    mail: 01tomas.gadea@gmail.com
- *Pau Matas Albiol* 🧑🏼‍💻
    mail: paumatasalbi@gmail.com
'''

    send_markdown(update, context, info)


def go(update, context):
    """ Given a destination (str) as an argument, starts the user's journey to reach the chosen destination. """
    """ Starts the user's journey to reach the choosen destination specified after /go. """

    global map

    try:
        location = context.user_data['location']  # KeyError if not shared

        message = str(' '.join(context.args))

        destination = guide.address_coord(message)  # (lat, long)
        if destination == None:
            raise dstError

        directions = guide.get_directions(map, location, destination)  # dict

        # Save vars in user dictionary
        store(context, message, destination, directions)

        send_photo(update, context, directions)
        send_first_text(update, context, directions)

    except KeyError:  # any location has been shared
        print(traceback.format_exc())
        locErr(update, context)

    except dstError:
        print(traceback.format_exc())
        dstErr(update, context)

    except Exception:
        print(traceback.format_exc())


def zoom(update, context):
    """ Sends a map with only the actual checkpoint and the path to reach the two folowing ones. """

    try:
        check = context.user_data['checkpoint']
        directions = context.user_data['directions']

        n = len(directions)

        end = check+3 if check+3 < n else n-1

        zoom_dir = directions[check:end]  # zoomed/chopped directions

        send_photo(update, context, zoom_dir)

    except Exception:
        print(traceback.format_exc())
        zoomErr(update, context)


def cancel(update, context):
    """ Stops the current user's journey. """

    user = update.effective_chat.first_name
    print("canceled by", user)

    # Reset initial conditions:
    del context.user_data['directions']
    del context.user_data['destination']
    context.user_data['checkpoint'] = 0


def jump(update, context):
    """ It's a debugging command that simulates an user's progress. """

    n = int(context.args[0])
    c = context.user_data['checkpoint']
    d = context.user_data['directions']

    if len(d)-1 < c+n:
        c = len(d)-1
        n = 0
    elif c+n < 0:
        c = 0
        n = 0

    src = context.user_data['directions'][c+n]['src']
    next = (src[0] - 0.0001, src[1] - 0.0001)
    context.user_data['location'] = next
    context.user_data['test'] = True  # bool to know if we are testing
    where(update, context)

# -------------------------------------------------------------------------------

# --------------------------------- Errors --------------------------------------


class Error(Exception):
    """ Base class for other exceptions """
    pass


class dstError(Error):
    """ Raised when address returned from guide.address_coord() is None """
    pass


def locErr(update, context):
    locErr = '''
Necessito saber la teva *ubicació en directe*!

Potser t'hauries de repassar les meves opcions amb */help*...
'''
    send_markdown(update, context, locErr)


def dstErr(update, context):
    dstErr = '''
No em dones prou informacio! No sé on vols anar🤷🏼‍♂️

Prova l'estructura */go* _Lloc, Localitat, País_
'''
    send_markdown(update, context, dstErr)


def zoomErr(update, context):
    zoomErr = '''
No has iniciat cap trajecte!

Utilitza la comanda */go* _destinació_ per començar la ruta.
'''
    send_markdown(update, context, zoomErr)

# -------------------------------------------------------------------------------

# ------------------------------- Messages --------------------------------------


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
    """ Sends the first text message that the user will recive when starts a journey. """

    info = '''
Comença al *Checkpoint #1*:
    %s
''' % (directions[0]['next_name'])

    send_markdown(update, context, info)


def send_mid_text(update, context, check):
    """ Sends text from middle checkpoints. """

    directions = context.user_data['directions']
    info = '''
Molt bé: has arribat al *Checkpoint %d*!

''' % (check)

    info += angle(directions, check)
    info += meters(directions, check)

    if directions[check]['next_name'] is not None:
        info += ''' per ''' + \
            directions[check]['next_name'] + \
                ''' per arribar al *Checkpoint %d*''' % (check+1)

    send_markdown(update, context, info)


def send_markdown(update, context, info):
    """ Sends a message containing the text info in markdown format. """

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=info,
        parse_mode=telegram.ParseMode.MARKDOWN)

# -------------------------------------------------------------------------------

# ----------------------------- Aux functions -----------------------------------


def store(context, message, destination, directions):
    """ Defines and stores the essential user data at the start of a journey. """

    context.user_data['address'] = message
    context.user_data['destination'] = destination
    context.user_data['directions'] = directions
    context.user_data['checkpoint'] = 0  # Create pair {'checkpoint' : int}


def end_route(update, context):
    """ Sends the last text message that the user will recive and stops the journey when the user finishes it. """

    user = update.effective_chat.first_name
    address = context.user_data['address']
    info = '''
Felicitats %s! 🥳
Has arribat a %s.
Ha estat un plaer guiar-te fins aquí. Que passis un bon dia 😁

(Pots continuar desplaçant-te amb la comanda */go*)
''' % (user, str(address))

    send_markdown(update, context, info)
    cancel(update, context)


def angle(directions, check):
    """ Returns a markdown string explaining the next direction that the user should take. """

    n = len(directions)
    if check <= 1 or check >= n:
        a = 0   # Assume first and last angle is 0
    else:
        a = directions[check]['angle']

    if 22.5 <= a <= 67.5 or -337.5 <= a <= -292.5:
        return '''Gira lleugerament a la dreta '''
    elif 67.5 <= a <= 112.5 or -292.5 <= a <= -247.5:
        return '''Gira a la dreta '''
    elif 112.5 <= a <= 157.5 or -202.5 <= a <= -157.5:
        return '''Gira pronunciadament a la dreta '''

    elif 202.5 <= a <= 247.5 or -67.5 <= a <= -22.5:
        return '''Gira lleugerament a l'esquerra '''
    elif 247.5 <= a <= 292.5 or -112.5 <= a <= -67.5:
        return '''Gira a l'esquerra '''
    elif 292.5 <= a <= 337.5 or -157.5 <= a <= -112.5:
        return '''Gira pronunciadament a l'esquerra '''

    return '''Segueix recte '''


def meters(directions, check):
    """ Returns a markdown message with the amount of meters that the user should travel. """

    try:
        if 'lenght' not in directions[check] or directions[check]['lenght'] != None:
            meters = '''i avança ''' + \
                str(round(directions[check]['length'])) + ''' metres'''
        else:
            print("no lenght")

        return meters

    except Exception:
        print(traceback.format_exc())


def init_map(city):
    """ Downloads and saves the city map, if it already exists only loads it. """

    global map
    try:
        map = guide.load_graph(city + "_map")
    except FileNotFoundError:
        print("downloading...")
        map = guide.download_graph(city)
        guide.save_graph(map, city + "_map")
        print("downloaded!")

# -------------------------------------------------------------------------------

# -------------------------- Location functions ---------------------------------


def where(update, context):
    """ Invokes the corresponding function if it's invoked automaticaly, if changes the current user location, or if we use jump command while debugging.  """

    if 'location' not in context.user_data or not context.user_data['test']:
        regular_where(update, context)

    else:
        testing_where(update, context)


def regular_where(update, context):
    """ Is invoked automaticaly if the user current location changes and actualizes it in our data base. """

    message = update.edited_message if update.edited_message else update.message
    loc = context.user_data['location'] = (
        message.location.latitude, message.location.longitude)

    common_where(update, context, loc)


def testing_where(update, context):
    """ Is invoked by the admin to debug and simulates the regular_where. """

    loc = context.user_data['location']
    common_where(update, context, loc)


def common_where(update, context, loc):
    """ Sends a message with new instructions to the user if he has advenced to another checkpoint. """

    check = context.user_data['checkpoint']
    directions = context.user_data['directions']

    dist_list = [guide.dist(loc, section['src']) for section in directions]
    nearest_check = np.argmin(dist_list)
    nearest_dist = dist_list[nearest_check]

    global distance

    if nearest_dist <= distance:  # user near next checkpoint
        next_checkpoint(update, context, nearest_check, directions)


def next_checkpoint(update, context, nearest_check, directions):
    """ Sends the message with the instructions to find the folowing checkpoint, in directions, to nearest_check. """

    nc = nearest_check
    last = len(directions) - 1
    if nc == last:  # last node
        end_route(update, context)

    else:
        context.user_data['checkpoint'] = nc
        send_photo(update, context, directions[nc:])
        send_mid_text(update, context, nc)

# -------------------------------------------------------------------------------


# Commands and handlers:
COMMANDS = {
    'start': "inicia la conversa amb mi.",
    'help': "et torno a oferir aquesta ajuda sobre les meves comandes disponibles els cops que necessitis.",
    'author': "si ets curiós et puc dir qui m'ha creat.",
    'go destí': "et començo a guiar per a arrivar de la teva posició actual fins al punt de destí que m'hagis especificat.🧭\nT'anire enviant indicacions al teu dispositiu de les direccions que has de prendre.📲",
    'cancel': "cancel·la el sistema de guia actiu.",
    'zoom': "Envia una foto ampliada amb els 3 pròxims checkpoints."
}


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('go', go))
dispatcher.add_handler(CommandHandler('cancel', cancel))
dispatcher.add_handler(CommandHandler('jump', jump))
dispatcher.add_handler(CommandHandler('zoom', zoom))
dispatcher.add_handler(MessageHandler(Filters.location, where))


################################################################################
