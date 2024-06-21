import socket
import threading
from network import *
from interface import *
import cv2
plan=0
name=''
def handle_video(video_client, id):
    cap = cv2.VideoCapture(0)
    data = b""
    while True:
        ret, frame = cap.read()
        payload = Payload(frame, gui.return_id)
        send_video(video_client, payload)

        frame, data = recv_video(video_client, data)
        frame = pickle.loads(frame)
        frame = cv2.resize(frame, (800, 600))
        gui.update(frame)


def handle_chat(chat_client, id):
    while True:
        message = chat_client.recv(4096).decode()
        gui.chat_box.insert(END, message + "\n")


def handle_file(ft_client, id):
    data = b""
    while True:
        file, data = recv_video(ft_client, data)
        file = pickle.loads(file)
        file_data = file.frame
        from_id, file_name = file.id.split(" ")
        gui.chat_box.insert(END, f"[Received] {file_name} From Client{from_id}\n")
        with open(f"Client{from_id}_{file_name}", "wb") as fp:
            fp.write(file_data)

def get_plan():
    global plan,name
    plan=int(plan_var.get().split(' ')[0])
    name=entryName.get()
    login.destroy()

plans=['5 minutes','10 minutes','15 minutes','20 minutes']
login = Tk()
plan_var=StringVar()
        # set the title
login.title("Login")
login.resizable(width=False, height=False)
login.geometry('400x400')

pls = Label(
    login, text="Please login to continue", justify=CENTER, font="Helvetica 14 bold"
)
pls.pack(pady=10)

labelName = Label(login, text="Name: ", font="Helvetica 12")
labelName.pack(pady=10)

entryName = Entry(login, font="Helvetica 14")
entryName.pack(pady=10)
entryName.focus()

plans_dropdown=ttk.Combobox(login,textvariable=plan_var,values=plans)
plans_dropdown.set("Select Plan")
# Corrected button binding here
go = Button(
    login,
    text="CONTINUE",
    font="Helvetica 14 bold",
    command=get_plan  # Change to start_gui method
)
plans_dropdown.pack(pady=10)
go.pack()

login.mainloop()

gui = Gui(plan,name)

video_client = socket.socket()
video_client.connect(("192.168.39.205", 7777))
gui.id, gui.max_clients = list(map(int, video_client.recv(size).decode().split("^")))
gui.return_id = gui.id
video_thread = threading.Thread(target=handle_video, args=(video_client, gui.id))
video_thread.start()

chat_client = socket.socket()
gui.chat_client = chat_client
chat_client.connect(("192.168.39.205", 7778))
chat_thread = threading.Thread(target=handle_chat, args=(chat_client, gui.id))
chat_thread.start()

ft_client = socket.socket()
gui.ft_client = ft_client
ft_client.connect(("192.168.39.205", 7779))
ft_thread = threading.Thread(target=handle_file, args=(ft_client, gui.id))
ft_thread.start()

gui.create_gui()
