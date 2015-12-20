# -*- encoding: utf-8 -*-
from lazyblacksmith.app import create_app
import config

app = create_app(config)

if __name__ == '__main__':
	app.run(port=config.PORT, host=config.HOST)