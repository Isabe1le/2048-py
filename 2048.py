from __future__ import annotations

from random import choice
from typing import (
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
TILE_SIZE: Final[int] = 150
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

class Tile:
    def __init__(
        self,
        value: Optional[int],
        x: int,
        y: int,
        font: pygame.font.Font,
        size: int,
    ) -> None:
        self.value = value
        self.x = x
        self.y = y
        self.font = font
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

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            self.colour,
            self._rect_info,
        )
        if self.value is not None:
            text = self.font.render(str(self.value), True, BLACK)
            text_rect = text.get_rect(center=self.center_pos)
            screen.blit(text, text_rect)
            pygame.display.update()


Board = List[List[Tile]]


def check_move_complete(old_board: Board, new_board: Board) -> bool:
    for y in range(len(old_board)):
        for x in range(len(old_board[y])):
            if old_board[y][x].value != new_board[y][x].value:
                return False
    return True


def create_board(font: pygame.font.Font, starting_board: bool = False) -> Board:
    board = [
        [
            Tile(
                value=None,
                x=x,
                y=y,
                font=font,
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

def move_up(old_board: Board) -> Board:
    new_board = create_board(font=old_board[0][0].font)
    # range(len(x)-1, -1, -1) : returns List[int] of decending indexes n long.
    # TODO: find a nicer way to do this
    new_board[0] = old_board[0]
    for y in range(len(old_board)-1, -1, -1):
        if y == 0:
            continue
        for x in range(len(old_board[y])):
            if old_board[y][x].value is None:
                continue
            elif old_board[y-1][x].value == old_board[y][x].value:
                new_board[y-1][x].value = old_board[y][x].value * 2 # type: ignore[reportOptionalOperand] (type checker wrong)
            elif old_board[y-1][x].value is None:
                new_board[y-1][x].value = old_board[y][x].value
            elif new_board[y][x].value is None:
                new_board[y][x].value = old_board[y][x].value
    return new_board


def move_down(old_board: Board) -> Board:
    new_board = create_board(font=old_board[0][0].font)
    new_board[-1] = old_board[-1]
    for y in range(len(old_board)):
        if y == len(old_board)-1:
            continue
        for x in range(len(old_board[y])):
            if old_board[y][x].value is None:
                continue
            elif old_board[y+1][x].value == old_board[y][x].value:
                new_board[y+1][x].value = old_board[y][x].value * 2 # type: ignore[reportOptionalOperand] (type checker wrong)
            elif old_board[y+1][x].value is None:
                new_board[y+1][x].value = old_board[y][x].value
            elif new_board[y][x].value is None:
                new_board[y][x].value = old_board[y][x].value
    return new_board


def move_left(old_board: Board) -> Board:
    new_board = create_board(font=old_board[0][0].font)

    for y in range(len(old_board)):
        for x in range(len(old_board[y])):
            if x == 0:
                new_board[y][x] = old_board[y][x]

    for y in range(len(old_board)):
        for x in range(len(old_board[y])):
            if x == 0:
                continue
            if old_board[y][x].value is None:
                continue
            elif old_board[y][x-1].value == old_board[y][x].value:
                new_board[y][x-1].value = old_board[y][x].value * 2 # type: ignore[reportOptionalOperand] (type checker wrong)
            elif old_board[y][x-1].value is None:
                new_board[y][x-1].value = old_board[y][x].value
            elif new_board[y][x].value is None:
                new_board[y][x].value = old_board[y][x].value
    return new_board


def move_right(old_board: Board) -> Board:
    new_board = create_board(font=old_board[0][0].font)

    for y in range(len(old_board)):
        for x in range(len(old_board[y])):
            if x == len(old_board)-1:
                new_board[y][x] = old_board[y][x]

    for y in range(len(old_board)):
        for x in range(len(old_board[y])):
            if x == len(old_board)-1:
                continue
            if old_board[y][x].value is None:
                continue
            elif old_board[y][x+1].value == old_board[y][x].value:
                new_board[y][x+1].value = old_board[y][x].value * 2 # type: ignore[reportOptionalOperand] (type checker wrong)
            elif old_board[y][x+1].value is None:
                new_board[y][x+1].value = old_board[y][x].value
            elif new_board[y][x].value is None:
                new_board[y][x].value = old_board[y][x].value
    return new_board


def print_board(board: Board) -> None:
    for y in range(len(board)):
        print("\t".join([str(tile.value or "0") for tile in board[y]]))
    print("=============")


def main() -> None:
    pygame.init()
    FONT: Final[pygame.font.Font] = pygame.font.SysFont('Arial', 25)
    board = create_board(font=FONT, starting_board=True)

    screen = pygame.display.set_mode(SCREEN_DIMENSIONS)

    pygame.display.set_caption("2048")

    done = False
    clock = pygame.time.Clock()

    for row in board:
        for tile in row:
            tile.draw(screen)
    print_board(board)

    while not done:
        moved = False
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    done = True
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_UP:
                            moved = True
                            new_board = move_up(board)
                            permutated_board = new_board
                            while True:
                                permutated_board = move_up(permutated_board)
                                move_complete = check_move_complete(permutated_board, new_board)
                                new_board = permutated_board
                                if move_complete:
                                    break
                            board = new_board
                        case pygame.K_DOWN:
                            moved = True
                            new_board = move_down(board)
                            permutated_board = new_board
                            while True:
                                permutated_board = move_down(permutated_board)
                                move_complete = check_move_complete(permutated_board, new_board)
                                new_board = permutated_board
                                if move_complete:
                                    break
                            board = new_board
                        case pygame.K_LEFT:
                            moved = True
                            new_board = move_left(board)
                            permutated_board = new_board
                            while True:
                                permutated_board = move_left(permutated_board)
                                move_complete = check_move_complete(permutated_board, new_board)
                                new_board = permutated_board
                                if move_complete:
                                    break
                            board = new_board
                        case pygame.K_RIGHT:
                            moved = True
                            new_board = move_right(board)
                            permutated_board = new_board
                            while True:
                                permutated_board = move_right(permutated_board)
                                move_complete = check_move_complete(permutated_board, new_board)
                                new_board = permutated_board
                                if move_complete:
                                    break
                            board = new_board
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
                    tile.draw(screen)

            print_board(board)

        clock.tick(5)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
