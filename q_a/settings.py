from q_a import app
from flask import render_template, session, request, url_for
from q_a.models import db, Assignment_types, Tags
from q_a.supplement import Amend, Check

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    Check.update()
    if not session.get('user'):
        return Check.login()
    if session.get('status') != 2:
        return Check.status()
    if request.method == 'GET':
        return render_template('settings.html',
                               Tags=Tags,
                               Assignment_types=Assignment_types)
    elif request.method == 'POST':
        tags = request.form.get('tags').split('/')
        types = request.form.get('assignments').split('/')
        existing_tags = [tag.text for tag in Tags.query.all()]
        existing_types = [type.text for type in Assignment_types.query.all()]
        for tag in tags:
            if tag:
                if tag not in existing_tags:
                    db.session.add(Tags(text=tag))
        for type in types:
            if type not in existing_types:
                if type:
                    db.session.add(Assignment_types(text=type))
        db.session.commit()
        return Amend.flash('Информация обновлена.', 'success',
                           url_for('settings'))
