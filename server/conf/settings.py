r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "SWNMU"

AUTH_PASSWORD_VALIDATORS = []
MULTISESSION_MODE = 2
MAX_NR_SIMULTANEOUS_PUPPETS = 5
MAX_NR_CHARACTERS = 10
AUTO_PUPPET_ON_LOGIN = False
AUTO_CREATE_CHARACTER_WITH_ACCOUNT = False
FUNCPARSER_PARSE_OUTGOING_MESSAGES_ENABLED = False


#########################################
# Godot websocket server
#########################################

# PORTAL_SERVICES_PLUGIN_MODULES.append('evennia.contrib.base_systems.godotwebsocket.webclient')
# GODOT_CLIENT_WEBSOCKET_PORT = 4008
# GODOT_CLIENT_WEBSOCKET_CLIENT_INTERFACE = "0.0.0.0"

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
