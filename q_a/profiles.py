from q_a import app
from flask import render_template, session, request
from q_a.models import User, Email
from q_a.supplement import Amend, Check

@app.route('/profiles', methods=['GET', 'POST'])
@app.route('/profiles/<int:page>', methods=['GET', 'POST'])
def profiles(page=1):
    Check.update()
    if not session.get('user'):
        return Check.login()
    if session.get('status') != 2:
        return Check.status()
    if request.method == 'GET':
        page_of_profiles = User.query.order_by(User.id.desc()).paginate(page, 20)
        profiles = page_of_profiles.items
        for n in range(len(profiles)):
            profiles[n].username = Amend.username(profiles[n].username)
        return render_template('profiles.html',
                               profiles=profiles,
                               items=page_of_profiles,
                               Email=Email)
    elif request.method == 'POST':
        page_of_profiles = User.query.order_by(User.id.desc()).paginate(page, 20)
        profiles = page_of_profiles.items
        for n in range(len(profiles)):
            profiles[n].username = Amend.username(profiles[n].username)
        return render_template('profiles.html',
                               profiles=profiles,
                               items=page_of_profiles,
                               Email=Email)
