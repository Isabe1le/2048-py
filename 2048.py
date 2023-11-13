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
from pygame import (
    Color as Colour,
    Surface,
    event as pyg_event,
    init as pyg_game_init,
    quit,
)
from pygame.display import (
    flip,
    set_caption,
    set_mode,
    update,
)
from pygame.draw import rect
from pygame.font import (
    Font,
    SysFont,
    init as pyg_font_init,
)
from pygame.time import Clock


pyg_font_init()


# Define some colors
BLACK: Final[Colour] = Colour("#000000")
UNKNOWN_COLOUR: Final[Colour] = Colour("#FFFF00")
BASE_COLOUR: Final[Colour] = Colour("#FFFFFF")
COLOURS: Final[Dict[int, Colour]] = {
    2:    Colour("#7ec0ee"),
    4:    Colour("#EDE0C8"),
    8:    Colour("#F2B179"),
    16:   Colour("#F59563"),
    32:   Colour("#F67C60"),
    64:   Colour("#F65E3B"),
    128:  Colour("#EDCF73"),
    256:  Colour("#EDCC62"),
    512:  Colour("#EDC850"),
    1024: Colour("#EDC53F"),
    2048: Colour("#EDC22D"),
}

# Define game settings (editable)
TILE_SIZE_PX: Final[int] = 100
FONT_NAME: Final[str] = "Arial"
FPS: Final[int] = 30
BOARD_SIZE: Final[Pos] = (4, 4)
SPAWNING_WEIGHTS: Final[Dict[int, float]] = {
    2: 0.9,
    4: 0.1,
}
KEYBINDS: Final[Dict[int, str]] = {
    pygame.K_UP:    'move_up',
    pygame.K_DOWN:  'move_down',
    pygame.K_LEFT:  'move_left',
    pygame.K_RIGHT: 'move_right',
}


# Calculated constants (don't edit)
SCREEN_DIMENSIONS: Final[Pos] = (
    int(TILE_SIZE_PX*BOARD_SIZE[0]),
    int(TILE_SIZE_PX*BOARD_SIZE[1]),
)
PADDING_BETWEEN_TILES_PX: Final[int] = int(TILE_SIZE_PX/20)
FONT_SIZE: Final[int] = int(TILE_SIZE_PX/4)
FONT: Final[Font] = SysFont(FONT_NAME, FONT_SIZE)
INNER_RECT_INFO_BOUNDING_SIZE: Final[int] = TILE_SIZE_PX-PADDING_BETWEEN_TILES_PX*2
HALF_TILE_SIZE_PX: Final[int] = int(TILE_SIZE_PX/2)


# Define custom types
Board = List[List['Tile']]
RectPos = Tuple[int, int, int, int]
Pos = Tuple[int, int]


# Game score
global score
score: int = 0


class Tile:
    __slots__: Final[Tuple[str, ...]] = (
        "value",
        "x",
        "y",
    )

    def __init__(
        self,
        value: Optional[int],
        x: int,
        y: int,
    ) -> None:
        self.value = value
        self.x = x
        self.y = y

    @property
    def _rect_info(self) -> RectPos:
        return (
            self.pos[0],
            self.pos[1],
            TILE_SIZE_PX,
            TILE_SIZE_PX,
        )

    @property
    def _inner_rect_info(self) -> RectPos:
        return (
            self.pos[0]+PADDING_BETWEEN_TILES_PX,
            self.pos[1]+PADDING_BETWEEN_TILES_PX,
            INNER_RECT_INFO_BOUNDING_SIZE,
            INNER_RECT_INFO_BOUNDING_SIZE,
        )

    @property
    def colour(self) -> Colour:
        if self.value == 0 or self.value is None:
            return BASE_COLOUR
        return COLOURS.get(self.value, BASE_COLOUR)

    @property
    def pos(self) -> Pos:
        return (self.x*TILE_SIZE_PX, self.y*TILE_SIZE_PX)

    @property
    def center_pos(self) -> Pos:
        return (
            int(self.pos[0] + HALF_TILE_SIZE_PX),
            int(self.pos[1] + HALF_TILE_SIZE_PX),
        )

    def draw(self, screen: Surface, font: Font) -> None:
        rect(
            screen,
            BASE_COLOUR,
            self._rect_info,
        )

        if self.value is not None:
            rect(
                screen,
                self.colour,
                self._inner_rect_info,
            )
            text = font.render(str(self.value), True, BLACK)
            text_rect = text.get_rect(center=self.center_pos)
            screen.blit(text, text_rect)
            update()


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
            ) for x in range(BOARD_SIZE[0])]
        for y in range(BOARD_SIZE[1])
    ]

    if starting_board:
        for _ in range(max([2, int(min(BOARD_SIZE[0], BOARD_SIZE[1])/2)])):
            x = choice(range(len(board[0])))-1
            y = choice(range(len(board)))-1
            board[y][x].value = _random_new_tile()

    return board


