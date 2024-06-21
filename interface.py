import cv2
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
from network import *


class Login:
    def __init__(self) -> None:
        self.login = Tk()
        # set the title
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)

        self.pls = Label(
            self.login, text="Please login to continue", justify=CENTER, font="Helvetica 14 bold"
        )
        self.pls.place(relheight=0.15, relx=0.2, rely=0.07)

        self.labelName = Label(self.login, text="Name: ", font="Helvetica 12")
        self.labelName.place(relheight=0.2, relx=0.1, rely=0.2)

        self.entryName = Entry(self.login, font="Helvetica 14")
        self.entryName.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.2)
        self.entryName.focus()

        # Corrected button binding here
        self.go = Button(
            self.login,
            text="CONTINUE",
            font="Helvetica 14 bold",
            command=self.login.destroy  # Change to start_gui method
        )
        self.go.place(relx=0.4, rely=0.55)
        self.login.mainloop()

class Gui:
    def __init__(self,plan,name):
        self.root = Tk()
        self.root.title("Video Conferencing App")
        self.id = 0
        self.return_id = 0
        self.max_clients = 0
        self.chat_client = None
        self.ft_client = None
        self.name=name
        self.mac = get_mac()
        self.duration = plan * 60
        self.remaining_time = self.duration
        self.tab_control = ttk.Notebook(self.root)

        self.video_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.video_tab, text="Video Conferencing")
        self.chat_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.chat_tab, text="Chat and file transfer")

        # Call the login method to initiate the login process
        

        # login window
       

    def create_gui(self):
        
        
        # Video Conferencng Tab Content
        self.video_timer_label = Label(
            self.video_tab, text=f"Time remaining: {self.duration} seconds"
        )
        self.video_label = Label(
            self.video_tab, text=f"Client {self.name} Video Room\nMac = {self.mac}"
        )
        self.canvas = Canvas(self.video_tab, width=800, height=600)
        self.next_button = Button(self.video_tab, text="NEXT", command=self.go_next)
        self.prev_button = Button(self.video_tab, text="PREV", command=self.go_prev)

        self.video_label.pack()
        self.video_timer_label.pack()
        self.canvas.pack()
        self.next_button.pack(side=RIGHT, padx=10)
        self.prev_button.pack(side=LEFT, padx=10)

        self.client_names = [f"Client {id}" for id in range(self.max_clients)]
        self.chat_client_var = StringVar()

        # Chat Tab Content
        self.chat_timer_label = Label(
            self.chat_tab, text=f"Time remaining: {self.duration} seconds"
        )
        self.chat_label = Label(
            self.chat_tab, text=f"Client {self.name} Chat Room\nMac = {self.mac}"
        )
        self.chat_box = Text(self.chat_tab, height=30, width=100)
        self.message_entry = Entry(self.chat_tab, width=50)
        self.broadcast_button = Button(
            self.chat_tab, text="Broadcast message", command=self.broadcast_message
        )
        self.unicast_button = Button(
            self.chat_tab, text="Unicast message", command=self.unicast_message
        )
        self.browse = Button(
            self.chat_tab, text="Browse File", command=self.choose_file
        )
        self.unicast_file_button = Button(
            self.chat_tab, text="Unicast File", command=self.unicast_file
        )
        self.broadcast_file_button = Button(
            self.chat_tab, text="Broadcast File", command=self.broadcast_file
        )
        self.chat_dropdown = ttk.Combobox(
            self.chat_tab, textvariable=self.chat_client_var, values=self.client_names
        )
        
        self.chat_dropdown.set("Select client")
        self.chat_label.pack()
        self.chat_timer_label.pack()
        self.chat_box.pack(pady=10)
        self.message_entry.pack(pady=10)
        self.broadcast_button.pack(side="left",pady=10)
        self.unicast_button.pack(side="left",pady=10)
        self.browse.pack(side="left")
        self.unicast_file_button.pack(side="right",pady=10)
        self.broadcast_file_button.pack(side="right",pady=10)
        self.chat_dropdown.pack()

        self.tab_control.pack(expand=1, fill="both")

        # Update timer every second
        self.root.after(1000, self.update_timer)
        self.root.mainloop()

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.video_timer_label.config(
                text=f"Time remaining: {self.remaining_time} seconds"
            )
            self.chat_timer_label.config(
                text=f"Time remaining: {self.remaining_time} seconds"
            )
            self.root.after(1000, self.update_timer)
        else:
            self.root.destroy()  # Close the Tkinter wi

    def update(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)  # Create a PIL image
        img = ImageTk.PhotoImage(image=img)  # Convert to Tkinter-compatible image
        self.canvas.create_image(0, 0, anchor=NW, image=img)
        self.canvas.img = img

    def go_next(self):
        self.return_id = (self.return_id + 1) % self.max_clients

    def go_prev(self):
        self.return_id = (self.return_id - 1) % self.max_clients

    def broadcast_message(self):
        message = self.message_entry.get()
        self.message_entry.delete(0, END)
        self.chat_client.send(message.encode())

    def unicast_message(self):
        message = self.message_entry.get()
        self.message_entry.delete(0, END)
        id = self.chat_client_var.get().split(" ")[1]
        message = f"/private {id} {message}"
        self.chat_client.send(message.encode())

    def choose_file(self):
        file_path = filedialog.askopenfilename()
        self.message_entry.delete(0, END)
        self.message_entry.insert(0, file_path)

    def broadcast_file(self):
        file_path = self.message_entry.get()
        file_name = file_path.split("/")[-1]
        with open(file_path, "rb") as file:
            file_data = file.read()
        payload = Payload(file_data, file_name)
        send_video(self.ft_client, payload)
        self.chat_box.insert(END, f"[Sent] {file_name} Broadcasted\n")

    def unicast_file(self):
        file_path = self.message_entry.get()
        file_name = file_path.split("/")[-1]
        name=file_name
        id = self.chat_client_var.get().split(" ")[1]
        with open(file_path, "rb") as file:
            file_data = file.read()
        file_name = f"/private {id} {file_name}"
        payload = Payload(file_data, file_name)
        send_video(self.ft_client, payload)
        self.chat_box.insert(END, f"[Sent] {name} to Client {id}\n")