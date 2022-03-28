import random,string,hashlib,base64

class UserService():
    ##密码加密
    @staticmethod
    def genPwd(pwd,salt):
        m=hashlib.md5()
        str="%s-%s"%(base64.encodebytes(pwd.encode('utf-8')),salt)
        m.update(str.encode('utf-8'))
        return m.hexdigest()


    ##生成随机加密字符串
    @staticmethod
    def geneSalt(length=16):
        keylist=[random.choice((string.ascii_letters+string.digits)) for i in range(length)]
        return ("".join(keylist))
