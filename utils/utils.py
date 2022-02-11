# model load_driver
import pkgutil
import importlib
import logging
from utils import DriverInterface
import sys
import numpy as np


def load_drivers():
    """
    Import all classes under the folder 'drivers'.
    >>> load_drivers()
    """
    driver_list = []
    for _, name, _ in pkgutil.iter_modules(['drivers']):
        driver_list.append(name)
        try:
            importlib.import_module(f'drivers.{name}')
        except ImportError as e:
            logging.warning(e)

    if len(driver_list) != len(DriverInterface.__subclasses__()):
        logging.error('import drivers error')
        sys.exit()

    return dict(zip(driver_list, DriverInterface.__subclasses__()))

def addtwodimdict(thedict, key_a, key_b, val):
    """ Example:
        addtwodimdict(mapdict, 'Chengdu', 'Guangzhou', 1243)
        print(mapdict['Chengdu']['Guangzhou'])
    """
    if key_a in thedict:
        thedict[key_a].update({key_b: val})
    else:
        thedict.update({key_a:{key_b: val}})
        
# colors
color_group = [(230,159,0),
               (86,180,233),
               (0,158,115),
               (240,228,66),
               (0,114,178),
               (213,94,0),
               (204,121,167)]

# circulate the color
def colorLoop(n):
    num = np.mod(n,len(color_group))
    return color_group[num]

# check if is a number
def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False