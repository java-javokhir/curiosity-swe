from flask import render_template, Blueprint, request

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

    query = request.form['query']
    if query:
        return redirect(url_for('results.result_page'), link=link)

@main.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about_us.html')

