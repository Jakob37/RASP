"""
RASP: Rapid Amplicon Sequence Pipeline

Copyright (C) 2016, Jakob Willforss and Björn Canbäck
All rights reserved.

This file is part of RASP.

RASP is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

RASP is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with RASP.  If not, <http://www.gnu.org/licenses/>.
"""

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