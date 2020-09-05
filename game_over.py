from curses_tools import draw_frame
from sleep import sleep

game_over_frame = r"""
   _____                         ____                 
  / ____|                       / __ \                
 | |  __  __ _ _ __ ___   ___  | |  | |_   _____ _ __ 
 | | |_ |/ _` | '_ ` _ \ / _ \ | |  | \ \ / / _ \ '__|
 | |__| | (_| | | | | | |  __/ | |__| |\ V /  __/ |   
  \_____|\__,_|_| |_| |_|\___|  \____/  \_/ \___|_|   
                                                      
"""


async def show_gameover(canvas):
    row_number, column_number = canvas.getmaxyx()
    label_row = row_number / 3
    label_column = column_number / 3
    while True:
        draw_frame(canvas, label_row, label_column, game_over_frame)
        await sleep()
