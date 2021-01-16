class SaveSettings:

    def __init__(self):
        self.records_format = []
        self.records_raw = []
        self.records_names = []

        with open("Sudoku Settings.txt", "r") as file:
            self.txt_file = file.read().split("\n")

    def reset_settings(self):
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

        SaveSettings.list_to_file(blank_file)

    def get_all_records(self):
        index_0 = self.txt_file.index('RECORDS: EASY')
        index_1 = self.txt_file.index('RECORDS: MEDIUM')
        index_2 = self.txt_file.index('RECORDS: HARD')
        index_3 = self.txt_file.index('RECORDS: EXPERT')
        index_4 = self.txt_file.index('RECORDS: END OF LIST')

        easy_count =    (index_1 - index_0 - 1) // 2
        medium_count =  (index_2 - index_1 - 1) // 2
        hard_count =    (index_3 - index_2 - 1) // 2
        expert_count =  (index_4 - index_3 - 1) // 2

        results = [[], [], [], []]
        for i in range(easy_count):
            results[0].append(f"  {i + 1}. {self.txt_file[index_0 + 1 + easy_count + i]} - {SaveSettings.format_time(self.txt_file[index_0 + 1 + i])}")
        for i in range(medium_count):
            results[1].append(f"  {i + 1}. {self.txt_file[index_1 + 1 + medium_count + i]} - {SaveSettings.format_time(self.txt_file[index_1 + 1 + i])}")
        for i in range(hard_count):
            results[2].append(f"  {i + 1}. {self.txt_file[index_2 + 1 + hard_count + i]} - {SaveSettings.format_time(self.txt_file[index_2 + 1 + i])}")
        for i in range(expert_count):
            results[3].append(f"  {i + 1}. {self.txt_file[index_3 + 1 + expert_count + i]} - {SaveSettings.format_time(self.txt_file[index_3 + 1 + i])}")

        #add blank rows
        for diff in results:
            if len(diff) < 10:
                for i in range(10 - len(diff)):
                    diff.append("")

        return results

    @staticmethod
    def list_to_file(lines):
        with open("Sudoku Settings.txt", "w") as file:
            for i, element in enumerate(lines):
                file.write(element)
                if i < len(lines) - 1:
                    file.write("\n")

    def update_highlight(self, color):
        new_file = []
        for line in self.txt_file:
            index = line.find("HIGHLIGHT:")
            if index != -1:
                new_file.append("HIGHLIGHT:" + color)
            else:
                new_file.append(line)

        self.txt_file = new_file
        self.list_to_file(self.txt_file)

    def get_highlight(self):
        for line in self.txt_file:
            index = line.find("HIGHLIGHT:")
            if index != -1:
                return line[10:]

    def update_error_recog(self, toggle):
        new_file = []
        show = 1 if toggle else 0

        for line in self.txt_file:
            index = line.find("ERRORS ON:")
            if index != -1:
                new_file.append("ERRORS ON:" + str(show))
            else:
                new_file.append(line)

        self.txt_file = new_file
        self.list_to_file(self.txt_file)

    def update_difficulty(self, difficulty):
        if difficulty == "CUSTOM":
            difficulty = "EASY"
        new_file = []
        for line in self.txt_file:
            index = line.find("DIFFICULTY:")
            if index != -1:
                new_file.append("DIFFICULTY:" + difficulty)
            else:
                new_file.append(line)

        self.txt_file = new_file
        self.list_to_file(self.txt_file)

    def get_difficulty(self):
        for line in self.txt_file:
            index = line.find("DIFFICULTY:")
            if index != -1:
                return line[11:]

    def get_error_recog(self):
        for line in self.txt_file:
            index = line.find("ERRORS ON:")
            if index != -1:
                ans = line[10:]
                break
        if ans == "1":
            return True
        return False

    def check_record(self, diff, time):
        if diff == "CUSTOM":
            return False

        max_rankings = 10
        new_record = False

        #list of top rankings and names
        st_index = self.txt_file.index("RECORDS: " + diff) + 1
        for i, line in enumerate(self.txt_file[st_index:], start=st_index):
            if line.find("RECORDS: ") != -1:
                end_index = i
                break

        #set up arrays of interest
        section_rankings = self.txt_file[st_index:end_index]
        section_times = section_rankings[:len(section_rankings) // 2]
        section_names = section_rankings[len(section_rankings) // 2:]

        # starting from blank
        if len(section_times) == 0:
            self.records_format = [SaveSettings.format_time(time)]
            self.records_raw = [str(time)]
            self.records_names = ["*YOUR NAME*"]
            self.pending_file = self.txt_file[:st_index] + self.records_raw + self.records_names + self.txt_file[end_index:]
            return True

        #ADD IN MY NAME IF APPROVED
        for i, entry in enumerate(section_times):
            if time < int(entry):
                new_record = True
                section_times.insert(i, str(time))
                section_names.insert(i, "*YOUR NAME*")
                break
        else:
            if len(section_times) < max_rankings:
                new_record = True
                section_times.append(str(time))
                section_names.append("*YOUR NAME*")

        #trim down if need be
        if len(section_times) > max_rankings:
            section_times = section_times[:max_rankings]
            section_names = section_names[:max_rankings]

        section_formatted = []
        for entry in section_times:
            section_formatted.append(SaveSettings.format_time(int(entry)))

        self.records_format = section_formatted
        self.records_raw = section_times
        self.records_names = section_names

        self.pending_file = self.txt_file[:st_index] + section_times + section_names + self.txt_file[end_index:]

        return new_record

    def update_record(self, my_name, diff):
        #update with my name
        for i, line in enumerate(self.pending_file):
            if line.find("*YOUR NAME*") != -1:
                self.pending_file[i] = my_name

        #re-establish same
        self.txt_file = []
        for line in self.pending_file:
            self.txt_file.append(line)

        #print(self.txt_file)
        SaveSettings.list_to_file(self.txt_file)

    @staticmethod
    def format_time(seconds):
        seconds = int(seconds)
        sec = seconds % 60
        min = (seconds - sec) // 60

        str_min = str(min)
        if min == 0:
            str_min = "00"
        elif min < 10:
            str_min = "0" + str_min

        str_sec = str(sec)
        if sec == 0:
            str_sec = "00"
        elif sec < 10:
            str_sec = "0" + str_sec

        return f"{str_min}:{str_sec}"
