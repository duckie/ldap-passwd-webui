import bjoern
from app import application as app

bjoern.run(app, '0.0.0.0', 8080)
