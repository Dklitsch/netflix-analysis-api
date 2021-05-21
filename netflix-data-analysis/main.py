import io

import flask
import werkzeug
from flask import request, Response, jsonify, send_file
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from flask_cors import CORS, cross_origin
import sys
import math
import datetime
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from io import StringIO

# Create the application.
app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cors = CORS(app)

plt.style.use('fivethirtyeight')
plt.rcParams.update({'figure.autolayout': True})

def flatten_list(list):
    return [item for sublist in list for item in sublist]


def director_per_year_count(name):
    return df[df.director.str.contains(name, na=False, case=False) == True].groupby('release_year').count().title


def cast_per_year_count(name):
    return df[df.cast.str.contains(name, na=False, case=False) == True].groupby('release_year').count().title


def country_per_year_count(name):
    return df[df.country.str.contains(name, na=False, case=False) == True].groupby('release_year').count().title


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
        return df.sort_values(by="release_year").title[:request.form['take']].fillna("Unknown").to_json(orient='records', force_ascii=False)
    else:
        return jsonify(df.fillna("Unknown").to_dict(orient='records'))


@app.route('/searchterms/<term>')
@cross_origin()
def search_terms_stg(term):
    director_names = Series(flatten_list([x.split(', ') for x in df.director.dropna()]))
    filtered_directors = director_names[director_names.str.contains(term, na=False, case=False) == True].unique()
    director_terms = [{"term": x, "type": "director"} for x in filtered_directors]

    cast_names = Series(flatten_list([x.split(', ') for x in df.cast.dropna()]))
    filtered_cast = cast_names[cast_names.str.contains(term, na=False, case=False) == True].unique()
    cast_terms = [{"term": x, "type": "cast"} for x in filtered_cast]

    country_names = Series(flatten_list([x.split(', ') for x in df.country.dropna()]))
    filtered_countries = country_names[country_names.str.contains(term, na=False, case=False) == True].unique()
    country_terms = [{"term": x, "type": "country"} for x in filtered_countries]
    return jsonify(director_terms + cast_terms + country_terms)


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


@app.route('/director/top5/yearBreakdown')
@cross_origin()
def director_top5_year_breakdown():
    top_5_directors = director_counts[:5]

    def format_result(name):
        return {'name': name, 'year_breakdown': director_per_year_count(name).to_dict()}

    return jsonify([format_result(name) for name in top_5_directors.keys()])


@app.route('/director/<name>')
@cross_origin()
def director_detail(name):
    titles = df[df.director.str.contains(name, na=False, case=False) == True]
    result = titles[['title', 'country', 'release_year']].sort_values(by="release_year")
    return jsonify(result.to_dict(orient='records'))


@app.route('/director/<name>/director collabs')
@cross_origin()
def director_detail_director_collabs(name):
    titles = df[df.director.str.contains(name, na=False, case=False) == True]
    collabs = Series(flatten_list([str(x).split(', ') for x in titles.director[titles.director.notnull()]]))
    director_collabs = collabs[collabs.str.contains(name, na=False, case=False) == False].value_counts(sort=True)
    return Response(director_collabs[director_collabs > 1].to_json(), mimetype='application/json')


@app.route('/director/<name>/cast collabs')
@cross_origin()
def director_detail_cast_collabs(name):
    titles = df[df.director.str.contains(name, na=False, case=False) == True]
    cast_collabs = Series(flatten_list([str(x).split(', ') for x in titles.cast[titles.cast.notnull()]])).value_counts(sort=True)
    return Response(cast_collabs[cast_collabs > 1].to_json(), mimetype='application/json')


@app.route('/cast/top5')
@cross_origin()
def cast_top5():
    return ccast_counts[:5].to_json(orient='columns', force_ascii=False)


@app.route('/cast/top5/yearBreakdown')
@cross_origin()
def cast_top5_year_breakdown():
    top_5_cast = ccast_counts[:5]

    def format_result(name):
        return {'name': name, 'year_breakdown': cast_per_year_count(name).to_dict()}

    return jsonify([format_result(name) for name in top_5_cast.keys()])


