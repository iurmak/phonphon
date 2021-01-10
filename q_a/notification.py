from q_a.models import db, Email, User, Subscription, Question, Action_types, Ping
from q_a.supplement import Check, Amend, Emails
from flask import session, render_template, request, url_for, redirect
from q_a import app
from itsdangerous import URLSafeSerializer

@app.route('/notifications/<int:page>', methods=['GET', 'POST'])
@app.route('/notifications', methods=['GET', 'POST'])
@app.route('/mail/<string:token>', methods=['GET', 'POST'])
@app.route('/mail/once_again/<int:user_id>', methods=['GET'])
def notification(token=None, user_id=None, page=1):
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if request.method == 'GET':
        if token:
            if URLSafeSerializer(app.config["SECRET_KEY"], salt='confirm_email').loads(token) == [session.get('user_id'), User.query.get(session.get('user_id')).email]:
                Email.query.filter_by(user_id=session.get('user_id')).first().confirmed = True
                db.session.commit()
                return Amend.flash('Имейл подтверждён.', 'success', url_for('profile'))
            else:
                return Amend.flash('Произошла ошибка. Проверьте, что подтверждаемый имейл принадлежит профилю, в который вы вошли.', 'danger', url_for('profile'))
        elif user_id:
            new_token = URLSafeSerializer(app.config["SECRET_KEY"], salt='confirm_email').dumps((user_id, User.query.get(user_id).email))
            Emails.send(about='Подтверждение имейла',
                        what=f'''<p>Вы зарегистрировались на сайте курса фонетики и фонологии.</p><p>Ссылка для подтверждения имейла – <b><a href="{url_for('notification', token=new_token, _external=True)}">{url_for('notification', token=new_token, _external=True)}</a></b>.</p>''',
                        emails=User.query.get(user_id).email)
            return Amend.flash('Письмо отправлено.', 'success', url_for('notification'))
        page_of_notifications = Ping.query.filter_by(target_id=session.get('user_id')).order_by(Ping.datetime.desc()).paginate(page, 10)
        notifications = page_of_notifications.items
        return render_template('notifications.html',
                               Email=Email,
                               Subscription=Subscription,
                               Question=Question,
                               Check=Check,
                               Amend=Amend,
                               notifications=notifications,
                               items=page_of_notifications,
                               Action_types=Action_types)
    if request.method == 'POST':
        print(list(request.form.items()))
        if request.form.get('email_settings'):
            if request.form.get('new_mentions'):
                Email.query.filter_by(user_id=session.get('user_id')).update({'new_mentions': True})
            else:
                Email.query.filter_by(user_id=session.get('user_id')).update({'new_mentions': False})
            if request.form.get('new_answers'):
                Email.query.filter_by(user_id=session.get('user_id')).update({'new_answers': True})
            else:
                Email.query.filter_by(user_id=session.get('user_id')).update({'new_answers': False})
            if request.form.get('assignments'):
                Email.query.filter_by(user_id=session.get('user_id')).update({'assignments': True})
            else:
                Email.query.filter_by(user_id=session.get('user_id')).update({'assignments': False})
            for question in list(request.form.items()):
                if not question[0].startswith('e') and not question[0].startswith('n'):
                    question_id = int(question[0])
                    user_id = session.get('user_id')
                    db.session.delete(Subscription.query.filter_by(
                        user_id=user_id,
                        question_id=question_id
                    ).first())
            db.session.commit()
            return Amend.flash('Настройки имейл-уведомлений обновлены.', 'success', url_for('notification'))
        if request.form.get('url'):
            return redirect(request.form.get('url'))
        for notification in request.form.items():
            id = notification[0]
            Ping.query.filter_by(ping_id=int(id)).update({'seen': True})
            db.session.commit()
        return Amend.flash('Уведомление удалено.', 'success', url_for('notification'))