from q_a import app
from flask import render_template, session, request, url_for
from q_a.models import Group, Email, User, Role_assignment, db
from q_a.supplement import Amend, Check, Emails
from re import sub
from itsdangerous import URLSafeSerializer

@app.route('/profiles/add', methods=['GET', 'POST'])
def add_user():
    Check.update()
    if not session.get('user'):
        return Check.login()
    if session.get('status') != 2:
        return Check.status()
    if request.method == 'GET':
        return render_template('add_user.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        username = sub(r'[^А-ЯЁа-яё\w_]', '', request.form.get('username'))
        firstname = request.form.get('firstname')
        surname = request.form.get('surname')
        group = request.form.get('group')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            taken_id = User.query.filter_by(email=email).first().id
            return Amend.flash(f'''Отображаемое имя занято (см. профиль <a href="{url_for('profile', user_id=taken_id)}">{User.query.filter_by(email=email).first().username}</a>).''', 'warning', url_for('add_user'))
        elif User.query.filter_by(username=username).first():
            taken_id = User.query.filter_by(username=username).first().id
            return Amend.flash(f'''Имейл занят (см. <a href="{url_for('profile', user_id=taken_id)}">профиль</a>).''', 'warning', url_for('add_user'))
        user = User(username=username,
                    email=email,
                    password=password,
                    firstname=firstname,
                    surname=surname,
                    datetime=Check.time())
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        group = Group(id=user_id,
                      group=group)
        db.session.add(group)
        db.session.add(Role_assignment(id=user_id))
        db.session.add(Email(user_id=user_id))
        db.session.commit()
        token = URLSafeSerializer(app.config["SECRET_KEY"], salt='confirm_email').dumps((user_id, email))
        Emails.send(about='Подтверждение имейла',
                    what=f'''<p>Для вас создан профиль на сайте курса фонетики и фонологии.</p><p>Ссылка для подтверждения имейла – <b><a href="{url_for('mail', token=token, _external=True)}">{url_for('mail', token=token, _external=True)}</a></b>.</p><p>Пароль для входа: <b>{password}</b>.</p><p>Если это письмо пришло вам по ошибке, проигнорируйте его.</p>''',
                    emails=email)
        return Amend.flash('Профиль создан.', 'success',
                           url_for('profiles'))