@app.route('/cast/<name>')
@cross_origin()
def cast_detail_stage(name):
    titles = df[df.cast.str.contains(name, na=False, case=False) == True]
    titles = titles.fillna("Unknown")
    result = titles[['title', 'country', 'release_year']].sort_values(by="release_year").to_dict(orient='records')
    return jsonify(result)


@app.route('/cast/<name>/director collabs')
@cross_origin()
def cast_detail_director_collabs(name):
    titles = df[df.cast.str.contains(name, na=False, case=False) == True]
    collabs = Series(flatten_list([str(x).split(', ') for x in titles.director[titles.director.notnull()]]))
    director_collabs = collabs[collabs.str.contains(name, na=False, case=False) == False].value_counts(sort=True)
    return Response(director_collabs[director_collabs > 1].to_json(), mimetype='application/json')


@app.route('/cast/<name>/cast collabs')
@cross_origin()
def cast_detail_cast_collabs(name):
    titles = df[df.cast.str.contains(name, na=False, case=False) == True]
    cast_collabs = Series(flatten_list([str(x).split(', ') for x in titles.cast[titles.cast.notnull()]]))
    cast_collabs = cast_collabs[cast_collabs.str.contains(name, na=False, case=False) == False]
    collab_count = cast_collabs.value_counts(sort=True)
    return Response(collab_count[collab_count > 1].to_json(), mimetype='application/json')


@app.route('/country/top10')
@cross_origin()
def country_top5():
    return Response(countries_counts[:10].to_json(orient='columns', force_ascii=False), mimetype='application/json')


@app.route('/country/counts')
@cross_origin()
def country_counts():
    result = [[x, int(countries_counts[x])] for x in countries_counts.keys()]
    return jsonify(result)


@app.route('/country/top5/yearBreakdown')
@cross_origin()
def country_top5_year_breakdown():
    def format_result(name):
        return {'name': name, 'counts': country_per_year_count(name).to_dict()}

    result = [format_result(name) for name in countries_counts[:5].keys()]
    return jsonify(result)


@app.route('/country/<name>')
@cross_origin()
def country_detail(name):
    titles = df[df.country.str.contains(name, case=False) == True]
    titles_count = len(titles)

    countrys_directors = Series(flatten_list([str(x).split(', ') for x in titles.director[titles.director.notnull()]]))
    country_director_counts = countrys_directors.value_counts(sort=True)
    top_directors = country_director_counts[country_director_counts > 1][:5].to_dict()

    countrys_cast = Series(flatten_list([str(x).split(', ') for x in titles.cast[titles.cast.notnull()]]))
    cast_counts = countrys_cast.value_counts(sort=True)
    top_cast = cast_counts[cast_counts > 1][:5].to_dict()

    count_by_year = country_per_year_count(name)

    result = {
        'countryName': name,
        'titleCount': titles_count,
        'topDirectors': top_directors,
        'topCast': top_cast
    }
    return jsonify(result)


@app.route('/country/<name>/yearchart.png')
@cross_origin()
def country_detail_year_chart(name):
    counts = df[df.country.str.contains(name, na=False, case=False) == True].release_year.value_counts().sort_index()

    fig = Figure()
    ax = fig.subplots()
    ax.plot(counts.index, counts)
    ax.set(xlabel='Release Year', ylabel='Count', title='Releases by release year')

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return Response(werkzeug.wsgi.FileWrapper(buf), mimetype="image/png", direct_passthrough=True)


@app.route('/releaseyear/yearchart.png')
def release_year_year_chart():
    counts = df.release_year.value_counts().sort_index()

    fig = Figure()
    ax = fig.subplots()
    ax.plot(counts.index, counts)
    ax.set_xlabel('Release Year')
    ax.set_ylabel('Count')
    ax.set_yticks([0, 200, 400, 600, 800, 1000, 1200])
    ax.set_title('Releases by release year')

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return Response(werkzeug.wsgi.FileWrapper(buf), mimetype="image/png", direct_passthrough=True)


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
