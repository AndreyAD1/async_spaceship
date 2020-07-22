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


def get_stars(canvas):
    line_number, column_number = curses.LINES, curses.COLS
    window_square = line_number * column_number
    star_list = []
    # for _ in range(int(window_square / 5)):
    for _ in range(5):
        star_line = random.randint(1, line_number)
        star_column = random.randint(1, column_number)
        s = blink(canvas, star_line, star_column)
        star_list.append(s)

    return star_list


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    stars = get_stars(canvas)

    while True:
        for s in stars:
            try:
                s.send(None)
            except StopIteration:
                continue
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
