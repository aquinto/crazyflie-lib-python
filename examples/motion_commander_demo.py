# -*- coding: utf-8 -*b-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2017 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.

"""
This script shows the basic use of the MotionCommander class.

Simple example that connects to the crazyflie at `URI` and runs a
sequence. Real-time logging variables are available, and can be printed to
file. This script requires some kind of location system, it has been
tested with (and designed for) the flow deck.

Change the URI variable to your Crazyflie configuration.
"""

import logging
import time

import cflib.crtp
from cflib.positioning.motion_commander import MotionCommander


URI = 'radio://0/70/2M'

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    # The crazyflie automatically logs kalman.stateX, kalman.stateY,
    # kalman.stateZ, controller.yaw, and timestamp data, 
    # but we can add more as a set in the format {'groupname.varname'}

    log_vars = {'stabilizer.roll', 'stabilizer.pitch'}

    with MotionCommander(crazyflie=None,  # crazyflie is optional
                         link_uri=URI,
                         log_vars=log_vars) as mc:

        # We take off when the commander is created
        time.sleep(3)

        # There is a set of functions that move a specific distance
        # We can move in all directions
        mc.forward(0.8)
        mc.back(0.8)
        time.sleep(1)

        mc.up(0.5)
        mc.down(0.5)
        time.sleep(1)

        # We can also set the velocity
        mc.right(0.5, velocity=0.8)
        time.sleep(1)
        mc.left(0.5, velocity=0.4)
        time.sleep(1)

        # We can do circles or parts of circles
        mc.circle_right(0.5, velocity=0.5, angle_degrees=180)

        # Or turn
        mc.turn_left(90)
        time.sleep(1)

        # We can move along a line in 3D space
        mc.move_distance(-1, 0.0, 0.5, velocity=0.6)
        time.sleep(1)

        # There is also a set of functions that start a motion. The
        # Crazyflie will keep on going until it gets a new command.

        mc.start_left(velocity=0.5)
        # The motion is started and we can do other stuff, printing for
        # instance
        for _ in range(5):
            print('Doing other work')
            time.sleep(0.2)

        # And we can stop
        mc.stop()

        # We can access the latest kalman x, y, z, as well as yaw, and 
        # timestamp data
        print('I am at: ' + str((mc.x, mc.y, mc.z, mc.yaw, mc.timestamp)))

        # and access our own real-time logging variables using dict syntax
        print('My roll is: ' + str(mc['stabilizer.roll']))

        # We can use this data to determine how much the crazyflie drifts in
        # the x direction in a given second
        xmax, xmin = mc.x, mc.x
        timestart = mc.timestamp
        while mc.timestamp - timestart < 10**4:  # 1 second
            x = mc.x
            if x > xmax:
                max_drift = x
            elif x < xmin:
                min_drift = x
        print('The crazyflie drifted over: ')
        print(str(xmax - xmin) + ' meters in the x axis')

        # In fact, we can even access the entire dict of lists data structure
        # that contains all logging data
        print('My third to last y value is:')
        print(mc.data['kalman.stateY'][-3])

        print('My fifteenth roll value is:')
        print(mc.data['stabilizer.roll'][15])

        # We can print all of our logging data to a file
        # (though we might want to wait several seconds to allow the stream to
        # flush)
        time.sleep(2)
        mc.print_data_to_file('my_data.csv')

        # We land when the MotionCommander goes out of scope
