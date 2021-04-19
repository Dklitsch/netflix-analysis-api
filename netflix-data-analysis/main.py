import flask
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from flask_cors import CORS, cross_origin

# Create the application.
app = flask.Flask(__name__)
cors = CORS(app)


def flatten_list(list):
    return [item for sublist in list for item in sublist]


df = pd.read_csv('../data/netflix_titles.csv')
type_counts = df['type'].value_counts()
director_counts = df['director'].value_counts()
ccast = Series(flatten_list([x.split(', ') for x in df.cast.dropna()]))
ccast_counts = ccast.value_counts()
countries_counts = Series(flatten_list([x.split(', ') for x in df.country.dropna()])).value_counts()


@app.route('/')
@cross_origin()
def index():
    return df.to_json(orient='records', force_ascii=False)


@app.route('/type')
@cross_origin()
def title_type():
    return type_counts.to_json(force_ascii=False)


@app.route('/director/top5')
@cross_origin()
def director_top5():
    return director_counts[:5].to_json(orient='columns', force_ascii=False)


@app.route('/cast/top5')
@cross_origin()
def cast_top5():
    return ccast_counts[:5].to_json(orient='columns', force_ascii=False)


@app.route('/country/top10')
@cross_origin()
def country_top5():
    return countries_counts[:10].to_json(orient='columns', force_ascii=False)


@app.route('/releaseyear/top10')
@cross_origin()
def release_year_top5():
    return df['release_year'].value_counts()[:10].to_json(orient='columns', force_ascii=False)


@app.route('/releaseyear/bottom10')
@cross_origin()
def release_year_bottom5():
    return df['release_year'].value_counts()[-10:].to_json(orient='columns', force_ascii=False)


if __name__ == '__main__':
    app.run(port=80)
