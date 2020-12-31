from q_a.models import db, Email, User, Subscription, Question, Log
from q_a.supplement import Check, Amend, Emails
from flask import session, render_template, request, url_for
from q_a import app
from itsdangerous import URLSafeSerializer

@app.route('/notifications', methods=['GET', 'POST'])
@app.route('/mail/<string:token>', methods=['GET', 'POST'])
@app.route('/mail/once_again/<int:user_id>', methods=['GET'])
def notification(token=None, user_id=None):
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
        return render_template('notifications.html',
                               Email=Email,
                               Subscription=Subscription,
                               Question=Question)
    if request.method == 'POST':
        if request.form.get('new_assignments'):
            Email.query.filter_by(user_id=session.get('user_id')).update({'new_assignments': True})
        else:
            Email.query.filter_by(user_id=session.get('user_id')).update({'new_assignments': False})
        if request.form.get('new_mentions'):
            Email.query.filter_by(user_id=session.get('user_id')).update({'new_mentions': True})
        else:
            Email.query.filter_by(user_id=session.get('user_id')).update({'new_mentions': False})
        if len(list(request.form.items())) > 2:
            for question in list(request.form.items())[2:]:
                question_id = int(question[0])
                user_id = session.get('user_id')
                log = Log(actor_id=user_id,
                          target_id=question_id,
                          action_id=5,
                          result_url=url_for('question', question_id=question_id, _external=True)
                          )
                db.session.add(log)
                db.session.commit()
                db.session.delete(Subscription.query.filter_by(
                    user_id=log.actor_id,
                    question_id=question_id
                ).first())
        db.session.commit()
        return Amend.flash('Настройки имейл-уведомлений обновлены..', 'success', url_for('notification'))