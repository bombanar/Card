import pygame
import sys
import json

with open('config.json') as json_data_file:
    config = json.load(json_data_file)

# --- Configuration Constants (Same as previous context) ---
SCREEN_WIDTH = config["screen_width"]
SCREEN_HEIGHT = config["screen_height"]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
GRAY = (150, 150, 150)
RED = (200, 50, 50)  # Color for active input box

# --- Initialization (Assuming pygame.init() is run once) ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("IP Input Interface")
font = pygame.font.SysFont('Arial', 32)
clock = pygame.time.Clock()
pygame.scrap.init()


def text_input_interface():
    """
    Displays an interface for user to input a Host IP address.
    Handles keyboard input, pasting (Ctrl+V or Cmd+V), and drawing.
    """
    input_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 40)

    # State variables
    user_text = 'host'  # Default text
    active = False  # Is the box currently being typed into?

    interface_running = True

    while interface_running:

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle active state if the mouse clicks inside the box
                if input_box_rect.collidepoint(event.pos):
                    active = not active
                else:
                    active = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    print(f"IP Submitted: {user_text}")
                    return user_text  # Return the IP and exit the function
                if active:
                    # Check for Enter key to "submit" the input

                    # Check for Backspace
                    if event.key == pygame.K_BACKSPACE:
                        user_text = ''

                    # --- Clipboard/Pasting Check (Ctrl+V or Cmd+V) ---
                    elif (event.key == pygame.K_v and
                          (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META)):
                        try:
                            # Get clipboard content
                            pasted_text = pygame.scrap.get(pygame.SCRAP_TEXT)
                            # Pygame scrap returns bytes; decode to string
                            if pasted_text:
                                user_text += pasted_text.decode('utf-8').strip('\x00').strip()
                        except pygame.error:
                            print("Clipboard access failed or Pygame scrap module not initialized.")

                    # Standard character input
                    else:
                        # Limit input length if desired (e.g., max 15 chars for IPv4)
                        if len(user_text) < 20:
                            user_text += event.unicode

        # --- Drawing and Updating ---
        screen.fill(BLACK)

        # 1. Draw "Host IP:" label (no change needed here)
        label_surface = font.render("Host IP:", True, WHITE)
        # Position the label slightly to the left of the input box
        label_rect = label_surface.get_rect(midright=(input_box_rect.centerx, input_box_rect.centery - 50))
        screen.blit(label_surface, label_rect)

        # 2. Draw Input Box Border (The color logic remains the same)
        color = RED if active else GRAY
        # The rect position used for drawing will be updated later

        # 3. Draw Input Text
        if user_text:
            text_surface = font.render(user_text, True, WHITE)

            # --- CENTERING CORRECTION STARTS HERE ---

            # Calculate the new width based on text
            new_width = max(200, text_surface.get_width() + 10)

            # Update the width and recalculate the x-position for centering
            input_box_rect.w = new_width
            input_box_rect.x = (SCREEN_WIDTH // 2) - (new_width // 2)

            # Draw the input box border with the new, centered coordinates
            pygame.draw.rect(screen, color, input_box_rect, 2)

            # Position and draw the text inside the newly centered box
            screen.blit(text_surface, (input_box_rect.x + 5, input_box_rect.y + 5))

        else:
            # If user_text is empty, ensure the box is still drawn/centered
            # with its default width
            default_width = 200
            input_box_rect.w = default_width
            input_box_rect.x = (SCREEN_WIDTH // 2) - (default_width // 2)
            pygame.draw.rect(screen, color, input_box_rect, 2)

        # 4. Draw instructions (no change needed here)
        inst_text = font.render("Press ENTER to connect. (host is for hosting)", True, GRAY)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        screen.blit(inst_text, inst_rect)

        pygame.display.flip()
        clock.tick(30)