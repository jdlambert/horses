# /// script
# requires-python = ">=3.11"
# dependencies = ["pygame-ce"]
# ///

import asyncio
import pygame

# RCade game dimensions
WIDTH = 336
HEIGHT = 262
FPS = 60
BOARD_SIZE = 4
BOARD_SIZES = (4, 6, 8)
BOARD_PIXELS = 256
PANEL_X = BOARD_PIXELS

# Colors
BACKGROUND = (18, 20, 35)
BOARD_LIGHT = (44, 49, 73)
BOARD_DARK = (34, 38, 59)
WHITE = (245, 247, 255)
MUTED = (164, 174, 202)
P1_COLOR = (74, 181, 255)
P1_TRAIL = (33, 105, 160)
P2_COLOR = (255, 174, 74)
P2_TRAIL = (160, 94, 31)
HIGHLIGHT = (255, 239, 124)
SUCCESS = (114, 225, 164)

KNIGHT_MOVES = (
    (-2, -1),
    (-2, 1),
    (-1, -2),
    (-1, 2),
    (1, -2),
    (1, 2),
    (2, -1),
    (2, 1),
)


def get_legal_moves(position, visited, board_size):
    row, column = position
    moves = []
    for row_delta, column_delta in KNIGHT_MOVES:
        destination = (row + row_delta, column + column_delta)
        destination_row, destination_column = destination
        if 0 <= destination_row < board_size and 0 <= destination_column < board_size:
            if visited[destination_row][destination_column] == 0:
                moves.append(destination)
    return moves


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Horses: Knight's Tour")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_started = False
        self.two_player = False
        self.board_size = BOARD_SIZE
        self.board_size_index = BOARD_SIZES.index(BOARD_SIZE)
        self.cell_size = BOARD_PIXELS // self.board_size
        self.game_over = False
        self.winner = None
        self.current_player = 1
        self.positions = {1: (0, 0), 2: (BOARD_SIZE - 1, BOARD_SIZE - 1)}
        self.visited = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.visited[0][0] = 1
        self.visited[BOARD_SIZE - 1][BOARD_SIZE - 1] = 2
        self.selection_index = 0
        self.ai_timer = 0.0
        self.previous_inputs = self.empty_inputs()

        self.font_large = pygame.font.Font(None, 34)
        self.font_medium = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 17)

    @staticmethod
    def empty_inputs():
        return {
            "p1": {"up": False, "down": False, "left": False, "right": False, "a": False, "b": False, "spinner": 0},
            "p2": {"up": False, "down": False, "left": False, "right": False, "a": False, "b": False, "spinner": 0},
            "system": {"start_1p": False, "start_2p": False},
        }

    def was_pressed(self, inputs, player, button):
        return inputs[player][button] and not self.previous_inputs[player][button]

    def start_game(self, two_player):
        self.game_started = True
        self.game_over = False
        self.two_player = two_player
        self.board_size = BOARD_SIZES[self.board_size_index]
        self.cell_size = BOARD_PIXELS // self.board_size
        self.winner = None
        self.current_player = 1
        self.positions = {1: (0, 0), 2: (self.board_size - 1, self.board_size - 1)}
        self.visited = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.visited[0][0] = 1
        self.visited[self.board_size - 1][self.board_size - 1] = 2
        self.selection_index = 0
        self.ai_timer = 0.0

    def end_game(self, winner):
        self.game_over = True
        self.winner = winner

    def make_move(self, destination):
        legal_moves = get_legal_moves(self.positions[self.current_player], self.visited, self.board_size)
        if destination not in legal_moves:
            return False

        self.positions[self.current_player] = destination
        row, column = destination
        self.visited[row][column] = self.current_player
        self.current_player = 2 if self.current_player == 1 else 1
        self.selection_index = 0
        self.ai_timer = 0.45

        if not get_legal_moves(self.positions[self.current_player], self.visited, self.board_size):
            self.end_game(2 if self.current_player == 1 else 1)
        return True

    def choose_ai_move(self, moves):
        best_move = moves[0]
        best_options = -1
        for move in moves:
            row, column = move
            self.visited[row][column] = 2
            options = len(get_legal_moves(move, self.visited, self.board_size))
            self.visited[row][column] = 0
            if options > best_options:
                best_move = move
                best_options = options
        return best_move

    def update_human(self, inputs, player):
        legal_moves = get_legal_moves(self.positions[player], self.visited, self.board_size)
        if not legal_moves:
            self.end_game(2 if player == 1 else 1)
            return

        controls = "p1" if player == 1 else "p2"
        spinner_delta = int(inputs[controls]["spinner"])
        if spinner_delta:
            self.selection_index = (self.selection_index + spinner_delta) % len(legal_moves)
        if self.was_pressed(inputs, controls, "up") or self.was_pressed(inputs, controls, "left"):
            self.selection_index = (self.selection_index - 1) % len(legal_moves)
        if self.was_pressed(inputs, controls, "down") or self.was_pressed(inputs, controls, "right"):
            self.selection_index = (self.selection_index + 1) % len(legal_moves)
        if self.was_pressed(inputs, controls, "b"):
            self.selection_index = (self.selection_index - 1) % len(legal_moves)
        if self.was_pressed(inputs, controls, "a"):
            self.make_move(legal_moves[self.selection_index])

    def update(self, inputs):
        if not self.game_started:
            spinner_delta = int(inputs["p1"]["spinner"])
            if spinner_delta:
                self.board_size_index = (self.board_size_index + spinner_delta) % len(BOARD_SIZES)
            if self.was_pressed(inputs, "p1", "left") or self.was_pressed(inputs, "p1", "up"):
                self.board_size_index = (self.board_size_index - 1) % len(BOARD_SIZES)
            if self.was_pressed(inputs, "p1", "right") or self.was_pressed(inputs, "p1", "down"):
                self.board_size_index = (self.board_size_index + 1) % len(BOARD_SIZES)
            if self.was_pressed(inputs, "system", "start_1p"):
                self.start_game(False)
            elif self.was_pressed(inputs, "system", "start_2p"):
                self.start_game(True)
        elif self.game_over:
            if self.was_pressed(inputs, "system", "start_1p") or self.was_pressed(inputs, "system", "start_2p"):
                self.start_game(not self.was_pressed(inputs, "system", "start_1p"))
        elif self.current_player == 2 and not self.two_player:
            self.ai_timer -= 1 / FPS
            if self.ai_timer <= 0:
                legal_moves = get_legal_moves(self.positions[2], self.visited, self.board_size)
                if legal_moves:
                    self.make_move(self.choose_ai_move(legal_moves))
                else:
                    self.end_game(1)
        else:
            self.update_human(inputs, self.current_player)

        self.previous_inputs = inputs

    def draw_text(self, text, position, font, color=WHITE):
        self.screen.blit(font.render(text, True, color), position)

    def draw_board(self, inputs):
        for row in range(self.board_size):
            for column in range(self.board_size):
                x = column * self.cell_size
                y = row * self.cell_size
                owner = self.visited[row][column]
                if owner == 1:
                    color = P1_TRAIL
                elif owner == 2:
                    color = P2_TRAIL
                else:
                    color = BOARD_LIGHT if (row + column) % 2 == 0 else BOARD_DARK
                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, (58, 63, 88), (x, y, self.cell_size, self.cell_size), 1)

        if self.game_started and not self.game_over:
            legal_moves = get_legal_moves(self.positions[self.current_player], self.visited, self.board_size)
            if legal_moves:
                selected = legal_moves[self.selection_index % len(legal_moves)]
                row, column = selected
                pygame.draw.rect(
                    self.screen,
                    HIGHLIGHT,
                    (column * self.cell_size + 5, row * self.cell_size + 5, self.cell_size - 10, self.cell_size - 10),
                    3,
                )
                for move in legal_moves:
                    move_row, move_column = move
                    pygame.draw.circle(
                        self.screen,
                        HIGHLIGHT,
                        (move_column * self.cell_size + self.cell_size // 2, move_row * self.cell_size + self.cell_size // 2),
                        3,
                    )

        for player, color in ((1, P1_COLOR), (2, P2_COLOR)):
            row, column = self.positions[player]
            center = (column * self.cell_size + self.cell_size // 2, row * self.cell_size + self.cell_size // 2)
            self.draw_ugly_horse(center, color, player == 1)

    def draw_ugly_horse(self, center, color, faces_right):
        center_x, center_y = center
        direction = 1 if faces_right else -1
        dark_color = tuple(max(channel - 55, 0) for channel in color)
        black = (20, 20, 27)

        body = pygame.Rect(center_x - 10, center_y - 3, 16, 10)
        pygame.draw.rect(self.screen, color, body)
        pygame.draw.rect(self.screen, WHITE, body, 1)
        pygame.draw.polygon(
            self.screen,
            color,
            [
                (center_x + direction * 5, center_y - 5),
                (center_x + direction * 10, center_y - 11),
                (center_x + direction * 12, center_y - 5),
                (center_x + direction * 7, center_y + 2),
            ],
        )
        pygame.draw.polygon(
            self.screen,
            dark_color,
            [
                (center_x + direction * 8, center_y - 10),
                (center_x + direction * 12, center_y - 14),
                (center_x + direction * 14, center_y - 5),
                (center_x + direction * 9, center_y - 4),
            ],
        )
        pygame.draw.rect(self.screen, dark_color, (center_x - 7, center_y + 5, 4, 8))
        pygame.draw.rect(self.screen, dark_color, (center_x + 3, center_y + 5, 4, 8))
        pygame.draw.rect(self.screen, dark_color, (center_x - 12, center_y - 5, 4, 3))
        pygame.draw.rect(self.screen, black, (center_x + direction * 10, center_y - 8, 2, 2))
        pygame.draw.rect(self.screen, black, (center_x - direction * 9, center_y - 7, 5, 2))

    def draw_panel(self, inputs):
        pygame.draw.rect(self.screen, BACKGROUND, (PANEL_X, 0, WIDTH - PANEL_X, HEIGHT))
        self.draw_text("HORSES", (PANEL_X + 8, 10), self.font_medium)
        pygame.draw.line(self.screen, (70, 76, 105), (PANEL_X + 8, 36), (WIDTH - 8, 36))

        if not self.game_started:
            self.draw_text("BOARD", (PANEL_X + 8, 55), self.font_medium, HIGHLIGHT)
            self.draw_text("{} x {}".format(BOARD_SIZES[self.board_size_index], BOARD_SIZES[self.board_size_index]), (PANEL_X + 8, 78), self.font_medium, WHITE)
            self.draw_text("SPIN / D-PAD", (PANEL_X + 8, 108), self.font_small, MUTED)
            self.draw_text("to select size", (PANEL_X + 8, 126), self.font_small, MUTED)
            self.draw_text("1P", (PANEL_X + 8, 151), self.font_medium, P1_COLOR)
            self.draw_text("1P START", (PANEL_X + 8, 160), self.font_small, MUTED)
            self.draw_text("2P", (PANEL_X + 8, 187), self.font_medium, P2_COLOR)
            self.draw_text("2P START", (PANEL_X + 8, 210), self.font_small, MUTED)
            return

        if self.game_over:
            self.draw_text("GAME", (PANEL_X + 8, 55), self.font_medium, SUCCESS)
            self.draw_text("OVER", (PANEL_X + 8, 78), self.font_medium, SUCCESS)
            self.draw_text("P{} wins".format(self.winner), (PANEL_X + 8, 115), self.font_small)
            self.draw_text("START restart", (PANEL_X + 8, 190), self.font_small, MUTED)
            return

        self.draw_text("{}P MODE".format(2 if self.two_player else 1), (PANEL_X + 8, 55), self.font_small, MUTED)
        self.draw_text("P{} TURN".format(self.current_player), (PANEL_X + 8, 78), self.font_medium, P1_COLOR if self.current_player == 1 else P2_COLOR)
        if self.current_player == 2 and not self.two_player:
            self.draw_text("AI THINKS", (PANEL_X + 8, 115), self.font_small, MUTED)
        else:
            self.draw_text("SPIN: choose", (PANEL_X + 8, 115), self.font_small, MUTED)
            self.draw_text("A: move", (PANEL_X + 8, 134), self.font_small, MUTED)
            self.draw_text("B: back", (PANEL_X + 8, 153), self.font_small, MUTED)
        self.draw_text("P1", (PANEL_X + 8, 205), self.font_small, P1_COLOR)
        self.draw_text("P2", (PANEL_X + 48, 205), self.font_small, P2_COLOR)

    def draw(self, inputs):
        self.screen.fill(BACKGROUND)
        self.draw_board(inputs)
        self.draw_panel(inputs)
        pygame.display.flip()

    async def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Get input from RCade controls (bridged from JS)
            inputs = _get_input().to_py()

            self.update(inputs)
            self.draw(inputs)
            self.clock.tick(FPS)
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    game = Game()
    await game.run()


asyncio.run(main())
