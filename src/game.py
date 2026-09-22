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
BOARD_SIZE = 8
BOARD_PIXELS = 256
CELL_SIZE = BOARD_PIXELS // BOARD_SIZE
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


def get_legal_moves(position, visited):
    row, column = position
    moves = []
    for row_delta, column_delta in KNIGHT_MOVES:
        destination = (row + row_delta, column + column_delta)
        destination_row, destination_column = destination
        if 0 <= destination_row < BOARD_SIZE and 0 <= destination_column < BOARD_SIZE:
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
        self.game_over = False
        self.winner = None
        self.current_player = 1
        self.positions = {1: (0, 0), 2: (7, 7)}
        self.visited = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.visited[0][0] = 1
        self.visited[7][7] = 2
        self.selection_index = 0
        self.ai_timer = 0.0
        self.previous_inputs = self.empty_inputs()

        self.font_large = pygame.font.Font(None, 34)
        self.font_medium = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 17)

    @staticmethod
    def empty_inputs():
        return {
            "p1": {"up": False, "down": False, "left": False, "right": False, "a": False, "b": False},
            "p2": {"up": False, "down": False, "left": False, "right": False, "a": False, "b": False},
            "system": {"start_1p": False, "start_2p": False},
        }

    def was_pressed(self, inputs, player, button):
        return inputs[player][button] and not self.previous_inputs[player][button]

    def start_game(self, two_player):
        self.game_started = True
        self.game_over = False
        self.two_player = two_player
        self.winner = None
        self.current_player = 1
        self.positions = {1: (0, 0), 2: (7, 7)}
        self.visited = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.visited[0][0] = 1
        self.visited[7][7] = 2
        self.selection_index = 0
        self.ai_timer = 0.0

    def end_game(self, winner):
        self.game_over = True
        self.winner = winner

    def make_move(self, destination):
        legal_moves = get_legal_moves(self.positions[self.current_player], self.visited)
        if destination not in legal_moves:
            return False

        self.positions[self.current_player] = destination
        row, column = destination
        self.visited[row][column] = self.current_player
        self.current_player = 2 if self.current_player == 1 else 1
        self.selection_index = 0
        self.ai_timer = 0.45

        if not get_legal_moves(self.positions[self.current_player], self.visited):
            self.end_game(2 if self.current_player == 1 else 1)
        return True

    def choose_ai_move(self, moves):
        best_move = moves[0]
        best_options = -1
        for move in moves:
            row, column = move
            self.visited[row][column] = 2
            options = len(get_legal_moves(move, self.visited))
            self.visited[row][column] = 0
            if options > best_options:
                best_move = move
                best_options = options
        return best_move

    def update_human(self, inputs, player):
        legal_moves = get_legal_moves(self.positions[player], self.visited)
        if not legal_moves:
            self.end_game(2 if player == 1 else 1)
            return

        controls = "p1" if player == 1 else "p2"
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
                legal_moves = get_legal_moves(self.positions[2], self.visited)
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
        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                x = column * CELL_SIZE
                y = row * CELL_SIZE
                owner = self.visited[row][column]
                if owner == 1:
                    color = P1_TRAIL
                elif owner == 2:
                    color = P2_TRAIL
                else:
                    color = BOARD_LIGHT if (row + column) % 2 == 0 else BOARD_DARK
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, (58, 63, 88), (x, y, CELL_SIZE, CELL_SIZE), 1)

        if self.game_started and not self.game_over:
            legal_moves = get_legal_moves(self.positions[self.current_player], self.visited)
            if legal_moves:
                selected = legal_moves[self.selection_index % len(legal_moves)]
                row, column = selected
                pygame.draw.rect(
                    self.screen,
                    HIGHLIGHT,
                    (column * CELL_SIZE + 5, row * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10),
                    3,
                )
                for move in legal_moves:
                    move_row, move_column = move
                    pygame.draw.circle(
                        self.screen,
                        HIGHLIGHT,
                        (move_column * CELL_SIZE + CELL_SIZE // 2, move_row * CELL_SIZE + CELL_SIZE // 2),
                        3,
                    )

        for player, color in ((1, P1_COLOR), (2, P2_COLOR)):
            row, column = self.positions[player]
            center = (column * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)
            pygame.draw.circle(self.screen, color, center, 10)
            pygame.draw.circle(self.screen, WHITE, center, 10, 2)

    def draw_panel(self, inputs):
        pygame.draw.rect(self.screen, BACKGROUND, (PANEL_X, 0, WIDTH - PANEL_X, HEIGHT))
        self.draw_text("HORSES", (PANEL_X + 8, 10), self.font_medium)
        pygame.draw.line(self.screen, (70, 76, 105), (PANEL_X + 8, 36), (WIDTH - 8, 36))

        if not self.game_started:
            self.draw_text("1P", (PANEL_X + 8, 55), self.font_medium, P1_COLOR)
            self.draw_text("1P START", (PANEL_X + 8, 78), self.font_small, MUTED)
            self.draw_text("2P", (PANEL_X + 8, 111), self.font_medium, P2_COLOR)
            self.draw_text("2P START", (PANEL_X + 8, 134), self.font_small, MUTED)
            self.draw_text("D-PAD + A", (PANEL_X + 8, 186), self.font_small, MUTED)
            self.draw_text("to move", (PANEL_X + 8, 204), self.font_small, MUTED)
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
            self.draw_text("D-pad: choose", (PANEL_X + 8, 115), self.font_small, MUTED)
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
