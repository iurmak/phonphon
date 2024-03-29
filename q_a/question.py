from q_a import app
from flask import request, render_template, redirect, \
    url_for, Markup, session
from q_a.models import db, Question, Answer, Ping, Subscription, User, Email
from q_a.supplement import Amend, Check, Emails
from re import sub

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
@app.route('/question/<int:question_id>/<int:page>', methods=['GET', 'POST'])
def question(question_id, page=1):
    Check.update()
    if session.get('user') == f'''Пользователь {session.get('user_id')}''':
        return redirect(url_for('login'))
    if not Question.query.get(question_id):
        return Amend.flash('Такого вопроса не существует.', 'danger', url_for('questions'))
    if request.method == 'GET':
        question = Question.query.get(question_id)
        page_of_answers = Answer.query.filter_by(question_id=question_id).order_by(Answer.datetime.desc()).paginate(page, 4)
        answers = page_of_answers.items
        return render_template('question.html',
                               question=question,
                               answers=answers,
                               items=page_of_answers,
                               Amend=Amend,
                               Subscription=Subscription)
    if request.method == 'POST':
        if request.form.get('subscribe'):
            user_id = session.get('user_id')
            db.session.add(Subscription(
                user_id=user_id,
                question_id=question_id
            ))
            db.session.commit()
            return Amend.flash('Подписка на новые ответы оформлена.', 'success', url_for('question', question_id=question_id))
        elif request.form.get('unsubscribe'):
            user_id = session.get('user_id')
            db.session.delete(Subscription.query.filter_by(
                user_id=user_id,
                question_id=question_id
            ).first())
            db.session.commit()
            return Amend.flash('Подписка на новые ответы отменена.', 'success', url_for('question', question_id=question_id))
        if request.form.get('new_answer'):
            if session.get('user_id'):
                user_id = session.get('user_id')
                url = url_for('question', question_id=question_id, _external=True)
                if request.form.get('anon'):
                    anon = True
                else:
                    anon = False
                text = request.form.get('new_answer')
                if '@' in text:
                    for token in text.split():
                        if token.startswith('@'):
                            username = sub(r'\W', '', token)
                            if User.query.filter_by(username=username).first():
                                db.session.add(Ping(datetime=Check.time(),
                                                    actor_id=user_id,
                                                    action_id=2,
                                                    target_id=User.query.filter_by(username=username).first().id,
                                                    result_url=url
                                ))
                                if Email.query.get(User.query.filter_by(username=username).first().id).confirmed and Email.query.get(User.query.filter_by(username=username).first().id).new_mentions:
                                    Emails.send('Новое упоминание', f'Здравствуйте. Вас упомянули на сайте курса фонетики и фонологии. Вероятно, стоит обратить внимание: {url}.', User.query.filter_by(username=username).first().email)
                db.session.add(Answer(user_id=user_id,
                                      question_id=question_id,
                                      text=text,
                                      is_anon=anon,
                                      datetime=Check.time(),
                                      last_edited=Check.time()))
                for user in Subscription.query.filter_by(question_id=question_id).all():
                    db.session.add(Ping(datetime=Check.time(),
                                        actor_id=user_id,
                                        action_id=1,
                                        target_id=user.user_id,
                                        result_url=url
                                        ))
                    if Email.query.get(user.user_id).confirmed and Email.query.get(user.user_id).new_mentions:
                        Emails.send('Новый ответ',
                                    f'Здравствуйте. Вы отслеживаете вопрос «{Amend.md(Question.query.get(question_id).title)}» на сайте курса фонетики и фонологии. Вероятно, стоит обратить внимание на новый ответ: {url}.',
                                    User.query.get(user.user_id).email)
                db.session.commit()
                return redirect(url_for('question', question_id=question_id))
            else:
                return Check.login()
        elif request.form.get('delete_question'):
            what = question_id
            if not Question.query.get(what):
                return Amend.flash('Такого вопроса не существует.', 'danger', url_for('questions'))
            db.session.delete(Question.query.get(what))
            db.session.commit()
            return Amend.flash('Вопрос удалён.', 'success', url_for('questions'))
        elif request.form.get('delete_answer'):
            what = request.form.get('delete_answer')
            if not Answer.query.get(what):
                return Amend.flash('Такого ответа не существует.', 'danger', url_for('questions'))
            db.session.delete(Answer.query.get(what))
            db.session.commit()
            return Amend.flash('Ответ удалён.', 'success', url_for('question', question_id=question_id))
        elif request.form.get('edit_answer'):
            if not Answer.query.get(request.form.get('edit_answer')):
                return Amend.flash('Такого ответа не существует.', 'danger', url_for('questions'))
            return redirect(url_for('edit',
                                    type='a',
                                    id=request.form.get('edit_answer')))
        elif request.form.get('edit_question'):
            if not Question.query.get(question_id):
                return Amend.flash('Такого вопроса не существует.', 'danger', url_for('questions'))
            return redirect(url_for('edit',
                                    type='q',
                                    id=question_id))
        elif request.form.get('praise_answer'):
            if Answer.query.get(request.form.get('praise_answer')).is_praised:
                Answer.query.filter_by(answer_id=request.form.get('praise_answer')).update({'is_praised': False})
            else:
                Answer.query.filter_by(answer_id=request.form.get('praise_answer')).update({'is_praised': True})
            db.session.commit()
            return redirect(url_for('question',
                                    question_id=question_id))
        elif request.form.get('pin_question'):
            if Question.query.get(question_id).is_pinned:
                Question.query.filter_by(question_id=question_id).update({'is_pinned': False})
            else:
                Question.query.filter_by(question_id=question_id).update({'is_pinned': True})
            db.session.commit()
            return redirect(url_for('question',
                                    question_id=question_id))