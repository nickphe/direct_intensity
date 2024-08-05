
home_dir = '/Users/nickphelps/Desktop/2024 07 26/levers'
output_dir = '/Users/nickphelps/Desktop/2024 07 26/dioutput'
caps = [1,2,3,4,5,6]
concs = [87.9, 1, 66.2, 20.0, 57.9, 107.4]
#concs = [1, 1, 1, 1, 1, 1]
removed_capillaries = [2]

max_radius = 65
min_radius =  35


class Config:
    def __init__(self):
        self.home_dir = home_dir
        self.output_dir = output_dir
        self.caps = caps
        self.concs = concs
        self.removed_capillaries = removed_capillaries
        self.min_radius = min_radius
        self.max_radius = max_radius