import tkinter as tk
import pygame
from PIL import Image, ImageTk
import numpy as np

from Astar import Node, Point, AStar


class MainWindow:
    _width = 750
    _height = 750
    _map = []
    _icons = []
    _game_size = 10
    _margin = 25
    _icon_repeat_times = 4
    _icon_count = _game_size ** 2 // _icon_repeat_times
    _icon_width = 70
    _icon_height = 70
    _bg_music_file = './audio/bg_music.ogg'
    _click_music_1 = './audio/click1.ogg'
    _click_music_2 = './audio/click2.ogg'
    _link_music = './audio/link.ogg'
    _bg_img_file = './images/bg.png'
    _icons_file = './images/fruits.png'

    _is_game_start = False
    _is_first_time_clicked = True

    NONE_LINK = 0
    LINK_LINK = 1

    EMPTY = -1

    def __init__(self):

        # Create main window
        self.window = tk.Tk()
        self.window.title('Link Game')
        self.window.minsize(self._width, self._height)
        self._window_center(self._width, self._height)

        # Create components
        self._add_components()

        # Background music
        pygame.mixer.init()
        self._play_music(self._bg_music_file)

        # Background
        self.bg_img = False
        self._draw_background()

        # Prepare icons
        self._extract_small_icon_list(self._icons_file)

        # Message loop
        self.window.mainloop()

    def _window_center(self, width, height):
        pos_x = (self.window.winfo_screenwidth() - width) // 2
        pos_y = (self.window.winfo_screenheight() - height) // 2
        size = '%dx%d+%d+%d' % (width, height, pos_x, pos_y)
        self.window.geometry(size)

    def _add_components(self):
        # Menubar
        self.menubar = tk.Menu(self.window, bg='lightgrey', fg='black')
        self.file_menu = tk.Menu(self.menubar, bg='lightgrey', fg='black')
        self.file_menu.add_command(
            label='New', command=self._file_menu_clicked, accelerator='Ctrl+N')
        self.menubar.add_cascade(label='Game', menu=self.file_menu)
        self.window.configure(menu=self.menubar)

        # Canvas
        self.canvas = tk.Canvas(self.window, bg='white',
                                width=self._width, height=self._height)
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self._canvas_clicked)

        frame = tk.Frame(self.window)
        frame.pack(side=tk.TOP)

    def _file_menu_clicked(self):
        self._stop_music()

        # clear the formmer map
        self.canvas.delete('outline_selected_area')
        self._is_first_time_clicked = True
        for row in range(self._game_size):
            for column in range(self._game_size):
                self.canvas.delete(f'image_{row}_{column}')

        # create new map
        self._init_map()
        self._draw_map()

    def _canvas_clicked(self, event):
        if self._is_game_start:
            point = self._get_game_point(event.x, event.y)
            if not self._is_clicked_on_margin(point):
                if self._is_first_time_clicked:
                    self._play_music(self._click_music_1)
                    self._is_first_time_clicked = False
                    self._draw_outline_selected_area(point)
                    self.formmer_point = point
                else:
                    self._play_music(self._click_music_2)
                    if point.is_equal(self.formmer_point):
                        self.canvas.delete('outline_selected_area')
                        self._is_first_time_clicked = True
                    else:
                        type = self._get_link_type(self.formmer_point, point)
                        if type['type'] == self.LINK_LINK:
                            self._clear_linked_blocks(
                                self.formmer_point, point)
                            self.canvas.delete('outline_selected_area')
                            self._is_first_time_clicked = True

    def _is_clicked_on_margin(self, point):
        if point.row < 0 or point.row > self._icon_count - 1 or point.column < 0 or point.column > self._icon_count - 1:
            return True
        if not self._map[point.row][point.column]:
            return True
        return False

    def _play_music(self, music_file, volume=0.5):
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()

    def _stop_music(self):
        pygame.mixer.music.stop()

    def _draw_background(self):
        self.bg_img = ImageTk.PhotoImage(file=self._bg_img_file)
        self.canvas.create_image((0, 0), anchor='nw', image=self.bg_img)

    def _init_map(self):
        records = []
        for i in range(self._icon_count):
            for _ in range(self._icon_repeat_times):
                records.append(i)
        self._map = np.array(records)
        np.random.shuffle(self._map)
        self._map = self._map.reshape(self._game_size, -1)

    def _draw_map(self):
        for row in range(self._game_size):
            for column in range(self._game_size):
                x, y = self._get_origin_coordinate(row, column)
                self.canvas.create_image(
                    (x, y), image=self._icons[self._map[row][column]], anchor='nw', tags=f'image_{row}_{column}')
        self._is_game_start = True

    def _draw_outline_selected_area(self, point):
        x_1, y_1 = self._get_origin_coordinate(point.row, point.column)
        x_2, y_2 = x_1 + self._icon_width, y_1 + self._icon_height
        self.canvas.create_rectangle(
            x_1, y_1, x_2, y_2, outline='red', tags='outline_selected_area')

    def _get_x(self, column):
        return self._margin + column * self._icon_width

    def _get_y(self, row):
        return self._margin + row * self._icon_height

    def _get_origin_coordinate(self, column, row):
        return self._get_x(column), self._get_y(row)

    def _get_game_point(self, x, y):
        point_row = -1
        point_column = -1
        if x - self._margin >= 0:
            point_row = (x - self._margin) // self._icon_width

        if y - self._margin >= 0:
            point_column = (y - self._margin) // self._icon_height

        return Point(point_row, point_column)

    def _get_link_type(self, point_1, point_2):
        if self._map[point_1.row][point_1.column] != self._map[point_2.row][point_2.column]:
            return {'type': self.NONE_LINK}
        start_node = Node(point_1, point_2)
        end_node = Node(point_2, point_2)
        path = AStar(self._map, start_node, end_node, self.EMPTY).start()
        if path:
            return {'type': self.LINK_LINK}
        else:
            return {'type': self.NONE_LINK}

    def _is_empty(self, point):
        return self._map[point.row][point.column] == self.EMPTY

    def _clear_linked_blocks(self, point_1, point_2):
        self.canvas.delete(f'image_{point_1.row}_{point_1.column}')
        self.canvas.delete(f'image_{point_2.row}_{point_2.column}')
        self._map[point_1.row][point_1.column] = self.EMPTY
        self._map[point_2.row][point_2.column] = self.EMPTY
        self._play_music(self._link_music)

    def _extract_small_icon_list(self, img_file):
        icons = Image.open(img_file)
        for i in range(self._icon_count):
            region = icons.crop((i * self._icon_width, 0, (i+1) *
                                 self._icon_width, self._icon_height))
            self._icons.append(ImageTk.PhotoImage(region))


if __name__ == "__main__":
    MainWindow()
