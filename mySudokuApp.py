from tkinter import *
import time
import csv
import random
from sudoku_brain2 import Brain
from sudokuGetter import Refresher
from settingFile import SaveSettings


class Game:

    # ALL GAME DEFAULTS/CONSTANTS
    background_color = "#79BFFD"
    my_yellow = "#B5A642"
    my_purple = "#e6e6ff"
    my_gray = "#E6E6E6"
    my_blue = "#E2F7FA"
    light_yellow = "#ffffc7"
    light_green = "#e5fbe5"
    light_blue = "#e8f4f8"
    highlight_color = light_yellow
    error_color = "#ff9a90"
    max_notes = 5

    # initialize the game...
    def __init__(self, master):
        self.master = master
        self.my_settings = SaveSettings()
        self.highlight_color = self.my_settings.get_highlight()
        self.config_menus()
        #self.setup_results_window()

        self.running = True
        self.started = False
        self.setting = False
        self.just_started = True
        self.reg = master.register(self.correct_entry)
        self.master.bind('<Left>', self.arrow_pressed)
        self.master.bind('<Right>', self.arrow_pressed)
        self.master.bind('<Up>', self.arrow_pressed)
        self.master.bind('<Down>', self.arrow_pressed)
        self.taking_notes = False
        self.errors_on = True
        self.recent_pause = time.time()
        self.total_pause = 0
        self.step_pause = 0
        self.is_paused = False
        self.just_paused = False
        self.multiple_asks = False
        self.pop_window = False

        #set up title frame
        self.title_frame = Frame(master, bg=Game.background_color)
        self.title_frame.pack(fill=X)
        self.title_label = Label(self.title_frame,
                                 text="DR Sudoku",
                                 bg=Game.background_color, fg="black")
        self.title_label.config(font=("Chalkduster", 34))
        self.title_label.pack()

        #set up button frame
        self.button_frame = Frame(master, bg="#F5F5F5")
        self.button_frame.pack(fill=X)
        self.difficulty = StringVar(self.button_frame)
        self.difficulty.set(self.my_settings.get_difficulty())

        self.buttons = [
            Button(self.button_frame, text="NEW GAME", command=self.new_game,
                   width=30, fg="blue", activeforeground="blue"),
            OptionMenu(self.button_frame, self.difficulty,
                       "EASY", "MEDIUM", "HARD", "EXPERT", "CUSTOM"),
            Button(self.button_frame, text="AUTO-SOLVE", command=self.check_autosolve_confirm,
                   width=30, fg="red", activeforeground="red"),
            Button(self.button_frame, text="SUBMIT", command=self.submit,
                   width=30, fg="green", activeforeground="green")
        ]
        self.buttons[1].config(width=30, bg="#F5F5F5")
        self.buttons[1].config(fg="green", activeforeground="green")
        self.difficulty.trace('w', self.adjust_difficulty)

        self.button_spacing = 10
        for i in range(4):
            self.button_frame.columnconfigure(i, weight=1)
            self.buttons[i].grid(row=0, column=i,
                                 ipadx=self.button_spacing, ipady=self.button_spacing)

        #set up playing/core frame
        self.core_frame = Frame(master, bg="black")
        self.core_frame.pack(expand=YES, fill=BOTH)

        #set up note buttons
        self.note_frame = Frame(master, bg="cyan")
        self.note_frame.pack(fill=X)
        #self.note_frame.rowconfigure(0, weight=1)
        self.note_buttons = [
            Button(self.note_frame, text=1, command=lambda: self.set_note(1),
                   fg="purple", font=("Chalkduster", 16)),
            Button(self.note_frame, text=2, command=lambda: self.set_note(2),
                   fg="purple", font=("Chalkduster", 16)),
            Button(self.note_frame, text=3, command=lambda: self.set_note(3),
                   fg="purple", font=("Chalkduster", 16)),
            Button(self.note_frame, text=4, command=lambda: self.set_note(4),
                   fg="purple", font=("Chalkduster", 16)),
            Button(self.note_frame, text=5, command=lambda: self.set_note(5),
                   fg="purple", font=("Chalkduster", 16)),
            Button(self.note_frame, text=6, command=lambda: self.set_note(6),
                   fg="purple", font=("Chalkduster", 16)),
            Button(self.note_frame, text=7, command=lambda: self.set_note(7),
                   fg="purple", font=("Chalkduster", 16)),
            Button(self.note_frame, text=8, command=lambda: self.set_note(8),
                   fg="purple", font=("Chalkduster", 16)),
            Button(self.note_frame, text=9, command=lambda: self.set_note(9),
                   fg="purple", font=("Chalkduster", 16))
        ]
        for i in range(9):
            self.note_frame.columnconfigure(i, weight=1)
            self.note_buttons[i].grid(row=0, column=i,
                            ipadx=40, ipady=5)

        #load in previous settings
        self.difficulty.set(self.my_settings.get_difficulty())
        self.og_diff = str(self.difficulty.get())
        if not self.my_settings.get_error_recog():
            self.toggle_errors()

        self.save_settings()

        self.original_grid = self.get_new_grid(self.difficulty.get())

        #set up working grid
        self.grid = []
        for i in range(9):
            self.grid.append([])
            for j in range(9):
                self.grid[i].append(self.original_grid[i][j])

        # set up user grid
        self.user_grid = []
        for i in range(9):
            self.user_grid.append([])
            for j in range(9):
                self.user_grid[i].append(self.original_grid[i][j])

        #set up noting, done later?
        self.noting = []
        for i in range(9):
            self.noting.append([])
            for j in range(9):
                self.noting[i].append(False)

        #self.grid = self.original_grid
        self.start_time = time.time()
        self.brain = Brain(self.original_grid)
        self.display()

        #FIX BY SETTING MIN LABEL SIZE
        #setup a timer... change to start at 0
        self.timer_frame = Frame(master, bg=Game.background_color)
        self.timer_frame.pack(fill=X)
        self.pause_img = PhotoImage(file='pause-button.png')
        self.pause_button = Button(self.timer_frame, image=self.pause_img,
                                   command=self.toggle_pause_button, bg=Game.my_blue,
                                   pady=4, padx=4)
        self.pause_button.pack(side=LEFT, padx=8)
        self.message_label = Label(self.timer_frame, text="",
                                   bg=Game.background_color, pady=10)
        self.message_label.config(font=("Chalkduster", 18))
        self.message_label.pack(side=LEFT, padx=5)
        self.timer_label = Label(self.timer_frame, text="",
                                 bg=Game.background_color, pady=15)
        self.timer_label.config(font=("Tahoma", 18))
        self.timer_label.pack(side=RIGHT,padx=5)
        def clock():
            if self.running and not self.is_paused:
                #prevents constant triggering by spacing out
                self.multiple_asks = False

                #bank paused time and then clear last pause timer
                if self.step_pause > 0:
                    self.total_pause += self.step_pause
                    self.step_pause = 0
                total_time = time.time() - self.start_time - self.total_pause
                minute = int(total_time // 60)
                second = int(total_time - (minute * 60))

                label = ""
                if minute < 10:
                    label = "0" + str(minute) + ":" + label
                else:
                    label = str(minute) + ":" + label
                if second < 10:
                    label = label + "0" + str(second)
                else:
                    label = label + str(second)

                #label = "TIME: " + label

                self.timer_label.config(text=label)
            self.timer_label.after(1000, clock)
        clock()

    # HANDLE ARROW KEYBOARD PRESS EVENTS
    def arrow_pressed(self, event):
        # DON'T ALLOW MOVEMENT, WHEN IN BETWEEN GAMES
        if not self.running:
            return

        # GET FOCUSED WIDGET IF EXISTS... ELSE - CANCEL MOVEMENT
        try:
            focused_w = self.master.focus_get()
        except AttributeError:
            return

        # BRING STATE BACK TO INITIAL PARAMETERS
        self.message_label.config(text="")
        all_sections = focused_w.master.master.winfo_children()[-9:]
        section_frame = focused_w.master
        section_list = section_frame.winfo_children()
        section_num = -1
        element_num = -1

        # ACTION HAS NOW TAKEN PLACE AFTER HAVING STARTED A NEW GAME
        self.just_started = False

        # GET THE SECTION NUMBER OF CURRENT WIDGET
        for i, section in enumerate(all_sections):
            if section is section_frame:
                section_num = i

        # GET CURRENT WIDGET'S CURRENT PLACE IN SECTION
        for i, item in enumerate(section_list):
            if item is focused_w:
                element_num = i

        # CONVERT POSITION UNITS TO REPRESENT OVERALL [ROW][COL] OF GRID
        entry_row = ((section_num // 3) * 3) + (element_num // 3)
        entry_col = ((section_num % 3) * 3) + (element_num % 3)

        # CHANGE OVERALL [ROW][COLUMN] POSITION BASED ON KEY PRESS
        if event.keysym == "Up":
            if entry_row > 0:
                entry_row -= 1
        elif event.keysym == "Down":
            if entry_row < 8:
                entry_row += 1
        elif event.keysym == "Left":
            if entry_col > 0:
                entry_col -= 1
        elif event.keysym == "Right":
            if entry_col < 8:
                entry_col += 1

        # DETERMINE WHICH SECTION NEW WIDGET IS IN
        section_index = -1
        if entry_row < 3:
            if entry_col < 3:
                section_index = 0
            elif entry_col < 6:
                section_index = 1
            else:
                section_index = 2
        elif entry_row < 6:
            if entry_col < 3:
                section_index = 3
            elif entry_col < 6:
                section_index = 4
            else:
                section_index = 5
        else:
            if entry_col < 3:
                section_index = 6
            elif entry_col < 6:
                section_index = 7
            else:
                section_index = 8

        new_section = all_sections[section_index]

        # DETERMINE WHICH POSTION IN NEW SECTION WE CHANGED TO
        element_index = -1
        if entry_row % 3 == 0:
            if entry_col % 3 == 0:
                element_index = 0
            elif entry_col % 3 == 1:
                element_index = 1
            else:
                element_index = 2
        elif entry_row % 3 == 1:
            if entry_col % 3 == 0:
                element_index = 3
            elif entry_col % 3 == 1:
                element_index = 4
            else:
                element_index = 5
        elif entry_row % 3 == 2:
            if entry_col % 3 == 0:
                element_index = 6
            elif entry_col % 3 == 1:
                element_index = 7
            else:
                element_index = 8

        element = new_section.winfo_children()[element_index]

        # ADJUST FOCUS TO NEW ELEMENT AND RECOLOR GRID
        element.focus_set()
        self.smart_colorize(element)
        self.color_errors(element)

        # GET CONTENTS OF NEW WIDGET IF ENTRY - RECOLOR NOTE BUTTONS
        try:
            content = element.get()
        except AttributeError:
            content = ""
        self.color_note_buttons(content)

    # SAVE ASSOCITATED SETTINGS FILE WITH NEW PREFERENCES
    def save_settings(self):
        self.my_settings.update_highlight(self.highlight_color)
        self.my_settings.update_difficulty(self.difficulty.get())
        self.my_settings.update_error_recog(self.errors_on)

    # TURN OFF ALL WIDGET FUNCTIONALITY
    def disable_all_widgets(self):
        # DISABLE ALL CONTROL BUTTONS
        for element in self.buttons:
            element.config(state=DISABLED)

        # DISABLE ALL NOTE-TAKING BUTTONS
        for element in self.note_buttons:
            element.config(state=DISABLED)

        # DISABLE ALL GRID VALUES
        for row in self.disp_grid:
            for element in row:
                element.config(state=DISABLED)

        # DISABLE THE PAUSE BUTTON
        self.pause_button.config(state=DISABLED)

    # TURN ON ALL WIDGET FUNCTIONALITY
    def enable_all_widgets(self):
        # ENABLE ALL CONTROL BUTTONS
        for element in self.buttons:
            element.config(state=NORMAL)

        # ENABLE ALL NOTE-TAKING BUTTONS
        for element in self.note_buttons:
            element.config(state=NORMAL)

        # ENABLE ALL GRID VALUES
        for row in self.disp_grid:
            for element in row:
                element.config(state=NORMAL)

        # ENABLE THE PAUSE BUTTON
        self.pause_button.config(state=NORMAL)

    # AFTER NEW HIGH SCORE...
    # SHOW WHERE YOU RANK AMONG THE LEADERBOARD
    def show_results_window(self):

        # TURN OFF ALL WIDGETS; COLORIZE GREEN GRID
        self.disable_all_widgets()
        self.set_grid_color(Game.light_green)

        # CREATE NEW "RESULTS" POP-UP WINDOW
        self.results_window = Toplevel(self.master)
        self.results_window.title("DR Sudoku")
        x_now = self.master.winfo_x()
        y_now = self.master.winfo_y()
        self.results_window.geometry(f"350x300+{x_now + 100}+{y_now + 25}")
        self.results_window.minsize(350, 300)
        self.results_window.bind('<Destroy>',
                                 lambda x: self.exit_submit_name())

        # CREATE AND SHOW TEXT HEADERS IN "RESULTS" WINDOW
        header = Label(self.results_window,
                       text=self.difficulty.get() + " DIFFICULTY",
                       font=("Tahoma bold", 32))
        header.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        name_title = Label(self.results_window, text="  RECORD HOLDERS",
                           width=6, font=("Tahoma bold", 18), fg="green")
        name_title.grid(row=1, column=0, sticky=NSEW)

        score_title = Label(self.results_window, text="BEST TIMES", width=6,
                            font=("Tahoma bold", 18), fg="green")
        score_title.grid(row=1, column=1, sticky=NSEW)

        # DISPLAY GRID OF UPDATED HIGH SCORES
        for i, line in enumerate(self.my_settings.records_format):
            new_name = Label(self.results_window,
                             text=f"  {i + 1}. "
                                  + self.my_settings.records_names[i],
                             anchor=W, font=("Chalkduster", 12))
            new_name.grid(row=i + 2, column=0, sticky=NSEW)

            new_time = Label(self.results_window, text=line,
                              font=("Chalkduster", 12))
            new_time.grid(row=i + 2, column=1, sticky=NSEW)

            # COLOR CURRENT GAME RESULTS GREEN TO STAND OUT...
            if self.my_settings.records_names[i] == "*YOUR NAME*":
                new_name.config(fg="green")
                new_time.config(fg="green")

            # CHANGE COLOR FROM GRAY TO WHITE EVERY ROW
            if i % 2 == 0:
                new_name.config(bg=Game.my_gray)
                new_time.config(bg=Game.my_gray)

        # PLACE EMPTY ROWS UNDERNEATH RESULTS UP TO 10 TOTAL ROWS
        for i in range(len(self.my_settings.records_format), 10):
            empty_row = Label(self.results_window,
                              text="", font=("Chalkduster", 12))
            empty_row2 = Label(self.results_window,
                               text="", font=("Chalkduster", 12))
            empty_row.grid(row=i + 2, column=0, sticky=NSEW)
            empty_row2.grid(row=i + 2, column=1, sticky=NSEW)

            # CHANGE COLOR FROM GRAY TO WHITE EVERY ROW
            if i % 2 == 0:
                empty_row.config(bg=Game.my_gray)
                empty_row2.config(bg=Game.my_gray)

        # CREATE AND SHOW NAME ENTRY LABEL
        name_label = Label(self.results_window, text="ENTER YOUR NAME: ",
                           anchor=E, font=("Tahoma bold", 12))
        name_label.grid(row=12, column=0, sticky=NSEW)

        # CREATE AND SHOW NAME ENTRY
        self.name_entry = Entry(self.results_window,
                                width=10, bg=Game.light_green,
                                justify=CENTER, font=("Chalkduster", 18))
        self.name_entry.grid(row=12, column=1, sticky=NSEW)

        # CREATE AND SHOW SAVE BUTTON - LINK TO SUBMIT_NAME FXN
        ok_button = Button(self.results_window, text="SAVE",
                           command=self.submit_name, fg="green",
                           font=("Tahoma bold", 26))
        ok_button.grid(row=13, column=1, sticky=EW)

        # CONFIGURE WINDOW TO SCALE ALL ROWS/COLUMNS EQUALLY...
        self.results_window.columnconfigure((0, 1), weight=1, minsize=50)
        for i in range(14):
            self.results_window.rowconfigure(i, weight=1, minsize=10)

    # AFTER NEW HIGH SCORE...
    # AFTER YOU SAVE YOUR NAME...
    def submit_name(self):

        # GET ENTERED NAME AND SAVE NAME/RESULTS TO FILE
        self.my_name = self.name_entry.get()
        self.my_settings.update_record(self.my_name, self.og_diff)

        # TURN ON ONLY THE NEW GAME/DIFFICULTY BUTTONS
        self.buttons[0].config(state=NORMAL)
        self.buttons[1].config(state=NORMAL)

        # DESTROY "RESULTS" POP-UP WINDOW
        self.results_window.destroy()

    # AFTER NEW HIGH SCORE...
    # IF YOU CANCEL OUT OF SAVING YOUR NAME...
    def exit_submit_name(self):
        # TURN ON ONLY THE NEW GAME/DIFFICULTY BUTTONS - NOTHING ELSE
        self.buttons[0].config(state=NORMAL)
        self.buttons[1].config(state=NORMAL)

    # AFTER USER REQUEST TO RESET ALL DATA...
    def reset_data(self):

        # DO NOT ALLOW REQUEST/POP-UP WINDOW WHILE IN BETWEEN GAMES
        if self.is_paused:
            return

        # LOG TIME OF PAUSE, UPDATE PAUSE, UPDATE POP-UP STATUS
        self.recent_pause = time.time()
        self.is_paused = True
        self.pop_window = True

        # REMOVE MASTER WINDOW FROM SCREEN; CREATE NEW "RESET" WINDOW
        self.master.withdraw()
        self.reset_window = Toplevel(self.master)
        self.reset_window.title("DR Sudoku")
        x_now = self.master.winfo_x()
        y_now = self.master.winfo_y()
        self.reset_window.geometry(f"300x200+{x_now + 140}+{y_now + 200}")
        self.reset_window.minsize(300, 200)
        self.reset_window.maxsize(300, 200)
        self.reset_window.bind('<Destroy>', lambda x: self.cancel_reset())

        # CREATE AND SHOW WARNING LABELS
        title_label = Label(self.reset_window, text="WARNING!",
                            font=("Tahoma bold", 42), fg="red")
        title_label.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        message_label = Label(self.reset_window,
                              text="Are you sure you want\nto reset all data?",
                              font=("Tahoma", 16), padx=10)
        message_label.grid(row=1, column=0, rowspan=2, sticky=NSEW)

        # CREATE AND SHOW BUTTONS FOR CONFIRMATION
        yes_button = Button(self.reset_window, text="CONFIRM",
                            command=self.confirm_reset, width=10,
                            fg="red")
        yes_button.grid(row=1, column=1, sticky=S, pady=4)
        no_button = Button(self.reset_window, command=self.cancel_reset,
                           text="NEVERMIND", width=10, fg="green")
        no_button.grid(row=2, column=1, sticky=N, pady=4)

        # CONFIGURE ALL ROWS GROW AT A PROPORTIONAL RATE
        self.reset_window.rowconfigure((0,1,2), weight=1, minsize=40)

    # AFTER USER CONFIRMS TO RESET ALL DATA...
    def confirm_reset(self):

        # SHOW MASTER GRID
        self.master.deiconify()

        # BANK LATEST TIME PAUSED INTO "STEP PAUSE" VAR; UPDATE BOOLEANS
        self.step_pause = round(time.time() - self.recent_pause)
        self.is_paused = False
        self.pop_window = False

        # RESET SETTING IN SAVE FILE; DESTROY POP-UP WINDOW
        self.my_settings.reset_settings()
        self.reset_window.destroy()

        # RECOLORIZE WINDOW
        try:
            focused_w = self.master.focus_get()
            self.smart_colorize(focused_w)
            self.color_errors(focused_w)
        except AttributeError:
            pass

    # AFTER USER CANCELS REQUEST TO RESET ALL DATA...
    def cancel_reset(self):

        # BANK LATEST TIME PAUSED INTO "STEP PAUSE" VAR; UPDATE BOOLEANS
        self.master.deiconify()
        self.step_pause = round(time.time() - self.recent_pause)
        self.is_paused = False
        self.pop_window = False

        # DESTROY POP UP WINDOW
        self.reset_window.destroy()

        # COLORIZE GRID
        try:
            focused_w = self.master.focus_get()
            self.smart_colorize(focused_w)
            self.color_errors(focused_w)
        except AttributeError:
            pass

    # AFTER USER REQUEST TO AUTOSOLVE GAME...
    def check_autosolve_confirm(self):

        # DO NOT ALLOW REQUEST/POP-UP WINDOW WHILE IN BETWEEN GAMES
        if self.is_paused:
            return

        # SAVE CURRENT TIME; UPDATE PAUSE BOOLEANS
        self.recent_pause = time.time()
        self.is_paused = True
        self.pop_window = True

        # HIDE MASTER GRID AND CREATE NEW POP-UP WINDOW
        self.master.withdraw()
        self.solve_window = Toplevel(self.master)
        self.solve_window.title("DR Sudoku")
        x_now = self.master.winfo_x()
        y_now = self.master.winfo_y()
        self.solve_window.geometry(f"300x120+{x_now + 140}+{y_now + 200}")
        self.solve_window.minsize(300, 120)
        self.solve_window.maxsize(300, 120)
        self.solve_window.bind('<Destroy>', lambda x: self.cancel_autosolve())

        # CREATE AND SHOW MESSAGE
        message = Label(self.solve_window, text="Are you sure?",
                        font=("Chalkduster", 22))
        message.grid(row=0, column=0, columnspan=2, sticky=NSEW)

        #CREATE AND SHOW YES/NO BUTTONS; LINK BUTTONS TO HANDLER FXNS
        yes_button = Button(self.solve_window, text="YES",
                            command=self.confirm_autosolve, width=10,
                            fg="green")
        yes_button.grid(row=1, column=0, sticky=E, padx=4)
        no_button = Button(self.solve_window, command=self.cancel_autosolve,
                           text="CANCEL", width=10, fg="red")
        no_button.grid(row=1, column=1, sticky=W, padx=4)

        # MAKE ALL WIDGETS EXPAND AT SAME RATE
        self.solve_window.columnconfigure((0,1), weight=1)
        self.solve_window.rowconfigure((0,1), weight=1)

    # AFTER CONFIRMATION TO AUTOSOLVE GAME
    def confirm_autosolve(self):

        # HIDE MASTER GRID WINDOW
        self.master.deiconify()

        # BANK PAUSE TIME INTO "STEP PAUSE" VAR; UPDATE PAUSE/POP-UPS
        self.step_pause = round(time.time() - self.recent_pause)
        self.is_paused = False
        self.pop_window = False

        # SOLVE THE GRID AND DESTROY POP-UP WINDOW
        self.solve_display()
        self.solve_window.destroy()

        # DISABLE AUTOSOLVE, SUBMIT, AND NOTE BUTTONS
        self.buttons[2].config(state=DISABLED)
        self.buttons[3].config(state=DISABLED)
        for button in self.note_buttons:
            button.config(state=DISABLED)

        # COLOR GRID WHITE
        self.set_grid_color("white")

    # AFTER CANCEL AUTOSOLVE GAME
    def cancel_autosolve(self):

        # SHOW MASTER GRID AGAIN
        self.master.deiconify()

        # BANK PAUSE TIME INTO "STEP PAUSE" VAR; UPDATE PAUSE/POP-UPS
        self.step_pause = round(time.time() - self.recent_pause)
        self.is_paused = False
        self.pop_window = False

        # DESTROY POP-UP WINDOW
        self.solve_window.destroy()

        #COLOR GRID IF WIDGET HAS A FOCUS
        try:
            focused_w = self.master.focus_get()
            self.smart_colorize(focused_w)
            self.color_errors(focused_w)
        except AttributeError:
            pass

    # AFTER USER REQUEST TO VIEW OLD RECORDS
    def view_records(self):

        # DISALLOW VIEW SCREEN IF GAME ALREADY PAUSED
        if self.is_paused:
            return

        # GAME NOT PAUSED - STORE TIME STARTED VIEWING
        # HIDE MAIN WINDOW - CREATE RESULTS WINDOW
        self.recent_pause = time.time()
        self.is_paused = True
        self.pop_window = True
        self.master.withdraw()
        self.view_window = Toplevel(self.master)
        self.view_window.title("DR Sudoku")
        x_now = self.master.winfo_x()
        y_now = self.master.winfo_y()
        self.view_window.geometry(f"350x100+{x_now}+{y_now + 25}")
        self.view_window.minsize(600, 500)
        self.view_window.maxsize(600, 500)
        self.view_window.bind('<Destroy>', lambda x: self.cancel_view())

        # GET OLD RECORDS LIST FROM SETTINGS OBJECT
        results = self.my_settings.get_all_records()

        # SET UP ALL TITLES ON RESULTS SCREEN
        title_label = Label(self.view_window, text="ALL-TIME RECORDS",
                            font=("Tahoma bold", 36), fg="blue")
        title_label.grid(row=0, column=0, columnspan=4, sticky=NSEW)

        easy_label = Label(self.view_window, text="EASY",
                           font=("Tahoma", 24), fg="green")
        medium_label = Label(self.view_window, text="MEDIUM",
                             font=("Tahoma", 24), fg=Game.my_yellow)
        hard_label = Label(self.view_window, text="HARD",
                           font=("Tahoma", 24), fg="orange")
        expert_label = Label(self.view_window, text="EXPERT",
                             font=("Tahoma", 24), fg="red")
        easy_label.grid(row=1, column=0, sticky=NSEW)
        medium_label.grid(row=1, column=1, sticky=NSEW)
        hard_label.grid(row=1, column=2, sticky=NSEW)
        expert_label.grid(row=1, column=3, sticky=NSEW)

        # SHOW TEN RESULTS FOR EACH DIFFICULTY
        for i in range(10):
            ez_row = Label(self.view_window, text=results[0][i], font=("Chalkduster", 12), anchor=W)
            md_row = Label(self.view_window, text=results[1][i], font=("Chalkduster", 12), anchor=W)
            hd_row = Label(self.view_window, text=results[2][i], font=("Chalkduster", 12), anchor=W)
            ex_row = Label(self.view_window, text=results[3][i], font=("Chalkduster", 12), anchor=W)

            ez_row.grid(row=i + 2, column=0, sticky=NSEW)
            md_row.grid(row=i + 2, column=1, sticky=NSEW)
            hd_row.grid(row=i + 2, column=2, sticky=NSEW)
            ex_row.grid(row=i + 2, column=3, sticky=NSEW)

            # ALTERNATING COLORS WHITE/GRAY
            if i % 2 == 0:
                ez_row.config(bg=Game.my_gray)
                md_row.config(bg=Game.my_gray)
                hd_row.config(bg=Game.my_gray)
                ex_row.config(bg=Game.my_gray)

        # CREATE USER BUTTON
        done_btn = Button(self.view_window, text="DONE", command=self.cancel_view,
                             font=("Tahoma bold", 24), fg="blue")
        done_btn.grid(row=12, column=0, columnspan=4)

        spacer = Label(self.view_window, text="", font=("Tahoma bold", 12))
        spacer.grid(row=13, column=0, sticky=NSEW)

        # CONFIGURE ROWS AND COLUMN WEIGHT
        self.view_window.columnconfigure((0,1,2,3), weight=1)
        for i in range(14):
            self.view_window.rowconfigure(i, weight=1)

    # AFTER EXITING VIEW-RECORDS WINDOW
    def cancel_view(self):

        # RESTORE MAIN WINDOW - END PAUSED TIME
        # DESTROY RESULTS WINDOW
        self.master.deiconify()
        self.step_pause = round(time.time() - self.recent_pause)
        self.is_paused = False
        self.pop_window = False
        self.view_window.destroy()

        # IF GAME STILL IN PROGRESS - RECOLORIZE GRID
        if self.running:
            try:
                focused_w = self.master.focus_get()
                self.smart_colorize(focused_w)
                self.color_errors(focused_w)
            except AttributeError:
                pass

    # AFTER USER REQUEST TO UPDATE SUDOKU BANK
    def confirm_update(self):

        # DISALLOW REQUEST IF GAME IS CURRENTLY PAUSED
        if self.is_paused:
            return

        # LOG LAST PAUSE TIME
        # HIDE MAIN WINDOW - SHOW POP-UP WINDOW
        self.recent_pause = time.time()
        self.is_paused = True
        self.pop_window = True
        self.master.withdraw()
        self.disable_all_widgets()
        self.update_window = Toplevel(self.master)
        self.update_window.title("DR Sudoku")
        x_now = self.master.winfo_x()
        y_now = self.master.winfo_y()
        self.update_window.geometry(f"350x100+{x_now + 140}+{y_now + 200}")
        self.update_window.minsize(300, 120)
        self.update_window.maxsize(300, 120)
        self.update_window.bind('<Destroy>', lambda x: self.cancel_update())

        # CREATE MESSAGES AND DISPLAY THEM
        message = Label(self.update_window, text="Are you sure?",
                        font=("Chalkduster", 22))
        message.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        sub_message = Label(self.update_window, text="This process may take several minutes...")
        sub_message.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        sub_message2 = Label(self.update_window, text="You must have internet access to update")
        sub_message2.grid(row=2, column=0, columnspan=2, sticky=NSEW)

        # CREATE AND DISPLAY YES/NO BUTTONS
        yes_button = Button(self.update_window, text="YES",
                            command=self.update_bank, width=10,
                            fg="green")
        yes_button.grid(row=3, column=0, sticky=E, padx=4)
        no_button = Button(self.update_window, command=self.cancel_update,
                           text="CANCEL", width=10, fg="red")
        no_button.grid(row=3, column=1, sticky=W, padx=4)

        # CONFIGURE ROWS AND COLUMNS
        self.update_window.columnconfigure((0,1), weight=1)
        self.update_window.rowconfigure((0,1,2,3), weight=1)

    # AFTER USER CONFIRMATION TO UPDATE SUDOKU BANK
    def update_bank(self):

        # CREATE REFRESHER OBJECT - UPDATE THE BANK
        Refresher()

        # DISPLAY THE MAIN WINDOW - LOG "UN-PAUSE" TIME
        self.master.deiconify()
        self.update_window.destroy()
        self.step_pause = round(time.time() - self.recent_pause)
        self.is_paused = False
        self.pop_window = False

        # IF GAME IS BEING PLAYED RIGHT NOW
        if self.running:
            self.enable_all_widgets()

        # COLORIZE GRID IF POSSIBLE
        try:
            focused_w = self.master.focus_get()
            self.smart_colorize(focused_w)
            self.color_errors(focused_w)
        except AttributeError:
            pass

    # AFTER CANCEL UPDATE TO SUDOKU BANK
    def cancel_update(self):

        # SHOW MAIN WINDOW - DESTROY POP-UP WINDOW
        # LOG "UN"PAUSED TIME
        self.master.deiconify()
        self.step_pause = round(time.time() - self.recent_pause)
        self.is_paused = False
        self.pop_window = False
        self.update_window.destroy()

        # IF NOT IN BETWEEN GAMES ENABLE WIDGETS
        if self.running:
            self.enable_all_widgets()

        # COLORIZE GRID IF POSSIBLE
        try:
            focused_w = self.master.focus_get()
            self.smart_colorize(focused_w)
            self.color_errors(focused_w)
        except AttributeError:
            pass

    # CHANGE GRID HIGHLIGHT COLOR
    def change_color(self, new_color):

        # INITIALIZE CHECK BUTTONS ALL FALSE
        self.yellow_check.set(False)
        self.purple_check.set(False)
        self.green_check.set(False)
        self.blue_check.set(False)
        self.clear_check.set(False)

        # SET CORRECT CHECK BUTTON AS TRUE
        if new_color == Game.light_yellow:
            self.yellow_check.set(True)
        if new_color == Game.my_purple:
            self.purple_check.set(True)
        if new_color == Game.light_green:
            self.green_check.set(True)
        if new_color == Game.light_blue:
            self.blue_check.set(True)
        if new_color == "white":
            self.clear_check.set(True)

        # UPDATE LOGGED COLOR
        Game.highlight_color = new_color
        self.highlight_color = Game.highlight_color
        self.save_settings()

        # ERRORS TURNED OFF
        if self.error_color != Game.error_color:
            self.error_color = self.highlight_color
        try:
            if self.started and self.running and not self.just_started:
                focused_w = self.master.focus_get()
                self.smart_colorize(focused_w)
                self.color_errors(focused_w)
        except AttributeError:
            pass

    # CHANGE ERROR PREFERENCE
    def toggle_errors(self):

        # IF ERRORS CURRENTLY TURNED ON
        if self.errors_on:
            self.error_color = self.highlight_color
            self.errors_on = False

        # IF ERRORS CURRENTLY TURNED OFF
        else:
            self.error_color = Game.error_color
            self.errors_on = True
        self.error_recog.set(self.errors_on)

        # COLOR GRID IF POSSIBLE AND NOT BETWEEN GAMES
        try:
            if self.started and self.running and not self.just_started:
                self.smart_colorize(self.master.focus_get())
                self.color_errors(self.master.focus_get())
        except AttributeError:
            pass

        self.save_settings()

    # PAUSE THE GAME - FROM PAUSE BUTTON ICON
    def toggle_pause_button(self):
        self.pause_check.set(True)
        self.toggle_pause()

    # CHECK IF THE SELECTED ITEM IS WITHIN CURRENT GAME LAYOUT
    def is_focus_valid(self):

        # NOT VALID IF BETWEEN GAMES
        # ATTEMPT TO GET SELECTED ITEM
        if not self.running:
            return False
        try:
            focused_w = self.master.focus_get()
        except AttributeError:
            return False

        # ACQUIRE MOST RECENT GRID
        current_sections = self.core_frame.winfo_children()[-9:]

        # ACQUIRE SELECTED GRID ITEM
        section_frame = focused_w.master

        # CHECK IF SELECTED GRID ITEM IS IN MOST RECENT GRID
        if section_frame in current_sections:
            return True
        return False

    # TOGGLE PAUSE GAME - FROM MENU BAR
    def toggle_pause(self):

        # DISALLOW PAUSE IF IN BETWEEN GAMES
        if self.pop_window or not self.running and not self.just_started:
            self.pause_check.set(False)
            return

        # ALLOW FUNCTION TO TOGGLE PAUSE ONLY ON FIRST PASS
        if self.pause_check.get() and not self.just_paused:
            self.just_paused = True
        else:
            self.just_paused = False
            self.multiple_asks = True

        # FUNCTION ALLOWED TO PAUSE GAME
        if self.just_paused and not self.multiple_asks:

            # LOG MOST RECENT PAUSED TIME
            # UPDATE GAME-PAUSE STATUS
            self.recent_pause = time.time()
            self.is_paused = True

            # HIDE MAIN WINDOW AND DISPLAY PAUSE WINDOW
            self.master.withdraw()
            self.pause_window = Toplevel(self.master)
            self.pause_window.title("DR Sudoku")
            x_now = self.master.winfo_x()
            y_now = self.master.winfo_y()
            self.pause_window.geometry(f"350x100+{x_now + 170}+{y_now + 100}")
            self.pause_window.minsize(265, 90)
            self.pause_window.maxsize(265, 90)
            self.pause_window.bind('<Destroy>', lambda x: self.toggle_pause())

            # CREATE LABELS AND BUTTONS WITHIN PAUSE WINDOW
            spacer = Label(self.pause_window, text="", font=("Tahoma bold", 10))
            spacer.grid(row=0, column=0, sticky=NSEW)
            spacer_left = Label(self.pause_window, text="", font=("", 10))
            spacer_left.grid(row=1, column=0, sticky=NSEW)
            resume_btn = Button(self.pause_window, text="RESUME",
                                command=self.toggle_pause, width=10,
                                fg="green", font=("Tahoma bold", 36))
            resume_btn.grid(row=1, column=1, sticky=NSEW, padx=4)

        # GAME HAS JUST BEEN "UN"PAUSED
        else:

            # DESTROY PAUSE WINDOW - SHOW MAIN WINDOW
            self.master.deiconify()
            self.pause_window.destroy()
            self.pause_check.set(False)
            self.just_paused = False
            self.step_pause = round(time.time() - self.recent_pause)
            self.is_paused = False

            # ATTEMPT TO COLOR GRID IF POSSIBLE
            try:
                focused_w = self.master.focus_get()
                self.smart_colorize(focused_w)
                self.color_errors(focused_w)
            except AttributeError:
                pass

    # SET UP ALL GAME MENUS
    def config_menus(self):

        # CREATE MAIN MENU BAR
        my_menu = Menu(self.master)
        self.master.config(menu=my_menu)
        command_menu = Menu(my_menu)
        options_menu = Menu(my_menu)

        # COMMAND MENU BAR
        my_menu.add_cascade(label="Commands", menu=command_menu)
        self.pause_check = BooleanVar()
        self.pause_check.set(False)
        command_menu.add_checkbutton(label="Pause Game", onvalue=1, offvalue=0,
                                     variable=self.pause_check, command=self.toggle_pause)
        command_menu.add_separator()
        command_menu.add_command(label="View Records", command=self.view_records)
        command_menu.add_separator()
        command_menu.add_command(label="Reset Data", command=self.reset_data)
        command_menu.add_command(label="Update Sudoku Bank",
                                 command=self.confirm_update)

        # OPTION MENU BAR
        my_menu.add_cascade(label="Options", menu=options_menu)

        # CREATE ALL FAV-COLOR CHECK VARIABLES
        self.yellow_check = BooleanVar()
        self.purple_check = BooleanVar()
        self.green_check = BooleanVar()
        self.blue_check = BooleanVar()
        self.clear_check = BooleanVar()

        # INITIALIZE ALL FAV-COLORS FALSE
        self.yellow_check.set(False)
        self.purple_check.set(False)
        self.green_check.set(False)
        self.blue_check.set(False)
        self.clear_check.set(False)

        # CHECK TRUE FOR CURRENT SELECTED FAVORITE
        if self.highlight_color == Game.light_yellow:
            self.yellow_check.set(True)
        elif self.highlight_color == Game.my_purple:
            self.purple_check.set(True)
        elif self.highlight_color == Game.light_green:
            self.green_check.set(True)
        elif self.highlight_color == Game.light_blue:
            self.blue_check.set(True)
        elif self.highlight_color == "white":
            self.clear_check.set(True)

        # CREATE ALL FAV-COLOR CHECK BUTTONS
        color_menu = Menu(options_menu)
        options_menu.add_cascade(label="Highlight Color", menu=color_menu)
        color_menu.add_checkbutton(label="Yellow", onvalue=1, offvalue=0,
                                   variable=self.yellow_check,
                                   command=lambda: self.change_color(Game.light_yellow))
        color_menu.add_checkbutton(label="Purple", onvalue=1, offvalue=0,
                                   variable=self.purple_check,
                                   command=lambda: self.change_color(Game.my_purple))
        color_menu.add_checkbutton(label="Green", onvalue=1, offvalue=0,
                                   variable=self.green_check,
                                   command=lambda: self.change_color(Game.light_green))
        color_menu.add_checkbutton(label="Blue", onvalue=1, offvalue=0,
                                   variable=self.blue_check,
                                   command=lambda: self.change_color(Game.light_blue))
        color_menu.add_checkbutton(label="None", onvalue=1, offvalue=0,
                                   variable=self.clear_check,
                                   command=lambda: self.change_color("white"))

        # INITIALIZE ERROR-RECOGNITION TRUE
        options_menu.add_separator()
        self.error_recog = BooleanVar()
        self.error_recog.set(True)
        options_menu.add_checkbutton(label="Error Recognition", onvalue=1, offvalue=0,
                                     variable=self.error_recog,
                                     command=self.toggle_errors)

    # UPDATE SUDOKU BOARD WITH NOTE NUMBERS
    def set_note(self, num):

        # IF USER HAS ALREADY SELECTED A CELL
        try:
            focused_widget = self.master.focus_get()
            current = focused_widget.get()

            # DETERMINE NEW LINE
            if current.find(str(num)) == -1:
                line = "".join(sorted(current+str(num)))
            else:
                line = current.replace(str(num), '')
            if len(line) > Game.max_notes:
                self.message_label.config(text=f"Only {Game.max_notes} notes allowed per cell...")
                return

            self.taking_notes = True
            # CLEAR FIELD
            while len(focused_widget.get()) > 0:
                focused_widget.delete(0)

            # ADJUST NOTE NUMBERS IN GRID
            focused_widget.insert(0, line)
            focused_widget.config(font=("Chalkduster", 12),
                                  justify=CENTER, fg="purple")

            # UPDATE NOTE BUTTON COLOR
            self.color_note_buttons(line)
            self.change_noting(focused_widget, True)
            self.taking_notes = False

        # IF USER HAS NOT YET SELECTED A CELL
        except AttributeError:
            self.message_label.config(text="Select a cell...")

    # LEFT OF HERE...
    def display(self):
        #   SET UP A FRAME FOR EACH QUADRANT
        self.sections = []
        sm_spacing, lg_spacing = 0.5, 2
        for i in range(3):
            self.sections.append([])
            self.core_frame.columnconfigure(i, weight=1, minsize=165)
            self.core_frame.rowconfigure(i, weight=1, minsize=165)
            for j in range(3):
                section_frame = Frame(self.core_frame, bg="black")
                section_frame.grid(row=i, column=j,
                                padx=lg_spacing, pady=lg_spacing,
                                sticky=NSEW)
                section_frame.columnconfigure((0, 1, 2), weight=1, minsize=55)
                section_frame.rowconfigure((0, 1, 2), weight=1, minsize=55)
                self.sections[i].append(section_frame)

        self.disp_grid = []
        for i in range(9):
            self.disp_grid.append([])

            #look up text widget
            for j in range(9):
                #check for each box
                #box started empty
                og_val = self.original_grid[i][j]
                grid_val = self.grid[i][j]
                user_val = self.user_grid[i][j]

                if og_val == 0:
                    if self.setting:
                        var_color = "black"
                    elif ((user_val == 0 or len(str(user_val)) > 1) and grid_val != 0) or self.noting[i][j]:
                        var_color = "blue"
                    elif user_val == grid_val:
                        var_color = "green"
                    elif user_val != 0:
                        var_color = "red"
                else:
                    var_color = "black"

                if self.grid[i][j] == 0:
                    new_icon = Entry(self.sections[i//3][j//3], width=1,
                                     insertontime=0,
                                     justify=CENTER, fg=var_color, bg="white",
                                     disabledbackground=Game.light_green, validate="key",
                                     validatecommand=(self.reg, '%S', '%d'))
                    new_icon.bind("<1>", self.on_click)
                    if self.setting:
                        new_icon.config(font=("Tahoma bold", 28))
                    else:
                        new_icon.config(font=("Chalkduster", 28))
                else:
                    new_icon = Label(self.sections[i//3][j//3],
                                     text=str(self.grid[i][j]),
                                     fg=var_color, bg="white",
                                     highlightthickness=2)
                    if self.original_grid[i][j] == 0:
                        new_icon.config(font=("Chalkduster", 28))
                    else:
                        new_icon.config(font=("Tahoma bold", 28))

                #CHANGES MADE HERE
                new_icon.grid(row=i%3, column=j%3,
                              padx=sm_spacing, pady=sm_spacing,
                              sticky=NSEW)
                self.disp_grid[i].append(new_icon)

    def adjust_difficulty(self, *args):
        if self.difficulty.get() == "EASY":
            self.buttons[1].config(fg="green",
                                   activeforeground="green")
        elif self.difficulty.get() == "MEDIUM":
            self.buttons[1].config(fg=Game.my_yellow,
                                   activeforeground=Game.my_yellow)
        elif self.difficulty.get() == "HARD":
            self.buttons[1].config(fg="orange",
                                   activeforeground="orange")
        elif self.difficulty.get() == "EXPERT":
            self.buttons[1].config(fg="red",
                                   activeforeground="red")
        elif self.difficulty.get() == "CUSTOM":
            self.buttons[1].config(fg="purple",
                                   activeforeground="purple")

        '''self.buttons[1].config(text=self.difficulty,
                               fg=diff_color,
                               activeforeground=diff_color)'''

    def solve_display(self):
        self.brain.update_grid(self.original_grid)

        #auto changes the grid...
        self.brain.solve()
        self.grid = self.brain.grid

        for i in range(9):
            for j in range(9):
                if self.original_grid[i][j] == 0:
                    val = self.disp_grid[i][j].get()
                    self.user_grid[i][j] = 0 if val == "" else int(val)

        self.message_label.config(text="Sudoku Auto-Solved!")
        self.display()
        self.running = False
        self.set_grid_color("white")

    def submit(self):

        for i in range(9):
            for j in range(9):
                if self.original_grid[i][j] == 0:
                    val = self.disp_grid[i][j].get()
                    self.user_grid[i][j] = 0 if val == "" else int(val)

        self.brain.update_grid(self.user_grid)
        if self.brain.eval():
            self.message_label.config(text="Perfect!")
            self.running = False
            for button in self.note_buttons:
                button.config(state=DISABLED)
            self.set_grid_color(Game.light_green)

            self.buttons[2].config(state=DISABLED)
            self.buttons[3].config(state=DISABLED)
            self.color_note_buttons("")

            new_r = self.my_settings.check_record(self.og_diff, int(time.time() - self.start_time - self.total_pause))
            if new_r:
                self.show_results_window()

        else:
            self.message_label.config(text="Sorry, try again!")
        self.brain.update_grid(self.original_grid)

    def new_game(self):
        self.og_diff = str(self.difficulty.get())
        self.total_pause = 0
        self.step_pause = 0
        self.is_paused = False
        self.just_paused = False
        self.multiple_asks = False
        self.pop_window = False
        self.just_started = True
        for button in self.note_buttons:
            button.config(state=NORMAL)

        if self.difficulty.get() == "CUSTOM":
            self.buttons[0].config(text="BEGIN", command=self.begin_custom)

            '''self.buttons[0] = Button(self.button_frame, text="BEGIN",
                                     command=self.begin_custom, width=30)
            self.buttons[0].grid(row=0, column=0,
                                 ipadx=self.button_spacing, ipady=self.button_spacing)'''
            for i in range(9):
                for j in range(9):
                    self.original_grid[i][j] = 0
                    self.grid[i][j] = 0
                    self.user_grid[i][j] = 0
            self.timer_label.config(text="00:00")

            for i in [1, 2, 3]:
                self.buttons[i].config(state=DISABLED)
            for i in range(9):
                self.note_buttons[i].config(state=DISABLED)
            self.pause_button.config(state=DISABLED)

            self.running = False
            self.setting = True
            self.started = True
        else:
            self.running = True
            self.message_label.config(text="")
            self.buttons[2].config(state=NORMAL)
            self.buttons[3].config(state=NORMAL)
            self.original_grid = self.get_new_grid(self.difficulty.get())
            self.grid = self.original_grid
            self.pause_button.config(state=NORMAL)

            # set up working grid
            self.user_grid = []
            for i in range(9):
                self.user_grid.append([])
                for j in range(9):
                    self.user_grid[i].append(self.original_grid[i][j])

            #setting note grid
            self.noting = []
            for i in range(9):
                self.noting.append([])
                for j in range(9):
                    self.noting[i].append(False)
            self.taking_notes = False
            self.started = True
            self.color_note_buttons("")
            self.just_started = True

        self.display()
        self.save_settings()

    def begin_custom(self):
        self.running = True
        self.setting = False
        self.just_started = True

        #re-enable buttons
        for i in [1, 2, 3]:
            self.buttons[i].config(state=NORMAL)
        for i in range(9):
            self.note_buttons[i].config(state=NORMAL)
        self.pause_button.config(state=NORMAL)

        self.start_time = time.time()
        self.buttons[0].config(text="NEW GAME", command=self.new_game)
        self.difficulty.set("EASY")

        '''self.buttons[0] = Button(self.button_frame, text="NEW GAME",
                                 command=self.new_game, width=30)
        self.buttons[0].grid(row=0, column=0,
                             ipadx=self.button_spacing, ipady=self.button_spacing)'''
        self.adjust_difficulty()

        for i in range(9):
            for j in range(9):
                val = self.disp_grid[i][j].get()
                if val == "":
                    val = 0
                else:
                    val = int(val)
                self.original_grid[i][j] = val
                self.grid[i][j] = val
                self.user_grid[i][j] = val

        self.color_note_buttons("")
        self.display()

    def get_new_grid(self, difficulty):
        grids = [[], [], [], []]
        pos = 0
        if difficulty == "EASY":
            pos = 0
        elif difficulty == "MEDIUM":
            pos = 1
        elif difficulty == "HARD":
            pos = 2
        elif difficulty == "EXPERT":
            pos = 3

        with open('Sudoku File', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            for i, line in enumerate(csv_reader):
                if i < 50:
                    grids[0].append(line[0])
                elif i < 100:
                    grids[1].append(line[0])
                elif i < 150:
                    grids[2].append(line[0])
                elif i < 200:
                    grids[3].append(line[0])

        line_grid = grids[pos][random.randint(0, 49)]
        new_grid = []
        for i, char in enumerate(line_grid):
            if i % 9 == 0:
                new_grid.append([])
            if char == '.':
                num = 0
            else:
                num = int(char)
            new_grid[i//9].append(num)

        self.start_time = time.time()
        return new_grid

    def correct_entry(self, x, type):
        focused_widget = self.master.focus_get()

        '''
        #SUPPOSEDLY THERE FOR BLANK INPUTS
        if x == "":
            return True'''
        if x.isdigit():
            if int(x) > 0:
                #focused_widget.insert(0, x)
                #somehow its returning none to no longer validate
                #focused_widget.icursor(0)
                focused_widget.delete(0, END)
                if self.setting:
                    focused_widget.config(font=("Tahoma bold", 28), fg="black")
                else:
                    focused_widget.config(font=("Chalkduster", 28), fg="green")
                if type == "1":
                    focused_widget.insert(0, x)
                    self.color_note_buttons(x)
                else:
                    self.color_note_buttons("")
                if self.running:
                    self.smart_colorize(focused_widget)
                    self.change_noting(focused_widget, False)
                    if not self.taking_notes:
                        self.color_errors(focused_widget)
                self.master.after_idle(lambda: focused_widget.config(validate='key'))
        return False

    def on_click(self, event):
        if not self.running:
            return
        self.message_label.config(text="")
        self.master.after_idle(event.widget.icursor, END)
        self.started = True
        self.just_started = False

        self.smart_colorize(event.widget)
        self.color_errors(event.widget)

        self.color_note_buttons(event.widget.get())

    def smart_colorize(self, focused_w):
        if self.just_started:
            return

        #focused_w = self.master.focus_get()
        all_sections = focused_w.master.master.winfo_children()[-9:]
        section_frame = focused_w.master
        section_list = section_frame.winfo_children()
        section_num = -1
        element_num = -1

        self.set_grid_color("white")
        for i, section in enumerate(all_sections):
            if section is section_frame:
                section_num = i

        section_frame.config(bg="black")
        for i, item in enumerate(section_list):
            item.config(bg=self.highlight_color)
            if item is focused_w:
                element_num = i

        entry_row = ((section_num // 3) * 3) + (element_num // 3)
        entry_col = ((section_num % 3) * 3) + (element_num % 3)

        #this is a label
        if self.original_grid[entry_row][entry_col] != 0:
            self.set_grid_color("white")
            focused_w.config(bg=self.highlight_color)
            return

        #highlight horizontal/vertical
        for i, section in enumerate(all_sections):
            #same horizontal
            if i // 3 == section_num // 3:
                for j, item in enumerate(section.winfo_children()):
                    if j // 3 == element_num // 3:
                        item.config(bg=self.highlight_color)
            #same vertical
            elif i % 3 == section_num % 3:
                for j, item in enumerate(section.winfo_children()):
                    if j % 3 == element_num % 3:
                        item.config(bg=self.highlight_color)

    def color_errors(self, focused_w):
        all_sections = focused_w.master.master.winfo_children()[-9:]
        section_frame = focused_w.master
        section_list = section_frame.winfo_children()
        section_num = -1
        element_num = -1
        err_found = False

        #get section num
        for i, section in enumerate(all_sections):
            if section is section_frame:
                section_num = i

        for i, item in enumerate(section_list):
            if item is focused_w:
                element_num = i

        entry_row = ((section_num // 3) * 3) + (element_num // 3)
        entry_col = ((section_num % 3) * 3) + (element_num % 3)

        try:
            entry_val = focused_w.get()
        except AttributeError:
            entry_val = str(self.original_grid[entry_row][entry_col])

        entry_noting = self.noting[entry_row][entry_col]
        if self.taking_notes and len(entry_val) > 1:
            entry_noting = True

        #highlight section errors
        for i, item in enumerate(section_list):
            if item is not focused_w:
                row = ((section_num // 3) * 3) + (i // 3)
                col = ((section_num % 3) * 3) + (i % 3)
                try:
                    item_val = item.get()
                except AttributeError:
                    item_val = str(self.original_grid[row][col])
                if item_val == entry_val and entry_val != "":
                    if not self.noting[row][col] and not entry_noting:
                        item.config(bg=self.error_color)
                        err_found = True

        #highlight horizontal/vertical
        for i, section in enumerate(all_sections):
            #same horizontal
            if i // 3 == section_num // 3:
                for j, item in enumerate(section.winfo_children()):
                    if j // 3 == element_num // 3:
                        row = ((i // 3) * 3) + (j // 3)
                        col = ((i % 3) * 3) + (j % 3)
                        try:
                            item_val = item.get()
                        except AttributeError:
                            item_val = str(self.original_grid[row][col])
                        if item_val == entry_val and entry_val != "":
                            if not self.noting[row][col] and not entry_noting:
                                if item is not focused_w:
                                    item.config(bg=self.error_color)
                                    err_found = True
            #same horizontal
            elif i % 3 == section_num % 3:
                for j, item in enumerate(section.winfo_children()):
                    if j % 3 == element_num % 3:
                        row = ((i // 3) * 3) + (j // 3)
                        col = ((i % 3) * 3) + (j % 3)
                        try:
                            item_val = item.get()
                        except AttributeError:
                            item_val = str(self.original_grid[row][col])
                        if item_val == entry_val and entry_val != "":
                            if not self.noting[row][col] and not entry_noting:
                                if item is not focused_w:
                                    item.config(bg=self.error_color)
                                    err_found = True

        #set focused if need be
        if err_found:
            focused_w.config(bg=self.error_color)

    def set_grid_color(self, color):
        core_grid = self.master.winfo_children()[3]
        for section in core_grid.winfo_children():
            for box in section.winfo_children():
                box.config(bg=color)

    def color_note_buttons(self, contents):
        for i in range(10):
            if str(contents).find(str(i)) == -1:
                self.note_buttons[int(i)-1].config(fg="purple")
            else:
                self.note_buttons[int(i)-1].config(fg="gray")

    def change_noting(self, focused_w, noting):
        all_sections = focused_w.master.master.winfo_children()[-9:]
        section_frame = focused_w.master
        section_list = section_frame.winfo_children()
        section_num = -1
        element_num = -1

        for i, section in enumerate(all_sections):
            if section is section_frame:
                section_num = i

        for i, item in enumerate(section_list):
            if item is focused_w:
                element_num = i

        row = ((section_num // 3) * 3) + (element_num // 3)
        col = ((section_num % 3) * 3) + (element_num % 3)
        self.noting[row][col] = noting

        #print(self.noting)


root = Tk()
root.title("DR Sudoku")
root.geometry("600x700+400+100")
root.minsize(500, 700)
root.maxsize(800,900)

root.lift()
'''root.attributes('-topmost',True)
root.after_idle(root.attributes,'-topmost',False)'''

game = Game(root)
root.mainloop()
