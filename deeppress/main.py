from trainer import TrainingApp
from bottle import install
from web import AuthPlugin
import config

install(AuthPlugin(config.LOCAL_AUTH_TOKEN))
app = TrainingApp()
app.register_routes()
app.run()