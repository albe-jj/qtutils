# -*- coding: utf-8 -*-
# @Author: TUD278249
# @Date:   2021-06-08 12:56:29
# @Last Modified by:   TUD278249
# @Last Modified time: 2021-06-08 13:25:14

import time

def autorange_lia(srs, max_changes=5, min_sens=0.0005, max_sens=0.5):
    def autorange_once():
        r = srs.R.get()
        sens = srs.sensitivity.get()
        if (r > 0.9 * sens) & (sens<max_sens):
            return srs.increment_sensitivity()
        elif (r < 0.1 * sens) & (sens>min_sens):
            return srs.decrement_sensitivity()
        return False
    sets = 0
    while autorange_once() and sets < max_changes:
        sets += 1
        time.sleep(srs.time_constant.get())