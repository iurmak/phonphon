from q_a import app
from flask import render_template, Markup
from q_a.models import Question
from q_a.supplement import Amend, Check

@app.route('/', methods=['GET', 'POST'])
@app.route('/questions/<int:page>', methods=['GET', 'POST'])
def questions(page=1):
    Check.update()
    page_of_questions = Question.query.order_by(Question.is_pinned.desc()).order_by(Question.datetime.desc()).paginate(page, 10)
    questions = page_of_questions.items
    answerers = dict()
    for question in questions:
        answerers.update({question.question_id: [answer.answerer.role.role for answer in question.answers.filter_by(question_id=question.question_id).all()]})
    return render_template('questions.html',
                           questions=questions,
                           items=page_of_questions,
                           Amend=Amend,
                           Markup=Markup,
                           answerers=answerers)
