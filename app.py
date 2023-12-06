#!/usr/bin/env python3
import re
import os
from flask import Flask, redirect, render_template, request
from flask_basicauth import BasicAuth
from octoprint import OctoPrint

app = Flask(__name__)

# Load .env file
from dotenv import load_dotenv

load_dotenv()

app.static_folder = "static"

# Configure basic auth credentials
app.config["BASIC_AUTH_USERNAME"] = os.getenv("BASIC_AUTH_USERNAME")
app.config["BASIC_AUTH_PASSWORD"] = os.getenv("BASIC_AUTH_PASSWORD")

basic_auth = BasicAuth(app)

site = os.getenv("OCTOPRINT_SITE")
key = os.getenv("OCTOPRINT_KEY")
API = OctoPrint(site, key)


# Gets the "important" group from a user
# Either "admins" or "co##"
def get_important_group(user):
    if "admins" in user["groups"]:
        return "admins"

    for group in user["groups"]:
        if group.startswith("co"):
            return group

    return "users"


@app.route("/")
@basic_auth.required
def index():
    users = API.get_users()["users"]

    # sort users by admin/co## groups, then by username
    users = sorted(users, key=lambda user: (get_important_group(user), user["name"]))
    years = ["co" + str(i) for i in range(27, 41)]
    return render_template("index.html", users=users, years=years)


# Static files
@app.route("/static/<path:path>")
def static_files(path):
    return app.send_static_file(path)


@app.route("/create", methods=["POST"])
@basic_auth.required
def create():
    username = request.form["username"]
    password = request.form["password"]
    year = request.form["year"]
    is_admin = "admin" in request.form
    print(year)

    if API.user_exists(username):
        return render_template("error.html", message="User already exists")

    groups = ["users", year]
    if is_admin:
        groups.append("admins")
    groups = [group for group in groups if group != ""]

    API.create_user(username, password, groups=groups)

    # Redirect back to the index page
    return redirect("/")


@app.route("/bulk", methods=["POST"])
@basic_auth.required
def bulk():
    year = request.form["year"]
    password = request.form["password"]
    # split the usernames by newlines or commas
    usernames = re.split(r"[\n,]", request.form["usernames"])
    usernames = [username.strip() for username in usernames]

    for username in usernames:
        if not API.user_exists(username):
            groups = [group for group in ["users", year] if group != ""]
            API.create_user(username, password, groups=groups)

    # Redirect back to the index page
    return redirect("/")


@app.route("/massdelete", methods=["POST"])
@basic_auth.required
def mass_delete():
    year = request.form["year"]
    API.mass_delete(year)

    # Redirect back to the index page
    return redirect("/")


@app.route("/delete", methods=["POST"])
@basic_auth.required
def delete():
    # Refuse to delete the 'pi' user
    if request.form["username"] == "pi":
        return render_template("error.html", message="Cannot delete pi user")

    API.delete_user(request.form["username"])
    return redirect("/")


@app.route("/reset", methods=["POST"])
@basic_auth.required
def reset():
    API.reset_password(request.form["username"], request.form["password"])
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
