import flask
import pandas as pd
import numpy as np
from pandas import DataFrame, Series

# Create the application.
APP = flask.Flask(__name__)


def flatten_list(list):
    return [item for sublist in list for item in sublist]


df = pd.read_csv('../data/netflix_titles.csv')
type_counts = df['type'].value_counts()
director_counts = df['director'].value_counts()
ccast = Series(flatten_list([x.split(', ') for x in df.cast.dropna()]))
ccast_counts = ccast.value_counts()


@app.route('/')
def index():
    return df.to_json(orient='records', force_ascii=False)


@app.route('/type')
def title_type():
    return type_counts.to_json(force_ascii=False)


@app.route('/director/top5')
def director_top5():
    return director_counts[:5].to_json(orient='columns', force_ascii=False)


@app.route('/cast/top5')
def cast_top5():
    return ccast_counts[:5].to_json(orient='columns', force_ascii=False)


if __name__ == '__main__':
    app.run(port=80)
