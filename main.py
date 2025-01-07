import threading

import World.AI_Main
import concurrent.futures
import GameInterface.Game_Main as Game_Main
import World.AI_Main as AI_Main
import helper
resume_event = threading.Event()
pause_thread = threading.Event()
import time
import arcade
import threading

lock = threading.Lock()
All_Time = 0

frame_rate = 60
frame_duration = 1.0 / frame_rate

def Game_thread():
    arcade.run()
    # if not pause_thread.is_set():
    #     Game.tick(tick_time)
    # else:
    #     resume_event.wait()  # 等待恢复事件
    #     resume_event.clear()  # 清除恢复事件
    #     pause_thread.clear()


def AI_thread():
    while True:
        AI_GAME.run()




def DeBug_thread():
    while True:
        user_input = input("输入 p 暂停, 输入 r 恢复")
        if user_input == 'p':
            pause_thread.set()
        if user_input == 'r':
            resume_event.set()
            pause_thread.clear()

def start():
    all_tick = 0
    load_path = None
    global Game, AI_GAME, All_Time
    control_by_ai = False
    #load_path = "data/load_game/game_data_11.json"
    Game = Game_Main.start_game(control_by_ai)
    AI_GAME = AI_Main.start_game(Game, load_path)
    thread2 = threading.Thread(target=AI_thread)
    thread3 = threading.Thread(target=DeBug_thread)
    thread2.start()
    thread3.start()
    Game_thread()
    thread2.join()
    thread3.join()
    # while True:
    #     if not pause_thread.is_set():
    #         thread_pool.submit(Game_thread, helper.Game_TICK_TIME)
    #         thread_pool.submit(AI_thread, helper.AI_TICK_TIME)
    #         all_tick += 1
    #     else:
    #         resume_event.wait()  # 等待恢复事件
    #         resume_event.clear()  # 清除恢复事件
    #         pause_thread.clear()

start()