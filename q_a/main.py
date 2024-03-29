from q_a import app
from flask import render_template, Markup, request, url_for, redirect, session
from q_a.models import Post, Tags, db
from q_a.supplement import Amend, Check

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:page>', methods=['GET', 'POST'])
def main(page=1):
    Check.update()
    if request.method == 'GET':
        page_of_news = Post.query.filter(Post.tag != 3).order_by(Post.datetime.desc()).paginate(page, 5)
        news = page_of_news.items
        return render_template('main.html',
                               items=page_of_news,
                               Amend=Amend,
                               Markup=Markup,
                               Tags=Tags,
                               posts=news)
    elif request.method == 'POST':
        if request.form.get('parameter'):
            if request.form.get('parameter'):
                news = Post.query.filter_by(tag=int(request.form.get('parameter'))).filter(Post.tag != 3).order_by(Post.datetime.desc()).all()
            else:
                news = Post.query.filter(Post.tag != 3).order_by(Post.datetime.desc()).all()
            return render_template('main.html',
                                   items=None,
                                   Amend=Amend,
                                   Markup=Markup,
                                   Tags=Tags,
                                   posts=news,
                                   current=int(request.form.get('parameter')))
        if request.form.get('delete_post') and session.get('status') == 2:
            db.session.delete(Post.query.get(request.form.get('delete_post')))
            db.session.commit()
            return Amend.flash('Пост удалён.', 'success', url_for('main'))
        elif request.form.get('edit_post') and session.get('status') == 2:
            return redirect(url_for('edit_post', post_id=request.form.get('edit_post')))
        return Check.status()
