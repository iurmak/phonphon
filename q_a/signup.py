from q_a import app
from flask import request, render_template, redirect, \
    url_for, flash, session
from q_a.models import db, User, Group, Role_assignment, Email
from q_a.supplement import Emails
from q_a.supplement import Amend, Check
from itsdangerous import URLSafeSerializer
from re import sub


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        if session.get('user'):
            return Amend.flash(f"Вы уже вошли как {session.get('user')}.", 'warning', url_for('questions'))
        return render_template('signup.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        username = sub(r'[^А-ЯЁа-яё\w_]', '', request.form.get('username'))
        firstname = request.form.get('firstname')
        surname = request.form.get('surname')
        group = request.form.get('group')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            return Amend.flash(f'''Отображаемое имя занято.''', 'warning', url_for('add_user'))
        elif User.query.filter_by(username=username).first():
            return Amend.flash(f'''Имейл занят.''', 'warning', url_for('add_user'))

            return redirect(url_for('signup'))
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
                    what=f'''<p>Вы зарегистрировались на сайте курса фонетики и фонологии.</p><p>Ссылка для подтверждения имейла – <b><a href="{url_for('notification', token=token, _external=True)}">{url_for('notification', token=token, _external=True)}</a></b>.</p>''',
                    emails=email)
        return Amend.flash('Вы успешно зарегистрировались. Войдите в свой профиль и проверьте почту.', 'success',
                           url_for('login'))
