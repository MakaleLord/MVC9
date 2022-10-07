#!/usr/bin/python3

from flask import Flask, render_template, redirect, url_for, abort, request, flash, session

import random, math

from .decorators import login_required, welcome_screen
from .post_models import (
    create_post_table,
    get_posts,
    find_post,
    random_post,
    insert_post,
    count_posts,
    paginated_posts,
)

from .user_models import create_user_table, get_user, insert_user


app = Flask(__name__)

######## SET THE SECRET KEY ###############
# You can write random letters yourself or
# Go to https://randomkeygen.com/ and select a
# random secret key
####################
app.secret_key = "your secret key here"

posts_per_page = 3

my_user = {"email": "panda@cwhq.com", "password": "panda123"}

with app.app_context():
    create_post_table()
    create_user_table()
    user_exist = get_user(my_user['email'], my_user['password'])
    if not user_exist:
        insert_user(my_user['email'], my_user['password'])

@app.route("/")
@welcome_screen
def home_page():
    total_posts = count_posts()
    pages = math.ceil(total_posts / posts_per_page)
    current_page = request.args.get("page", 1, int)
    posts_data = paginated_posts(current_page, posts_per_page)
    return render_template(
        "page.html",
        posts=posts_data,
        current_page=current_page,
        total_posts=total_posts,
        pages=pages,
    )


@app.route("/welcome")
def welcome_page():
    return render_template("welcome.html")


@app.route("/<post_link>")
@welcome_screen
def post_page(post_link):
    post = find_post(post_link)
    if post:
        return render_template("post.html", post=post)
    else:
        abort(404)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


@app.route("/random")
def random_post_page():
    post = random_post()
    return redirect(url_for("post_page", post_link=post["permalink"]))

@app.route("/new-post", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "GET":
        return render_template("newpost.html", post_data={})
    else:
        post_data = {
            "title": request.form["post-title"],
            "author": request.form["post-author"],
            "content": request.form["post-content"],
            "permalink": request.form["post-title"].replace(" ", "-"),
            "tags:": request.form["post-tags"],
        }

        existing_post = find_post(post_data["permalink"])
        if existing_post:
            app.logger.warning(f"duplicate post: {post_data['title']}")
            flash(
                "error", "There's already a similar post, maybe use a different title"
            )
            return render_template("newpost.html")
        else:
            insert_post(post_data)
            app.logger.info(f"new post: {post_data['title']}")
            flash("success", "Congratulations on publishing another blog post.")
            return redirect(url_for("post_page", post_link=post_data["permalink"]))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email-id']
        password = request.form['password']
        user = get_user(email, password)
        if user:
            session['logged_in'] = True
            flash('success', 'You are now logged in')
            return redirect(url_for('home_page'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))
###### E X E R C I S E S #########
#
#   Exercise 1: Render the login page
#   Exercise 2: Add a user in the database
#   Exercise 3: Get the email and password from the login form
#   Exercise 4: Show the new post page only when logged in
#   
#   Homework 1: Add a logout button
#   In `app.py`
#       -Create a new function called `logout()`
#   Inside `logout()`
#       -Set the session variable `logged_in` to `False`
#       -Redirect the route to `login` page
#   In `layout.html`
#   Inside the `.navbar` div
#   At the end of the div with class `.container-fluid`           
#       -add an `if` statement to check the value of session variable `logged_in`
#       -Inside above `if`, add an `a` tag with a Bootstrap button class
#       -Set the `href` to url for `logout` page.
#       -Use `i` tag to add a logout icon.
#   Docs Link: https://icons.getbootstrap.com/icons/box-arrow-right/

#
#   Homework 2: Show the login link in navigation
#       In `layout.html`
#       Inside the div with class `.navbar`
#           -Before the new post anchor tag, add an `if else` statement to check the value of session variable logged_in
#           -Move the `a` tag for adding new post inside above `if` statement.
#           -`for the `else`, add an anchor tag for `login` page.
#           -Set the class of anchor tag to `nav-link` and `href` to url of `login` page.
#           Add a Bootstrap icon to represent login
#               -try searching "person" or "login" in the filter input
#           Docs Link: https://icons.getbootstrap.com/icons
#       Image: https://icons.getbootstrap.com/icons screenshot emphasizing the search bar
#           or gif of using the search bar

##################################
