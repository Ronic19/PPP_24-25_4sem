import asyncio
import websockets
import json


def print_instructions():
        print('\n======= АВТОРИЗАЦИЯ / РЕГИСТРАЦИЯ =======\n')
        print('login email password - вход')
        print('signup email password - регистрация\n')


def correct_format(msg):
    msg = msg.split()
    if len(msg) != 3:
          print({"ERROR": "неверная команда"})
    elif msg[0] != 'login' and msg[0] != 'signup':
         print({"ERROR": "команда должна начинаться с login или signup"})
    else:
         return True
    return False


async def connect_to_server():
    print_instructions()
    msg = input(">>> ")

    while not correct_format(msg):
        print_instructions()
        msg = input(">>> ")

    user_email = msg.split()[1]
    async with websockets.connect(f"ws://localhost:8000/ws/{user_email}") as websocket:

        while msg != 'exit':

            await websocket.send(msg)
            response = await websocket.recv()

            response = json.loads(response)
            if (msg.split()[0] == 'login' or msg.split()[0] == 'signup') and response["status"] == "SUCCESS":
                user_email = response["email"]

            if msg == 'task':
                while response["status"] != "ERROR" and response["status"] != "SUCCESS":
                    print(response)
                    response = await websocket.recv()
                    response = json.loads(response)

            print(response)
        
            print_instructions()
            print('=========== ДЛИТЕЛЬНЫЕ ЗАДАЧИ ===========\n')
            print('task - бинаризация изображения\n')
            print('================= ВЫХОД =================\n')
            print('exit - выход\n')

            msg = input(">>> ")



asyncio.get_event_loop().run_until_complete(connect_to_server())