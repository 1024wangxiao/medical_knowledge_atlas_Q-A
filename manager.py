

##项目启动
from application import app
from www import *


if __name__=='__main__':
    # app.config['JSON_AS_ASCII'] = False
    app.run("0.0.0.0")
