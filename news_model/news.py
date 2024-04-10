import json

from flask import Blueprint, render_template, Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

# 这里对数据库内容进行提取
# spider_modul.run()
import useful_functions

datalist = useful_functions.get_datalist()
# datalist2 = useful_functions.get_datalist2()
# datalist_reverse = datalist
# datalist_reverse.reverse()
# 这里分析数据库内容，提炼出数据库信息，并对文本内容分词
datainfo1, string = useful_functions.get_datalist_info(datalist)

# 计算 topK=8 的词汇对应的词频
words, weights = useful_functions.get_word_weights(string, topK=8)

app = Flask(__name__)


app.config["SECRET_KEY"] = "12345678"

news_bp =Blueprint('news_bp',__name__,url_prefix='/news',template_folder='template')



# 新闻缩略页
#源
@news_bp.route('/news')
def news_page():
    return render_template("news.html",news=datalist)

#第二个
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

# 缓存
cache = Cache(app,  config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 10})

@news_bp.route('/news2')
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
