"""Server for movie ratings app."""

from flask import (Flask, render_template, request, flash, session,
                   redirect)
from model import connect_to_db, db
import crud

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined



@app.route('/')
def homepage():
    """View homepage."""

    return render_template('homepage.html')


# Replace this with routes and view functions!

@app.route('/movies')
def all_movies():
    """View all movies."""

    movies = crud.get_movies()

    return render_template("all_movies.html", movies=movies)

@app.route("/movies/<movie_id>")
def movie_details(movie_id):
    """"Show movie details"""

    movie = crud.get_movie_by_id(movie_id)

    return render_template("movie_details.html", movie=movie)

@app.route("/users")
def all_users():

    users = crud.get_users()

    return render_template("all_users.html", users=users)

@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""
    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if user:
        flash("Cannot create an account with that email. Try again.")
    else:
        user = crud.create_user(email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")
    return redirect("/")


@app.route("/users/<user_id>")
def user_profile(user_id):

    user = crud.get_user_by_id(user_id)

    return render_template("user_details.html", user=user)

@app.route("/login", methods=["POST"])
def process_login():
    """Process use login."""
    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if not user or user.password != password:
        flash("The email or password you entered was incorrect.")
    else:
        # log in user by storing the user's email in session
        session["use_email"] = user.email
        flash(f"Welcome back, {user.email}!")
    return redirect("/")

@app.route("/update_rating/<rating_id>", methods=["POST"])
def update_rating(rating_id):
    """rating_id = request.form["rating_id"]"""
    updated_score = request.form["updated_score"]
    print("************************************************")
    print(f"updated_score={updated_score}")
    crud.update_rating(rating_id, updated_score)
    db.session.commit()

    return "Success"

@app.route("/movies/<movie_id>/ratings", methods=["POST"])
def create_rating(movie_id):
    """Create a new rating for the movie."""

    logged_in_email = session.get("user_email")
    rating_score = request.form.get("rating")

    if logged_in_email is None:
        flash("You must log in to rate a movie.")
    elif not rating_score:
        flash("Error: you didn't select a score for your rating.")
    else:
        user = crud.get_user_by_email(logged_in_email)
        movie = crud.get_movie_by_id(movie_id)

        rating = crud.create_rating(user, movie, int(rating_score))
        db.session.add(rating)
        db.session.commit()

        flash(f"You rated this movie {rating_score} out of 5.")

    return redirect(f"/movies/{movie_id}")
    
if __name__ == "__main__":
    # DebugToolbarExtension(app)
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
