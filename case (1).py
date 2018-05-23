# Declarative part.
import local
import time
import tkinter as tk
from math import pi, cos, sin
from random import randint


class Train:
    CARRIAGE_LEN_M = 20

    def __init__(self, number, start_pos, clockwise, speed, carriages):
        self.number = int(number)
        self.prev_pos = float(start_pos)
        self.pos = float(start_pos)
        self.clockwise = bool(int(clockwise))
        self.speed = float(speed)
        if self.clockwise:
            self.pos += 0.0001
            self.prev_pos += 0.0001
        else:
            self.pos -= 0.0001
            self.prev_pos -= 0.0001
            self.speed = -self.speed

        self.pos %= 1
        self.carriages = int(carriages)

        self.stay_left = 0

    def step(self, sec):
        # Seconds in the model.
        if self.stay_left > 0:
            # стоим
            self.stay_left -= sec
            self.stay_left = max(0, self.stay_left)

        if self.stay_left <= 0:
            # If the time ran out -> the train goes farther.
            self.prev_pos = self.pos
            self.pos += self.speed * sec
            self.pos %= 1

    def check_station(self, station):
        # Checking, if the train on the station.

        if self.stay_left == 0:
            if self.clockwise:
                if self.prev_pos < self.pos:
                    if self.prev_pos <= station.pos <= self.pos:
                        self.stay_left = randint(2, 12) * 10
                else:
                    if (self.prev_pos - 1) <= station.pos <= self.pos:
                        self.stay_left = randint(2, 12) * 10
            else:
                if self.prev_pos > self.pos:
                    if self.prev_pos >= station.pos >= self.pos:
                        self.stay_left = randint(2, 12) * 10
                else:
                    if self.prev_pos >= station.pos >= (self.pos - 1):
                        self.stay_left = randint(2, 12) * 10

    def __str__(self):
        return "{}: {:.2f} {} {:.2f}".format(self.number, self.pos, "c" if self.clockwise else "a", self.stay_left)

    @staticmethod
    def load_from(lines, stations):
        trains = []
        for line in lines:
            args = line.split(" ")
            args[1] = stations[args[1]].pos
            trains.append(Train(*args))
        return trains


class Station:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos

    @staticmethod
    def create_stations(d):
        mid_v = 30  # Minutes for going around the ring.
        return {k: Station(k, v / 30) for k, v in d.items()}


class Model:
    def __init__(self, stations, metro):
        self.stations = stations
        self.trains = metro
        # Length in metres.
        self.len = 19400
        # How many usual seconds in a second of the model.
        self.time_coef = 30
        self.time = 0

        for train in self.trains:
            train.speed /= self.len

    def step(self, sec):
        # sec -- seconds in the real life.
        # And this in the model.
        sec_game = sec * self.time_coef
        for train in self.trains:
            for station in self.stations.values():
                train.check_station(station)
            train.step(sec_game)
        self.time += sec_game


class Window:
    def __init__(self, model):
        self.win = tk.Tk()
        self.win.title(local.mos_kol)
        self.metr_by_pixel = 10
        self.model = model
        self.adder = 100  # How many pixels on each side we should remain.
        self.R = self.model.len / self.metr_by_pixel / (2 * pi)  # Radius of the circle.
        self.center = self.adder + self.R  # Centre of the circle.

        self._init()

    def _get_coord(self, pos, R=None):
        R = R or self.R
        # pos from 0 to 1.
        pos *= 2 * pi
        pos -= pi / 2
        return R * cos(pos) + self.center, R * sin(pos) + self.center

    def _get_pos_by_meter(self, meter):
        return meter / self.model.len

    def _init(self):
        self.start_btn = tk.Button(text = local.start, command = self.game)
        self.start_btn.pack()

        self.stop_btn = tk.Button(text = local.stop, command = self.stop)
        self.stop_btn.pack()

        self.canvas = tk.Canvas(self.win,
                                width = int(2 * self.R) + 2 * self.adder,
                                height = int(2 * self.R) + 2 * self.adder)
        self.canvas.pack()

    def _circle(self):
        self.canvas.create_oval(self.adder, self.adder,
                                int(2 * self.R) + self.adder, int(2 * self.R) + self.adder)

    def draw_stantion(self, station):
        line_len = 10
        pos = station.pos
        self.canvas.create_line(*self._get_coord(pos, self.R - line_len),
                                *self._get_coord(pos, self.R + line_len)
                                )
        anchor = tk.W
        if pos > 0.5:
            anchor = tk.E

        self.canvas.create_text(
            *self._get_coord(pos, self.R + line_len),
            anchor = anchor,
            font = "Arial",
            text = station.name
        )

    def draw_train(self, train):
        carriage_R = 1
        pos = train.pos

        # Drawing necessary number of cars.
        for i in range(train.carriages):
            pos = train.pos - i * self._get_pos_by_meter(Train.CARRIAGE_LEN_M)
            c = self._get_coord(pos, self.R)
            c1 = c[0] - carriage_R, c[1] - carriage_R
            c2 = c[0] + carriage_R, c[1] + carriage_R
            self.canvas.create_oval(*c1, *c2)

        anchor = tk.W
        if pos > 0.5:
            anchor = tk.E

        self.canvas.create_text(
            *self._get_coord(train.pos, self.R - 20),
            anchor = anchor,
            font = "Arial",
            text = str(train.number)
        )

    def game(self):
        start = time.time()
        delay = 1000 / 25
        self.model.step(delay / 1000)
        self.draw()
        end = time.time()
        self.start_btn.after(int(delay - (end - start) * 1000), self.game)
        print((end - start) * 1000 // 1, " ms")

    def stop(self):
        self.win.destroy()

    def draw_time(self):
        tm = int(self.model.time)
        sec = tm % 60
        min = tm // 60 % 60
        hour = tm // 60 // 60
        self.canvas.create_text(0, 20, anchor = tk.W, font = "Arial",
                                text = "{}:{}:{}".format(hour, min, sec))

    def draw(self):
        self.canvas.delete("all")

        self._circle()

        for station in self.model.stations.values():
            self.draw_stantion(station)

        for train in self.model.trains:
            self.draw_train(train)

        self.draw_time()

    def run(self):
        self.draw()
        self.win.mainloop()