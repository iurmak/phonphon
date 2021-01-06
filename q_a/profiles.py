from q_a import app
from flask import render_template, session, request, url_for
from q_a.models import User, Email, Group
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
        if request.form.get('query'):
            if request.form.get('parameter') == 'ID':
                try:
                    page_of_profiles = User.query.filter_by(id=int(request.form.get('query'))).order_by(User.id.desc()).paginate(page, 20)
                    profiles = page_of_profiles.items
                    for n in range(len(profiles)):
                        profiles[n].username = Amend.username(profiles[n].username)
                except:
                    return Amend.flash('Введите число.', 'danger', url_for('profiles'))
            elif request.form.get('parameter') == 'group':
                try:
                    users = [user.id for user in Group.query.all() if user.group == int(request.form.get('query'))]
                    page_of_profiles = User.query.filter(User.id.in_(users)).order_by(User.id.desc()).paginate(page, 20)
                    profiles = page_of_profiles.items
                    for n in range(len(profiles)):
                        profiles[n].username = Amend.username(profiles[n].username)
                except:
                    return Amend.flash('Введите число.', 'danger', url_for('profiles'))
            elif request.form.get('parameter') == 'username':
                page_of_profiles = User.query.filter_by(username=request.form.get('query')).order_by(User.id.desc()).paginate(page, 20)
                profiles = page_of_profiles.items
                for n in range(len(profiles)):
                    profiles[n].username = Amend.username(profiles[n].username)
            elif request.form.get('parameter') == 'firstname':
                page_of_profiles = User.query.filter_by(firstname=request.form.get('query')).order_by(User.id.desc()).paginate(page, 20)
                profiles = page_of_profiles.items
                for n in range(len(profiles)):
                    profiles[n].username = Amend.username(profiles[n].username)
            elif request.form.get('parameter') == 'surname':
                page_of_profiles = User.query.filter_by(surname=request.form.get('query')).order_by(User.id.desc()).paginate(page, 20)
                profiles = page_of_profiles.items
                for n in range(len(profiles)):
                    profiles[n].username = Amend.username(profiles[n].username)
            elif request.form.get('parameter') == 'email':
                page_of_profiles = User.query.filter_by(email=request.form.get('query')).order_by(User.id.desc()).paginate(page, 20)
                profiles = page_of_profiles.items
                for n in range(len(profiles)):
                    profiles[n].username = Amend.username(profiles[n].username)
            return render_template('profiles.html',
                                   profiles=profiles,
                                   items=page_of_profiles,
                                   Email=Email)
        return Amend.flash('Введите поисковый запрос.', 'danger', url_for('profiles'))
