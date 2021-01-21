

# HANDLES ALL INTERACTION WITH SAVE FILE
class SaveSettings:

    # READ INITIAL SAVE FILES
    def __init__(self):

        # CREATE BLANK LISTS
        self.records_format = []
        self.records_raw = []
        self.records_names = []

        # ACQUIRE ALL LINES IN TEXT FILE
        with open("Sudoku Settings.txt", "r") as file:
            self.txt_file = file.read().split("\n")

    # CLEAR FILE HISTORY
    def reset_settings(self):

        # CREATE DEFAULT FILE LINES
        blank_file = [
            "HIGHLIGHT:#ffffc7",
            "DIFFICULTY:EASY",
            "ERRORS ON:1",
            "RECORDS: EASY",
            "RECORDS: MEDIUM",
            "RECORDS: HARD",
            "RECORDS: EXPERT",
            "RECORDS: END OF LIST"
        ]

        # SAVE DEFAULTS TO FILE
        SaveSettings.list_to_file(blank_file)

    # ACQUIRE ALL HIGH SCORES
    def get_all_records(self):

        # STARTING POSITIONS FOR EACH DIFFICULTY
        index_0 = self.txt_file.index('RECORDS: EASY')
        index_1 = self.txt_file.index('RECORDS: MEDIUM')
        index_2 = self.txt_file.index('RECORDS: HARD')
        index_3 = self.txt_file.index('RECORDS: EXPERT')
        index_4 = self.txt_file.index('RECORDS: END OF LIST')

        # FIND QUANTITIES OF SAVES FOR EACH DIFFICULTY
        easy_count = (index_1 - index_0 - 1) // 2
        medium_count = (index_2 - index_1 - 1) // 2
        hard_count = (index_3 - index_2 - 1) // 2
        expert_count = (index_4 - index_3 - 1) // 2

        # CREATE 2D LIST OF HIGH SCORES - EASY, MEDIUM, HARD, EXPERT
        results = [[], [], [], []]
        for i in range(easy_count):
            name = self.txt_file[index_0 + 1 + easy_count + i]
            score = SaveSettings.format_time(self.txt_file[index_0 + 1 + i])
            results[0].append(f"  {i + 1}. {name} - {score}")
        for i in range(medium_count):
            name = self.txt_file[index_1 + 1 + medium_count + i]
            score = SaveSettings.format_time(self.txt_file[index_1 + 1 + i])
            results[1].append(f"  {i + 1}. {name} - {score}")
        for i in range(hard_count):
            name = self.txt_file[index_2 + 1 + hard_count + i]
            score = SaveSettings.format_time(self.txt_file[index_2 + 1 + i])
            results[2].append(f"  {i + 1}. {name} - {score}")
        for i in range(expert_count):
            name = self.txt_file[index_3 + 1 + expert_count + i]
            score = SaveSettings.format_time(self.txt_file[index_3 + 1 + i])
            results[3].append(f"  {i + 1}. {name} - {score}")

        # ADD MORE BLANK ROWS UNTIL TEN ROWS TAKEN
        for diff in results:
            if len(diff) < 10:
                for i in range(10 - len(diff)):
                    diff.append("")

        return results

    # OVERWRITE A FILE WITH VARIABLE LIST
    @staticmethod
    def list_to_file(lines):

        # WRITE TO TEXT FILE LINE BY LINE
        with open("Sudoku Settings.txt", "w") as file:
            for i, element in enumerate(lines):
                file.write(element)
                if i < len(lines) - 1:
                    file.write("\n")

    # CHANGE HIGHLIGHT VALUE IN SAVE FILE
    def update_highlight(self, color):

        # FIND "HIGHLIGHT" IN TEXT FILE - OVERWRITE NEW COLOR
        new_file = []
        for line in self.txt_file:
            index = line.find("HIGHLIGHT:")
            if index != -1:
                new_file.append("HIGHLIGHT:" + color)
            else:
                new_file.append(line)

        # SAVE NEW TEXT LINES TO FILE
        self.txt_file = new_file
        self.list_to_file(self.txt_file)

    # ACQUIRE HIGHLIGHT PREFERENCES
    def get_highlight(self):

        # FIND "HIGHLIGHT" LINE - RETURN END OF LINE
        for line in self.txt_file:
            index = line.find("HIGHLIGHT:")
            if index != -1:
                return line[10:]

    # CHANGE ERROR RECOGNITION IN SAVE FILE
    def update_error_recog(self, toggle):

        # CONVERT TRUE / FALSE TO 1 / 0
        new_file = []
        show = 1 if toggle else 0

        # FIND "ERRORS ON" IN TEXT FILE - OVERWRITE PREFERENCE
        for line in self.txt_file:
            index = line.find("ERRORS ON:")
            if index != -1:
                new_file.append("ERRORS ON:" + str(show))
            else:
                new_file.append(line)

        # SAVE NEW TEXT LINES TO FILE
        self.txt_file = new_file
        self.list_to_file(self.txt_file)

    # CHANGE DIFFICULTY VALUE IN SAVE FILE
    def update_difficulty(self, difficulty):

        # FORCE CUSTOM DIFFICULTY TO "EASY"
        if difficulty == "CUSTOM":
            difficulty = "EASY"

        # FIND "DIFFICULTY" IN TEXT FILE - OVERWRITE NEW DIFFICULTY
        new_file = []
        for line in self.txt_file:
            index = line.find("DIFFICULTY:")
            if index != -1:
                new_file.append("DIFFICULTY:" + difficulty)
            else:
                new_file.append(line)

        # SAVE NEW TEXT LINES TO FILE
        self.txt_file = new_file
        self.list_to_file(self.txt_file)

    # ACQUIRE DIFFICULTY PREFERENCE
    def get_difficulty(self):

        # FIND "DIFFICULTY" LINE - RETURN END OF LINE
        for line in self.txt_file:
            index = line.find("DIFFICULTY:")
            if index != -1:
                return line[11:]

    # ACQUIRE ERROR-RECOGNITION PREFERENCE
    def get_error_recog(self):

        # FIND "ERRORS ON" LINE - RETURN END OF LINE
        for line in self.txt_file:
            index = line.find("ERRORS ON:")
            if index != -1:
                ans = line[10:]
                break
        if ans == "1":
            return True
        return False

    # EVALUATE LAST GAME FOR NEW HIGH SCORE
    def check_record(self, diff, time):

        # DISALLOW RECORD SAVING IF PLAYING CUSTOM GAME
        if diff == "CUSTOM":
            return False

        # SET MAXIMUM RANKINGS - DEFAULT NO RECORD
        max_rankings = 10
        new_record = False

        # LIST OF TOP RANKINGS AND NAMES
        st_index = self.txt_file.index("RECORDS: " + diff) + 1
        for i, line in enumerate(self.txt_file[st_index:], start=st_index):
            if line.find("RECORDS: ") != -1:
                end_index = i
                break

        # SET UP ARRAYS OF INTEREST
        section_rankings = self.txt_file[st_index:end_index]
        section_times = section_rankings[:len(section_rankings) // 2]
        section_names = section_rankings[len(section_rankings) // 2:]

        # STARTING FROM BLANK
        if len(section_times) == 0:
            self.records_format = [SaveSettings.format_time(time)]
            self.records_raw = [str(time)]
            self.records_names = ["*YOUR NAME*"]
            self.pending_file = self.txt_file[:st_index] + self.records_raw + \
                                self.records_names + self.txt_file[end_index:]

            # NEW HIGH SCORE
            return True

        # INSERT PLAYER NAME IF APPROVED
        for i, entry in enumerate(section_times):
            if time < int(entry):
                new_record = True
                section_times.insert(i, str(time))
                section_names.insert(i, "*YOUR NAME*")
                break

        # APPEND PLAYER NAME TO END OF LIST
        else:
            if len(section_times) < max_rankings:
                new_record = True
                section_times.append(str(time))
                section_names.append("*YOUR NAME*")

        # TRIM RECORD LIST IF NEED BE
        if len(section_times) > max_rankings:
            section_times = section_times[:max_rankings]
            section_names = section_names[:max_rankings]

        # CREATE FORMATTED RECORD LIST
        section_formatted = []
        for entry in section_times:
            section_formatted.append(SaveSettings.format_time(int(entry)))

        self.records_format = section_formatted
        self.records_raw = section_times
        self.records_names = section_names

        # SAVE NEW FILE PENDING CONFIRMATION
        self.pending_file = self.txt_file[:st_index] + section_times + \
                            section_names + self.txt_file[end_index:]

        # RETURN IF NEW RECORD BOOLEAN
        return new_record

    # CONFIRM HIGH SCORE WITH PLAYER-SUBMITTED NAME
    def update_record(self, my_name, diff):

        # UPDATE WITH PLAYER NAME
        for i, line in enumerate(self.pending_file):
            if line.find("*YOUR NAME*") != -1:
                self.pending_file[i] = my_name

        # CONFIRM SAVE PENDING FILE
        self.txt_file = []
        for line in self.pending_file:
            self.txt_file.append(line)

        # WRITE FILE LINES TO TEXT FILE
        SaveSettings.list_to_file(self.txt_file)

    # FORMAT TOTAL SECONDS AS "MM:SS"
    @staticmethod
    def format_time(seconds):

        # CALCULATE MINUTES AND REMAINING SECONDS
        seconds = int(seconds)
        sec = seconds % 60
        min = (seconds - sec) // 60

        # ADD ZEROS UNTIL TWO-DIGIT MINUTE
        str_min = str(min)
        if min == 0:
            str_min = "00"
        elif min < 10:
            str_min = "0" + str_min

        # ADD ZEROS UNTIL TWO-DIGIT SECONDS
        str_sec = str(sec)
        if sec == 0:
            str_sec = "00"
        elif sec < 10:
            str_sec = "0" + str_sec

        return f"{str_min}:{str_sec}"
