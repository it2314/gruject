from flask import Flask, render_template, redirect, url_for, flash
from forms import ContactForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'replace-this-with-secure-random-in-prod')

logger = logging.getLogger(__name__)


# Database configuration: prefer DATABASE_URL (Postgres) for Kubernetes, fallback to SQLite file
def build_database_uri():
    raw = os.environ.get('DATABASE_URL', '')
    if raw:
        raw = raw.strip()
        # try to validate the given URL using SQLAlchemy's parser if available
        try:
            from sqlalchemy.engine.url import make_url

            make_url(raw)
            return raw
        except Exception as e:
            logger.warning('DATABASE_URL present but invalid: %s (%s)', raw, e)

    # try to build URL from individual environment variables commonly used
    user = os.environ.get('POSTGRES_USER') or os.environ.get('DB_USER') or os.environ.get('PGUSER')
    password = os.environ.get('POSTGRES_PASSWORD') or os.environ.get('DB_PASSWORD') or os.environ.get('PGPASSWORD')
    host = os.environ.get('POSTGRES_HOST') or os.environ.get('DB_HOST') or os.environ.get('PGHOST') or 'postgres'
    db = os.environ.get('POSTGRES_DB') or os.environ.get('DB_NAME') or os.environ.get('PGDATABASE')
    port = os.environ.get('POSTGRES_PORT') or os.environ.get('DB_PORT') or os.environ.get('PGPORT') or '5432'
    if user and password and db:
        return f'postgresql://{user}:{password}@{host}:{port}/{db}'

    logger.warning('No valid DATABASE_URL or Postgres env vars found; falling back to sqlite.')
    return 'sqlite:///data.db'


app.config['SQLALCHEMY_DATABASE_URI'] = build_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# log chosen database URI (avoid printing secrets in production)
try:
    logger.info('Using SQLALCHEMY_DATABASE_URI=%s', app.config.get('SQLALCHEMY_DATABASE_URI'))
except Exception:
    pass

db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Message {self.id} {self.email}>"


def ensure_db():
    try:
        # ensure we run create_all inside an application context
        with app.app_context():
            db.create_all()
    except Exception as e:
        # If DB isn't available at startup, continue; requests will fail when attempting to save
        logger.exception('ensure_db failed: %s', e)
        pass


# Register the ensure_db hook if the Flask app exposes before_first_request.
# Some runtime environments or frameworks may not provide that attribute;
# in that case call ensure_db immediately as a best-effort fallback so
# module import won't fail with AttributeError.
if hasattr(app, 'before_first_request'):
    try:
        app.before_first_request(ensure_db)
    except Exception:
        # If registration fails for any reason, try to run once now.
        try:
            ensure_db()
        except Exception:
            pass
else:
    try:
        ensure_db()
    except Exception:
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
