__author__ = 'jakob'

import time


"""
The purpose of this class is to give a quick and simple way to check
for how long time different parts of the program takes to execute_test.
It is based on real time passed, not processor time, so the time may
vary with runs, and how busy the computer is
"""


class Timer:

    DIGITS_DEFAULT = 4

    def __init__(self):
        self._base_time = time.time()

    def reset(self):
        self._base_time = time.time()

    def get_raw_time(self):
        return time.time() - self._base_time

    def get_formatted_time(self, significant_digits):
        build_string = "{0:." + str(significant_digits) + "f}"

        if significant_digits <= 0:
            raise Exception("At least one significant digit is needed!")
        elif significant_digits == 1:
            return str(int(self.get_raw_time()))
        else:
            return build_string.format(self.get_raw_time())

    def simple_print(self):
        print("[Timer] Passed time: " + self.get_formatted_time(self.DIGITS_DEFAULT))