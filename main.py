from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


API_KEY = "Your API Key"
MOVIES_SEARCH_ENDPOINT = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}"
MOVIES_ID_ENDPOINT = "https://api.themoviedb.org/3/movie/"
MOVIES_IMG_URL="https://image.tmdb.org/t/p/w300_and_h450_bestv2"
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class EditForm(FlaskForm):
    rating = StringField(label="Your Rating Out of 10", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


class AddMovie(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


# Create table using SQLAlchemy
with app.app_context():
    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        year = db.Column(db.Integer, nullable=False)
        description = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.Float, nullable=True)
        ranking = db.Column(db.Integer, unique=True, nullable=True)
        review = db.Column(db.String(250), nullable=True)
        img_url = db.Column(db.String(250), unique=True, nullable=False)

        def __repr__(self):
            return f'<Book {self.title}>'

    db.create_all()


# Home page with movie list
@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies=all_movies)


# Add new movie to the list
@app.route('/add', methods=["GET", "POST"])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        movie_keyword = form.title.data
        response = requests.get(url=MOVIES_SEARCH_ENDPOINT, params={"api_key": API_KEY, "query": movie_keyword})
        data = response.json()['results']
        return render_template('select.html', options=data)
    return render_template('add.html', form=form)


@app.route("/find")
def find_movie():
    movie_id = request.args.get('id')
    if movie_id:
        movie_id_url = f"{MOVIES_ID_ENDPOINT}{movie_id}?api_key={API_KEY}"
        response = requests.get(url=movie_id_url, params={"api_key": API_KEY})
        data = response.json()
        new_movie = Movie(title=data["title"], year=data["release_date"], description=data["overview"],
                          img_url=f"{MOVIES_IMG_URL}{data['poster_path']}")
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('update', id=new_movie.id))


@app.route("/select", methods=["GET", "POST"])
def select():
    movie_details_endpoint = f"https://api.themoviedb.org/3/movie/603?api_key={API_KEY}"
    response = requests.get(url=movie_details_endpoint)
    data = response.json()
    new_movie = Movie(title=data["title"], year=data["release_date"], description=data["overview"],
                      rating=None, ranking=None, review=None, img_url=data["poster_path"])
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('home'))


# Update rating and review details using WTForms
@app.route("/update", methods=["GET", "POST"])
def update():
    form = EditForm()
    movie_id = request.args.get("id")
    movie_to_update = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie_rating = form.rating.data
        movie_review = form.review.data
        movie_to_update.rating = movie_rating
        movie_to_update.review = movie_review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie_to_update, form=form)


# Delete a movie
@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
