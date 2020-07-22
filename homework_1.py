import asyncio
import time
from collections import defaultdict
import curses
import random


TIC_TIMEOUT = 0.1


class Timeout:
    def __init__(self, seconds):
        self.seconds = seconds

    def __await__(self):
        return (yield self)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await Timeout(2)

        canvas.addstr(row, column, symbol)
        await Timeout(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await Timeout(0.5)

        canvas.addstr(row, column, symbol)
        await Timeout(0.3)


async def fire(
        canvas,
        start_row,
        start_column,
        rows_speed=-0.3,
        columns_speed=0
):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await Timeout(0.4)

    canvas.addstr(round(row), round(column), 'O')
    await Timeout(0.3)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await Timeout(0.2)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def get_stars(canvas, line_number, column_number):
    window_square = line_number * column_number
    stars_per_blink_time = defaultdict(list)
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
        initial_lighting_time = round(time.time() + random.random() * 3, 1)
        stars_per_blink_time[initial_lighting_time].append(star)

    return stars_per_blink_time


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    line_number, column_number = canvas.getmaxyx()
    coroutines = get_stars(canvas, line_number, column_number)
    [[star.send(None) for star in c_list] for c_list in coroutines.values()]
    shot = fire(canvas, line_number / 2, column_number / 2)
    canvas.refresh()
    coroutines[round(time.time() + 0.1)].append(shot)

    while True:
        current_time = round(time.time(), 1)
        coroutines_to_work = coroutines.pop(current_time, [])
        try:
            for coroutine in coroutines_to_work:
                blink_timeout = coroutine.send(None).seconds - TIC_TIMEOUT
                next_light_time = current_time + blink_timeout
                coroutines[round(next_light_time, 1)].append(coroutine)
        except StopIteration:
            canvas.border()
            continue
        canvas.refresh()
        time.sleep(0.01)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
