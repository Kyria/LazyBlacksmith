from lazyblacksmith.app_factory import create_app
import config

app = create_app(config)
app.run(port=config.PORT, host=config.HOST)