def _random_new_tile() -> int:
    weighted_list: List[int] = []
    for tile, weight in SPAWNING_WEIGHTS.items():
        weight = int(weight * 100)
        weighted_list.extend([tile for _ in range(weight)])
    return choice(weighted_list)


def move_up(board: Board, merges: bool = False) -> Board:
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
                and merges
            ):
                board[y][x].value = tile_value * 2
                score += tile_value * 2
                board[y+1][x].value = None
    return board


def move_down(board: Board, merges: bool = False) -> Board:
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
                and merges
            ):
                board[y][x].value = tile_value * 2
                score += tile_value * 2
                board[y-1][x].value = None
    return board


def move_left(board: Board, merges: bool = False) -> Board:
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
                and merges
            ):
                board[y][x].value = tile_value * 2
                score += tile_value * 2
                board[y][x+1].value = None
    return board


def move_right(board: Board, merges: bool = False) -> Board:
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
                and merges
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

    for _ in range(max(BOARD_SIZE[0], BOARD_SIZE[1])**2):
        new_board = move_func(new_board)
    new_board = move_func(new_board, merges=True)
    for _ in range(max(BOARD_SIZE[0], BOARD_SIZE[1])**2):
        new_board = move_func(new_board)

    boards_are_same = check_boards_are_same(board, new_board)
    if not boards_are_same:
        board = new_board

    return board, not boards_are_same


def check_more_moves_possible(board: Board) -> bool:
    move_functions = [move_up, move_down, move_left, move_right]
    for move_func in move_functions:
        new_board = deepcopy(board)
        moved_board = move_func(new_board, merges=True)
        move_changed_board = not check_boards_are_same(board, moved_board)
        if move_changed_board:
            return True
    return False


def draw_loose_screen(screen: Surface, font: Font) -> None:
    global score
    surface = Surface(SCREEN_DIMENSIONS)
    surface.set_alpha(128)
    surface.fill(BLACK)
    screen.blit(surface, (0,0))
    text = font.render(f"You lost :(  |  Score: {score}", True, BLACK)
    text_rect = text.get_rect(center=(
        SCREEN_DIMENSIONS[0] / 2,
        SCREEN_DIMENSIONS[1] / 2,
    ))
    screen.blit(text, text_rect)
    update()

def main() -> None:
    pyg_game_init()
    board = create_board(starting_board=True)

    screen = set_mode(SCREEN_DIMENSIONS)

    set_caption("2048")

    done = False
    clock = Clock()

    for row in board:
        for tile in row:
            tile.draw(screen, FONT)

    text = FONT.render(f"Score: {score}", True, BLACK)
    text_rect = text.get_rect()
    screen.blit(text, text_rect)

    # print_board(board)

    while not done:
        moved = False
        for event in pyg_event.get():
            match event.type:
                case pygame.QUIT:
                    done = True
                case pygame.KEYDOWN:
                    move_func = KEYBINDS.get(event.key, None)
                    if move_func is not None:
                        move_func = globals()[move_func]
                        board, moved = complete_move(board, move_func)
                case _:
                    pass

        if moved:
            # Find all open positions
            open_positions: List[Pos] = []
            for y in range(len(board)):
                for x in range(len(board[y])):
                    if board[y][x].value is None:
                        open_positions.append((x, y))

            # Add a new tile, if possible.
            if len(open_positions) != 0:
                new_tile_position = choice(open_positions)
                x, y = new_tile_position
                board[y][x].value = _random_new_tile()

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

        clock.tick(FPS)
        flip()
    quit()


if __name__ == "__main__":
    main()
