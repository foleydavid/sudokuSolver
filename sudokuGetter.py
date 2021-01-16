from bs4 import BeautifulSoup
import requests

class Refresher:

    def __init__(self):
        large_list = []
        for i in range(4):
            for j in range(50):
                large_list.append(Refresher.get_sudoku(i + 1))

        Refresher.save_list_txt("Sudoku File", large_list)

    @staticmethod
    def get_sudoku(level):
        source = requests.get(f'https://nine.websudoku.com/?level={level}').text
        soup = BeautifulSoup(source, 'lxml')

        ids = []
        for i in range(9):
            for j in range(9):
                ids.append("f"+str(j)+str(i))

        sudoku_line = ""
        for id_name in ids:
            num = soup.find('input', id=id_name)
            try:
                sudoku_line += num['value']
            except:
                sudoku_line += "."
        sudoku_line += ","

        return sudoku_line

    @staticmethod
    def save_list_txt(name_only, my_list):
        with open(name_only + ".txt", "w") as file:
            for i, element in enumerate(my_list):
                file.write(element)
                if i < len(my_list) - 1:
                    file.write("\n")
