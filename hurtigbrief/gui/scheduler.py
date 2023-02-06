# Compute scheduling intervals.
#
# Author: Malte J. Ziebarth (mjz.science@fmvkb.de)
#
# Copyright (C) 2023 Malte J. Ziebarth
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import List

class Scheduler:
    """
    Compute scheduling times.
    """
    compile_times: List[float]
    keystroke_times: List[float]
    ct_id: int
    kt_id: int

    def __init__(self):
        self.compile_times = [0.0] * 10
        self.ct_id = 0
        self.keystroke_times = [0.0] * 1000
        self.kt_id = 0

    def propose_delay(self) -> float:
        """
        This method proposes a delay to wait after a keystroke
        before starting the latex compilation.
        """
        # TODO use log-logistic distribution to describe
        # keystrokes, which has been found by Gonzales et al (2021)
        # to be the preferable distribution to describe keystroke
        # fly times.
        #
        # González, N., Calot, E. P., Ierache, J. S., Hasperué, W.: On the shape
        # of timings distributions in free-text keystroke dynamics profiles
        return sum(self.keystroke_times) / len(self.keystroke_times)

    def register_keystroke_waiting_time(self, T: float):
        """
        Register the waiting time between two keystrokes.
        """
        self.keystroke_times[self.kt_id] = T
        self.kt_id += 1

