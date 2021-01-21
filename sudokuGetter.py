from bs4 import BeautifulSoup
import requests


# MANAGES ACQUIRING SUDOKU DATA FROM ONLINE
class Refresher:

    # CREATE OBJECT TO ACQUIRE DATA
    def __init__(self):

        # INITIALIZE SUDOKU LIST
        large_list = []

        # FOUR DIFFICULTIES 1, 2, 3, 4
        for i in range(4):

            # GRAB 50 RANDOM SUDOKU PER DIFFICULTY
            for j in range(50):

                # APPEND NEW SUDOKU TO SAVED SUDOKU LIST
                large_list.append(Refresher.get_sudoku(i + 1))

        Refresher.save_list_txt("Sudoku File", large_list)

    # ACQUIRE NEW RANDOM SUDOKU
    @staticmethod
    def get_sudoku(level):

        # ACQUIRE DATA FROM WEBSITE
        web_url = f"https://nine.websudoku.com/?level={level}"
        source = requests.get(web_url).text
        soup = BeautifulSoup(source, 'lxml')

        # CREATE ID LOOK-UP VALUES
        ids = []
        for i in range(9):
            for j in range(9):
                ids.append("f"+str(j)+str(i))

        # APPEND SUDOKU LINE NUMS AND BLANKS
        sudoku_line = ""
        for id_name in ids:
            num = soup.find('input', id=id_name)
            try:
                sudoku_line += num['value']
            except:
                sudoku_line += "."
        sudoku_line += ","

        return sudoku_line

    # SAVE SUDOKU LIST TO FILE
    @staticmethod
    def save_list_txt(name_only, my_list):

        # WRITE TO FILE - LINE BY LINE
        with open(name_only + ".txt", "w") as file:
            for i, element in enumerate(my_list):
                file.write(element)
                if i < len(my_list) - 1:
                    file.write("\n")
