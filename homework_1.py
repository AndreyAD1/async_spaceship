import time
from collections import defaultdict
import curses
import random


TIC_TIMEOUT = 0.1


class EventLoopCommand:
    def __await__(self):
        return (yield self)


class BlinkTimeout(EventLoopCommand):
    def __init__(self, seconds):
        self.seconds = seconds


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await BlinkTimeout(2)

        canvas.addstr(row, column, symbol)
        await BlinkTimeout(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await BlinkTimeout(0.5)

        canvas.addstr(row, column, symbol)
        await BlinkTimeout(0.3)


def get_stars(canvas):
    line_number, column_number = curses.LINES, curses.COLS
    window_square = line_number * column_number
    stars_per_blink_time = defaultdict(list)
    for _ in range(int(window_square / 10)):
        star_line = random.randint(2, line_number - 2)
        star_column = random.randint(2, column_number - 2)
        star_symbol = random.choice('+*.:')
        star = blink(canvas, star_line, star_column, symbol=star_symbol)
        initial_lighting_time = round(time.time() + random.random() * 1.9, 1)
        stars_per_blink_time[initial_lighting_time].append(star)

    return stars_per_blink_time


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    stars = get_stars(canvas)
    [[star.send(None) for star in star_list] for star_list in stars.values()]
    canvas.refresh()

    while True:
        current_time = round(time.time(), 1)
        lighting_stars = stars.pop(current_time, [])
        try:
            for star in lighting_stars:
                blink_timeout = star.send(None)
                next_light_time = current_time + blink_timeout.seconds - TIC_TIMEOUT
                stars[round(next_light_time, 1)].append(star)
        except StopIteration:
            break
        canvas.refresh()
        time.sleep(0.01)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
