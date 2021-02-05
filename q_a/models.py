from q_a import app
from flask_sqlalchemy import SQLAlchemy
from time import gmtime
from calendar import timegm

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text(40), nullable=False, unique=True)
    firstname = db.Column(db.Text(40), nullable=False)
    surname = db.Column(db.Text(40), nullable=False)
    email = db.Column(db.Text(100), unique=True)
    password = db.Column(db.Text(100))
    datetime = db.Column(db.Integer, default=timegm(gmtime()))
    group = db.relationship('Group', backref='users', uselist=False)
    role = db.relationship('Role_assignment', backref='users', uselist=False)
    subscriptions = db.relationship('Subscription', backref='user')
    answers = db.relationship('Answer', backref='answerer')
    questions = db.relationship('Question', backref='user')
    created_assignments = db.relationship('Assignment', backref='author')
    comments = db.relationship('Comment', backref='user')
    assignments = db.relationship('Handed_assignment', backref='user')
    posts = db.relationship('Post', backref='user')


class Role_assignment(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role = db.Column(db.Integer, default=1)


class Role_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, unique=True)


class Group(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    group = db.Column(db.Integer)


class Email(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    confirmed = db.Column(db.Boolean, default=False)
    new_mentions = db.Column(db.Boolean, default=True)
    new_answers = db.Column(db.Boolean, default=True)
    assignments = db.Column(db.Boolean, default=True)


class Subscription(db.Model):
    subscription_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'))


class Action_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text)


class Question(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    datetime = db.Column(db.Integer)
    title = db.Column(db.Text(150), nullable=False)
    text = db.Column(db.Text(20000), nullable=False)
    is_anon = db.Column(db.Boolean())
    is_pinned = db.Column(db.Boolean(), default=False)
    answers = db.relationship('Answer', backref='question', cascade='all, delete, delete-orphan', lazy='dynamic')
    subscriptions = db.relationship('Subscription', backref='question', cascade='all, delete, delete-orphan')


class Answer(db.Model):
    answer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'))
    datetime = db.Column(db.Integer, default=timegm(gmtime()))
    text = db.Column(db.Text(20000), nullable=False)
    is_anon = db.Column(db.Boolean())
    is_praised = db.Column(db.Boolean())


class Assignment(db.Model):
    assignment_id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.Integer)
    deadline = db.Column(db.Integer, default=None)
    assigner = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignees = db.Column(db.Text, default='all')
    title = db.Column(db.Text(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('assignment_types.id'))
    type = db.relationship('Assignment_types', backref='assignments')
    is_grade = db.Column(db.Boolean, default=False)
    assignments = db.relationship('Handed_assignment', backref='assignment', cascade='all, delete, delete-orphan')


class Handed_assignment(db.Model):
    source_assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'))
    assignment_id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.Integer)
    assignee = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer = db.Column(db.Text(20000))
    checked_by = db.Column(db.Integer)
    is_checked = db.Column(db.Boolean, default=False)
    when_checked = db.Column(db.Integer)
    main_comment = db.Column(db.Text)
    grade = db.Column(db.Integer, default=None)
    status_id = db.Column(db.Integer, db.ForeignKey('assignment_status.id'), default=1)
    status = db.relationship('Assignment_status', backref='assignments')
    discussion = db.relationship('Comment', backref='assignment', cascade='all, delete, delete-orphan')


class Assignment_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, unique=True)
    rate = db.Column(db.Float)


class Assignment_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, unique=True)


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('handed_assignment.assignment_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)


class Ping(db.Model):
    ping_id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.Integer)
    target_id = db.Column(db.Integer, nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action_id = db.Column(db.Integer, db.ForeignKey('action_types.id'))
    result_url = db.Column(db.Text)
    seen = db.Column(db.Boolean, default=False)


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    datetime = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.Text)
    tag = db.Column(db.Integer, db.ForeignKey('tags.id'))


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, unique=True)
    host = db.Column(db.Text)
