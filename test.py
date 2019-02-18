import asyncio
import websockets
import threading
import time
from itertools import cycle
import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog

# def _asyncio_thread(loop, text):
#     async def send():
#         async with websockets.connect(
#                 'ws://salieri.me:6999') as websocket:
#             await websocket.send(text)
#             print(await websocket.recv())
#
#     loop.run_until_complete(send())
#
#
# def SendMes(ev):
#     loop = asyncio.get_event_loop()
#     t = threading.Thread(target=_asyncio_thread, args=(loop,textbox.get('1.0', 'end'),)).start()

class Net:
    @staticmethod
    def init(frame):
        async def wakeup():
            while True:
                await asyncio.sleep(1)

        loop = asyncio.get_event_loop()
        loop.create_task(wakeup())
        threading.Thread(target=Net._asyncio_thread, args=(loop, frame)).start()

    @staticmethod
    def _asyncio_thread(loop, frame):
        async def send():
            async with websockets.connect(
              'ws://salieri.me:6999') as websocket:
                while True:
                    cmd = await websocket.recv()
                    print(cmd)

                    print(cmd.startswith('user'))

                    if cmd.startswith('user'):
                        args = cmd.split()[1:]
                        print(args)
                        avaFrame = frame.avatars[int(args[0])]
                        avaFrame.avatar = tk.PhotoImage(data=await websocket.recv())
                        avaFrame.avaLabel.configure(image=avaFrame.avatar)


        try:
            loop.run_until_complete(send())
        except KeyboardInterrupt:
            pass


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry("1280x720")
        self.resizable(0, 0)

        container = tk.Frame(bg='#36393f')
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.title("Secret Utkin || Test")

        self.frames = {}
        for F in (StartPage, GamePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
        Net.init(self.frames["StartPage"])

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.configure(bg='#36393f')

        frame = tk.Frame(bg='#36393f')
        frame.place(in_=parent, anchor="c", relx=.5, rely=.5)

        self.avatars = []
        for _ in range(10):
            self.avatars.append(None)

        self.avatars[0] = Avatar(frame, tk.PhotoImage(file="Avatars/K_Vilvi.png"), "vilverin", status="player")
        self.avatars[1] = Avatar(frame, tk.PhotoImage(file="Avatars/L_Nikminer.png"), "Nikminer")
        self.avatars[2] = Avatar(frame, tk.PhotoImage(file="Avatars/L_Risa.png"), "risa-chan")
        self.avatars[3] = Avatar(frame, tk.PhotoImage(file="Avatars/K_Mjaroslav.png"), "mjaroslav", status='alpaca')
        self.avatars[4] = Avatar(frame, tk.PhotoImage(file="Avatars/L_Enotello.png"), "enotello", status='clear')
        self.avatars[5] = Avatar(frame, tk.PhotoImage(file="Avatars/L_Raven.png"), "Raven")
        self.avatars[6] = Avatar(frame, tk.PhotoImage(file="Avatars/U_Utkin.png"), "Utkin")
        self.avatars[7] = Avatar(frame, tk.PhotoImage(file="Avatars/L_ElvenMeat.png"), "ElvenMeat")
        self.avatars[8] = Avatar(frame, tk.PhotoImage(file="Avatars/K_Ryoka.png"), "Ryoka", status='clear')
        self.avatars[9] = Avatar(frame, tk.PhotoImage(file="Avatars/L_Event.png"), "eventhorizon")

        self.avatars[2].changeStatus('alive', True)
        self.avatars[8].changeStatus('alive', False, True)

        self.factions = ['#0067bf', '#97612b', '#bfa200', 'black']

        for i, avatar in enumerate(self.avatars):
            avatar.grid(row=(i//5)+1, column=(i % 5)+1, padx=10, pady=10)
            avatar.avaLabel.bind("<Button-1>", lambda _, s=avatar.nickname: print(s))
            avatar.nickLabel.bind("<Button-1>", lambda _, col=cycle(self.factions), a=avatar: a.nickLabel.configure(fg=next(col)))


class Avatar(tk.Frame):
    def __init__(self, parent, avatar, nickname, status="alive"):
        tk.Frame.__init__(self, parent)
        self.avatar = avatar
        self.nickname = nickname

        self.status = status
        self.colors = {
            'alive': None,
            'alpaca': 'gray',
            'player': 'green',
            'clear': '#92b6ef'
        }

        self.configure(highlightthickness=5, highlightbackground="black", borderwidth=2, relief="ridge")

        nickFont = tkfont.Font(family='Helvetica', size=18, weight="bold")

        self.avaLabel = tk.Label(self, image=self.avatar)
        self.nickLabel = tk.Label(self, text=nickname, font=nickFont, bg=self.colors[self.status])
        self.avaLabel.pack(side="bottom", fill="both")
        self.nickLabel.pack(fill="x")

    def changeStatus(self, status, president=False, chancellor=False):
        if status != self.status:
            self.status = status
            self.nickLabel.configure(bg=self.colors[self.status])

        if president:
            self.configure(highlightbackground="#10afe4")
        elif chancellor:
            self.configure(highlightbackground="#f5c976")
        else:
            self.configure(highlightbackground="black")


class GamePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
