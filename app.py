from flask import Flask, render_template, redirect, url_for, flash
from forms import ContactForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'replace-this-with-secure-random-in-prod')

# Database configuration: prefer DATABASE_URL (Postgres) for Kubernetes, fallback to SQLite file
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Message {self.id} {self.email}>"


@app.before_first_request
def ensure_db():
    try:
        db.create_all()
    except SQLAlchemyError:
        # If DB isn't available at startup, continue; requests will fail when attempting to save
        pass


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ContactForm()
    if form.validate_on_submit():
        # save into DB
        msg = Message(name=form.name.data, email=form.email.data, message=form.message.data)
        try:
            db.session.add(msg)
            db.session.commit()
            flash(f"Thanks {form.name.data}! We received your message.", 'success')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Could not save your message right now. Please try again later.', 'danger')
        return redirect(url_for('index'))
    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
