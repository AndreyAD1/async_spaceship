import asyncio
import curses
from itertools import cycle
import os.path
import random
import time

from curses_tools import draw_frame, read_controls, get_frame_size
from explosion import explode
from game_over import show_gameover
from obstacles import Obstacle
from physics import update_speed
from sleep import sleep


TIC_TIMEOUT = 0.1
MIN_TIC_OFFSET = 1
MAX_TIC_OFFSET = 30
ANIMATION_REPEAT_RATE = 2
BORDER_SIZE = 1
OFFSET_TO_SPACESHIP_EDGE = 2

SPACESHIP_ANIMATION_FILE_NAMES = ['rocket_frame_1.txt', 'rocket_frame_2.txt']
GARBAGE_ANIMATION_FILE_NAMES = [
    'duck.txt',
    'hubble.txt',
    'lamp.txt',
    'trash_large.txt',
    'trash_small.txt',
    'trash_xl.txt'
]

coroutines = []
obstacles = []
obstacles_in_last_collisions = []
spaceship_frame = ''


async def blink(canvas, row, column, offset_tics, symbol='*'):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    await sleep(offset_tics)

    while True:
        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await sleep()

    canvas.addstr(round(row), round(column), 'O')
    await sleep()
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return

        canvas.addstr(round(row), round(column), symbol)
        await sleep()
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def run_spaceship(canvas, start_row, start_column):
    row_number, column_number = canvas.getmaxyx()
    max_row = row_number - BORDER_SIZE
    max_column = column_number - BORDER_SIZE
    row_speed = column_speed = 0

    while True:
        rows_direction, columns_direction, pressed_space = read_controls(canvas)
        row_speed, column_speed = update_speed(
            row_speed,
            column_speed,
            rows_direction / 10,
            columns_direction / 10
        )
        new_row = start_row + row_speed
        new_column = start_column + column_speed
        ship_height, ship_width = get_frame_size(spaceship_frame)
        frame_max_row = new_row + ship_height
        frame_max_column = new_column + ship_width
        new_row = min(frame_max_row, max_row) - ship_height
        new_column = min(frame_max_column, max_column) - ship_width
        new_row = max(new_row, BORDER_SIZE)
        new_column = max(new_column, BORDER_SIZE)

        start_row, start_column = new_row, new_column
        draw_frame(canvas, start_row, start_column, spaceship_frame)
        drawn_frame = spaceship_frame

        if pressed_space:
            fire_column = start_column + OFFSET_TO_SPACESHIP_EDGE
            coroutines.append(fire(canvas, start_row, fire_column))

        await sleep()
        draw_frame(canvas, start_row, start_column, drawn_frame, negative=True)

        ship_collided = False
        for obstacle in obstacles:
            ship_collided = ship_collided or obstacle.has_collision(
                start_row,
                start_column,
                obj_size_rows=ship_height,
                obj_size_columns=ship_width
            )

        if ship_collided:
            break

    await show_gameover(canvas)


async def animate_spaceship(animation_frames):
    for frame in cycle(animation_frames):
        global spaceship_frame
        spaceship_frame = frame
        await sleep(2)


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


async def fill_orbit_with_garbage(canvas, garbage_frames):
    _, column_number = canvas.getmaxyx()
    while True:
        new_garbage_appears = random.choices([True, False], weights=[1, 6])[0]
        if new_garbage_appears:
            garbage_frame = random.choice(garbage_frames)
            garbage_column = random.randrange(1, column_number)
            garbage_body = fly_garbage(canvas, garbage_column, garbage_frame)
            coroutines.append(garbage_body)
        await sleep()


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)
    obstacle_height, obstacle_width = get_frame_size(garbage_frame)
    obstacle = Obstacle(
        0,
        column,
        rows_size=obstacle_height,
        columns_size=obstacle_width
    )
    obstacles.append(obstacle)

    row = 0

    while row < rows_number and obstacle not in obstacles_in_last_collisions:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row = row

    if obstacle in obstacles_in_last_collisions:
        center_obstacle_row = row + obstacle_height / 2
        center_obstacle_column = column + obstacle_width / 2
        await explode(canvas, center_obstacle_row, center_obstacle_column)
        obstacles_in_last_collisions.remove(obstacle)

    obstacles.remove(obstacle)


async def show_obstacles(canvas):
    """Display bounding boxes of every obstacle in a list"""

    while True:
        boxes = []

        for obstacle in obstacles:
            boxes.append(obstacle.dump_bounding_box())

        for row, column, frame in boxes:
            draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        for row, column, frame in boxes:
            draw_frame(canvas, row, column, frame, negative=True)


def draw(canvas):
    canvas.nodelay(True)
    canvas.border()
    curses.curs_set(False)
    row_number, column_number = canvas.getmaxyx()
    row, column = row_number / 2, column_number / 2

    stars = get_stars(canvas, row_number, column_number)
    coroutines.extend(stars)

    spaceship_frames = get_frames(SPACESHIP_ANIMATION_FILE_NAMES)
    spaceship = animate_spaceship(spaceship_frames)
    spaceship.send(None)
    coroutines.append(spaceship)

    spaceship_motion = run_spaceship(canvas, row, column)
    coroutines.append(spaceship_motion)

    garbage_frames = get_frames(GARBAGE_ANIMATION_FILE_NAMES)
    new_garbage_bodies = fill_orbit_with_garbage(canvas, garbage_frames)
    coroutines.append(new_garbage_bodies)
    obstacle_borders = show_obstacles(canvas)
    coroutines.append(obstacle_borders)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        canvas.border()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
