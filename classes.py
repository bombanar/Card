import json

with open("config.json", "r") as f:
    config = json.load(f)

mp = config["screen_width"]/1920

card_width = mp * config["card_width"]
card_height = mp * config["card_height"]


class Card:
    def __init__(self, name, index, description, power, cost, counter = 0, scale = 1, status = "hand", dims = None):
        self.name = name
        self.index = index
        self.description = description
        self.power = power
        self.status = status
        self.dims = dims
        self.cost = cost
        self.scale = scale
        self.counter = counter

        if dims is None:
            self.dims = [500, 500]
        else:
            self.dims = dims

    def get_name(self):
        return self.name
    def get_index(self):
        return self.index
    def get_description(self):
        return self.description
    def get_power(self):
        return self.power
    def get_status(self):
        return self.status
    def get_dims(self):
        return self.dims[0] + card_width/2 - self.scale * card_width/2, self.dims[1] + card_height/2 - self.scale * card_height/2
    def get_scale(self):
        return self.scale
    def get_cost(self):
        return self.cost
    def get_counter(self):
        return self.counter

    def set_status(self, status):
        self.status = status
    def set_power(self, power):
        self.power = power
    def set_x(self, x):
        self.dims[0] = x
    def set_y(self, y):
        self.dims[1] = y
    def set_scale(self, scale):
        self.scale = scale
    def set_name(self, name):
        self.name = name
    def set_counter(self, counter):
        self.counter = counter

    def tick_counter(self):
        self.counter -= 1

    def get_width(self):
        return card_width * self.scale
    def get_height(self):
        return card_height * self.scale

    def display(self):
        out = self.name

        if self.scale != 1:
            out += "_big"
        return out