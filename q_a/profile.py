from q_a import app
from flask import request, render_template, \
    url_for, Markup, session, redirect
from q_a.models import db, User, Role_types, Email, Handed_assignment
from q_a.supplement import Amend, Check, Emails
from itsdangerous import URLSafeSerializer
from re import sub

@app.route('/profile', methods=['POST', 'GET'])
@app.route('/profile/<int:user_id>', methods=['POST', 'GET'])
def profile(user_id=None):
    Check.update()
    if session.get('user') == f'''Пользователь {session.get('user_id')}''':
        return redirect(url_for('login'))
    if not session.get('user_id'):
        return Check.login()
    if user_id is None:
        user_id = session.get('user_id')
    if request.method == 'GET':
        if User.query.get(user_id) is None:
            return Check.page()
        if user_id != session.get('user_id') and session.get('status') != 2:
            return Check.status(url_for('profile'))
        user = User.query.get(user_id).username
        firstname = User.query.get(user_id).firstname
        surname = User.query.get(user_id).surname
        email = User.query.get(user_id).email
        group = User.query.get(user_id).group.group
        role = Role_types.query.get(User.query.get(user_id).role.role).type
        date = Amend.datetime(User.query.get(user_id).datetime)
        roles = Role_types.query.all()
        questions = User.query.get(user_id).questions
        answers = User.query.get(user_id).answers
        for question in questions:
            question.title = Markup(Amend.md(question.title))
        for answer in answers:
            answer.question.title = Markup(Amend.md(answer.question.title))
        return render_template('profile.html',
                               user_id=user_id,
                               user=user,
                               firstname=firstname,
                               surname=surname,
                               email=email,
                               group=group,
                               role=role,
                               roles=roles,
                               role_id=User.query.get(user_id).role.role,
                               questions=questions,
                               answers=answers,
                               date=date,
                               emails=Email,
                               handed_assignments=Handed_assignment.query.filter_by(assignee=user_id).all(),
                               Amend=Amend)
    if request.method == 'POST':
        updates = dict(request.form)
        user = User.query.get(user_id)
        if updates.get('username'):
            if User.query.filter_by(username=updates.get('username')).first():
                return Amend.flash('Это имя занято.', 'danger', request.url)
            user.username = sub(r'[^А-ЯЁа-яё\w_]', '', updates.get('username'))
        if updates.get('email'):
            if User.query.filter_by(email=updates.get('email')).first():
                return Amend.flash('Этот имейл уже используется.', 'danger', request.url)
            token = URLSafeSerializer(app.config["SECRET_KEY"], salt='confirm_email').dumps((user_id, updates.get('email')))
            Emails.send(about='Подтверждение имейла',
                        what=f'''<p>Вы сменили имейл на сайте курса фонетики и фонологии.</p><p>Ссылка для подтверждения нового имейла – <b><a href="{url_for('notification', token=token, _external=True)}">{url_for('notification', token=token, _external=True)}</a></b>.</p>''',
                        emails=updates.get('email'))
            Email.query.filter_by(user_id=user_id).update({'confirmed': False})
            user.email = updates.get('email')
            Amend.flash('Вам было выслано письмо для подтверждения нового имейла.', 'warning')
        if updates.get('firstname'):
            user.firstname = updates.get('firstname')
        if updates.get('surname'):
            user.surname = updates.get('surname')
        if updates.get('group'):
            user.group.group = updates.get('group')
        if updates.get('role'):
            user.role.role = updates.get('role')
        if updates.get('new_password') and session.get('status') == 2:
            user.password = updates.get('new_password')
            db.session.commit()
            return Amend.flash('Пароль изменён.',
                               'success',
                               url_for('profile', user_id=user_id))
        elif updates.get('new_password'):
            if updates.get('current_password') == user.password:
                user.password = updates.get('new_password')
                db.session.commit()
                return Amend.flash('Пароль изменён.',
                                   'success',
                                   url_for('profile', user_id=user_id))
            else:
                return Amend.flash('Текущий пароль введён неверно.',
                                   'danger',
                                   url_for('profile', user_id=user_id))
        elif updates.get('ban') and session.get('status') == 2:
            user.password = None
            user.email = None
            user.username = f'Пользователь {user_id}'
            db.session.commit()
            return Amend.flash('Профиль заблокирован.',
                               'success',
                               url_for('profile', user_id=user_id))
        db.session.commit()
        return Amend.flash('Вы успешно обновили данные профиля.',
                           'success',
                           url_for('profile', user_id=user_id))