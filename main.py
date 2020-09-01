import asyncio
import curses
from itertools import cycle
import os.path
import random
import time

from curses_tools import draw_frame, read_controls, get_frame_size
from space_garbage import get_garbage_bodies


TIC_TIMEOUT = 0.1
MIN_TIC_OFFSET = 1
MAX_TIC_OFFSET = 30
ANIMATION_REPEAT_RATE = 2
BORDER_SIZE = 1

SPACESHIP_ANIMATION_FILE_NAMES = ['rocket_frame_1.txt', 'rocket_frame_2.txt']
GARBAGE_ANIMATION_FILE_NAMES = [
    'duck.txt',
    'hubble.txt',
    'lamp.txt',
    'trash_large.txt',
    'trash_small.txt',
    'trash_xl.txt'
]


async def blink(canvas, row, column, offset_tics, symbol='*'):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    for _ in range(offset_tics):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, start_row, start_column, animation_frames):
    row_number, column_number = canvas.getmaxyx()
    frame_sizes = [get_frame_size(frame) for frame in animation_frames]
    max_ship_height = max(frame_sizes, key=lambda x: x[0])[0]
    max_ship_width = max(frame_sizes, key=lambda x: x[1])[1]
    doubled_frames = [
        f for f in animation_frames for _ in range(ANIMATION_REPEAT_RATE)
    ]
    max_row = row_number - BORDER_SIZE
    max_column = column_number - BORDER_SIZE

    for frame in cycle(doubled_frames):
        rows_dir, columns_dir, space_pressed = read_controls(canvas)
        new_row = start_row + rows_dir
        new_column = start_column + columns_dir
        frame_max_row = new_row + max_ship_height
        frame_max_column = new_column + max_ship_width
        new_row = min(frame_max_row, max_row) - max_ship_height
        new_column = min(frame_max_column, max_column) - max_ship_width
        new_row = max(new_row, BORDER_SIZE)
        new_column = max(new_column, BORDER_SIZE)

        start_row, start_column = new_row, new_column
        draw_frame(canvas, start_row, start_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, frame, negative=True)


def get_stars(canvas, line_number, column_number):
    window_square = line_number * column_number
    stars = []
    used_coords = []
    first_line, first_column = 1, 1
    last_active_line, last_active_column = line_number - 2, column_number - 2
    for _ in range(int(window_square / 10)):
        while True:
            star_line = random.randint(first_line, last_active_line)
            star_column = random.randint(first_column, last_active_column)
            if (star_line, star_column) not in used_coords:
                break
        star_symbol = random.choice('+*.:')
        star = blink(
            canvas,
            star_line,
            star_column,
            random.randint(MIN_TIC_OFFSET, MAX_TIC_OFFSET),
            symbol=star_symbol
        )
        used_coords.append((star_line, star_column))
        stars.append(star)

    return stars


def get_frames(file_names):
    frames = []
    for file_name in file_names:
        file_path = os.path.join('animation', file_name)
        with open(file_path, 'r') as file:
            frame = file.read()
        frames.append(frame)

    return frames


def draw(canvas):
    canvas.nodelay(True)
    canvas.border()
    curses.curs_set(False)
    row_number, column_number = canvas.getmaxyx()
    row, column = row_number / 2, column_number / 2
    stars = get_stars(canvas, row_number, column_number)
    shot = fire(canvas, row, column)
    spaceship_frames = get_frames(SPACESHIP_ANIMATION_FILE_NAMES)
    spaceship = animate_spaceship(canvas, row, column, spaceship_frames)
    garbage_frames = get_frames(GARBAGE_ANIMATION_FILE_NAMES)
    garbage_bodies = get_garbage_bodies(canvas, garbage_frames)
    coroutines = [spaceship, shot, *stars, *garbage_bodies]

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        if random.choices([True, False], weights=[1, 5])[0]:
            new_garbage_bodies = get_garbage_bodies(canvas, garbage_frames)
            coroutines.extend(new_garbage_bodies)

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
