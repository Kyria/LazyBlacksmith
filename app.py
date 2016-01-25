# -*- encoding: utf-8 -*-
import config

from lazyblacksmith.app import create_app

app = create_app(config)

if __name__ == '__main__':
    app.run(port=config.PORT, host=config.HOST)
