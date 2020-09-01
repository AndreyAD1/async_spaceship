import asyncio
import random

from curses_tools import draw_frame


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


def get_garbage_bodies(canvas, garbage_frames):
    _, column_number = canvas.getmaxyx()
    garbage_bodies = []
    body_number = random.randint(0, 4)
    for _ in range(body_number):
        garbage_frame = random.choice(garbage_frames)
        garbage_column = random.randrange(1, column_number)
        garbage_body = fly_garbage(canvas, garbage_column, garbage_frame)
        garbage_bodies.append(garbage_body)

    return garbage_bodies
