import pkgutil
import importlib
import logging
from libs.driver_interface import DriverInterface


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

    return dict(zip(driver_list, DriverInterface.__subclasses__()))


def test_driver():
    driver_list = load_drivers()
    print(driver_list)
    model = 'moduleB'
    visa_address = 'GPIB::1'
    if model in driver_list:
        test_instrument = driver_list[model](visa_address)
        test_instrument.performOpen()
        test_instrument.performGetValue()


if __name__ == '__main__':
    a, b = load_drivers()
    print(a)
    print(b)
