from config import config
from src import init_app

configuration = config['development']
app = init_app(configuration)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5050)