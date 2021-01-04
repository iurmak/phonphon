from flask import Flask

app = Flask(__name__)
app.secret_key = '228'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phon_questions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yurmkrv@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'yurmkrv@gmail.com'
app.config['MAIL_PASSWORD'] = 'go@iu@112'
app.config['URL'] = 'http://127.0.0.1:5000'

import q_a.login, q_a.questions, q_a.question, \
    q_a.edit, q_a.profile, q_a.new_question, q_a.signup, q_a.notification, \
    q_a.profiles, q_a.new_assignment, q_a.assignments, q_a.assignment, \
    q_a.add_user, q_a.todo_student, q_a.todo_teacher, q_a.check_assignment, \
    q_a.massive_assessment, q_a.all_grades, q_a.main, q_a.new_post, q_a.settings
