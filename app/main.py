from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Dev"

#configure SQL ALchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///staffing.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#DB Model
class User(db.Model):
    #Class Variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_user_admin = db.Column(db.Boolean, default=False)
    is_provider_admin = db.Column(db.Boolean, default=False)
    is_customer_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        print ("checking password")
        return check_password_hash(self.password_hash, password)
    
    def set_user_admin(self, admin):
        if isinstance(admin, bool):
            self.is_user_admin = admin

    def set_provider_admin(self, admin):
        if isinstance(admin, bool):
            self.is_provider_admin = admin

    def set_customer_admin(self, admin):
        if isinstance(admin, bool):
           self.is_customer_admin = admin

#Routes
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return render_template("auth.html")

#Login
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    error = None
    if not user:
        flash("Username not found")
        return render_template("auth.html")
    
    if not user.check_password(password):
        flash("Incorrect password")
        return render_template("auth.html")
     
    session["username"] = username
    return redirect(url_for("dashboard"))
    
    
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
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)