import asyncio
import websockets
import json


def print_instructions():
        print('\n\n=========АВТОРИЗАЦИЯ / РЕГИСТРАЦИЯ=========\n')
        print('login email password - вход')
        print('signup email password - регистрация')
        print('exit - выход')


def correct_format(msg):
    msg = msg.split()
    if len(msg) != 3:
          print('ошибка')
    elif msg[0] != 'login' and msg[0] != 'signup':
         print('команда должна начинаться с login или signup')
    else:
         return True
    return False


async def connect_to_server():
    user_email = '0'
    async with websockets.connect(f"ws://localhost:8000/ws/{user_email}") as websocket:
        print_instructions()
        msg = input(">>> ")

        while msg != 'exit':

            await websocket.send(msg)
            response = await websocket.recv()

            response = json.loads(response)
            if (msg.split()[0] == 'login' or msg.split()[0] == 'signup') and response["status"] == "SUCCESS":
                user_email = response["email"]

            # print(f'ПОЛЬЗОВАТЕЛЬ: {user_email}\n')
            # print(response)

            if msg == 'task':
                while response["status"] != "ERROR" and response["status"] != "SUCCESS":
                    print(response)
                    await websocket.send('waiting')
                    response = await websocket.recv()
                    response = json.loads(response)
            else:
                print(f'ПОЛЬЗОВАТЕЛЬ: {user_email}\n')
            print(response)
        
            print_instructions()
            print('task - бинаризация изображения')
            msg = input(">>> ")



        # while not correct_format(msg):
        #     print_instructions()
        #     msg = input(">>> ")

        # user_email = msg.split()[1]

        # while msg != 'exit':
        #     # user_email = msg.split()[1]
        #     await websocket.send(msg)
        #     response = await websocket.recv()
        #     print(f"Received: {response}")
        #     msg = input(">>> ")


asyncio.get_event_loop().run_until_complete(connect_to_server())