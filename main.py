import sys
import pygame

import menu
import game
import asset_loader
import deck_editor

pygame.init()

while True:
    action = menu.main_menu()
    if action == "QUIT":
        sys.exit()
    elif action == "DECK EDITOR":
        deck_editor.main()
    else:
        asset_loader.main()
        game.main(action)