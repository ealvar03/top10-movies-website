from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


class EditForm(FlaskForm):
    rating = StringField(label="Your Rating Out of 10", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create table using SQLAlchemy
with app.app_context():
    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        year = db.Column(db.Integer, nullable=False)
        description = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.Float, nullable=False)
        ranking = db.Column(db.Integer, unique=True, nullable=False)
        review = db.Column(db.String(250), nullable=False)
        img_url = db.Column(db.String(250), unique=True, nullable=False)

        def __repr__(self):
            return f'<Book {self.title}>'

    db.create_all()


# Home page with movie list
@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)


# Add new movie to the list
@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data = request.form
        new_movie = Movie(title=data["title"], year=data["year"], description=data["description"],
                          rating=data["rating"], ranking=data["ranking"], review=data["review"],
                          img_url=data["img_url"])
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html')


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
