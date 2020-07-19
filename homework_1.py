import time
import curses
import random


TIC_TIMEOUT = 0.1


class EventLoopCommand:
    def __await__(self):
        return (yield self)


class BlinkTimeout(EventLoopCommand):
    def __init__(self, timeout):
        self.timeout = timeout


async def do_blinking(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await BlinkTimeout(2)

        canvas.addstr(row, column, symbol)
        await BlinkTimeout(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await BlinkTimeout(0.5)

        canvas.addstr(row, column, symbol)
        await BlinkTimeout(0.3)


async def light_the_star(canvas, row, column, symbol='*'):
    star = do_blinking(canvas, row, column, symbol=symbol)
    await star


def get_stars(canvas):
    line_number, column_number = curses.LINES, curses.COLS
    window_square = line_number * column_number
    star_list = []
    for _ in range(int(window_square / 10)):
        star_line = random.randint(1, line_number - 1)
        star_column = random.randint(1, column_number - 1)
        s = light_the_star(canvas, star_line, star_column)
        star_list.append(s)

    return star_list


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    stars = get_stars(canvas)

    while True:
        for s in stars:
            try:
                blink_timeout = s.send(None)
            except StopIteration:
                break
        canvas.refresh()
        time.sleep(blink_timeout.timeout - TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
