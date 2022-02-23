from functools import wraps

import sqlalchemy.exc
from flask import (g, Blueprint, request, redirect, url_for, render_template, session)
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

merchant = Blueprint('merchant', __name__, url_prefix='/merchant')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']


# 登录后默认页
@merchant.route('/index')
def index():
    return render_template("merchant/index.html")


# 用户注册
@merchant.route('/register', methods=['GET', 'POST'])
def register():
    from platform_take_out import forms, db
    from platform_take_out.models import Merchant
    form = forms.RegisterForm(request.form)
    try:
        if form.validate_on_submit():
            merchant_instance = Merchant(username=form.username.data, password=generate_password_hash(form.password.data),
                                     email=form.email.data, tel=form.tel.data, address=form.address.data)
            db.session.add(merchant_instance)
            db.session.commit()
            return redirect(url_for("merchant.login"))
        else:
            try:
                if form.errors['csrf_token'][0] == 'The CSRF tokens do not match.':
                    merchant_instance = Merchant(username=form.username.data,
                                                 password=generate_password_hash(form.password.data),
                                                 email=form.email.data, tel=form.tel.data, address=form.address.data)
                    db.session.add(merchant_instance)
                    db.session.commit()
                    return redirect(url_for("merchant.login"))
            except KeyError:
                print(form.errors)
    except sqlalchemy.exc.IntegrityError:
        return "The shop name or telephone is already registered"
    return render_template("merchant/register.html", form=form)


@merchant.route('/login', methods=['GET', 'POST'])
def login():
    from platform_take_out import forms
    from platform_take_out.models import Merchant
    form = forms.LoginForm(request.form)
    if request.method == 'POST':
        data = form.data
        if form.validate_on_submit():
            merchant_instance = Merchant.query.filter_by(username=data["username"]).first()
            if not merchant_instance.check_pwd(data["password"]):
                return "密码错误！"
            session["merchant_id"] = data["username"]
            return redirect(url_for('merchant.index'))
        elif 'csrf_token' in form.errors:
            merchant_instance = Merchant.query.filter_by(username=data["username"]).first()
            if not merchant_instance.check_pwd(data["password"]):
                return "密码错误！"
            session["merchant_id"] = data["username"]
            return redirect(url_for('merchant.index'))
    if request.method == 'GET':
        return render_template("merchant/login.html", form=form)


# 登录装饰器
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "merchant_id" not in session:
            return redirect(url_for("merchant.login"))
        return f(*args, **kwargs)

    return decorated_function


# 用户注销
@merchant.route("/logout")
@user_login_req
def logout():
    session.clear()
    if "merchant_id" in session:
        print("注销后：", session["merchant_id"])
    g.user = None
    return redirect(url_for("merchant.index"))


@merchant.before_app_request
def load_logged_in_user():
    from platform_take_out.models import Merchant
    merchant_id = session.get('merchant_id')
    if merchant_id is None:
        g.user = None
    else:
        # 得到用户实例
        g.user = Merchant.query.filter_by(username=session["merchant_id"]).first()


# 资料页
@merchant.route('/<string:username>/profile', methods=['GET', 'POST'])
def profile(username):
    from platform_take_out import forms
    from platform_take_out.models import Merchant, db, Follow
    form = forms.ProfileForm(request.form)
    try:
        if username != g.user.username:
            pass
    except AttributeError:
        merchant_instance = Merchant.query.filter_by(username=username).first()
        if not merchant_instance:
            return "无此商家"
        return render_template("merchant/profile_for_other.html", username=username, m_i=merchant_instance)
    if request.method == 'POST' and username == g.user.username:
        merchant_instance = Merchant.query.filter_by(username=g.user.username).first()
        gender = form.data['gender']
        lst = ['男', '女', None]
        merchant_instance.gender = lst[int(gender) - 1]
        tel = form.data['tel']
        merchant_instance.tel = tel
        address = form.data['address']
        merchant_instance.address = address
        db.session.add(merchant_instance)
        db.session.commit()
    elif username != g.user.username:
        merchant_instance = Merchant.query.filter_by(username=username).first()
        if not merchant_instance:
            return "无此商家"
        return render_template("merchant/profile_for_other.html", username=username, m_i=merchant_instance)
    if request.args.get('edit'):
        return render_template('merchant/profile_edit.html', form=form)
    return render_template("merchant/profile_display.html", username=g.user.username, form=form)


