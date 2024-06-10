import pickle
from flask import Flask

# --------------------------------------------------------------------------------------------------

app = Flask(__name__)

# --------------------------------------------------------------------------------------------------

@app.route('/')
def main():
    return 'OpenActive All Data Harvester'

# --------------------------------------------------------------------------------------------------

@app.route('/feeds')
def feeds():
    return pickle.load(open(f'../volume-1/data-feeds/feeds.pickle', 'rb'))

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))