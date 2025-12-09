import pygame
import os
import glob
import json
import random
import threading
import queue
import sys
# --- LOCAL IMPORTS ---g
import sysf
import net
import classes as cl
from menu import font_size
from sysf import make_card


def deserialize_board_data(data_list):
    """Converts a list of serialized card dicts back into cl.Card objects."""
    new_board = []
    for card_data in data_list:
        # Assuming cl.Card constructor can take name, id, desc, power, cost
        card = cl.Card(
            card_data['name'],
            card_data['id'],
            card_data['desc'],
            card_data['power'],
            card_data['cost']
        )
        # Re-set other necessary attributes like scale and status
        card.set_scale(1.2)  # Use a default if not present
        card.set_status(card_data.get('status', 'board'))
        new_board.append(card)
    return new_board

def main(HOST_IP):
    # --- END LOCAL IMPORTS ---

    # --- 1. P2P ROLE SELECTION AND NETWORK START ---
    # To test, set one instance to True (Host) and the other to False (Client).
    # Best practice is to use command-line arguments (sys.argv) as discussed previously,
    # but for simplicity, we'll keep it as a flag here.
    if HOST_IP == 'host':
        IS_HOST = True # <--- TOGGLE THIS MANUALLY FOR HOST/CLIENT TESTING
    else:
        IS_HOST = False

    # Placeholder connection details (used by Client to connect to Host)
    HOST_PORT = 65432

    if IS_HOST:
        # Host sets up the listener (0.0.0.0 listens on all interfaces)
        net_thread = threading.Thread(target=net.start_host, args=('0.0.0.0', HOST_PORT))
    else:
        # Client connects to the host's IP
        net_thread = threading.Thread(target=net.start_client, args=(HOST_IP, HOST_PORT))

    net_thread.daemon = True
    net_thread.start()
    # --- END NETWORK START ---

    with open("config.json", "r") as f:
        config = json.load(f)
    with open("cards.json", "r") as f:
        cards = json.load(f)

    SCREEN_WIDTH = config["screen_width"]
    SCREEN_HEIGHT = config["screen_height"]
    mp = SCREEN_WIDTH / 1920
    font_size = int(config["font_size"] * mp)
    playfield = config["playfield"]
    for key in playfield.keys():
        playfield[key] *= mp
    power_dims = config["power"]
    for key in power_dims.keys():
        power_dims[key] *= mp

    money_dims = config["money"]
    for key in money_dims.keys():
        money_dims[key] *= mp

    score_dims = config["score"]
    for key in score_dims.keys():
        score_dims[key] *= mp

    hand = []
    enemy_hand_size = 0
    board = []
    shop = []
    enemy_board = []

    # --- 2. BOARD STATE TRACKING FOR SENDING ---
    # Used to determine if the local board has changed and needs to be sent.
    last_sent_board_ids = []

    deck = sysf.shuffle_deck(sysf.load_deck())

    for i in range(3):
        # Using cl.Card from your classes file
        shop.append(make_card(deck[-1], i))
        deck.pop()

    sysf.adjust_shop(shop)

    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bombad")

    BLACK = (0, 0, 0)
    GOLD = (255, 215, 0)

    drag_x, drag_y = 0, 0
    dragged = None
    placeholder_on = None
    last_left_mb_state = False
    end_turn = False
    score = 0

    player_power = 0
    money_delta = 0
    enemy_power = 0
    money = 100
    id = 1000
    buy_free = 1

    images = sysf.load_and_scale_images('cache/card_imgs')
    background = pygame.image.load('cache/background.png')
    card_back = pygame.image.load('cache/card_back.png')
    background_pas = pygame.image.load('cache/background_pas.png')

    placeholder = cl.Card("card_placeholder", -1, "Description", 0, 0, 0, 1.2)




    running = True
    while running:
        # --- CHECK FOR INCOMING NETWORK DATA ---
        try:
            # Non-blocking check for new network messages
            incoming_data = net.INCOMING_QUEUE.get_nowait()

            # Check if the message is the opponent's board update
            if incoming_data.get('type') == 'board_update':
                # Deserialize the received list of card attributes
                serialized_board = incoming_data.get('board', [])

                # Reconstruct the Card objects and replace the old enemy_board
                enemy_board = deserialize_board_data(serialized_board)
                print("Received and updated enemy board.")

                enemy_hand_size = incoming_data.get('len_enemy_hand')
                enemy_money = incoming_data.get('money')
                money += incoming_data.get('money_delta')


            elif incoming_data.get('type') == 'end_turn' and end_turn == True:
                for i, card in enumerate(board):
                    if card.get_counter() > 0:
                        card.tick_counter()
                        for act in cards[card.get_name()]["on_count"].keys():
                            value = cards[card.get_name()]["on_count"][act]
                            if act == "gain_money":
                                money += value
                            if act == "reduce_enemy_money":
                                money_delta -= value
                            if act == "steal_from_shop":
                                buy_free += value
                            if act == "lose_money":
                                money -= value
                            if act == "grow":
                                card.set_power(card.get_power() + value)
                    if card.get_power() < 1:
                        board.pop(i)


                net.send_board_update(board, len(hand), money, money_delta)
                player_power = sysf.power_of(board)
                enemy_power = sysf.power_of(enemy_board)
                if enemy_power > player_power:
                    score -= 1
                elif enemy_power < player_power:
                    score += 1
                end_turn = False
                money_delta = 0

        except queue.Empty:
            # No new messages, just continue the game loop
            pass
        # --- END RECEIVING LOGIC ---

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        m_pos = pygame.mouse.get_pos()

        sysf.adjust_hand(hand)

        col = int(sysf.collision(hand))
        for card in hand:
            if card.get_status() != "drag":
                card.set_scale(1)
        if col > -1:
            hand[col].set_scale(1.2)

        if end_turn == False:
            if pygame.mouse.get_pressed()[0] == 1 and (col > -1 or dragged != None):
                # ... (Dragging logic - Placeholder manipulation)
                if dragged == None:
                    dragged = col
                hand[dragged].set_status("drag")
                if drag_x == 0 and drag_y == 0:
                    drag_x, drag_y = hand[dragged].get_dims()[0] - m_pos[0], hand[dragged].get_dims()[1] - m_pos[1]
                hand[dragged].set_x(m_pos[0] + drag_x)
                hand[dragged].set_y(m_pos[1] + drag_y)

                # Placeholder insertion/removal logic...
                if 100 < m_pos[0] < 1800 and 100 < m_pos[1] < 800:
                    last_placeholder = placeholder_on
                    if placeholder_on == None:
                        board.append(placeholder)
                        last_placeholder = -1
                        placeholder_on = 0

                    # Logic to determine new placeholder position (omitted for brevity)
                    if m_pos[0] < board[0].get_dims()[0]:
                        placeholder_on = 0
                    elif m_pos[0] > board[-1].get_dims()[0]:
                        placeholder_on = len(board) - 1
                    else:
                        for i in range(len(board) - 1):
                            if board[i].get_dims()[0] < m_pos[0] < board[i + 1].get_dims()[0]:
                                placeholder_on = i
                                break

                    # Safely handle popping and inserting placeholder
                    try:
                        board.pop(last_placeholder)
                    except IndexError:
                        if placeholder_on is not None:
                            board.pop(placeholder_on)

                    board.insert(placeholder_on, placeholder)
                else:
                    if placeholder_on != None:
                        board.pop(placeholder_on)
                    placeholder_on = None

            elif dragged != None:
                if playfield['x1'] < m_pos[0] < playfield['x2'] and playfield['y1'] < m_pos[1] < playfield['y2'] and placeholder_on != None:
                    # --- Card successfully placed on board (BOARD CHANGED) ---

                    hand[dragged].set_status("board")
                    hand[dragged].set_scale(1.2)
                    board.pop(placeholder_on)
                    board.insert(placeholder_on, hand[dragged])
                    hand.pop(dragged)
                    placeholder_on = None
                else:
                    # Card returned to hand
                    hand[dragged].set_status("hand")
                    if placeholder_on != None:
                        board.pop(placeholder_on)
                    placeholder_on = None

                dragged = None
                drag_y = 0
                drag_x = 0

            col = sysf.collision(shop)
            if col > -1 and pygame.mouse.get_pressed()[0] == 1 and last_left_mb_state == False:
                if money - shop[col].get_cost() >= 0:
                    hand.append(shop[col])
                    if buy_free == 0:
                        money -= shop[col].get_cost()
                    else:
                        buy_free -= 1
                    if len(deck) > 0:
                        # Assuming this is a simple "buy" action that doesn't affect the board list itself
                        shop[col] = sysf.make_card(deck[-1], id)
                        deck.pop()
                        id += 1
                    else:
                        shop.pop(col)

            if sysf.end_turn(m_pos) and pygame.mouse.get_pressed()[0] == 1 and last_left_mb_state == False:
                end_turn = True

        # --- 3. SENDING LOGIC (Check and send own board updates) ---
        # Current state of the board, represented by a list of card IDs (excluding placeholder)

        if end_turn == True:
            # The board state has changed (card placed/removed/rearranged).
            net.send_end_turn()
        # --- END SENDING LOGIC ---

        sysf.adjust_shop(shop)
        sysf.adjust_board(board)
        sysf.adjust_enemy_board(enemy_board)

        # Note: sysf.power_of() returns a string, so direct use in render() is fine
        player_power = sysf.power_of(board)
        enemy_power = sysf.power_of(enemy_board)

        screen.blit(background, (0, 0))
        if end_turn == True:
            screen.blit(background_pas, (0, 0))

        font = pygame.font.SysFont('Arial', font_size)

        text_surface = font.render(player_power, True, BLACK)
        screen.blit(text_surface, (power_dims["ally_x"], power_dims["ally_y"]))

        text_surface = font.render(enemy_power, True, BLACK)
        screen.blit(text_surface, (power_dims["enemy_x"], power_dims["enemy_y"]))

        text = font.render(str(money), True, GOLD)
        screen.blit(text, (money_dims['x'], money_dims['y']))

        text = font.render(f"Score: {str(score)}", True, BLACK)
        screen.blit(text, (score_dims['x'], score_dims['y']))

        for card in board + enemy_board + hand:
            # Skip drawing the placeholder if it's not currently being hovered/dragged over the board
            if card.get_name() == "card_placeholder" and card not in board:
                continue

            screen.blit(images[card.display()], card.get_dims())
            if card.get_power() > 0:
                text = font.render(str(card.get_power()), True, BLACK)
                screen.blit(text, card.get_dims())

        for card in shop:
            screen.blit(images[card.display()], card.get_dims())
            if card.get_power() > 0:
                text = font.render(str(card.get_power()), True, BLACK)
                screen.blit(text, card.get_dims())
            text = font.render(str(card.get_cost()), True, GOLD)
            screen.blit(text, sysf.cost_dims(card.get_dims()))

        for i in sysf.enemy_hand(enemy_hand_size):
            screen.blit(card_back, i)

        pygame.display.flip()

        last_left_mb_state = pygame.mouse.get_pressed()[0]
