import os
import pickle
from flask import Flask

# --------------------------------------------------------------------------------------------------

app = Flask(__name__)

# --------------------------------------------------------------------------------------------------

@app.route('/')
def main():
    try:
        with open(f'../volume-1/data-analysis/analysis.pickle', 'rb') as file_in:
            analysis = pickle.load(file_in)
        return analysis
    except:
        return None

# --------------------------------------------------------------------------------------------------

@app.route('/feeds')
def feeds():
    try:
        with open(f'../volume-1/data-feeds/feeds.pickle', 'rb') as file_in:
            feeds = pickle.load(file_in)
        return feeds
    except:
        return None

# --------------------------------------------------------------------------------------------------

if (__name__ == '__main__'):
    app.run(
        debug = True,
        host = '0.0.0.0',
        port = int(os.environ.get('PORT', 8080)),
    )