#
# Created on Jan 26, 2018
#
# @author: naxvm
#

import time
import threading
from datetime import datetime

t_cycle = 150  # ms


class ThreadNetwork(threading.Thread):

    def __init__(self, network):
        ''' Threading class for Camera. '''
        self.network = network # 'is' for modifying the network (alias it on self.network)
        threading.Thread.__init__(self)


    def run(self):
        ''' Updates the thread. '''
        while(True):
            start_time = datetime.now()
            if self.network.activated:
                self.network.predict()
            end_time = datetime.now()

            dt = end_time - start_time
            dtms = ((dt.days * 24 * 60 * 60 + dt.seconds) * 1000 +
                    dt.microseconds / 1000.0)

            if(dtms < t_cycle):
                time.sleep((t_cycle - dtms) / 1000.0)

    def runOnce(self):
        '''Processes one image, and then stops again.'''
        if not self.network.activated:
            self.network.predict()

