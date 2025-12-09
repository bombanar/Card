import pygame
import os
import glob
import pyautogui
import json
import random
import classes

with open("config.json", "r") as f:
    config = json.load(f)

with open("cards.json", "r") as f:
    cards = json.load(f)

screen_width = config["screen_width"]
screen_height = config["screen_height"]

mp = screen_width/1920

hand_height = mp * config["hand_height"]
border_margin = mp * config["border_margin"]
card_height = mp * config["card_height"]
card_width = mp * config["card_width"]
board_height = mp * config["board_height"]
enemy_hand_height = mp * config["enemy_hand_height"]
enemy_board_height = mp * config["enemy_board_height"]

card_collection = config["card_collection"]
for key in card_collection.keys():
    card_collection[key] *= mp

end_turn_collider = config["end_turn"]
for key in end_turn_collider.keys():
    end_turn_collider[key] *= mp

shop = config["shop"]
for key in shop.keys():
    shop[key] *= mp

# Define the target size for all images
CARD_SIZE = (card_width, card_height)
BORDER_SIZE = (card_width + 2*border_margin, card_height + 2*border_margin)


def load_and_scale_images(folder_path):
    image_dict = {}
    supported_extensions = ['*.png', '*.jpg', '*.jpeg']

    for ext in supported_extensions:
        for file_path in glob.glob(os.path.join(folder_path, ext)):
            key = os.path.splitext(os.path.basename(file_path))[0]

            try:
                image_surface = pygame.image.load(file_path).convert_alpha()

                # --- RESCALING STEP ---
                # Rescale the loaded image surface to the fixed TARGET_SIZE
                # scaled_image = pygame.transform.scale(image_surface, CARD_SIZE)
                # -----------------------

                image_dict[key] = image_surface

            except pygame.error as e:
                print(f"Skipping {file_path} due to error: {e}")

    return image_dict

def load_deck():
    with open("deck.json", "r") as f:
        deck = json.load(f)
    return deck


def shuffle_deck(deck):
    keys_list = list(deck.keys())

    output = []
    while len(deck) > 0:
        random_key = random.choice(keys_list)
        output.append(random_key)
        deck[random_key] -= 1
        if deck[random_key] == 0:
            del deck[random_key]
            keys_list = list(deck.keys())
    return output

def make_card(name, index):
    with open("cards.json", "r") as f:
        cards = json.load(f)
    return classes.Card(name, index, cards[name]["description"], cards[name]["power"], cards[name]["cost"], cards[name]["counter"])

def border_dims(dimensions):
    return dimensions[0] - border_margin, dimensions[1] - border_margin

def cost_dims(dimensions):
    return dimensions[0] + card_width - 3/2*border_margin, dimensions[1]

def shift_dim_x(dimensions, shift):
    return dimensions[0] + shift, dimensions[1]

def adjust_hand(hand):
    pos = screen_width/2
    for card in hand:
        pos -= card_width/2 + 2*border_margin
    pos += 2*border_margin
    for card in hand:
        if card.get_status() == "hand":
            card.set_y(hand_height)
            card.set_x(pos)
        pos += card_width + 4*border_margin

def adjust_board(board):
    pos = screen_width/2
    for card in board:
        pos -= card_width/2 + 2*border_margin
    pos += 2*border_margin
    for card in board:
        card.set_y(board_height)
        card.set_x(pos)
        pos += card_width + 4*border_margin

def adjust_enemy_board(board):
    pos = screen_width/2
    for card in board:
        pos -= card_width/2 + 2*border_margin
    pos += 2*border_margin
    for card in board:
        card.set_y(enemy_board_height)
        card.set_x(pos)
        pos += card_width + 4*border_margin

def adjust_row(row, height):
    pos = screen_width/2
    pos -= (card_width/2 + 2*border_margin)*len(row)
    pos += 2*border_margin
    for card in row:
        card.set_y(height)
        card.set_x(pos)
        pos += card_width + 4*border_margin

def adjust_shop(shopp):
    pos = shop['y']
    for card in shopp:
        card.set_y(pos)
        card.set_x(shop['x'])
        pos += card_height

def adjust_card_collection(collection):
    pos_x = card_collection["x1"]
    pos_y = card_collection["y1"]
    for card in collection:
        if pos_x < card_collection["x2"]:
            card.set_x(pos_x)
            card.set_y(pos_y)
            pos_x += card_width + 4*border_margin
        else:
            pos_x = card_collection["x1"]
            pos_y += card_height + 6*border_margin
            card.set_x(pos_x)
            card.set_y(pos_y)

def enemy_hand(size):
    output = []
    pos = screen_width/2
    pos -= (card_width/2 + 2*border_margin)*size
    for i in range(size):
        output.append((pos, enemy_hand_height))
        pos += card_width + 4*border_margin
    return output

def collision(hand):
    cursor = pygame.mouse.get_pos()
    for i, card in enumerate(hand):
        x, y = card.get_dims()
        if x < cursor[0] < x + card.get_width() and y < cursor[1] < y + card.get_height():
            return i
    return -1

def end_turn(pos):
    if not (end_turn_collider['x1'] <= pos[0] < end_turn_collider['x2']):
        return False
    if not (end_turn_collider['y1'] <= pos[1] < end_turn_collider['y2']):
        return False
    return True

def power_of(board):
    output = 0
    for card in board:
        output += card.get_power()
    return str(output)

# Example Usage:
# game_images = load_and_scale_images('assets')