from application import app
from flask import request,g


@app.before_request
def before_request():
    app.logger.info("--------before_request------------")
    user_info=check_login()
    g.user=None
    if user_info:
        g.user=user_info
    app.logger.info(g.user)
    return



@app.after_request
def after_request(response):
    app.logger.info("--------after_request------------")

    return response


"""
判断用户是否登录
"""
def check_login():
    cookies=request.cookies
    cookie_name=app.config['USER_LOG']
    cookie_reply=app.config['USER_REPLY']
    username_cookie=cookies[cookie_name] if cookie_name in cookies else ""
    reply_cookie=cookies[cookie_reply] if cookie_reply in cookies else ""
    if username_cookie is None:
        return False


    return username_cookie