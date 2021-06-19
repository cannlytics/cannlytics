#gui.py

from flaskwebgui import FlaskUI
from console.core.wsgi import application

ui = FlaskUI(application, start_server='django')
ui.run()
