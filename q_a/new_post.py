from q_a import app
from flask import request, render_template, \
    url_for, session
from q_a.supplement import Check, Amend
from q_a.models import db, Post, Tags

@app.route('/new/post', methods=['POST', 'GET'])
def create_post():
    Check.update()
    if not session.get('user_id'):
        return Check.login()
    if session.get('status') != 2:
        return Check.status()
    if request.method == 'GET':
        return render_template('new_post.html',
                               Tags=Tags)
    elif request.method == 'POST':
        text = request.form.get('text')
        title = request.form.get('title')
        tag_id = request.form.get('tag')
        user_id = session.get('user_id')
        post = Post(text=text,
                    tag=tag_id,
                    user_id=user_id,
                    datetime=Check.time(),
                    title=title)
        db.session.add(post)
        db.session.commit()
        return Amend.flash('Пост опубликован.', 'success', url_for('main'))