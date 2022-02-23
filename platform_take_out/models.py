from platform_take_out import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(120))
    head = db.Column(db.String(120))
    gender = db.Column(db.String(12))
    tel = db.Column(db.String(80), unique=True)
    address = db.Column(db.String(120))

    def __init__(self, username, email, password, head="default.png", gender=None, tel=None, address=None):
        self.username = username
        self.email = email
        self.password = password
        self.head = head
        self.gender = gender
        self.tel = tel
        self.address = address
        User.usertype = 'user'

    def __repr__(self):
        return '<User %r>' % self.username

    def check_pwd(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    followed = db.Column(db.String(80))
    follower = db.Column(db.String(80))
    activation = db.Column(db.Boolean())

    def __init__(self, followed, follower, activation):
        self.followed = followed
        self.follower = follower
        self.activation = activation

    def __repr__(self):
        return '<Follow>'


class Merchant(db.Model):
    # 商家必备属性
    username = db.Column(db.String(80), primary_key=True)
    shop_name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    email = db.Column(db.String(120))
    tel = db.Column(db.String(80), unique=True)
    address = db.Column(db.String(120))
    # 可选属性
    head = db.Column(db.String(120))
    # 标签，关联商家与标签
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.tag_id'))
    tag = db.relationship('Tag',
                          backref=db.backref('merchants', lazy='dynamic'))

    def __init__(self, username, email, password, tag=None, tel=None, address=None, head="default.png"):
        self.username = username
        self.shop_name = username
        self.email = email
        self.password = password
        self.head = head
        self.tel = tel
        self.address = address
        Merchant.usertype = 'merchant'
        self.tag = tag

    def __repr__(self):
        return '<Merchant %r>' % self.username

    def check_pwd(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)


# 物品
class Item(db.Model):
    # 物品的id，名字，描述，图片，所属商家
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    picture = db.Column(db.String(50))
    username = db.Column(db.String(80), db.ForeignKey('merchant.username'))
    # 关联物品与商家
    merchant = db.relationship('Merchant',
                               backref=db.backref('items', lazy='dynamic'))

    def __init__(self, name, price, description, username, picture='default.png'):
        self.name = name
        self.price = price
        self.description = description
        self.picture = picture
        self.username = username

    def __repr__(self):
        return '<Item %r>' % self.name


class Comment(db.Model):
    # 评论的id，文字内容，被评论者，发起者
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    user = db.Column(db.String(50))
    merchant = db.Column(db.String(80), db.ForeignKey('merchant.username'))

    def __init__(self, name, user, merchant):
        self.name = name
        self.username = user
        self.merchant = merchant

    def __repr__(self):
        return '<Comment %r>' % self.name


# 标签
class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 标题

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag %r>" % self.name

# tag = Tag("breakfast")
# merchant = Merchant("mgy","123456","123456",tag)
# 使用商家标签分类
# tag.merchants.all()

# 可直接创建所有以上不存在的表格：
db.create_all()
