#
# Created on Mar 7, 2017
#
# @author: dpascualhe
#
# Based on @nuriaoyaga code:
# https://github.com/RoboticsURJC-students/2016-tfg-nuria-oyaga/blob/
#     master/gui/threadgui.py
#

import time
import threading
from datetime import datetime



class ThreadGUI(threading.Thread):


    def __init__(self, gui):
        ''' Threading class for GUI. '''

        self.t_cycle = 50  # ms
        
        self.gui = gui
        threading.Thread.__init__(self)

    def run(self):
        ''' Updates the thread. '''
        while(True):
            start_time = datetime.now()
            self.gui.updGUI.emit()
            end_time = datetime.now()
            dt = end_time - start_time
            dtms = ((dt.days * 24 * 60 * 60 + dt.seconds) * 1000
                + dt.microseconds / 1000.0)

            if(dtms < self.t_cycle):
                time.sleep((self.t_cycle - dtms) / 1000.0)
