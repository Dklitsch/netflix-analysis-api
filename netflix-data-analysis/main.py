import json

import flask
from flask import request
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from flask_cors import CORS, cross_origin
import sys
from flask import jsonify
import math

# Create the application.
app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cors = CORS(app)


def flatten_list(list):
    return [item for sublist in list for item in sublist]


df = pd.read_csv('../data/netflix_titles.csv')
type_counts = df['type'].value_counts()
director_counts = Series(flatten_list([x.split(', ') for x in df.director.dropna()])).value_counts()
ccast = Series(flatten_list([x.split(', ') for x in df.cast.dropna()]))
ccast_counts = ccast.value_counts()
countries_counts = Series(flatten_list([x.split(', ') for x in df.country.dropna()])).value_counts()
listed_in_counts = Series(flatten_list([x.split(', ') for x in df.listed_in.dropna()])).value_counts()

@app.route('/')
@cross_origin()
def index():
    if 'order' in request.form and request.form['order'] == 'desc' and 'take' in request.form:
        return df.sort_values(by="release_year").title[:request.form['take']].to_json(orient='records', force_ascii=False)
    else:
        return jsonify(df.to_dict(orient='records'))


@app.route('/searchterms')
@cross_origin()
def search_terms():
    director_names = Series(flatten_list([x.split(', ') for x in df.director.dropna()])).unique()
    return jsonify([{"term": x, "type": "director"} for x in director_names])


@app.route('/movie')
@cross_origin()
def movie():
    try:
        if request.args.get('order') and request.args.get('take'):
            take = int(request.args.get('take'))
            sort_ascending = request.args.get('order') != 'desc'
            result = df[df['type'] == 'Movie'].sort_values(by="release_year", ascending=sort_ascending)[:take]
            return result.to_json(orient='records', force_ascii=False)
        else:
            return df[df['type'] == 'Movie'].to_json(orient='records', force_ascii=False)
    except ValueError as e:
        return df[df['type'] == 'Movie'].to_json(orient='records', force_ascii=False)


@app.route('/tvshow')
@cross_origin()
def tv_show():
    try:
        if request.args.get('order') and request.args.get('take'):
            take = int(request.args.get('take'))
            sort_ascending = request.args.get('order') != 'desc'
            result = df[df['type'] == 'TV Show'].sort_values(by="release_year", ascending=sort_ascending)[:take]
            return result.to_json(orient='records', force_ascii=False)
        else:
            return df[df['type'] == 'TV Show'].to_json(orient='records', force_ascii=False)
    except ValueError as e:
        return df[df['type'] == 'TV Show'].to_json(orient='records', force_ascii=False)


@app.route('/type')
@cross_origin()
def title_type():
    return type_counts.to_json(force_ascii=False)


@app.route('/director/top5')
@cross_origin()
def director_top5():
    return director_counts[:5].to_json(orient='columns', force_ascii=False)


@app.route('/director/<name>')
@cross_origin()
def director(name):
    titles = df[df.director.str.contains(name, na=False, case=False) == True]
    collabs = Series(flatten_list([x.split(', ') for x in titles.director]))
    director_collabs = collabs[collabs.str.contains(name, na=False, case=False) == False].value_counts()
    cast_collabs = Series(flatten_list([x.split(', ') for x in titles.cast])).value_counts()
    result = {
        'titles': titles[['title', 'country', 'release_year']].sort_values(by="release_year").to_dict(orient='records'),
        'director collabs': director_collabs.sort_values(ascending=False).to_dict(),
        'cast collabs': cast_collabs[cast_collabs > 1].sort_values(ascending=False).to_dict()
    }
    return jsonify(result)


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
def release_year_top10():
    return df['release_year'].value_counts()[:10].to_json(orient='columns', force_ascii=False)


@app.route('/releaseyear/bottom10')
@cross_origin()
def release_year_bottom10():
    return df['release_year'].value_counts()[-10:].to_json(orient='columns', force_ascii=False)


@app.route('/listedin/top10')
@cross_origin()
def listed_in_top10():
    return listed_in_counts[:10].to_json(orient='columns', force_ascii=False)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.run(port=80, debug=True)
