import logging
import sqlite3
import sys

from flask import Flask, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

number_of_connections = 0


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global number_of_connections
    number_of_connections += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


def get_post_count():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(id) FROM posts').fetchone()[0]
    connection.close()
    return post_count


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info("Post with id: \"{}\" does not exist!".format(post_id))
        return render_template('404.html'), 404
    else:
        app.logger.info("Article - \"{}\" retrieved!".format(post[2]))
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("About Us page rendered!")
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            app.logger.info("Article cannot be created without a title!")
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            app.logger.info("Article \"{}\" was created!".format(title))
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz', methods=["GET"])
def health_endpoint():
    return app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )


@app.route('/metrics', methods=["GET"])
def metrics_endpoint():
    global number_of_connections
    return app.response_class(
        response=json.dumps({"db_connection_count": number_of_connections,
                             "post_count": get_post_count()}),
        status=200,
        mimetype='application/json'
    )


# start the application on port 3111
if __name__ == "__main__":
    # Logging Configuration
    log_file_handler = logging.FileHandler("app.log")
    log_stream_handler = logging.StreamHandler(sys.stdout)
    log_format = logging.Formatter('%(asctime)s %(message)s')
    log_file_handler.setFormatter(log_format)
    log_stream_handler.setFormatter(log_format)
    app.logger.addHandler(log_file_handler)
    app.logger.addHandler(log_stream_handler)
    app.logger.setLevel(logging.DEBUG)

    app.run(host='0.0.0.0', debug=True, port='3111')
