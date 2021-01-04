from q_a import app
from flask import render_template, Markup
from q_a.models import Post, Tags
from q_a.supplement import Amend, Check

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:page>', methods=['GET', 'POST'])
def main(page=1):
    Check.update()
    page_of_news = Post.query.order_by(Post.datetime.desc()).paginate(page, 10)
    news = page_of_news.items
    return render_template('main.html',
                           items=page_of_news,
                           Amend=Amend,
                           Markup=Markup,
                           Tags=Tags,
                           posts=news)
