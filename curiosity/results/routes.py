from flask import render_template, Blueprint, request, redirect, url_for
from youtubesearchpython import *
from curiosity.main.utils import meta_dict_corp,train_model, query_result

results = Blueprint('results', __name__)


@results.route("/results", methods=['GET', 'POST'])
def result_page():
    query = request.form['query']

    meta_dict_corp()
    train_model()
    episode_num, timestamp = query_result(query)

    playlist = Playlist('https://www.youtube.com/playlist?list=PLrAXtmErZgOdP_8GztsuKi9nrraNbKKp4')

    while playlist.hasMoreVideos:
        playlist.getNextVideos()
    for video in playlist.videos:
        if episode_num in video['title']:
            link = video['id']

    return render_template('results.html', link=link, start=timestamp-20, end=timestamp+300)


