from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from apisearch import search_movie

# CREATE APP
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
bootstrap = Bootstrap5(app)


#CREATE FORMS
class FindMovieForm(FlaskForm):
    title =  StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")

class RateForm(FlaskForm):
    rating = IntegerField(label="Your Rating (over 10)", validators=[DataRequired(), NumberRange(max=10, message="Rating is on a scale of 10")])
    review = StringField(label="Your Review (What did you like about the movie?)", validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class EditForm(FlaskForm):
    title =  StringField(label="Movie Title", validators=[DataRequired()])
    rating = IntegerField(label="Your Rating (over 10)",
                          validators=[DataRequired(), NumberRange(max=10, message="Rating is on a scale of 10")])
    review = StringField(label="Your Review (What did you like about the movie?)", validators=[DataRequired()])
    submit = SubmitField(label="Submit")
    release_year = IntegerField(label="Release Year", validators=[DataRequired()])
    overview = StringField(label="Overview", validators=[DataRequired()])
    edit = SubmitField(label='Edit Movie')


# CREATE DB
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE FORMAT FOR DB
class Movie(db.Model):
    __tablename__ = 'movies'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    review: Mapped[str] = mapped_column(String(500))
    overview: Mapped[str] = mapped_column(String(1000))

with app.app_context():
    db.create_all()

#ROUTES

@app.route("/")
def home():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)

@app.route("/add", methods=["POST", "GET"])
def add():
    movie_form = FindMovieForm()

    if movie_form.validate_on_submit():
        print("Form validated")
        title = movie_form.title.data
        options = search_movie(title)
        return render_template('select.html', options=options)
    else:
        print("Not validated")
        print(movie_form.errors)
    return render_template('add.html', form=movie_form)


@app.route("/rate", methods=["POST", "GET"])
def rate():
    form = RateForm()
    if form.validate_on_submit():
        title = request.form.get('title')
        release_date = request.form.get('release_date')
        release_year = release_date.split('-')[0]
        overview = request.form.get('overview')
        rating = form.rating.data
        review = form.review.data
        new_movie = Movie(title=title,release_year=release_year, rating=rating, review=review, overview=overview)

        try:
            db.session.add(new_movie)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            flash("Error encountered while saving movie.")
            print("DB Error:", e)

    else:
        title = request.args.get('title')
        release_date = request.args.get('release_date')
    return render_template('rate.html', form=form, title=title, release_date=release_date)


@app.route("/edit/<int:movie_id>", methods = ["POST", "GET"])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    movie_form = EditForm(obj=movie)
    if movie_form.validate_on_submit():
        print("Form validated")
        new_title = movie_form.title.data
        new_release_year = movie_form.release_year.data
        new_rating = movie_form.rating.data
        new_review = movie_form.review.data
        new_overview = movie_form.overview.data

        try:
            if new_title:
                movie.title = new_title
            if new_release_year:
                movie.release_year = new_release_year
            if new_rating:
                movie.rating = new_rating
            if new_review:
                movie.review = new_review
            if new_overview:
                movie.overview = new_overview
            db.session.commit()
            flash("Movie was updated successfully!", "success")
            return redirect("/")

        except Exception as e:
            flash("Error encountered while updating")
            print("Error:", e)
            return render_template('edit', movie=movie, form=movie_form)

    return render_template('edit.html', movie=movie, form=movie_form)

@app.route("/delete/<int:movie_id>")
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    try:
        if movie:
            db.session.delete(movie)
            deleted_id = movie.id
            Movie.query.filter(Movie.id > deleted_id).update(
                {Movie.id: Movie.id - 1}
            )
            db.session.commit()
            flash("Movie was successfully removed. Remember to update your top ten list")
        else:
            flash("Movie was not found!")


    except Exception as e:
        db.session.rollback()
        flash("Error deleting movie.")

    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
