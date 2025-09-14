from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

#Routes



    
#register
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user:
        flash("User already exists")
        return render_template("auth.html")
    else:
        new_user= User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username']= username
        return redirect(url_for('dashboard'))

#Dashboard
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session['username'])

#log out
@app.route("/logout")
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)