import sys
sys.path.append('src/')

from routes import app

if __name__ == "main":
    app.run()