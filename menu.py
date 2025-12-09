import pygame
import join_game
import os
import sys  # Used for quitting the game
import json

with open('config.json') as json_data_file:
    config = json.load(json_data_file)

# --- Configuration Constants (Same as previous context) ---
SCREEN_WIDTH = config["screen_width"]
SCREEN_HEIGHT = config["screen_height"]

# --- Configuration Constants ---
pygame.init()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)  # Color for hover
GRAY = (150, 150, 150)  # Default text color

os.environ['SDL_VIDEO_CENTERED'] = '1'

# --- Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bombad")
# Using a system font for simplicity
font_size = 50
font = pygame.font.SysFont('Arial', font_size, bold=True)
clock = pygame.time.Clock()


def main_menu():
    """
    Displays the main menu with Join Game, Deck Editor, and Quit options.
    Handles mouse hover and click events.
    """
    menu_running = True

    # Define menu options and their respective actions
    menu_items = {
        "JOIN GAME": lambda: print("Action: Starting a game..."),
        "DECK EDITOR": lambda: print("Action: Opening Deck Editor..."),
        "QUIT": lambda: print("Action: Quiting...")
    }

    # Calculate initial positions for text rendering
    text_y_start = 150
    spacing = 100

    # Store the rendered text and their bounding rectangles
    # This allows for easy collision checking later
    menu_surfaces = {}

    for i, (text, action) in enumerate(menu_items.items()):
        # Render the text initially (we'll re-render on hover)
        text_surface = font.render(text, True, GRAY)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, text_y_start + i * spacing))

        menu_surfaces[text] = {
            'surface': text_surface,
            'rect': text_rect,
            'action': action
        }

    while menu_running:
        # Get the current mouse position for hover checks
        mouse_pos = pygame.mouse.get_pos()

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check for clicks on all menu items
                    for text, item in menu_surfaces.items():
                        if item['rect'].collidepoint(mouse_pos):
                            # Execute the action associated with the clicked item
                            item['action']()
                            # If the action was not QUIT, we might want to exit the menu loop
                            if text == "JOIN GAME":
                                text = join_game.text_input_interface()
                            return  text

        # --- Drawing and Updating ---
        screen.fill(BLACK)

        # Draw a title
        title_surface = font.render("MAIN MENU", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)

        # Draw menu items
        for text, item in menu_surfaces.items():
            # Check for hover
            is_hovering = item['rect'].collidepoint(mouse_pos)
            color = GREEN if is_hovering else GRAY

            # Re-render the text with the appropriate color
            current_surface = font.render(text, True, color)

            # Blit the text onto the screen
            screen.blit(current_surface, item['rect'])

        # Update the full display surface to the screen
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)
