import random

from termcolor import colored


def get_title():
    rocket_colour = 'red'
    text_color = 'blue'

    text = [
        # One
        colored("\n      /\        ", rocket_colour) + colored("______                            ", text_color) + colored("|\**/|    \n", rocket_colour) \
    + colored("     /  \       ", rocket_colour) + colored("| ___ \                           ", text_color) + colored("\ == /    \n", rocket_colour) \
    + colored("     |  |       ", rocket_colour) + colored("| |_/ / ___   ___  _ __ ___       ", text_color) + colored(" |  |     \n", rocket_colour) \
    + colored("     |  |       ", rocket_colour) + colored("| ___ \/ _ \ / _ \| '_ ` _ \      ", text_color) + colored(" |  |     \n", rocket_colour) \
    + colored("    / == \      ", rocket_colour) + colored("| |_/ / (_) | (_) | | | | | |     ", text_color) + colored(" \  /     \n", rocket_colour) \
    + colored("    |/**\|      ", rocket_colour) + colored("\____/ \___/ \___/|_| |_| |_|     ", text_color) + colored("  \/      \n", rocket_colour)
        # Two
        , colored("\n      /\        ", rocket_colour) + colored("    ____                          ", text_color) + colored("|\**/|    \n", rocket_colour) \
    + colored("     /  \       ", rocket_colour) + colored("   / __ )____  ____  ____ ___     ", text_color) + colored("\ == /    \n", rocket_colour) \
    + colored("     |  |       ", rocket_colour) + colored("  / __  / __ \/ __ \/ __ `__ \    ", text_color) + colored(" |  |     \n", rocket_colour) \
    + colored("     |  |       ", rocket_colour) + colored(" / /_/ / /_/ / /_/ / / / / / /    ", text_color) + colored(" |  |     \n", rocket_colour) \
    + colored("    / == \      ", rocket_colour) + colored("/_____/\____/\____/_/ /_/ /_/     ", text_color) + colored(" \  /     \n", rocket_colour) \
    + colored("    |/**\|      ", rocket_colour) + colored("                                  ", text_color) + colored("  \/      \n", rocket_colour)]
    
    return random.choice(text)