import asyncio
import curses
from itertools import cycle
import os.path
import random
import time

from curses_tools import draw_frame, read_controls, get_frame_size


TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*'):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    for _ in range(random.randint(1, 30)):
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
    for frame in cycle(animation_frames):
        try:
            draw_frame(canvas, start_row, start_column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, start_row, start_column, frame, negative=True)
        except asyncio.CancelledError:
            draw_frame(canvas, start_row, start_column, frame, negative=True)
            break


def get_stars(canvas, line_number, column_number):
    window_square = line_number * column_number
    stars = []
    used_coords = []
    for _ in range(int(window_square / 10)):
        while True:
            star_line = random.randint(1, line_number - 2)
            star_column = random.randint(1, column_number - 2)
            if (star_line, star_column) not in used_coords:
                break
        star_symbol = random.choice('+*.:')
        star = blink(canvas, star_line, star_column, symbol=star_symbol)
        used_coords.append((star_line, star_column))
        stars.append(star)

    return stars


def get_spaceship_frames():
    file_names = ['rocket_frame_1.txt', 'rocket_frame_2.txt']
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
    spaceship_frames = get_spaceship_frames()
    frame_sizes = [get_frame_size(frame) for frame in spaceship_frames]
    max_ship_height = max(frame_sizes, key=lambda x: x[0])[0]
    max_ship_width = max(frame_sizes, key=lambda x: x[1])[1]
    spaceship = animate_spaceship(canvas, row, column, spaceship_frames)
    coroutines = [shot, *stars]

    while True:
        for s in coroutines.copy():
            try:
                s.send(None)
            except StopIteration:
                coroutines.remove(s)

        rows_dir, columns_dir, space_pressed = read_controls(canvas)
        if rows_dir or columns_dir:
            new_row = row + rows_dir
            new_column = column + columns_dir
            jutted_left_or_upper_edge = min([new_row, new_column]) <= 0
            jutted_lower_edge = new_row + max_ship_height > row_number
            jutted_right_edge = new_column + max_ship_width > column_number - 1
            spaceship_is_outside_canvas = any([
                    jutted_left_or_upper_edge,
                    jutted_lower_edge,
                    jutted_right_edge
                ]
            )
            if not spaceship_is_outside_canvas:
                row, column = new_row, new_column
                try:
                    spaceship.throw(asyncio.CancelledError)
                except StopIteration:
                    spaceship_frames.append(spaceship_frames.pop(0))
                    spaceship = animate_spaceship(
                        canvas,
                        row,
                        column,
                        spaceship_frames
                    )

        spaceship.send(None)
        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
