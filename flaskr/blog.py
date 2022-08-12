## --blog用のBlueprintを作成しているファイル-- ##
from crypt import methods
from distutils.log import error
from tkinter import INSERT
from flask import(Blueprint, flash , g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from werkzeug.utils import secure_filename
import flaskr.art_create

bp = Blueprint('blog', __name__)

## blog / のview
@bp.route('/')
def index():
  db = get_db()
  posts = db.execute(
    'SELECT p.id, title, created, author_id, username'
    ' FROM post p JOIN user u ON p.author_id = u.id' 
    ' ORDER BY created DESC'
  ).fetchall() 
  return render_template('blog/index.html', posts=posts)

##--アートを作成する為のview--##
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
  if request.method == 'POST':
    title = request.form['title']
    error = None
    
    if not title: #もしもtitleがなければエラーを表示
      error = 'タイトルは必須です'

    if error is not None: #もしもerrorにNoneデータが入っていれば
      flash(error)
    
    else: #以下、処理記述
      trance_title = flaskr.art_create.deepL(title)
      print(trance_title)
      filepath_list = flaskr.art_create.create_art(trance_title)
      filepath1 = filepath_list[0]
      filepath2 = filepath_list[1]
      filepath3 = filepath_list[2]
      filepath4 = filepath_list[3]
      
      db = get_db()
      db.execute(
        'INSERT INTO post (title, author_id, filepath1, filepath2, filepath3, filepath4)'
        ' VALUES (?, ?, ?, ?, ?, ?)',  ## valuesは #title,body,g.user,filepathを
        (title, g.user['id'], filepath1, filepath2, filepath3, filepath4)
      )
      db.commit()
      return redirect(url_for('blog.index')) #登録したらindexへ

  return render_template('blog/create.html') ##それ以外の場合はcreate.htmlに

#--更新するIDが一致している確認
def get_post(id, check_author=True): ##idが一致してるか確認
  post = get_db().execute(
    'SELECT p.id, title, created, author_id, username, filepath1, filepath2, filepath3, filepath4'
    ' FROM post p JOIN user u ON p.author_id = u.id' ##p.id u.idが一致しているところを探す
    ' WHERE p.id = ?',
    (id,)
  ).fetchone()

  if post is None: ##もしもpost idが無かったらエラーを返す
    abort(404, "IDが {id} のアートは存在しません。".format(id))
  #もしログインユーザーIDと投稿のユーザーIDが一致していなければエラー
  if check_author and post['author_id'] != g.user['id']:
    abort(403)

  return post

 #-View画面
@bp.route('/<int:id>/update', methods=('POST', 'GET'))
@login_required
def update(id):
  post = get_post(id)

  return render_template('blog/update.html', post=post)

 #--削除をする関数--#
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
  get_post(id)
  db = get_db()
  db.execute('DELETE FROM post WHERE id = ?' , (id,))
  db.commit()
  return redirect(url_for('blog.index'))