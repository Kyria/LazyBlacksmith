# -*- encoding: utf-8 -*-
""" Main app entry / wsgi entry point """
import logging
import sys

import config

from lazyblacksmith.app import create_app

APP = create_app(config)


def set_loggers():
    """ Define logger format and level for the whole app """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)

    logger = logging.getLogger('lb.utils')
    logger.addHandler(console)
    logger.setLevel(logging.DEBUG)

    logger = logging.getLogger('lb.ajax')
    logger.addHandler(console)
    logger.setLevel(logging.DEBUG)

    logger = logging.getLogger('sqlalchemy.engine')
    logger.addHandler(console)
    logger.setLevel(logging.ERROR)  # DEBUG for queries + results


if __name__ == '__main__':
    set_loggers()

    if config.DEBUG:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(APP)
        except ImportError:
            print("Library 'flask-debugtoolbar' is missing. Please install it using 'pip'")
            sys.exit()

    APP.run(port=config.PORT, host=config.HOST)
