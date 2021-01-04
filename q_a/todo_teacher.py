from q_a import app
from flask import render_template, session, Markup, url_for
from q_a.models import Assignment, Handed_assignment
from q_a.supplement import Amend, Check

@app.route('/todo/check/', methods=['POST', 'GET'])
@app.route('/todo/check/page/<int:page>', methods=['GET'])
def todo_teacher(page=1):
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if session.get('status') == 2:
        try:
            page_of_assignments = Handed_assignment.query.filter(Handed_assignment.is_checked == 0, Handed_assignment.status_id.in_([2, 3]), Handed_assignment.grade == None).order_by(Handed_assignment.datetime.desc()).paginate(page, 10)
        except:
            return Check.page(url_for('todo_teacher'))
        assignments = page_of_assignments.items
        for n in range(len(assignments)):
            assignments[n].assignment.title = Amend.md(assignments[n].assignment.title)
            if assignments[n].assignment.deadline and assignments[n].assignment.deadline != 'нет':
                assignments[n].assignment.deadline = Amend.datetime(assignments[n].assignment.deadline)
            else:
                assignments[n].assignment.deadline = 'нет'
        return render_template('todo_teacher.html',
                               assignments=assignments,
                               items=page_of_assignments,
                               Amend=Amend)
