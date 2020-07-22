import asyncio
import time
import curses
import random


TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


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

    while True:
        for s in stars:
            try:
                s.send(None)
            except StopIteration:
                continue
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
