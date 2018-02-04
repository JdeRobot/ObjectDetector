#
# Created on Jan 26, 2017
#
# @author: naxvm
#

import time
import threading
from datetime import datetime

t_cycle = 400  # ms


class ThreadNetwork(threading.Thread):

    def __init__(self, network):
        ''' Threading class for Camera. '''
        self.network = network # 'is' for modifying the network (alias it on self.network)
        threading.Thread.__init__(self)


        self.activated = True
    def run(self):
        ''' Updates the thread. '''
        while(True):
            start_time = datetime.now()
            if self.activated:
                self.network.predict()
            end_time = datetime.now()

            dt = end_time - start_time
            dtms = ((dt.days * 24 * 60 * 60 + dt.seconds) * 1000 +
                    dt.microseconds / 1000.0)

            if(dtms < t_cycle):
                time.sleep((t_cycle - dtms) / 1000.0)
