"""
    http://www.drdobbs.com/testing/unit-testing-with-python/240165163
    http://www.onlamp.com/pub/a/python/2004/12/02/tdd_pyunit.html
"""

from modules.config import *
from modules.pool import *

import numpy as np
np.random.seed()


class System(object):
    """
        SYSTEM
        ------
    """

    def __init__(self):
        self.pool = Pool()


    def run(self):
        """
            Run
            ---
        """
        while True:
            # FITNESS
            self.pool.fitness()

            # SELECT
            self.pool.selection()

            # REPLICATE
            self.pool.replicate()



if __name__ == '__main__':
    driver = System()
    driver.run()
