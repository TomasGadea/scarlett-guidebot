# Scarlett guidebot

One Paragraph of project description goes here

## Getting Started

This project is divided in two parts:

* `guide.py` provides all the geographic operations on the graphs representing maps. These operations go from getting the graphs to getting the coordinates of an address.

* `bot.py` provides all the telegram API. It's job is to guide the users to their destinations reading commands and using guide.

Although guide is used in bot, the libraries used on one module are not used in the other one because of they are focused in different utilities.

### Prerequisites

You will need to have `python3` and `pip3` updated. Check it with:
```
pip3 install --upgrade pip3
pip3 install --upgrade python3
```
If you are using macOS you will need to install [brew](https://brew.sh) in your enviroment using:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```

### Installing

All the requisites are explained in `requirements.txt`.

The required libraries and their installation commands are:

* **networkx** used for graph manipulation:
```
pip3 install networkx
```
* **osmnx** used for getting and treat with geographic graphs:
```
brew install spatialindex
pip3 install osmnx
```
if you are using linux you only need:
```
apt install libspatialindex-dev
pip3 install osmnx
```
* **haversine** used for calculating coordinates distances:
```
pip3 install haversine
```
* **staticmap** used for drawing maps:
```
pip3 install staticmap
```
* **python-telegram-bot** used for developing a telegram bot interface:
```
pip3 install python-telegram-bot
```
* **numpy** used for mathematical calcules:
```
pip3 install numpy
```

## Usage

To run the bot you must follow these steps:

* **FIRST STEP** - *run bot module* - Keep the module running, some comments and errors will be shown:
```
python3 bot.py
```
* **SECOND STEP** - *discover Scarlett* - Go to [Scarlett](t.me/scarlett_guidebot), start the conversation, ask Scarlett for her commands with `/help` and follow the instructions.
![2nd step](2nd-step.png)

* **THIRD STEP** - *start the journey* - After sharing your localization with Scarlett you can give him your destination with `/go destination`.
`tomas ho hauries de fer tu perque queda molt feo una foto desde masquefa``![3rd step_1](2nd-step.png)`
During the route Scarlett will provide you updates of this type:
![3rd step_2](3rd-step_2.png)
If you don't see very well the map you can use `/zoom`:
![3rd step_3](3rd-step_3.png)

### Running the tests

To run tests with the bot you must follow the same steps of the normal use, but instead of walking or moving yourself you can use `/jump x` to move you `x` nodes:
![Tests 1](Tests_1.png)
Also you can go back:
![Tests 2](Tests_2.png)

```
^^^^^
|||||
Serio
-------------------------
utils
|||||
fletxa cap abaix
```



# scarlett-guidebot
AP2 project (GCED)
## Commands autopep8

[Source link](https://pypi.org/project/autopep8/#usage)

- `autopep8` + `<filename>` : doesn't change the file, just outputs the autopep8 version in terminal.
- `autopep8 --in-place --aggressive --aggressive` + `<filename>` :  changes the file, notice `--in-place`.

## links
- [Lliçons de bots de Telegram](https://lliçons.jutge.org/python/telegram.html)

- [Lliçons de fitxers en Python](https://lliçons.jutge.org/python/fitxers-i-formats.html)

- [Tutorial de NetworkX](https://networkx.github.io/documentation/stable/tutorial.html)

- [Tutorial d'OSMnx](https://geoffboeing.com/2016/11/osmnx-python-street-networks/)

- [github Jordi Petit](https://github.com/jordi-petit/ap2-guidebot)

- [staticmap github](https://github.com/komoot/staticmap/blob/master/README.md)

- [osmnx nearest nodes/edges](https://osmnx.readthedocs.io/en/stable/osmnx.html#osmnx.utils.get_nearest_node)

- [† † †](https://www.youtube.com/watch?v=Vl8UIuHfbX8)