# 更换头像处理
@merchant.route('/<string:username>/signature', methods=['GET', 'POST'])
@user_login_req
def signature(username):
    from platform_take_out import forms
    from platform_take_out.models import Merchant, db
    form = forms.ProfileForm(request.files)
    if request.method == 'POST':
        filename = secure_filename(form.photo.data.filename)
        if filename and allowed_file(filename):
            merchant_instance = Merchant.query.filter_by(username=g.user.username).first()
            merchant_instance.head = filename
            db.session.add(merchant_instance)
            db.session.commit()
            form.photo.data.save('D:\\flaskProject\\platform_take_out\\static\\merchant_signature\\' + filename)
            return redirect(url_for('merchant.profile', username=g.user.username))
        elif not allowed_file(filename):
            return "请上传正确格式"
    return render_template("merchant/head.html", username=g.user.username, form=form)


@merchant.route('/<string:username>/tag', methods=['GET', 'POST'])
@user_login_req
def add_tag(username):
    from platform_take_out import forms
    from platform_take_out.models import Merchant, db, Tag
    form = forms.ProfileForm(request.form)
    if request.method == 'POST':
        merchant_instance = Merchant.query.filter_by(username=g.user.username).first()
        tag = Tag.query.filter_by(name=form.data['tag']).first()
        if tag:
            merchant_instance.tag = tag
        else:
            tag = Tag(name=form.data['tag'])
            db.session.add(tag)
            db.session.commit()
            merchant_instance.tag = tag
        db.session.add(merchant_instance)
        db.session.commit()
        return redirect(url_for('merchant.profile', username=g.user.username))
    return render_template("merchant/tag.html", form=form)


@merchant.route('/<string:username>/items', methods=['GET', 'POST'])
@user_login_req
def add_item(username):
    from platform_take_out import forms
    from platform_take_out.models import Item, db
    form = forms.ItemForm(request.form)
    if request.args.get('edit'):
        return render_template("merchant/item_add.html", form=form)
    if request.method == 'POST':
        name = form.data.get('name')
        price = form.data.get('price')
        description = form.data.get('description')
        filename = secure_filename(request.files.get('picture').filename)
        if filename and allowed_file(filename):
            request.files.get('picture').save('D:\\flaskProject\\platform_take_out\\static\\item_img\\' + filename)
        elif not allowed_file(filename):
            return "请上传正确格式"
        item = Item(name=name, price=price, description=description, username=g.user.username, picture=filename)
        db.session.add(item)
        db.session.commit()
    return render_template("merchant/item_display.html")


@merchant.route('/<string:username>/items/<int:item_id>', methods=['GET', 'POST'])
@user_login_req
def update_item(username, item_id):
    from platform_take_out.models import Item, db
    from platform_take_out import forms
    form = forms.ItemForm(request.form)
    item = Item.query.filter_by(id=item_id).first()
    if item.username != g.user.username:
        return "无权限访问其他商家的物品"
    if request.method == 'POST':
        name = form.data.get('name')
        price = form.data.get('price')
        description = form.data.get('description')
        filename = secure_filename(request.files.get('picture').filename)
        if filename and allowed_file(filename):
            request.files.get('picture').save('D:\\flaskProject\\platform_take_out\\static\\item_img\\' + filename)
        elif not allowed_file(filename):
            return "请上传正确格式"
        item.name = name
        item.price = price
        item.description = description
        item.picture = filename
        db.session.add(item)
        db.session.commit()
        return render_template("merchant/item_display.html")
    return render_template("merchant/item_edit.html", form=form, item_id=item_id)


@merchant.route('/merchant_list')
def merchant_list():
    from platform_take_out.models import Merchant
    lst = Merchant.query.filter_by()
    print(lst)
    return render_template("merchant/merchant_list.html", lst=lst)
