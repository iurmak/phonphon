from q_a import app
from flask import request, render_template, redirect, \
    url_for, session
from q_a.supplement import Amend, Check, Emails
from q_a.models import db, Question, Subscription

@app.route('/new/question', methods=['POST', 'GET'])
def create_question():
    Check.update()
    if session.get('user') == f'''Пользователь {session.get('user_id')}''':
        return redirect(url_for('login'))
    if not session.get('user_id'):
        return Check.login()
    if request.method == 'GET':
        return render_template('new_question.html')
    elif request.method == 'POST':
        title = Amend.anti_html(request.form.get('essence'))
        text = Amend.anti_html(request.form.get('question'))
        user_id = session.get('user_id')
        if request.form.get('anon'):
            anon = True
        else:
            anon = False
        question = Question(user_id=user_id,
                            title=title,
                            text=text,
                            is_anon=anon,
                            datetime=Check.time(),
                            last_edited=Check.time())
        db.session.add(question)
        db.session.commit()
        user_id = session.get('user_id')
        db.session.add(Subscription(
            user_id=user_id,
            question_id=question.question_id
        ))
        db.session.commit()
        Emails.send('Новый вопрос на сайте', f'На сайте задали новый вопрос: <a href="{url_for("question", question_id=question.question_id, _external=True)}">{Amend.md(question.title)}</a>. Его содержание:<br><br>{Amend.md(question.text)}', 'iurmak@bk.ru')
        return redirect(url_for('questions'))