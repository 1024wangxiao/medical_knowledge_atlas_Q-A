

##初始化,全局变量


from flask import Flask
import os



app=Flask(__name__)

app.config.from_pyfile("config/base_setting.py")
if "ops_config" in os.environ:
    app.config.from_pyfile("config/%s_setting.py"%(os.environ["ops_config"]))

