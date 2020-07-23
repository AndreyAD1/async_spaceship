import asyncio
import time
import curses
import random


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


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    line_number, column_number = canvas.getmaxyx()
    stars = get_stars(canvas, line_number, column_number)
    shot = fire(canvas, line_number / 2, column_number / 2)
    coroutines = [shot, *stars]

    while True:
        for s in coroutines.copy():
            try:
                s.send(None)
            except StopIteration:
                coroutines.remove(s)
                canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
