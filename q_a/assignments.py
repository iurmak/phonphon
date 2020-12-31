from q_a import app
from flask import render_template, session, Markup, url_for
from q_a.models import Assignment
from q_a.supplement import Amend, Check

@app.route('/assignments', methods=['POST', 'GET'])
@app.route('/assignments/page/<int:page>', methods=['GET'])
def assignments(page=1):
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if session.get('status') != 2:
        return Check.status()
    try:
        page_of_assignments = Assignment.query.order_by(Assignment.assignment_id.desc()).paginate(page, 10)
    except:
        return Check.page(url_for('assignments'))
    assignments = page_of_assignments.items
    for n in range(len(assignments)):
        assignments[n].assigner = Amend.username(assignments[n].author.username)
        assignments[n].assignees = ', '.join(assignments[n].assignees.split()).replace('*', '')
        assignments[n].title = Markup(Amend.md(assignments[n].title))
        if assignments[n].deadline:
            assignments[n].deadline = Amend.datetime(assignments[n].deadline)
        else:
            assignments[n].deadline = 'нет'
    return render_template('assignments.html',
                           assignments=assignments,
                           items=page_of_assignments,
                           Check=Check,
                           Amend=Amend)
