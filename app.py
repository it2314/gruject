from flask import Flask, render_template, redirect, url_for, flash
from forms import ContactForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace-this-with-secure-random-in-prod'


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ContactForm()
    if form.validate_on_submit():
        # In a real app you'd process/store/send the data
        flash(f"Thanks {form.name.data}! We received your message.", 'success')
        return redirect(url_for('index'))
    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
