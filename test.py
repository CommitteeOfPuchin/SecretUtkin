import asyncio
import websockets
import threading
import time, sys
import queue
import ast
from itertools import cycle
import tkinter as tk
from tkinter import font as tkfont


class Net:
    def __init__(self, address, nickname, frame=None):
        self.address = address
        if ':' not in address:
            self.address = '%s:6999' % self.address

        self.defaultIcon = None
        self.nick = nickname
        self.frame = frame
        self.players = []
        self.avatars = []
        self.format = [
            [2, ],
            [2, 7],
            [1, 2, 3],
            [1, 2, 3, 7],
            [1, 6, 2, 3, 8],
            [1, 2, 3, 6, 7, 8],
            [0, 1, 2, 3, 4, 6, 8],
            [0, 1, 2, 3, 4, 6, 7, 8],
            [0, 1, 2, 3, 4, 5, 7, 8, 9],
            range(10)
        ]
        self.closed = False
        self.thread = None
        self.loop = asyncio.get_event_loop()
        self.connect_status = 0
        self.tasks = []

    def set_frame(self, frame):
        self.frame = frame

    def connect(self):
        self.thread = threading.Thread(target=Net._asyncio_thread, args=(self, self.loop))
        self.thread.start()

    def _asyncio_thread(self, loop):
        async def send():
            try:
                async with websockets.connect(
                  'ws://%s' % self.address) as websocket:
                    self.connect_status = 1

                    await websocket.send(self.nick)

                    while not websocket.closed:
                        try:
                            cmd = await websocket.recv()
                        except asyncio.CancelledError:
                            print('oof')
                            await websocket.close(reason='hyu')
                            raise

                        print(cmd)

                        if cmd == 'hs.players':
                            self.players = ast.literal_eval(await websocket.recv())
                            self.avatars = ast.literal_eval(await websocket.recv())
                            self.frame.updatePlayers(self.format, self.avatars, self.players)

                        if cmd == 'hs.default':
                            dat = await websocket.recv()
                            self.frame.placeholder = tk.PhotoImage(data=dat)
                            self.frame.placeholders()

                        if cmd == 'hs.you':
                            self.frame.playerid = int(await websocket.recv())
                            print(self.frame.playerid)

                        if cmd == 'player.join':
                            dat = ast.literal_eval(await websocket.recv())
                            print(dat)
                            self.players.append(dat[0])
                            self.avatars.append(dat[1])
                            self.frame.updatePlayers(self.format, self.avatars, self.players)

                        if cmd == 'player.leave':
                            dat = int(await websocket.recv())
                            del self.players[dat]
                            del self.avatars[dat]
                            if self.frame.playerid > dat:
                                self.frame.playerid -= 1
                            self.frame.updatePlayers(self.format, self.avatars, self.players)

            except asyncio.CancelledError:
                print('oof')
                raise
            else:
                self.connect_status = -1

        try:
            self.tasks.append(loop.create_task(send()))
            loop.run_forever()
        except KeyboardInterrupt:
            pass


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry("1280x720")
        self.resizable(0, 0)

        self.container = tk.Frame(bg='#36393f')
        self.container.place(relheight=1, relwidth=1, relx=0.5, rely=0.5, anchor='c')
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.net = None

        self.title("Secret Utkin || Test")

        self.frames = {}
        for F in (MainPage, GamePage, ClosingPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        for f in self.frames.values():
            f.grid_forget()

        frame = self.frames[page_name]
        frame.grid(row=0, column=0)
        return frame


class GamePage(tk.Frame):
    def updatePlayers(self, f, images, names):
        self.placeholders()

        fmt = f[len(names)-1]
        for i in range(len(names)):
            a = self.avatars[fmt[i]]
            a.avatar = tk.PhotoImage(data=images[i])
            a.nickname = names[i]
            a.upd()

            if i == self.playerid:
                a.changeStatus('player')

    def placeholders(self):
        for ava in self.avatars:
            ava.avatar = self.placeholder
            ava.avaLabel.configure(image=self.placeholder)
            ava.nickLabel.configure(text="Свободно")
            ava.changeStatus('alive')

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.ready = False
        self.controller = controller
        self.playerid = 0

        self.configure(bg='#36393f')

        self.placeholder = tk.PhotoImage()
        self.avatars = [Avatar(self, self.placeholder, "") for _ in range(10)]

        self.factions = ['#0067bf', '#97612b', '#bfa200', 'black']

        for i, avatar in enumerate(self.avatars):
            avatar.grid(row=(i//5)+1, column=(i % 5)+1, padx=10, pady=5)
            avatar.avaLabel.bind("<Button-1>", lambda _, s=avatar.nickname: print(s))
            avatar.nickLabel.bind("<Button-1>", lambda _, col=cycle(self.factions), a=avatar: a.nickLabel.configure(fg=next(col)))

        self.ready = True


class Avatar(tk.Frame):
    def __init__(self, parent, avatar, nickname, status="alive"):
        tk.Frame.__init__(self, parent)
        self.avatar = avatar
        self.nickname = nickname

        self.status = status
        self.colors = {
            'alive': "#f0f0f0",
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

    def upd(self):
        self.avaLabel.configure(image=self.avatar)
        self.nickLabel.configure(text=self.nickname)


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg_col = '#36393f'

        self.configure(bg=self.bg_col, borderwidth=2, relief='solid')
        self.e1 = tk.Entry(self, font='Helvetica 10', width=20, fg='grey')
        self.e2 = tk.Entry(self, font='Helvetica 10', width=20, fg='grey')

        def_text = ['test', 'test2']
        self.def_e = {}

        for i, e in enumerate((self.e1, self.e2)):
            e.insert(0, def_text[i])
            self.def_e[e] = def_text[i]
            e.bind('<FocusIn>', self.entry_focus_in)
            e.bind('<FocusOut>', self.entry_focus_out)

        self.e1.grid(row=0, column=1, padx=5)
        self.e2.grid(row=1, column=1, padx=5)

        l1 = tk.Label(self, text='Никнейм', bg=self.bg_col, font='Helvetica 10 bold', fg='white')
        l1.grid(row=0, column=0, sticky='e', padx=5, pady=5)

        l2 = tk.Label(self, text='IP', bg=self.bg_col, font='Helvetica 10 bold', fg='white')
        l2.grid(row=1, column=0, sticky='e', padx=5, pady=5)

        self.b = tk.Button(self, text="Войти", font='Helvetica 12', width=20)
        self.b.grid(row=2, column=0, columnspan=2, pady=10)
        self.b.bind('<Button-1>', self.login)

    def login(self, event):
        if event.widget['state'] == 'normal':
            nick = 'Anon'

            if self.e1.get() != '':
                nick = self.e1.get()

            if self.e2.get() != '':
                self.controller.net = Net(self.e2.get(), nick)
                self.controller.net.connect()

                while not self.controller.net.connect_status:
                    pass

                if self.controller.net.connect_status == 1:
                    print('nice')
                    self.controller.show_frame("GamePage")
                    self.controller.net.frame = self.controller.frames["GamePage"]
                else:
                    print('whoops')
                    self.b.configure(text='Упс...')
                    self.controller.net.connect_status = 0

    def entry_focus_in(self, event):
        if event.widget.get() == self.def_e[event.widget]:
            event.widget.configure(fg='black')
            event.widget.delete(0, 'end')
            event.widget.insert(0, '')

    def entry_focus_out(self, event):
        if event.widget.get() == '':
            event.widget.insert(0, self.def_e[event.widget])
            event.widget.configure(fg='grey')


class ClosingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.configure(bg='#36393f')

        label = tk.Label(self, text='Подождите, закрывается...', font='Helvetica 24', bg='black', fg='white')
        label.pack()


def on_closing():
    app.wait_visibility(app.show_frame('ClosingPage'))

    loop = asyncio.get_event_loop()
    loop.stop()

    pending = asyncio.Task.all_tasks(loop=loop)
    gathered = asyncio.gather(*pending, loop=loop)
    gathered.cancel()

    sys.exit(0)



if __name__ == "__main__":
    app = MainWindow()
    flags = []
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
