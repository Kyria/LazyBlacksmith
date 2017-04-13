# -*- encoding: utf-8 -*-
import config
import logging

from lazyblacksmith.app import create_app

app = create_app(config)

if __name__ == '__main__':
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

    app.run(port=config.PORT, host=config.HOST)
