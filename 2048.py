from __future__ import annotations
from copy import deepcopy

from random import choice
from typing import (
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Tuple,
)

import pygame

ColourType = Tuple[int, int, int]

# Define some colors
BLACK: Final[ColourType] = (0, 0, 0)
WHITE: Final[ColourType] = (255, 255, 255)
TILE_SIZE: Final[int] = 100
BOARD_SIZE: Final[int] = 4
SCREEN_DIMENSIONS: Final[Tuple[int, int]] = (TILE_SIZE*BOARD_SIZE, TILE_SIZE*BOARD_SIZE)
UNKNOWN_COLOUR: Final[pygame.Color] = pygame.Color("#FFFF00")
BASE_COLOUR: Final[pygame.Color] = pygame.Color("#FFFFFF")
COLOURS: Final[Dict[int, pygame.Color]] = {
    2:    pygame.Color("#7ec0ee"),
    4:    pygame.Color("#EDE0C8"),
    8:    pygame.Color("#F2B179"),
    16:   pygame.Color("#F59563"),
    32:   pygame.Color("#F67C60"),
    64:   pygame.Color("#F65E3B"),
    128:  pygame.Color("#EDCF73"),
    256:  pygame.Color("#EDCC62"),
    512:  pygame.Color("#EDC850"),
    1024: pygame.Color("#EDC53F"),
    2048: pygame.Color("#EDC22D"),
}

global score
score: int = 0


class Tile:
    def __init__(
        self,
        value: Optional[int],
        x: int,
        y: int,
        size: int,
    ) -> None:
        self.value = value
        self.x = x
        self.y = y
        self._size = size

    @property
    def _rect_info(self) -> Tuple[int, int, int, int]:
        return (
            self.pos[0],
            self.pos[1],
            self._size,
            self._size,
        )

    @property
    def colour(self) -> pygame.Color:
        if self.value == 0 or self.value is None:
            return BASE_COLOUR
        return COLOURS.get(self.value, BASE_COLOUR)

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.x*self._size, self.y*self._size)

    @property
    def center_pos(self) -> Tuple[int, int]:
        return (
            int(self.pos[0] + (self._size/2)),
            int(self.pos[1] + (self._size/2)),
        )

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(
            screen,
            self.colour,
            self._rect_info,
        )
        if self.value is not None:
            text = font.render(str(self.value), True, BLACK)
            text_rect = text.get_rect(center=self.center_pos)
            screen.blit(text, text_rect)
            pygame.display.update()


Board = List[List[Tile]]


def check_boards_are_same(old_board: Board, new_board: Board) -> bool:
    for y in range(len(old_board)):
        for x in range(len(old_board[y])):
            if old_board[y][x].value != new_board[y][x].value:
                return False
    return True


def create_board(
    starting_board: bool = False,
    fixed_start: Optional[List[List[int]]] = None,
) -> Board:
    if starting_board and fixed_start is not None:
        raise ValueError("Cannot have `starting_board` and `fixed_start` enabled.")
    board = [
        [
            Tile(
                value=(
                    None if fixed_start is None
                    else (
                        None if fixed_start[y][x] == 0
                        else fixed_start[y][x]
                    )
                ),
                x=x,
                y=y,
                size=TILE_SIZE,
            ) for x in range(BOARD_SIZE)]
        for y in range(BOARD_SIZE)
    ]

    if starting_board:
        for _ in range(max([2, int(BOARD_SIZE/2)])):
            x = choice(range(len(board)))
            y = choice(range(len(board[0])))
            board[y][x].value = choice([2, 4])

    return board

def move_up(board: Board) -> Board:
    global score
    for y in range(len(board)):
        if y == len(board)-1:
            continue
        for x in range(len(board[y])):
            tile_value = board[y][x].value
            tile_below_value = board[y+1][x].value
            if (
                tile_value is None
                and tile_below_value is not None
            ):
                board[y][x].value = tile_below_value
                board[y+1][x].value = None
            elif (
                tile_value == tile_below_value
                and tile_value is not None
            ):
                board[y][x].value = tile_value * 2
                score += tile_value * 2
                board[y+1][x].value = None
    return board


def move_down(board: Board) -> Board:
    global score
    for y in range(len(board)):
        if y == 0:
            continue
        for x in range(len(board[y])):
            tile_value = board[y][x].value
            tile_below_value = board[y-1][x].value
            if (
                tile_value is None
                and tile_below_value is not None
            ):
                board[y][x].value = tile_below_value
                board[y-1][x].value = None
            elif (
                tile_value == tile_below_value
                and tile_value is not None
            ):
                board[y][x].value = tile_value * 2
                score += tile_value * 2
                board[y-1][x].value = None
    return board


