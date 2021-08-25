# model load_driver
import pkgutil
import importlib
import logging
from libs.driver_interface import DriverInterface
import sys


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
