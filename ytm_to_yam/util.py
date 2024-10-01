import logging
import time

import requests.exceptions


logger = logging.getLogger(__name__)


def retry(func):
    def wrapper(*args, **kwargs):
        sleep_time = 1
        while True:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.ReadTimeout as e:
                logger.error('Got ReadTimeout exception when invoking %s. Going to retry immediately',
                             func.__name__)
            except requests.exceptions.ConnectionError as e:
                logger.error('Got exception %s (%s) when invoking %s. Going to retry after %.2f seconds',
                             e.__class__.__name__, e, func.__name__, sleep_time)
                time.sleep(sleep_time)
                sleep_time *= 2

    return wrapper