def move_left(board: Board) -> Board:
    global score
    for y in range(len(board)):
        for x in range(len(board[y])):
            if x == len(board[y])-1:
                continue
            tile_value = board[y][x].value
            tile_below_value = board[y][x+1].value
            if (
                tile_value is None
                and tile_below_value is not None
            ):
                board[y][x].value = tile_below_value
                board[y][x+1].value = None
            elif (
                tile_value == tile_below_value
                and tile_value is not None
            ):
                board[y][x].value = tile_value * 2
                score += tile_value * 2
                board[y][x+1].value = None
    return board


def move_right(board: Board) -> Board:
    global score
    for y in range(len(board)):
        for x in range(len(board[y])):
            if x == 0:
                continue
            tile_value = board[y][x].value
            tile_below_value = board[y][x-1].value
            if (
                tile_value is None
                and tile_below_value is not None
            ):
                board[y][x].value = tile_below_value
                board[y][x-1].value = None
            elif (
                tile_value == tile_below_value
                and tile_value is not None
            ):
                board[y][x].value = tile_value * 2
                score += tile_value * 2
                board[y][x-1].value = None
    return board


def print_board(board: Board) -> None:
    for y in range(len(board)):
        print("\t".join([str(tile.value or "0") for tile in board[y]]))
    print("=========================")


def complete_move(board: Board, move_func: Callable[..., Board]) -> Tuple[Board, bool]:
    new_board = deepcopy(board)
    for _ in range(BOARD_SIZE**2):
        new_board = move_func(new_board)

    boards_are_same = check_boards_are_same(board, new_board)
    if not boards_are_same:
        board = new_board

    return board, not boards_are_same


def check_more_moves_possible(board: Board) -> bool:
    move_functions = [move_up, move_down, move_left, move_right]
    for move_func in move_functions:
        new_board = deepcopy(board)
        moved_board = move_func(new_board)
        move_changed_board = not check_boards_are_same(board, moved_board)
        if move_changed_board:
            return True
    return False


def draw_loose_screen(screen: pygame.Surface, font: pygame.font.Font) -> None:
    global score
    surface = pygame.Surface(SCREEN_DIMENSIONS)
    surface.set_alpha(128)
    surface.fill(BLACK)
    screen.blit(surface, (0,0))
    text = font.render(f"You lost :(  |  Score: {score}", True, BLACK)
    text_rect = text.get_rect(center=(
        SCREEN_DIMENSIONS[0] / 2,
        SCREEN_DIMENSIONS[1] / 2,
    ))
    screen.blit(text, text_rect)
    pygame.display.update()

def main() -> None:
    pygame.init()
    FONT: Final[pygame.font.Font] = pygame.font.SysFont('Arial', 25)
    board = create_board(starting_board=True)

    screen = pygame.display.set_mode(SCREEN_DIMENSIONS)

    pygame.display.set_caption("2048")

    done = False
    clock = pygame.time.Clock()

    for row in board:
        for tile in row:
            tile.draw(screen, FONT)

    text = FONT.render(f"Score: {score}", True, BLACK)
    text_rect = text.get_rect()
    screen.blit(text, text_rect)

    # print_board(board)

    while not done:
        moved = False
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    done = True
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_UP:
                            board, moved = complete_move(board, move_up)
                        case pygame.K_DOWN:
                            board, moved = complete_move(board, move_down)
                        case pygame.K_LEFT:
                            board, moved = complete_move(board, move_left)
                        case pygame.K_RIGHT:
                             board, moved = complete_move(board, move_right)
                        case _:
                            pass
                case _:
                    pass

        if moved:
            # Find all open positions
            open_positions: List[Tuple[int, int]] = []
            for y in range(len(board)):
                for x in range(len(board[y])):
                    if board[y][x].value is None:
                        open_positions.append((x, y))

            # Add a new tile, if possible.
            if len(open_positions) != 0:
                new_tile_position = choice(open_positions)
                x, y = new_tile_position
                board[y][x].value = choice([2, 4])

            for row in board:
                for tile in row:
                    tile.draw(screen, FONT)

            more_moves_possible = check_more_moves_possible(board)
            if not more_moves_possible:
                draw_loose_screen(screen, FONT)

            else:
                text = FONT.render(f"Score: {score}", True, BLACK)
                text_rect = text.get_rect()
                screen.blit(text, text_rect)

        clock.tick(30)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
