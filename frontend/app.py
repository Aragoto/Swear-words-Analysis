# Group 66 Swear Words Analysis
# Xinshu Li 875109
# Dongting Hu 960886
# Qinwei Yuan 1006223
# Ansheng Dong  989973
# Tonghao Wang 1039694
from flask import Flask, render_template, url_for, redirect
import os
from importlib import reload
import process_json
import socket

from get_nodes import get_ip

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/map', methods=['GET'])
def map():
    return render_template('map.html')


@app.route('/statistics')
def statistics():
    data = process_json.output_data()
    emotion_stat = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    for city in data:
        emotion_stat['Positive'] += city['EMOTION_POSITIVE']
        emotion_stat['Negative'] += city['EMOTION_NEGATIVE']
        emotion_stat['Neutral'] += city['EMOTION_NEUTRAL']
    education_distribution, economic_distribution, unemployment_distribution, wordcount_distribution = process_json.output_stat()
    return render_template('statistics.html', data=data,
                           education_distribution=education_distribution,
                           economic_distribution=economic_distribution,
                           unemployment_distribution=unemployment_distribution,
                           wordcount_distribution=wordcount_distribution,
                           emotion_stat=emotion_stat,
                           id_to_name=process_json.id_to_name)


@app.route('/monitor')
def monitor():
    ip = get_ip('nginx')
    return redirect('http://' + ip+ ':4040', code=301)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


@app.context_processor
def context_processor():
    # load and reload the data from process_json.py
    def get_data():
        reload(process_json)
        data = process_json.output_data()
        return data

    # get dynamic urls with timestamp for updating css links in Flask
    def dated_url_for(endpoint, **values):
        if endpoint == "static":
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(app.root_path, endpoint, filename)
                values['q'] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)

    return dict(url_for=dated_url_for,
                get_data=get_data)


if __name__ == '__main__':
    app.run(debug=True)
