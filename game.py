from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
import random
import time

""" 
    I created this app with kivy, and it could be
    deployed to android or our tablets with "buildozer",
    but i read that i need to have linux installed,
    so i can only test it on my pc
"""

"""
    I will create 3 screens
    In the first one the user willbe able to insert the nr
    of rown, colums (height and width) and the nr of bombs
    The second screen will be the game screen
    The third one will be the screen where the score will be 
    displayed at the end
"""

class Mine_Sweeper(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.intro_screen = Screen_Intro(name='screen_intro')
        self.game_screen = Screen_Game(name='screen_game')
        self.score_screen = Screen_Score(name='screen_score')

        self.add_widget(self.intro_screen)
        self.add_widget(self.game_screen)
        self.add_widget(self.score_screen)


class Screen_Intro(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.screen = BoxLayout(padding=100, orientation='vertical', spacing=25)

        self.start_button = Button(text="Start", background_color=(1,1,255,1))
        self.start_button.bind(on_press=self.begin_game)

        # create labels
        self.height_text = Label(text="Height")
        self.width_text = Label(text="Width")
        self.bombs_text = Label(text="Number of Bombs")

        # create text inputs for size and nr of bombs
        self.height_input = TextInput(text='', multiline=False)
        self.width_input = TextInput(text='', multiline=False)
        self.bomb_input = TextInput(text='', multiline=False)

        # add labels and input fields to screen
        self.screen.add_widget(self.width_text)
        self.screen.add_widget(self.width_input)
        self.screen.add_widget(self.height_text)
        self.screen.add_widget(self.height_input)
        self.screen.add_widget(self.bombs_text)
        self.screen.add_widget(self.bomb_input)
        self.screen.add_widget(self.start_button)
        self.add_widget(self.screen)

    def begin_game(self, _):
        # get values from inputs fields
        height = self.height_input.text
        width = self.width_input.text
        bomb_nr = self.bomb_input.text

        """
            we should check if the user had entered
            valid values for height, width and bombs nr
            The game should have at least 1 bomb

            If the values are not correct we return
            to the same screen

            check if values are numeric
            check if values are bigger than 1
            and check if the nr of bombs if 
            smaller that the nr of cells

            I alse check if the nr of rows did not exceed 20 because
            the number in the cells will be unreadeble
        """
        if (not height.isnumeric() or not width.isnumeric() or not bomb_nr.isnumeric() \
            or int(height) < 1 or int(width) < 1 or int(bomb_nr) < 1 or int(bomb_nr)  > int(width) * int(height) \
            or int(height) > 20 or int(width) > 20):
            screen_intro_name = 'screen_intro'
            # set input fields empty
            self.clean_inputs()
            self.manager.current = screen_intro_name
            return

        # get values from txt to int
        height = int(height)
        width = int(width)
        bomb_nr = int(bomb_nr)

        """
            After we check the values and make sure that 
            they are ok we can now select the next screen
            and pass the nr of cols, rows and bomb nr
        """
        game_screen_name = 'screen_game'
        game_screen = self.manager.get_screen(game_screen_name)
        game_screen.init(height, width, bomb_nr)
        self.manager.current = game_screen_name

    def clean_inputs(self):
        self.height_input._refresh_text("")
        self.width_input._refresh_text("")
        self.bomb_input._refresh_text("")


class Screen_Game(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.init_all()

    def init_all(self):
        self.screen = None
        self.list_cells = None
        self.rows = None
        self.cols = None
        self.remaining_cells_nr = None
        self.bomb_nr = None
        self.game_started = False
        self.start_time = None

    def init(self, height, width, bomb_nr):
        # set cols, rown and nr of cells
        self.init_all()
        self.rows = height
        self.cols = width
        self.remaining_cells_nr = self.cols * self.rows

        # create screen
        self.screen = GridLayout(cols=self.cols, rows=self.rows)

        # generate the random bombs
        self.bomb_nr = bomb_nr
        """
            We will create a list containg all cells nr
            after that we shuffle the list
            and place bombs in the first 'n' cells
        """
        bombs = list(range(self.cols * self.rows))
        random.shuffle(bombs)
        bombs = bombs[:self.bomb_nr]

        # create a list containg all cells
        temp_list = []
        for i in range(self.cols * self.rows):
            temp_list.append(Cell(self,i))
        self.list_cells = temp_list

        """
            We will set all bombs on their associated cells
            and for each neighbour we will increment the number 
            (number of bombs nearby)
        """
        for bomb_index in bombs:
            # set cell as a bomb
            self.list_cells[bomb_index].set_bomb()

            # increment neighbour numbers
            left, right, top, bottom = bomb_index-1, bomb_index+1, bomb_index-self.cols, bomb_index+self.cols
            if top >= 0:
                self.list_cells[top].number += 1
            if bottom <= len(self.list_cells) - 1:
                self.list_cells[bottom].number += 1
            if left >= 0 and left % self.cols != self.cols - 1:
                self.list_cells[left].number += 1
            if right <= len(self.list_cells) - 1 and right % self.cols != 0:
                self.list_cells[right].number += 1

        # add cells to screen
        for cell in self.list_cells:
            self.screen.add_widget(cell)
        self.add_widget(self.screen)

    # this function will be called when the user press on a cell
    def on_press_callback(self, index):
        score_screen_name = 'screen_score'

        """
            start timer
            if this is the first press
            we set game_start flag to true
            and we start the timer
        """
        if not self.game_started:
            self.start_time = time.time()
            self.game_started = True

        # check if the pressed cell is a bomb or not
        if self.list_cells[index].is_bomb():
            # Lost
            # if the user had press a bomb we change to score screen
            # and initialise the lost_screen 
            game_screen = self.manager.get_screen(score_screen_name)
            game_screen.init_lost_screen(int(time.time() - self.start_time))
            self.manager.current = score_screen_name
        else:
            # if the cell was not a bomb we will expand the rest of the neighbour cells
            self.expand(self.list_cells[index], root=True)
            # check if the nr of remaining cells is equal to the nr of remaining bombs
            # if so... it means that the user had finished
            if self.remaining_cells_nr == self.bomb_nr:
                # Win
                game_screen = self.manager.get_screen(score_screen_name)
                game_screen.init_win_screen(int(time.time() - self.start_time))
                self.manager.current = score_screen_name

    """
        We will expand as many cells as we can

        First we check of the cell was already visited, than we do nothig
        than if our cell is not the root cell (the one that we've click)
        or is a cell that has a bomb as a neoghbour we just expand that
        Otherwise we expand the current cell and try to expand the neighbours
    """
    def expand(self, cell, root=False):
        if cell.is_visited():
            return
        elif cell.is_neighbour() and not root:
            cell.show_number()
            cell.set_visited()
            self.remaining_cells_nr -= 1
            return
        else:
            cell.show_number()
            cell.set_visited()
            self.remaining_cells_nr -= 1
            index = cell.get_cell_index()
            left, right, top, bottom = index-1, index+1, index-self.cols, index+self.cols
            if top >= 0 and not self.list_cells[top].is_bomb():
                self.expand(self.list_cells[top])
            if bottom <= len(self.list_cells) - 1 and not self.list_cells[bottom].is_bomb():
                self.expand(self.list_cells[bottom])
            if left >= 0 and left % self.cols != self.cols - 1 and not self.list_cells[left].is_bomb():
                self.expand(self.list_cells[left])
            if right <= len(self.list_cells) - 1 and right % self.cols != 0 and not self.list_cells[right].is_bomb():
                self.expand(self.list_cells[right])

"""
    This class will hold information abour each cell
        If it is bomb, if it si visited, the nr of bombs that are nearby
"""
class Cell(Button):
    def __init__(self, game, index, is_bomb_flag=False, number=0, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.cell_index = index
        self.is_bomb_flag = is_bomb_flag
        self.number = number
        self.text = ''
        self.background_color=(1,1,255,1)
        self.visited = False

    def set_bomb(self):
        self.is_bomb_flag = True

    def is_bomb(self):
        return self.is_bomb_flag

    def on_press(self):
        self.game.on_press_callback(self.cell_index)

    def get_cell_index(self):
        return self.cell_index

    def get_nr(self):
        return self.number

    def show_number(self):
        # show nr of neighbour bombs 
        # if the cell has 0 bombs nearby don't show any number
        if(self.number == 0):
            self.text = ''
        else:
            self.text = str(self.number)

        self.disabled = True

    def is_visited(self):
        return self.visited

    def set_visited(self):
        self.visited = True

    def is_neighbour(self):
        if(self.number > 0):
            return True
        else:
            return False


class Screen_Score(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.exit_button = Button(text="Exit", background_color=(1,1,255,1))
        self.exit_button.bind(on_press=self.exit_game)

    # create lost screen and add score and text
    def init_lost_screen(self, score):
        screen = BoxLayout(spacing=10, padding=200, orientation='vertical')
        screen.add_widget(Label(text=":( Sad, but you lost"))
        screen.add_widget(Label(text="It took " + str(score) + " sec"))
        screen.add_widget(self.exit_button)
        self.add_widget(screen)

    # create win screen and add score and text
    def init_win_screen(self, score):
        screen = BoxLayout(spacing=10, padding=200, orientation='vertical')
        screen.add_widget(Label(text="You Won"))
        screen.add_widget(Label(text="It took " + str(score) + " sec"))
        screen.add_widget(self.exit_button)
        self.add_widget(screen)

    def exit_game(self, action):
        exit()

class Mine_Sweeper_Game(App):
    def build(self):
        return Mine_Sweeper()

if __name__ == '__main__':
    Mine_Sweeper_Game().run()