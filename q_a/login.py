from q_a import app
from flask import request, render_template, redirect, \
    url_for, session, flash, Markup
from q_a.models import db, User
from q_a.supplement import Emails, Amend
from itsdangerous import URLSafeTimedSerializer, exc

@app.route('/auth', methods=['POST', 'GET'])
@app.route('/auth/<string:token>', methods=['POST', 'GET'])
def login(token=None):
    if request.method == 'GET':
        if token:
            try:
                email, password = URLSafeTimedSerializer(app.config['SECRET_KEY'],
                                                         salt='recover_password').loads(token,
                                                                                        max_age=3600)
            except exc.SignatureExpired:
                flash('Ссылка устарела.',
                      'alert alert-danger')
                return redirect(url_for('login'))
            User.query.filter_by(email=email).first().password = password
            db.session.commit()
            return Amend.flash('Пароль изменён.', 'success', url_for('login'))
        if session.get('user'):
            session.clear()
        return render_template('login.html')
    elif request.method == 'POST':
        login = request.form.get('login')
        if request.form.get('new_password'):
            email = request.form.get('email')
            if User.query.filter_by(email=email).first():
                token = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='recover_password').dumps(
                    [email, request.form.get('new_password')])
                Emails.send('Восстановление пароля',
                           f'''<p>Здравствуйте!</p>
<p>Если вы запрашивали изменение пароля, перейдите по ссылке:
<a href="{url_for('login', token=token, _external=True)}">{url_for('login', token=token, _external=True)}</a>.</p>
<p>Если это письмо пришло по ошибке, проигнорируйте его.</p>''',
                           email
                           )
                flash(Markup('Следуйте инструкциям, отправленным на имейл.'),
                      'alert alert-warning')
                return redirect(url_for('login'))
            else:
                flash(Markup('Профиля с таким имейлом не существует.'),
                      'alert alert-danger')
                return redirect(url_for('login'))
        password = request.form.get('password')
        if '@' in login and User.query.filter_by(email=login).first() and password == User.query.filter_by(
                email=login).first().password:
            session['user'] = User.query.filter_by(email=login).first().username
            session['user_id'] = User.query.filter_by(email=login).first().id
            session['status'] = User.query.filter_by(email=login).first().role.role
            flash(Markup(f'''Вы успешно вошли как {session.get('user')}!'''),
                  'alert alert-success')
        elif User.query.filter_by(username=login).first() and password == User.query.filter_by(
                username=login).first().password:
            session['user'] = User.query.filter_by(username=login).first().username
            session['user_id'] = User.query.filter_by(username=login).first().id
            session['status'] = User.query.filter_by(username=login).first().role.role
            flash(Markup(f'''Вы успешно вошли как {session.get('user')}!'''),
                  'alert alert-success')
        else:
            flash(Markup(
                'Пользователя с указанными данными не существует.<br>Если вы зарегистрированы, перепроверьте логин и пароль.'),
                  'alert alert-danger')
            return redirect(url_for('login'))
        return redirect(url_for('main'))
