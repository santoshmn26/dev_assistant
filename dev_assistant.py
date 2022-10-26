import datetime
import os
import re
import time
import json
import pickle
import psutil
import tkinter
import pandas as pd
import tkinter.filedialog
from sql_formatter.core import format_sql
from assistant import answer_question as assistant


TIMER_MESSAGE = u"\u23F0 " + "Time's up!!"
RAM_UNICODE = u"\u2633"
CPU_UNICODE = u"\u2622"

# TODO: ADD a function to create dependent files if they don't exist
# TODO: pandas integration


class Helper:

    def today_agenda(self) -> None:
        """
        Function to get the news of the day
        :return:
        """

        if not self.time_sheet_reminder:
            if datetime.datetime.today().weekday() == 3 and datetime.datetime.now().hour == 15 and datetime.datetime.now().minute == 0:
                self.time_sheet_reminder = 1
                self.window.after(1000, self.send_message("timesheet"))


    def add_to_clipboard(self, text: str) -> None:
        """
        Add text to clipboard
        :param text: string to be added to clipboard
        """

        command = 'echo ' + text.strip() + '| clip'
        os.system(command)


    def get_all_notes(self):
        """
        Get all the notes
        :return: list of notes
        """
        self.all_notes = []
        for file in os.listdir(self.notes_path):
            if file.endswith(".txt"):
                self.all_notes.append(file[:-4])


    def validate_json_in_clipboard(self) -> None:
        """
        Validate the json in clipboard
        """
        try:
            json.loads(self.window.clipboard_get())
            self.send_message("Valid JSON")

        except Exception:
            self.send_message("Invalid JSON")


    def format_json_in_clipboard(self) -> None:
        """
        Format the json in clipboard
        """
        try:
            json_data = json.loads(self.window.clipboard_get())
            formatted_json = json.dumps(json_data, indent=4)
            self.window.clipboard_clear()
            self.window.clipboard_append(formatted_json)
            self.send_message("Formatted JSON")

        except Exception:
            self.send_message("Invalid JSON")


    def compare_clipboard_values(self, first_value: str=None) -> None:
        """
        Compare the clipboard values
        :param first_value: If the first value is given,
        then compare the first value with the current clipboard value
        """

        if first_value is None:

            second_value = self.window.clipboard_get()

            if self.clipboard_value_1 != '':
                first_value = self.clipboard_value_1

            else:
                self.helper_response['text'] = "Set first value"

            if first_value == second_value:
                self.helper_response['text'] = "Same"

            else:
                self.helper_response['text'] = "Different"

            self.open_path.delete(0, 'end')
            self.clipboard_value_1 = ''

        else:

            self.clipboard_value_1 = self.window.clipboard_get()
            self.helper_response['text'] = "ready.."
            self.open_path.delete(0, 'end')


    def format_sql_in_clipboard(self) -> None:
        """
        Format the sql in clipboard
        """
        try:
            sql = self.window.clipboard_get()
            formatted_sql = format_sql(sql)
            self.window.clipboard_clear()
            self.window.clipboard_append(formatted_sql)
            self.send_message("Formatted SQL")

        except Exception as e:
            print(e)
            self.send_message("Invalid SQL")


    def pandas_read_file_in_clipboard(self):
        """
        Read the file using pandas
        """
        file_path = self.window.clipboard_get()
        file_path = file_path.replace("\\", "\\\\")
        file_path = file_path.replace("/", "\\\\")

        try:
            self.df = pd.read_csv(file_path)
            self.send_message("Read SUCCESS")
            self.open_path.delete(0, 'end')

        except Exception:
            self.send_message("Invalid file path")
            self.open_path.delete(0, 'end')


    def exit_window(self):
        """
        Exit the window
        When this function is called, the window is destroyed
        """
        self.window.destroy()
        exit()


    def send_message(self, message: str) -> None:
        """
        Message to be updated in text box
        :param message: Message to display to the user
        """

        print(self.hide_entry_window)

        if self.hide_entry_window==0:
            self.open_path.delete(0,'end')
            self.helper_response['text'] = message

        else:
            self.hide_entry()
            self.helper_response['text'] = message


    # TODO: Convert this code to update home_button
    def update_time_left(self, time_left: int, seconds: int = 0):
        """
        Update the time left in the text box
        :param time_left: time left in minutes
        :param seconds: time left in seconds
        """

        if (time_left != 0) and (seconds == 0):
            minutes = time_left - 1
            seconds = 60

        else:
            minutes = time_left

        if (time_left <= 0) & (seconds == 0):
            self.send_message(TIMER_MESSAGE)
            return

        self.helper_response['text'] = f"{time_left}:{seconds}"
        self.window.after(1000, lambda: self.update_time_left(minutes, seconds-1))


    def log(self) -> None:
        """
        Log any event in the log file
        """

        action, time = '', ''
        event = self.user_request.split(":")

        if len(event) > 1:
            action = event[1]

        if len(event) > 2:
            time = event[2]

        else:
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        content_to_log = f"{time}\007{action}"

        with open('data/log.txt', 'a') as f:
            f.write(f"{content_to_log}\n")
            f.close()

        self.open_path.delete(0, 'end')
        self.send_message(f"Logged: {action.lstrip().split(' ')[0]}")


    def update_home_button_timer(self, photo):

        self.home_button['image'] = photo
        self.window.update()


    def timer(self):
        """
        Timer function triggered when given timer is up
        Timer is given in Minutes
        """
        timer_message = u"\u23F0 " + "Time's up!!"
        self.user_request = self.user_request.split(" ")

        try:
            time_in_min = int(self.user_request[1].strip())
            self.update_time_left(time_in_min)
            self.window.after((time_in_min * 100 * 60), lambda: self.send_message(timer_message))

        except Exception:
            self.open_path.delete(0, 'end')
            self.open_path.insert(0, 'Invalid time')

        return


    def cmd_command(self):
        """
        Function to execute given command prompt commands
        """
        command = self.user_request.split(":")[1]
        os.system(command)


    def add_to_memory(self):
        """
        Add a given information to memory stored as json file
        """
        content_to_remember = self.user_request.split(" ")[1]
        clipboard_content = self.window.clipboard_get()

        with open('data/memory.json') as f:
            data = json.load(f)
            data[content_to_remember] = clipboard_content

        with open('data/memory.json', 'w') as f:
            json.dump(data, f)

        self.send_message(f"Added {content_to_remember}!")


    def get_from_memory(self):
        """
        Get a given information from memory stored as json file
        """
        self.send_message("ready..")
        content_to_fetch_from_memory = self.user_request.split(" ")[1]

        with open('data/memory.json') as f:
            data = json.load(f)

        self.window.clipboard_clear()
        self.window.clipboard_append(data[content_to_fetch_from_memory])

        self.send_message(f"Fetched")


    def activate_super_mode(self):
        """
        Activate super mode
        """
        self.send_message("Super mode activated!")

        if self.super_mode == 0:

            self.super_mode = 1
            self.Frame_1 = tkinter.Frame(self.main_frame)
            self.Frame_1.pack(side=tkinter.BOTTOM)
            self.super_mode_text = tkinter.Text(self.Frame_1, font=self.large_font, bg="#101010", fg="#00FF00", bd=1,width=50, height=20, insertbackground="#00FF00")
            self.super_mode_text.pack(side=tkinter.BOTTOM, padx=0, pady=0)

        return


    def deactivate_super_mode(self):
        """
        Deactivate super mode
        """
        self.send_message("Super mode deactivated!")
        self.super_mode = 0
        self.super_mode_text.destroy()
        self.Frame_1.destroy()
        return


    def developer_mode(self):
        """
        Developer mode
        :return:
        """
        clip = self.window.clipboard_get()
        user_commands = self.user_request.split(':')
        todo = user_commands[1].strip()

        if (todo == 'quote_all'):
            if len(user_commands) > 2:
                sep = user_commands[2]

            else:
                sep = ','
            clip = (', '.join('"' + item + '"' for item in clip.split(sep)))
            self.window.clipboard_clear()
            self.window.clipboard_append(clip)
            self.send_message('Done!')
            self.open_path.delete(0, 'end')

        elif todo == 'snake_to_camel':
            clip = clip.split('_')
            clip = clip[0] + ''.join(x.title() for x in clip[1:])
            self.window.clipboard_clear()
            self.window.clipboard_append(clip)
            self.send_message('Done!')
            self.open_path.delete(0, 'end')

        elif todo == 'camel_to_snake':
            clip = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', clip)
            clip = re.sub('([a-z0-9])([A-Z])', r'\1_\2', clip).lower()
            self.window.clipboard_clear()
            self.window.clipboard_append(clip)
            self.send_message('Done!')
            self.open_path.delete(0, 'end')

        elif todo == 'get_file_name':
            clip = os.path.basename(clip)
            self.window.clipboard_clear()
            self.window.clipboard_append(clip)
            self.send_message('Done!')
            self.open_path.delete(0, 'end')

        elif todo == 'get_file_ext':
            clip = os.path.splitext(clip)[1]
            self.window.clipboard_clear()
            self.window.clipboard_append(clip)
            self.send_message('Done!')
            self.open_path.delete(0, 'end')

        elif todo == 'one_line':
            clip = clip.replace('\n', '')
            self.window.clipboard_clear()
            self.window.clipboard_append(clip)
            self.send_message('Done!')
            self.open_path.delete(0, 'end')


    def ram_usage(self):
        """
        Get ram usage
        :return:
        """
        self.open_path.delete(0, 'end')
        RAM_UNICODE = u"\u2633"
        psutil.virtual_memory()

        ram_usage = dict(psutil.virtual_memory()._asdict())['percent']
        response = RAM_UNICODE + " : " + str(ram_usage) + str("%  ")

        self.send_message(response)


    def clear_response(self):
        """
        Clear response
        :return:
        """
        self.open_path.delete(0, 'end')
        self.helper_response['text'] = ''


    def create_note(self):
        """
        Create new note
        :return:
        """
        self.open_path.delete(0, 'end')
        self.send_message("Creating new ticket...")

        user_inputs = self.user_request.split(":")
        note_name = user_inputs[1].strip()
        self.current_ticket = note_name

        if os.path.exists(f"data/tickets/{note_name}.txt"):
            self.send_message("Note already exists!")
            self.open_note()
            return

        with open(f'data/tickets/{note_name}.txt', 'w+') as new_ticket:
            pass

            if self.super_mode != 1:

                self.super_mode = 1

                self.Frame_1 = tkinter.Frame(self.main_frame)
                self.Frame_1.pack(side=tkinter.BOTTOM)
                self.Frame_1['bg'] = '#101010'

                header_text = f"{note_name}"
                self.text_box_header = tkinter.Label(self.Frame_1, font=('sans',12), text=header_text, bg="black",
                                                     fg="#00FF00", bd=1, height=1, width=61, anchor='center')
                self.text_box_header.pack(side=tkinter.TOP, padx=0, pady=0)

                self.super_mode_text = tkinter.Text(self.Frame_1, font=self.large_font, bg="#101010", fg="#00FF00",
                                                    bd=1,width=50, height=20, insertbackground="#00FF00", borderwidth=2)
                self.super_mode_text.pack(side=tkinter.BOTTOM, padx=0, pady=0)

                self.super_mode_text.focus_set()

        self.send_message(f"{note_name} created!")


    def super_mode_focus(self):
        """
        Focus on super mode
        :return:
        """
        if self.super_mode == 1:
            self.super_mode_text.focus_set()


    def open_note(self):
        """
        Open ticket
        :return:
        """
        self.open_path.delete(0, 'end')
        self.send_message("Opening ticket...")

        user_inputs = self.user_request.split(":")
        note_name = user_inputs[1].strip()
        self.current_ticket = note_name

        with open(f'data/tickets/{note_name}.txt', 'r') as ticket:
            ticket_content = ticket.read()

        if self.super_mode == 0:
            self.super_mode = 1
            self.Frame_1 = tkinter.Frame(self.main_frame)
            self.Frame_1.pack(side=tkinter.BOTTOM)

            self.Frame_1['bg'] = '#101010'

            header_text = f"{note_name}"
            self.text_box_header = tkinter.Label(self.Frame_1, font=('sans', 12), text=header_text, bg="black",
                                                 fg="#00FF00", bd=1, height=1, width=61, anchor='center')
            self.text_box_header.pack(side=tkinter.TOP, padx=0, pady=0)

            self.super_mode_text = tkinter.Text(self.Frame_1, font=self.large_font, bg="#101010", fg="#00FF00", bd=1,
                                                width=50, height=20, insertbackground="#00FF00", borderwidth=2)

            self.super_mode_text.pack(side=tkinter.BOTTOM, padx=0, pady=0)
            self.super_mode_text.bind("<Escape>", lambda e: self.open_path.focus_set())
            self.open_path.bind("<Down>", lambda e: self.super_mode_focus())

        self.super_mode_text.insert(tkinter.END, ticket_content)
        self.send_message(f"{note_name} opened!")
        self.super_mode_text.focus_set()

        return


    def delete_note(self):
        """
        Delete ticket
        :return:
        """
        self.open_path.delete(0, 'end')
        self.send_message("Deleting ticket...")

        user_inputs = self.user_request.split(":")
        note_name = user_inputs[1].strip()

        os.remove(f'data/tickets/{note_name}.txt')
        self.send_message(f"{note_name} deleted!")


    def save_note(self):
        """
        Save ticket
        :return:
        """
        self.open_path.delete(0, 'end')
        self.send_message("Saving ticket...")

        with open(f'data/tickets/{self.current_ticket}.txt', 'w+') as ticket:
            ticket_content = self.super_mode_text.get("1.0", tkinter.END)
            ticket.write(ticket_content)

        self.send_message(f"{self.current_ticket} saved!")


    def close_note(self):
        """
        Close ticket
        :return:
        """
        self.open_path.delete(0, 'end')
        self.send_message("Closing ticket...")

        with open(f'data/tickets/{self.current_ticket}.txt', 'w+') as ticket:
            ticket_content = self.super_mode_text.get("1.0", "end-1c")
            ticket.write(ticket_content)

        self.super_mode = 0
        self.Frame_1.destroy()
        self.send_message(f"{self.current_ticket} closed!")
        return


    def add_folder_to_database(self):

        self.open_path.delete(0, 'end')
        self.user_request = self.user_request.split(' ')

        if (self.user_request[2] in self.keywords):
            self.helper_response['text'] = "Keyword Error!"
            return

        # Adding Folder
        elif (self.user_request[1] == "folder:"):
            self.askfile = 0
            self.helper_response['text'] = "Please select a folder"

        if (self.user_request[2] not in self.database_dict.keys()):
            self.add_folder_to_quick_access()
            self.helper_response['text'] = "Added!"

        else:
            self.open_path.delete(0, 'end')
            self.helper_response['text'] = "Path already exists!"

    def open_quick_access_folder(self):

        if self.user_request in self.database_dict.keys():

            self.open_path.delete(0, 'end')
            os.startfile(f"{str(self.database_dict[self.user_request])}")

        else:
            self.open_path.delete(0, 'end')
            self.open_path.insert(0, "Unknown cmd!")


    def add_to_ai_memory(self):
        """
        Add to AI memory
        :return:
        """
        self.open_path.delete(0, 'end')
        user_inputs = self.user_request.split(":")

        with open(f'data/ai_memory.txt', 'a') as memory:
            memory_content = (user_inputs[1].replace('today', str(datetime.date.today()))
                                .replace('Today', str(datetime.date.today()))
                                .replace('TODAY', str(datetime.date.today()))
                                .replace('yesterday', str(datetime.date.today() - datetime.timedelta(days=1)))
                                .replace('Yesterday', str(datetime.date.today() - datetime.timedelta(days=1)))
                                .replace('YESTERDAY', str(datetime.date.today() - datetime.timedelta(days=1)))
                                .replace('tomorrow', str(datetime.date.today() + datetime.timedelta(days=1)))
                                .replace('Tomorrow', str(datetime.date.today() + datetime.timedelta(days=1)))
                                .replace('TOMORROW', str(datetime.date.today() + datetime.timedelta(days=1)))
                                .replace('now', str(datetime.datetime.now()))
                                .replace('Now', str(datetime.datetime.now()))
                                .replace('NOW', str(datetime.datetime.now()))
                                .replace('next week', str(datetime.date.today() + datetime.timedelta(days=7)))
                                .replace('Next week', str(datetime.date.today() + datetime.timedelta(days=7)))
                                .replace('NEXT WEEK', str(datetime.date.today() + datetime.timedelta(days=7)))
                                .replace('last week', str(datetime.date.today() - datetime.timedelta(days=7)))
                                .replace('Last week', str(datetime.date.today() - datetime.timedelta(days=7)))
                                .replace('LAST WEEK', str(datetime.date.today() - datetime.timedelta(days=7)))
                                .replace('next month', str(datetime.date.today() + datetime.timedelta(days=30)))
                                .replace('Next month', str(datetime.date.today() + datetime.timedelta(days=30)))
                                .replace('NEXT MONTH', str(datetime.date.today() + datetime.timedelta(days=30)))
                                .replace('last month', str(datetime.date.today() - datetime.timedelta(days=30)))
                                .replace('Last month', str(datetime.date.today() - datetime.timedelta(days=30)))
                                .replace('LAST MONTH', str(datetime.date.today() - datetime.timedelta(days=30)))
                                .replace('next year', str(datetime.date.today() + datetime.timedelta(days=365)))
                                .replace('Next year', str(datetime.date.today() + datetime.timedelta(days=365)))
                                .replace('NEXT YEAR', str(datetime.date.today() + datetime.timedelta(days=365)))
                                .replace('last year', str(datetime.date.today() - datetime.timedelta(days=365)))
                                .replace('Last year', str(datetime.date.today() - datetime.timedelta(days=365)))
                                .replace('LAST YEAR', str(datetime.date.today() - datetime.timedelta(days=365)))
                                .replace('monday', str(datetime.date.today() + datetime.timedelta(days=0)))
                                .replace('Monday', str(datetime.date.today() + datetime.timedelta(days=0)))
                                .replace('MONDAY', str(datetime.date.today() + datetime.timedelta(days=0)))
                                .replace('tuesday', str(datetime.date.today() + datetime.timedelta(days=1)))
                                .replace('Tuesday', str(datetime.date.today() + datetime.timedelta(days=1))))

            memory.write(f"{memory_content}.\n")

        self.send_message("Updated memory...")


    def answer_question(self):
        """
        Answer Question using GPT-3 model
        """
        self.open_path.delete(0, 'end')
        self.helper_response['text'] = "..."

        question = self.user_request
        with open("data/ai_memory.txt", "r") as f:
            ai_memory = f.read()

        ai_response = assistant(question, ai_memory, self.tokenizer, self.model)
        self.open_path.delete(0, 'end')
        self.helper_response['text'] = f"{int(ai_response[1]*100)}: {ai_response[0]}"
        self.window.clipboard_clear()
        self.window.clipboard_append(ai_response)


    def execute_user_request(self, list_box_suggestion=None):
        """
        Check for user request, validate the type of request, validate request arguments and finally
        execute the user request. Also, update the database if required.
        """
        if list_box_suggestion == None:
            self.update_database_dict()
            self.user_request = self.open_path.get()
            self.get_all_notes()

        else:
            self.user_request = list_box_suggestion


        # Reset the additional_args to 0
        if self.additional_args==1:
            self.additional_args=0
            return

        if self.user_request == 'exit':
            self.exit_window()
            return

        elif self.user_request.startswith('cmd:'):
            self.cmd_command()
            return
        
        elif self.user_request.startswith('timer:'):
            self.timer()
            return

        elif self.user_request.startswith('remember:'):
            self.add_to_memory()
            return

        elif self.user_request.startswith('fetch:'):
            self.get_from_memory()
            return

        elif self.user_request.startswith('log:'):
            self.log()
            return

        elif self.user_request == 'compare1':
            self.compare_clipboard_values(self.window.clipboard_get())
            return

        elif self.user_request == 'compare2':
            self.compare_clipboard_values()
            return

        elif self.user_request == 'validate_json':
            self.validate_json_in_clipboard()
            return

        elif self.user_request == 'format_json':
            self.format_json_in_clipboard()
            return

        elif self.user_request == 'format_sql':
            self.format_sql_in_clipboard()
            return

        elif self.user_request.startswith('super_mode:'):
            self.activate_super_mode()
            return

        elif self.user_request.startswith('super_mode_off:'):
            self.deactivate_super_mode()
            return

        elif self.user_request.startswith('dev:'):
            self.developer_mode()
            return

        elif self.user_request == 'ram':
            self.ram_usage()
            return

        elif self.user_request in ['clear', 'cls']:
            self.clear_response()
            return

        elif self.user_request == 'add':
            self.add_folder_to_database()
            return

        elif self.user_request.endswith('?'):
            self.answer_question()
            return

        elif self.user_request.startswith('open_note:'):
            self.open_note()
            return

        elif self.user_request.startswith('note:'):
            self.create_note()
            return

        elif self.user_request.startswith('save_note'):
            self.save_note()
            return

        elif self.user_request.startswith('close'):
            self.close_note()
            return

        elif self.user_request.startswith('delete_note:'):
            self.delete_note()
            return

        elif self.user_request.endswith('r:'):
            self.add_to_ai_memory()
            return


        else:
            self.open_quick_access_folder()
            return

    # Updating the self.database_dict
    def update_database_dict(self):
        """
        Update the database dictionary
        :return:
        """
        self.database_dict=dict()
        with open(self.database_file, 'r') as f:
            for row in f:
                self.database.append(row)
                if (row != "\n"):
                    row = row.rstrip()
                    row = row.split(",")
                    if(len(row)<3):
                        self.database_dict.update({row[0]: row[1]})
            f.close()

    def update_memory_dict(self):

        with open('data/memory.json') as f:
            if f.read() == '':
                self.memory_dict = dict()
            else:
                self.memory_dict = json.load(f)


