

from application import app
from controllers.index import index_page
from controllers.member import member_page
# from controllers.app import app_page
from flask_debugtoolbar import DebugToolbarExtension
toolbar=DebugToolbarExtension(app)




"""
拦截器处理和错误处理器
"""
from interceptors.Auth import *
from interceptors.errorHandler import *




"""
路由注册
"""
app.register_blueprint(index_page,url_prefix='/')
app.register_blueprint(member_page,url_prefix='/member')
# app.register_blueprint(app_page,url_prefix='/app')


"""
模板函数
"""

from common.libs.UrlManager import UrlManager
app.add_template_global(UrlManager.buildStaticUrl,"buildStaticUrl")
app.add_template_global(UrlManager.buildUrl,"buildUrl")