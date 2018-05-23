"""Case-study#6 Basics of modeling
Developers:
Vishnevskaya A (100%), Yakuhina Y. (100%), Ganbat S. (100%)
"""

# Executable part.
from case import *
import local

if __name__ == "__main__":
    stations = {
        local.pros_mir: 0,
        local.coms: 3,
        local.curs: 6,
        local.tagan: 8,
        local.pavel: 11,
        local.dobr: 13,
        local.oktyab: 14,
        local.park_k: 17,
        local.kiev: 20,
        local.krasn: 22,
        local.belor: 25,
        local.novos: 27,
    }

    stations = Station.create_stations(stations)

    trains = Train.load_from(
        open("metro.txt", "rt").readlines(),
        stations)

    model = Model(stations, trains)

    win = Window(model)

    win.run()