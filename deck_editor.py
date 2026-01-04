import json
import pygame

import sysf

def main():
    with open('cards.json', 'r') as f:
        cards = json.load(f)

    with open('config.json', 'r') as f:
        config = json.load(f)

    id = 1000

    mp = config['screen_width']/1920
    SCREEN_WIDTH = config['screen_width']
    SCREEN_HEIGHT = config['screen_height']

    row_height = config['rarity_rows']

    scroll_speed = config['scroll_speed'] * mp

    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    images = sysf.load_and_scale_images('cache/card_imgs')
    background = pygame.image.load('cache/deck_background.png')

    deck_src = sysf.load_deck()
    rows = {"bronze": [], "silver": [], "gold": []}
    for key in deck_src.keys():
        while deck_src[key] > 0:
            deck_src[key] -= 1
            rarity = cards[key]["rarity"]
            rows[rarity].append(sysf.make_card(key, id))
            id += 1

    collection = []

    shift_x = 0

    click = 0
    last_click = 0

    for key in cards.keys():
        collection.append(sysf.make_card(key, id))
        collection[-1].set_scale(1.2)
        id += 1

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEWHEEL:
                shift_x += event.y * scroll_speed

        last_click = click
        click = pygame.mouse.get_pressed()[0]

        sysf.adjust_card_collection(collection)
        for card in collection:
            card.set_x(card.get_dims()[0] + shift_x)

        col = sysf.collision(collection)
        for card in collection:
            card.set_scale(1)
        if col > -1:
            collection[col].set_scale(1.2)
        if click and not last_click and col > -1:
            rows[cards[collection[col].get_name()]["rarity"]].append(sysf.make_card(collection[col].get_name(), id))
            id += 1
        if col == -1:
            for rarity, row in rows.items():
                col = sysf.rev_collision(row)
                for card in row:
                    card.set_scale(1)
                if col > -1:
                    row[col].set_scale(1.2)
                if click and not last_click and col > -1:
                    row.pop(col)
                    break

        sysf.adjust_row(rows["bronze"], row_height["bronze"])
        sysf.adjust_row(rows["silver"],  row_height["silver"])
        sysf.adjust_row(rows["gold"],  row_height["gold"])


        screen.blit(background, (0, 0))

        for card in collection + rows["bronze"] + rows["silver"] + rows["gold"]:
            screen.blit(images[card.display()], card.get_dims())

        pygame.display.flip()

    output = {}
    for card in rows["bronze"] + rows["silver"] + rows["gold"]:
        if card.get_name() not in output.keys():
            output[card.get_name()] = 1
        else:
            output[card.get_name()] += 1

    with open('deck.json', 'w') as f:
        json.dump(output, f)
