#!/usr/bin/env python3

import random
import abc


class GetOutOfLoop(Exception):
    pass


class Map:
    __metaclass__ = abc.ABCMeta

    width = 0
    height = 0
    matrix = None

    def __init__(self, width=64, height=64):
        self.width = width
        self.height = height

    @abc.abstractmethod
    def generate(self, **kwargs):
        """Generate 2d list with booleans"""
        pass

    @abc.abstractmethod
    def get_model(self):
        """Make 3d vertexes for this map"""
        pass


class Cave(Map):
    def generate(self, birth_limit=4, death_limit=3, initial_chance=0.4, steps=3):
        self.matrix = [[random.random() < initial_chance for x in range(self.width)] for y in range(self.height)]

        for _ in range(steps):
            step_map = [[False for x in range(self.width)] for y in range(self.height)]

            for y, row in enumerate(self.matrix):
                for x, cell in enumerate(row):
                    count = self.count_alive_neighbours(x, y)

                    if self.matrix[y][x]:
                        if count < death_limit:
                            step_map[y][x] = False
                        else:
                            step_map[y][x] = True
                    else:
                        if count > birth_limit:
                            step_map[y][x] = True
                        else:
                            step_map[y][x] = False

            self.matrix = step_map

        return self.matrix

    def count_alive_neighbours(self, x, y):
        count = 0

        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbour_x = x + i
                neighbour_y = y + j

                if i == 0 and j == 0:
                    pass  # self
                elif neighbour_x < 0 or neighbour_y < 0 \
                        or neighbour_x == len(self.matrix[0]) or neighbour_y == len(self.matrix):
                    count = count + 1  # out of border
                elif self.matrix[neighbour_y][neighbour_x]:
                    count = count + 1  # alive in matrix

        return count

    def get_model(self):
        pass


class Room(Map):
    def generate(self, **kwargs):
        pass

    def get_model(self):
        pass


class Arena(Map):
    def generate(self, **kwargs):
        pass

    def get_model(self):
        pass


def render_map(matrix):
    for row in matrix:
        for cell in row:
            if cell:
                print(int(cell), end='')
            else:
                print(' ', end='')
        print('')


if __name__ == '__main__':
    map_matrix = Cave(16, 16).generate()
    render_map(map_matrix)