# Delete a path from the database
    def delete_database_path(self):
        f = open(self.database_file, 'r')
        lines = f.readlines()
        f.close()
        f = open(self.database_file, 'w')
        for line in lines:
            line = line.split(",")
            if(line[0]==self.user_request[2]):
                continue
            else:
                f.write(str(line[0]) +","+str(line[1]))
        self.update_database_dict()
        f.close()
        

    def write_path_to_database(self,tempdir,path):
        f=open(self.database_file, 'a')
        f.write(path+","+tempdir+"\n")       
        self.update_database_dict()        
        f.close()

    def add_folder_to_quick_access(self):
        root = tkinter.Tk()
        root.withdraw()  

        currdir = os.getcwd()

        if(self.askfile==0):
            tempdir = tkinter.filedialog.askdirectory(parent=root, initialdir=currdir, title='Please select a directory')

        elif(self.askfile==1):
            tempdir = tkinter.filedialog.askopenfilename(parent=root, initialdir=currdir, title='Please select a file')

        else: 
            tempdir=self.user_request[3]

        tempdir = "\""+tempdir+"\""

        if len(tempdir) > 0:
            self.write_path_to_database(tempdir, self.user_request[2])
            self.open_path.delete(0, 'end')
            self.helper_response['text'] = "Added!"

        else:
            self.open_path.delete(0, 'end')
            self.helper_response['text'] = "Error!"


    def dragwin(self,event):
        x = self.window.winfo_pointerx() - self._offsetx
        y = self.window.winfo_pointery() - self._offsety
        self.window.geometry('+{x}+{y}'.format(x=x,y=y))

    def clickwin(self,event):
        self._offsetx = event.x
        self._offsety = event.y
        
    def hider(self,event=0):
        if(self.hide==1):
            self.window.attributes('-alpha', 1)
            self.hide=0
        else:
            self.window.attributes('-alpha', 0.3)
            self.hide=1

    def exit(self):
        self.window.destroy()
        
    def hide_entry(self):
        try:
            self.open_path.delete(0, 'end')
        except:
            pass
        if(self.hide_entry_window==1):

            self.hide_entry_window=0
            sv = tkinter.StringVar()
            sv.trace("w", lambda name, index, mode, sv=sv: self.callback(sv))

            self.Frame_0['background'] = 'white'
            self.home_button['image'] = self.active_photo

            self.helper_response=tkinter.Label(self.Frame_0,font = self.large_font, bg="#101010",fg="#00FF00",bd=1,width=1,anchor='w')
            self.helper_response.pack(side=tkinter.TOP, padx=0, pady=0, anchor='w')

            self.open_path=tkinter.Entry(self.Frame_0,font=self.large_font,bg="#101010",fg="#00FF00",bd=1,width=1,insertbackground="#00FF00",textvariable=sv)
            self.open_path.pack(side=tkinter.BOTTOM, padx=0, pady=0, anchor='w')

            self.open_path.focus()
            self.open_path.config(highlightbackground="#8B0000")
            self.open_path.bind('<Up>', lambda x: self.upkey())
            self.open_path.bind('<Down>', lambda x: self.downkey())
            self.open_path.bind("<Return>", lambda x: self.execute_user_request())


            for i in range (1,21):

                try:
                    self.open_path["width"]=i
                    self.helper_response["width"]=i
                    self.window.update()
                except:
                    pass

                self.window.update()
                time.sleep(0.003)

        else:
            if self.list_box_present == 1:
                self.listbox.destroy()
                self.list_box_present = 0

            if self.super_mode == 1:
                self.super_mode_text.destroy()
                self.Frame_1.destroy()
                self.super_mode = 0

            for i in range (1,21):
                self.open_path["width"]=20-i
                self.helper_response["width"]=20-i
                self.window.update()
                time.sleep(0.003)

            self.home_button['image'] = self.inactive_photo
            self.helper_response.destroy()
            self.open_path.destroy()
            self.hide_entry_window=1
            self.window.update()


    # Adding features for version 4.0
    def do_nothing(self):        
        pass
        
    def callback(self,sv):

        if self.super_mode == 1:
            return

        path = sv.get()
        insert = 0
        if len(path) > 20 and len(path) < 40:
            self.open_path["width"] = len(path)

        elif len(path) > 40:
            self.open_path["width"] = 40

        else:
            self.open_path["width"] = 20


        if self.open_path.get() != '':
            if self.list_box_present == 0:
                self.Frame_1=tkinter.Frame(self.main_frame)
                self.Frame_1.pack(side=tkinter.RIGHT)            
                self.listbox = tkinter.Listbox(self.Frame_1,width=26,height=2,bd=0,bg='black',fg='#00FF00',font=self.large_font, activestyle='underline',selectbackground='black',selectforeground='#00FF00',highlightthickness=0)
                self.listbox.bind('<Return>', lambda x: self.selected_from_list_box(self.listbox.get(tkinter.ACTIVE)))
                self.listbox.bind("<Escape>", lambda x: self.open_path.focus())
                self.listbox.pack(side="bottom",fill="both", expand=True)
                self.list_box_present = 1
                self.listbox.delete(0,tkinter.END)
        else:
            self.listbox.destroy()
            self.Frame_1.destroy()
            self.window.update()
            self.list_box_present = 0 
        
        if(path!=''):

            all = list(self.database_dict.keys()) + self.keywords + list(self.memory_dict.keys()) + self.all_notes
            temp=[]

            for i in all:
                if i.startswith(path):
                    temp.append(i)

                self.listbox['height'] = len(temp)

            for i in temp:
                self.listbox.insert(insert,i)
                insert = 1

            if insert == 0:
                self.listbox.destroy()
                self.Frame_1.destroy()
                self.window.update()
                self.list_box_present = 0


    def downkey(self):
        self.listbox.focus()


    def upkey(self):
        self.listbox.focus()


    # Main function to open paths
    def open_path_function(self):
        self.update_database_dict()
        self.get_path = self.open_path.get()


    def selected_from_list_box(self, selected_suggestion):
        """
        This function is called when user selects an item from the listbox
        """
        self.open_path.delete(0, 'end')
        self.open_path.insert(0, selected_suggestion)

        self.listbox.destroy()
        self.Frame_1.destroy()
        self.window.update()
        self.list_box_present = 0

        if selected_suggestion in self.keywords:
            self.execute_user_request()
        elif selected_suggestion in self.all_notes:
            self.execute_user_request(list_box_suggestion=f'open_note: {selected_suggestion}')

        elif selected_suggestion in self.memory_dict.keys():
            self.execute_user_request(list_box_suggestion=f'open_memory: {selected_suggestion}')


    def enterkey(self):
        selected = self.listbox.get(tkinter.ACTIVE)
        self.open_path.delete(0, tkinter.END)
        self.open_path.insert(0, selected)
        self.open_path_function()
        self.execute_user_request()


    def validate_dependency_files(self):
        """
        This function will validate the dependency files
        """
        predifined_user_files = ["Documents","Downloads","Pictures","Music","Videos"]
        predefined_apps = ["control","settings","calc","cmd",'notepad','SnippingTool']

        if os.path.isfile(self.database_file) is not True:
            with open("data/database.txt",'w+') as database_file:

                current_user = os.getlogin()

                for each_file in predifined_user_files:
                    database_file.write(each_file.lower()+","+"c:/Users/"+current_user+"/"+each_file+"\n")

                for each_app in predefined_apps:
                    database_file.write(each_app+","+"c:/Windows/system32/"+each_app+".exe"+"\n")

        if os.path.isfile(self.memory_file) is not True:
            with open("data/memory.txt",'w+') as memory_file:
                pass

        if os.path.isfile(self.log_file) is not True:
            with open("data/log.txt",'w+') as log_file:
                pass

        if os.path.isfile(self.ai_memory_file) is not True:
            with open("data/ai_memory.txt",'w+') as ai_memory_file:
                pass

        if os.path.isfile(self.memory_file) is not True:
            with open("data/memory.json",'w+') as memory_json:
                pass

    def __init__(self,full=0):

        if(full!=1):
            exit()

        self.additional_args=0
        self.prev_args=[]
        self.user_request=None
        self.database=list()
        self.database_dict={}
        self.memory_dict = {}
        self.window=tkinter.Tk()
        self.window.title("Final AI")
        self._offsetx = 0
        self._offsety = 0
        self.super_mode = 0
        self.time_sheet_reminder = 0
        self.hide=1
        self.list_box_present = 0
        self.askfile=0
        self.help_window_active=0
        self.small_font = ('sans',12)
        self.compare_value_1 = ''
        self.compare_value_2 = ''
        self.events=[]
        self.database_file="data/database.txt"
        self.memory_file = "data/memory.json"
        self.log_file = "data/log.txt"
        self.ai_memory_file = "data/ai_memory.txt"
        self.notes_path = "data/notes/"
        self.hide_entry_window=1
        self.large_font = ('sans',15)
        self.all_notes = []
        self.main_frame=tkinter.Frame(self.window)
        self.main_frame.pack(side=tkinter.TOP)
        self.Frame_0=tkinter.Frame(self.main_frame)
        self.Frame_0.pack(side=tkinter.TOP)
        self.Frame_1=tkinter.Frame(self.main_frame)
        self.Frame_1.pack(side=tkinter.RIGHT)
        
        # Check for the database file and update the database.txt
        self.validate_dependency_files()
        self.update_database_dict()
        self.update_memory_dict()
        self.get_all_notes()

        filename = 'finalized_model.sav'
        self.model = pickle.load(open(filename, 'rb'))

        token_filename = 'tokenizer.sav'
        self.tokenizer = pickle.load(open(token_filename, 'rb'))

        self.background_color={'black': '#101010', 'white': '#FFFFFF', 'red': '#FF0000', 'green': '#00FF00'}
        self.keywords=["exit","add","macro","exe","gmail","github","linkedin","shutdown","lock","facebook","help",'ram']

        sv = tkinter.StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.callback(sv))

        self.open_path=tkinter.Entry(self.Frame_1,font=self.large_font,width=20,textvariable=sv)
        self.open_path["bg"] = "#101010"
        self.open_path["fg"] = "#00FF00"
        self.open_path["insertbackground"] = "#00FF00" 

        self.inactive_photo=tkinter.PhotoImage(file = "icons/d3.png")
        self.active_photo = tkinter.PhotoImage(file = "icons/d5.png")

        self.home_button=tkinter.Button(self.Frame_0,image=self.inactive_photo,width=53,height=50,command=lambda: self.hide_entry())
        self.home_button["bd"] = 0
        self.home_button.pack(side=tkinter.LEFT)

        self.listbox = tkinter.Listbox(self.Frame_1,width=20,height=4,bg='black',fg="white",font=10)
        self.Frame_0['background']='white'
        self.Frame_1['background']='white'

        self.Frame_1['height']=2
        self.main_frame['background']='white'
        
        self.home_button.bind('<Button-1>',self.clickwin)
        self.home_button.bind('<B1-Motion>',self.dragwin)
        self.home_button.bind('<Triple-Button-1>', self.do_nothing())
        self.home_button.bind('<Double-Button-1>', self.do_nothing())

        self.window.wm_attributes("-transparentcolor", "white")
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", 1)

        self.window.after(10000, lambda:  self.today_agenda())
        self.window.mainloop()

        
p=Helper(1)