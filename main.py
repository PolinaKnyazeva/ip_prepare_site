from flask import Flask, render_template, url_for, request
from werkzeug.utils import redirect

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

from datetime import datetime

app = Flask(__name__)
user_in = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)


class Topic(db.Model):
    __tablename__ = "Topic"

    topic_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Integer)
    password = db.Column(db.String)
    tickets = db.relationship("Ticket")
    date_creating = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return "Topic id %r" % self.topic_id


class Ticket(db.Model):
    __tablename__ = "Ticket"

    ticket_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('Topic.topic_id'))
    text = db.Column(db.Text)
    date_creating = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return "Ticket id %r" % self.id


@app.route('/')
@app.route('/home')
def show_home_page():
    return render_template("home.html")


@app.route('/topics')
def show_all_topics():
    text_search = request.args.get('search')

    found_topics = Topic.query.all()
    if text_search:
        found_topics = Topic.query.filter(Topic.title.contains(text_search)).all()
    return render_template("topics.html", found_topics=found_topics, len=len)


@app.route('/add_topic', methods=['POST', 'GET'])
def add_new_topic():
    if request.method == "POST":
        topic_title = request.form['topic_title']
        topic_password = None
        if request.form['topic_password']:
            topic_password = request.form['topic_password']
        try:
            topic = Topic(title=topic_title, password=topic_password)
            db.session.add(topic)
            db.session.commit()
        except:
            print('Ошибка создания темы')
        return redirect('/topics')
    else:
        return render_template("add_topic.html")


@app.route('/topics/delete/<int:topic_id>')
def delete_topic(topic_id):
    ticket_topic = Topic.query.get_or_404(topic_id)
    try:
        db.session.delete(ticket_topic)
        db.session.commit()
        return redirect('/topics')
    except:
        return "При удалении произошла ошибка"


@app.route('/topics/<topic_id>')
def show_ticket_from_topic(topic_id):
    found_topic = Topic.query.get_or_404(topic_id)

    text_search = request.args.get('search')
    # if text_search:
    #     found_tickets = Ticket.query.filter(Ticket.text.contains(text_search)).all()
    found_tickets = found_topic.tickets
    return render_template("ticket.html", topic=found_topic, found_tickets=found_tickets)


@app.route('/topics/<int:topic_id>/create_ticket', methods=['POST', 'GET'])
def add_new_ticket(topic_id):
    if request.method == "POST":
        text = request.form['text']
        try:
            ticket = Ticket(text=text, topic_id=topic_id)
            db.session.add(ticket)
            db.session.commit()
            return redirect('/topics/{}'.format(topic_id))
        except:
            print('Ошибка создания')
    else:
        return render_template('create_ticket.html')


@app.route('/topics/<int:topic_id>/delete/<ticket_id>')
def delete_ticket(topic_id, ticket_id):
    ticket_deleted = Ticket.query.get_or_404(ticket_id)
    try:
        db.session.delete(ticket_deleted)
        db.session.commit()
        return redirect('/topics/{}'.format(topic_id))
    except:
        return "При удалении произошла ошибка"


@app.route('/topics/<int:topic_id>/recording/<ticket_id>', methods=['POST', 'GET'])
def edit_ticket(topic_id, ticket_id):
    ticket_editing = Ticket.query.get_or_404(ticket_id)
    if request.method == "POST":
        ticket_editing.text = request.form['text']
        try:
            db.session.commit()
            return redirect('/topics/{}'.format(topic_id))
        except:
            return "При редактировании произошла ошибка"
    else:
        return render_template('edit_ticket.html', ticket=ticket_editing)


if __name__ == '__main__':
    app.run(debug=False)
