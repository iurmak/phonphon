from q_a import app
from flask import render_template, Markup, request
from q_a.models import Question
from q_a.supplement import Amend, Check
from pymorphy2 import MorphAnalyzer
from re import sub, compile, DOTALL


@app.route('/questions/', methods=['GET', 'POST'])
@app.route('/questions/<int:page>', methods=['GET', 'POST'])
def questions(page=1):
    Check.update()
    if request.method == 'GET':
        page_of_questions = Question.query.order_by(Question.is_pinned.desc()).order_by(Question.last_edited.desc()).paginate(page, 10)
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
    elif request.method == 'POST':
        morph = MorphAnalyzer()
        punct = compile(r'''[^А-ЯЁа-яё]''')
        if request.form.get('parameter') == 'both':
            query = punct.sub('', morph.parse(request.form.get('query'))[0].normal_form.lower())
            page_of_questions = Question.query.all()
            questions = list()
            res = dict()
            for q in page_of_questions:
                res.update({q.question_id: []})
                for token in punct.sub('', q.title).split():
                    res[q.question_id].append(morph.parse(token)[0].normal_form.lower())
                for token in punct.sub('', q.text).split():
                    res[q.question_id].append(morph.parse(token)[0].normal_form.lower())
            for q in res:
                if query in res[q][0]:
                    questions.append(Question.query.get(q))
            answerers = dict()
            for question in questions:
                answerers.update({question.question_id: [answer.answerer.role.role for answer in question.answers.filter_by(
                    question_id=question.question_id).all()]})
            print(res)
        elif request.form.get('parameter') == 'title':
            query = punct.sub('', morph.parse(request.form.get('query'))[0].normal_form.lower())
            page_of_questions = Question.query.all()
            questions = list()
            res = dict()
            for q in page_of_questions:
                res.update({q.question_id: []})
                for token in punct.sub('', q.title).split():
                    res[q.question_id].append(morph.parse(token)[0].normal_form.lower())
            for q in res:
                if query in res[q][0]:
                    questions.append(Question.query.get(q))
            answerers = dict()
            for question in questions:
                answerers.update(
                    {question.question_id: [answer.answerer.role.role for answer in question.answers.filter_by(
                        question_id=question.question_id).all()]})
        return render_template('questions.html',
                               questions=questions,
                               items=None,
                               Amend=Amend,
                               Markup=Markup,
                               answerers=answerers)
