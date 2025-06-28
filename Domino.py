import pygame
import sys
import random
import os
import pickle
import hashlib

pygame.init()

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
TILE_WIDTH = 65
TILE_HEIGHT = 110
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (150, 205, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 155)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Domino Game")
font = pygame.font.SysFont("Arial", 24)

SAVE_FILE = "domino_game_save.pkl"
USER_DATA_FILE = "user_data.txt"
def save_game(data):
    with open(SAVE_FILE, "wb") as f:
        pickle.dump(data, f)

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "rb") as f:
            return pickle.load(f)
    return None

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return {line.split(",")[0]: line.split(",")[1].strip() for line in f.readlines()}
    return {}

def save_user_data(username, password):
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username},{hashlib.sha256(password.encode()).hexdigest()}\n")


def input_box(prompt):
    input_text = ''
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        screen.fill(GREEN)
        render_text(prompt, font, BLUE, screen, 50, 50)
        render_text(input_text, font, WHITE, screen, 50, 100)

        pygame.display.flip()
    return input_text

def render_text(text, font, color, surface, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def calculate_score(hand):
    return sum(left + right for left, right in hand)

def draw_domino(surface, x, y, width, height, dots1, dots2):
    """Draws a domino shape on the given Pygame surface."""
    pygame.draw.rect(surface, WHITE, (x, y, width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 2)
    mid = y + height // 2
    pygame.draw.line(surface, BLACK, (x, mid), (x + width, mid), 2)

    def draw_dots(dots, cx, cy):
        """Draw dots on one side of the domino."""
        dot_radius = 5
        positions = {
            1: [(0, 0)],
            2: [(-15, -15), (15, 15)],
            3: [(-15, -15), (0, 0), (15, 15)],
            4: [(-15, -15), (15, -15), (-15, 15), (15, 15)],
            5: [(-15, -15), (15, -15), (0, 0), (-15, 15), (15, 15)],
            6: [(-15, -15), (15, -15), (-15, 0), (15, 0), (-15, 15), (15, 15)],
        }
        for dx, dy in positions.get(dots, []):
            pygame.draw.circle(surface, BLACK, (cx + dx, cy + dy), dot_radius)

    draw_dots(dots1, x + width // 2, y + height // 4)
    draw_dots(dots2, x + width // 2, y + 3 * height // 4)

def generate_unique_dominoes():
    dominoes = [(i, j) for i in range(7) for j in range(i, 7)]
    random.shuffle(dominoes)
    return dominoes

def draw_hand(surface, hand, start_x, start_y):
    for i, (left, right) in enumerate(hand):
        draw_domino(surface, start_x + i * (TILE_WIDTH + 10), start_y, TILE_WIDTH, TILE_HEIGHT, left, right)

def can_place(domino, board):
    if not board:
        return True
    left_end = board[0][0]
    right_end = board[-1][1]
    return domino[0] == left_end or domino[1] == right_end or domino[0] == right_end or domino[1] == left_end

def place_domino(domino, board):
    if not board:
        board.append(domino)
    else:
        left_end = board[0][0]
        right_end = board[-1][1]
        if domino[0] == left_end:
            board.insert(0, (domino[1], domino[0]))
        elif domino[1] == left_end:
            board.insert(0, domino)
        elif domino[0] == right_end:
            board.append(domino)
        elif domino[1] == right_end:
            board.append((domino[1], domino[0]))


class Button:
    def __init__(self, x, y, width, height, text, action=None, abled=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.font = pygame.font.SysFont("Arial", 24)
        self.abled = abled

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 200), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surface, (self.x + (self.width - text_surface.get_width()) // 2,
                                    self.y + (self.height - text_surface.get_height()) // 2))

    def is_hovered(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        return self.x < mouse_x < self.x + self.width and self.y < mouse_y < self.y + self.height

    def click(self):
        if self.action and self.abled is True:
            self.action()

def login_window():
    username_input = input_box("Enter your username: ")
    password_input = input_box("Enter your password: ")
    input_active = "username"
    running = True

    enter_button = Button(600, 300, 300, 80, "Submit", game(), True)
    while running:
        screen.fill(GREEN)
        title = font.render("Domino Game", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                mouse_x, mouse_y = event.pos
                if input_active == "username":
                    if event.key == pygame.K_BACKSPACE:
                        username_input = username_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        input_active = "password"
                    else:
                        username_input += event.unicode
                elif input_active == "password":
                    if event.key == pygame.K_BACKSPACE:
                        password_input = password_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        users = load_user_data()
                        if username_input in users and users[username_input] == hashlib.sha256(password_input.encode()).hexdigest():
                            running = False
                            home()
                        else:
                            print("Invalid credentials")
                    else:
                        password_input += event.unicode
        pygame.display.flip()

def register_window():
    username_input = input_box("Enter your username: ")
    password_input = input_box("Enter your password: ")
    confirm_password_input = input_box("Confirm your password: ")

    if password_input == confirm_password_input:
        users = load_user_data()
        if username_input in users:
            print("Username already exists.")
        else:
            save_user_data(username_input, password_input)
            print("Registration successful!")
            login_window()
    else:
        print("Passwords do not match.")
        return False

def login_or_register():
    running = True

    def login():
        login_window()

    def register():
        register_window()

    while running:
        screen.fill(GREEN)
        title = font.render("Domino Game", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        login_button = Button(600, 300, 300,80, "Login", login_window, True)
        register_button = Button(600, 400, 300, 80, "Register", register_window, True)

        login_button.draw(screen)
        register_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if login_button.is_hovered((mouse_x, mouse_y)):
                    login_button.click()
                elif register_button.is_hovered((mouse_x, mouse_y)):
                    register_button.click()

        pygame.display.flip()

def home():
    running = True

    def start_new_game():
        game()

    def continue_game():
        saved_data = load_game()
        if saved_data:
            game(**saved_data)

    new_game_button = Button(600, 300, 300, 80, "New Game", start_new_game, True)
    continue_button = Button(600, 400, 300, 80, "Continue", continue_game, True)

    while running:
        screen.fill(GREEN)
        title = font.render("Domino Game", True, BLUE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        new_game_button.draw(screen)
        continue_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if new_game_button.is_hovered((mouse_x, mouse_y)):
                    new_game_button.click()
                elif continue_button.is_hovered((mouse_x, mouse_y)):
                    continue_button.click()

        pygame.display.flip()


def game(player1_hand=None, player2_hand=None, board=None, current_player=None, all_dominoes=None):
    if player1_hand is None or player2_hand is None or board is None or current_player is None or all_dominoes is None:
        all_dominoes = generate_unique_dominoes()
        player1_hand = all_dominoes[:7]
        player2_hand = all_dominoes[7:14]
        board = []
        current_player = random.choice([1, 2])

    running = True
    clock = pygame.time.Clock()

    def save_current_game():
        save_game({
            "player1_hand": player1_hand,
            "player2_hand": player2_hand,
            "board": board,
            "current_player": current_player,
            "all_dominoes": all_dominoes
        })

    def take_domino():
        nonlocal current_player
        if current_player == 1 and len(all_dominoes) > 14:
            player1_hand.append(all_dominoes[14])
            all_dominoes.pop(14)
        elif current_player == 2 and len(all_dominoes) > 14:
            player2_hand.append(all_dominoes[14])
            all_dominoes.pop(14)

    Domino_taking_button = Button(680, 720, 140, 50, "Take domino", take_domino, True)
    warning_text = None
    can_take = False

    while running:
        screen.fill(GREEN)
        board_width = len(board) * (TILE_WIDTH + 10) - 10
        x_offset = (SCREEN_WIDTH - board_width) // 2
        y_offset = (SCREEN_HEIGHT - TILE_HEIGHT) // 2

        for i, (left, right) in enumerate(board):
            draw_domino(screen, x_offset + i * (TILE_WIDTH + 10), y_offset, TILE_WIDTH, TILE_HEIGHT, left, right)

        if len(player1_hand) > len(player2_hand):
            hand_width = len(player1_hand) * (TILE_WIDTH + 10) - 10
        else:
            hand_width = len(player2_hand) * (TILE_WIDTH + 10) - 10

        player1_x_offset = (SCREEN_WIDTH - hand_width) // 2
        player2_x_offset = (SCREEN_WIDTH - hand_width) // 2

        draw_hand(screen, player1_hand, player1_x_offset, (SCREEN_HEIGHT // 2) - 200)
        draw_hand(screen, player2_hand, player2_x_offset, (SCREEN_HEIGHT // 2) + 100)

        turn_text = font.render(f"Player {current_player}'s Turn", True, BLUE)
        screen.blit(turn_text, (SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 30))

        if warning_text:
            screen.blit(warning_text, (SCREEN_WIDTH // 2 - warning_text.get_width() // 2, SCREEN_HEIGHT // 2 + 280))

        Domino_taking_button.draw(screen)

        if not player1_hand:
            winner_text = font.render("Player 1 Wins!", True, BLUE)
            screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 250))
            score_text = font.render(f"Player 1's Score: {calculate_score(player2_hand)}", True, RED)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 250))
            pygame.display.flip()
            pygame.time.wait(10000)
            running = False

        elif not player2_hand:
            winner_text = font.render("Player 2 Wins!", True, BLUE)
            screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 250))
            score_text = font.render(f"Player 2's Score: {calculate_score(player1_hand)}", True, RED)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 250))
            pygame.display.flip()
            pygame.time.wait(10000)
            running = False

        elif len(all_dominoes) == 14:
            score_text = font.render(f"Player 1's Score: {calculate_score(player2_hand)}", True, RED)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 240))
            score_text = font.render(f"Player 2's Score: {calculate_score(player1_hand)}", True, RED)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 270))
            Domino_taking_button = Button(680, 720, 140, 50, "Take domino", take_domino, False)
            warning_text = None
            pygame.display.flip()
            pygame.time.wait(8000)
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_current_game()
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                placed = False

                if current_player == 1:
                    for i, (left, right) in enumerate(player1_hand):
                        tile_x = player1_x_offset + i * (TILE_WIDTH + 10)
                        tile_y = (SCREEN_HEIGHT // 2) - 200
                        if tile_x < mouse_x < tile_x + TILE_WIDTH and tile_y < mouse_y < tile_y + TILE_HEIGHT:
                            if can_place((left, right), board):
                                place_domino((left, right), board)
                                player1_hand.pop(i)
                                placed = True
                                warning_text = None
                                break
                    if not placed:
                        warning_text = font.render("Invalid move! Press 'Take domino' to pick a new one.", True, RED)
                        can_take = True

                elif current_player == 2:
                    for i, (left, right) in enumerate(player2_hand):
                        tile_x = player2_x_offset + i * (TILE_WIDTH + 10)
                        tile_y = (SCREEN_HEIGHT // 2) + 100
                        if tile_x < mouse_x < tile_x + TILE_WIDTH and tile_y < mouse_y < tile_y + TILE_HEIGHT:
                            if can_place((left, right), board):
                                place_domino((left, right), board)
                                player2_hand.pop(i)
                                placed = True
                                warning_text = None
                                break
                    if not placed:
                        warning_text = font.render("Invalid move! Press 'Take domino' to pick a new one.", True, RED)
                        can_take = True

                if placed:
                    current_player = 2 if current_player == 1 else 1
                    can_take = False

                if Domino_taking_button.is_hovered((mouse_x, mouse_y)) and can_take:
                    warning_text = font.render("Domino taken.", True, RED)
                    Domino_taking_button.click()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    login_or_register()
