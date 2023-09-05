# Adapted from https://github.com/liyanage/python-modules/blob/master/running_stats.py
import numpy as np


class RunningStatsArray:
    def __init__(self, width: int, n: int = 0):
        self.width = width
        self.n = 0
        self.old_m = np.zeros(width)
        self.new_m = np.zeros(width)
        self.old_s = np.zeros(width)
        self.new_s = np.zeros(width)

    def clear(self) -> None:
        self.n = 0

    def push(self, x: np.array) -> 'RunningStatsArray':
        self.n += 1
        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = np.zeros(self.width)
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s
        if np.any(np.isnan(self.new_m)):
            import pdb; pdb.set_trace()
        return self

    def mean(self) -> np.array:
        return self.new_m if self.n else np.zeros(self.width)

    def variance(self) -> np.array:
        return self.new_s / (self.n - 1) if self.n > 1 else np.zeros(self.width)

    def standard_deviation(self) -> np.array:
        return np.sqrt(self.variance())


    def pooled_variance(self, other: 'RunningStatsArray') -> np.array:
        return (self.variance() * self.n + other.variance() * other.n) / (self.n + other.n)