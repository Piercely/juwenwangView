
from flask import Flask, render_template
import pymysql
from model.forms import SearchForm
from flask import request
import useful_functions
import spider_modul
from flask import render_template, flash
import json
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask import make_response

from flask import Flask, session, redirect, url_for, escape, request

from news_model.news import news_bp

# 这里对数据库内容进行提取
# spider_modul.run()
datalist = useful_functions.get_datalist()
# datalist2 = useful_functions.get_datalist2()
# datalist_reverse = datalist
# datalist_reverse.reverse()
# 这里分析数据库内容，提炼出数据库信息，并对文本内容分词
datainfo1, string = useful_functions.get_datalist_info(datalist)

# 计算 topK=8 的词汇对应的词频
words, weights = useful_functions.get_word_weights(string, topK=8)

app = Flask(__name__)


app.register_blueprint(news_bp)

app.config["SECRET_KEY"] = "12345678"


# 首页重定位
@app.route('/index')
def home_page():
    return index()


@app.route('/temp')
def temp_page():
    return index()


@app.route('/')
def index():
    global weights
    global words
    global data_info
    print(words, weights)
    data_info = datainfo1
    return render_template("index.html", news_info=data_info)


# 登录页
@app.route('/denglu', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid username or password. Please try again!'
        else:

            #闪现
            flash('You were successfully logged in')
            session['username'] = request.form['username']
            return redirect(url_for('index.html'))

    return render_template('login.html', error=error)


# 注册页
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template("register_1.html")


# 退出登录
@app.route('/logout')
def logout():
    # remove the username from the session if it is there

    session.pop('username', None)
    return redirect(url_for('index'))


# 新闻缩略页
#源
@app.route('/news')
def news_page():
    return render_template("news.html",news=datalist)

#第二个
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

# 缓存
cache = Cache(app,  config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 10})

@app.route('/news2')
@cache.cached()
def news2():
    sql = "select `data`, `data_type`, `name`, `created` from hotrows " \
          "where id in (select max(id) from hotrows group by data_type)"
    rows = db.engine.execute(sql)
    results = []
    for row in rows:
        results.append({
            'data': json.loads(row.data),
            'data_type': row.data_type,
            'name': row.name,
            'created': row.created.strftime("%Y-%m-%d %H:%M:%S")
        })
        # print(row);
    return render_template('news2.html', results=results)

@app.route('/api')
@cache.cached()
def index_api():
    rows = db.engine.execute("select * from hotrows")
    results = []
    for row in rows:
        results.append({
            'data': json.loads(row.data),
            'data_type': row.data_type,
            'name': row.name,
            'created': row.created.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(results)


# 基于词频绘制的词云
@app.route('/word')
def word_page():
    return render_template("word.html", news_info=data_info)



# 基于词频绘制的词云
@app.route('/data_analysis')
def data_analysis():
    return render_template("data_analysis_index.html")


# 基于词频绘制的词云
@app.route('/analysis_index')
def analysis_index():
    return render_template("analysis_index.html")



# 链接到我的个人主页
@app.route('/team')
def team_page():
    return render_template("team.html")


# 数据库文本信息分析，topK8的词语及频率，暂时用的是直方图
@app.route('/analysis')
def analysis_page():
    return render_template("analysis.html", words=words, weights=weights)


# 搜索界面
@app.route('/search')
def search_page():
    form = SearchForm()
    return render_template('search.html', form=form)


# 搜索  搜索结果返回界面，返回时展示数据库中所有内容，包括正文文本
@app.route('/news_result', methods=['POST', 'GET'])
def newsResult_page():
    form = SearchForm()
    search = request.args.get("query")
    search_list = []
    cnn_search = pymysql.connect(host='127.0.0.1', user='root', password='123456', port=3306,
                                 database='news_with_keyword',
                                 charset='utf8')
    cursor_search = cnn_search.cursor()
    sql_search = "select * from guanchazhe where content like '{}'".format('%' + search + '%')
    print(sql_search)
    cursor_search.execute(sql_search)
    for item_search in cursor_search.fetchall():
        search_list.append(item_search)
    cursor_search.close()
    cnn_search.close()
    print(search_list)
    return render_template("news_result.html", form=form, news=search_list)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
