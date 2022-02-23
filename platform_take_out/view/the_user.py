from functools import wraps

import sqlalchemy.exc
from flask import (g, Blueprint, request, redirect, url_for, render_template, session)
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

user = Blueprint('user', __name__, url_prefix='/user')


# 登录后默认页
@user.route('/index')
def index():
    return render_template("index.html")


# 用户注册
@user.route('/register', methods=['GET', 'POST'])
def register():
    from platform_take_out import forms, db
    from platform_take_out.models import User
    form = forms.RegisterForm(request.form)
    try:
        if form.validate_on_submit():
            user_instance = User(username=form.username.data, password=generate_password_hash(form.password.data), email=form.email.data)
            db.session.add(user_instance)
            db.session.commit()
            return redirect(url_for("user.login"))
        else:
            try:
                if form.errors['email']:
                    return form.errors['email'][0]
            except KeyError:
                print(form.errors)
    except sqlalchemy.exc.IntegrityError:
        return "The user name is already registered"
    return render_template("register.html", form=form)


# 用户登录
@user.route('/login', methods=['GET', 'POST'])
def login():
    from platform_take_out import forms
    from platform_take_out.models import User
    form = forms.LoginForm(request.form)
    if request.method == "POST":
        data = form.data
        if form.validate_on_submit():
            user_instance = User.query.filter_by(username=data["username"]).first()
            if not user_instance:
                return "此用户名未被注册"
            if not user_instance.check_pwd(data["password"]):
                return "密码错误！"
            session["username"] = data["username"]
            return redirect(url_for('user.index'))
        elif 'csrf_token' in form.errors:
            user_instance = User.query.filter_by(username=data["username"]).first()
            if not user_instance:
                return "此用户名未被注册"
            if not user_instance.check_pwd(data["password"]):
                return "密码错误！"
            session["username"] = data["username"]
            return redirect(url_for('user.index'))
    if request.method == 'GET':
        return render_template("login.html", form=form)


# 请求前载入
@user.before_app_request
def load_logged_in_user():
    from platform_take_out.models import User
    username = session.get("username")
    if username is None:
        g.user = None
    else:
        # 得到用户实例
        g.user = User.query.filter_by(username=session["username"]).first()


# 登录装饰器
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("user.login"))
        return f(*args, **kwargs)

    return decorated_function


# 用户注销
@user.route("/logout")
@user_login_req
def logout():
    session.clear()
    g.user = None
    return redirect(url_for("user.index"))


# 个人资料页
@user.route('/<string:username>/profile', methods=['GET', 'POST'])
@user_login_req
def profile(username):
    from platform_take_out import forms
    from platform_take_out.models import User, db, Follow
    form = forms.ProfileForm(request.form)
    if request.method == 'POST' and username == g.user.username:
        user_instance = User.query.filter_by(username=g.user.username).first()
        gender = form.data['gender']
        lst = ['男', '女', None]
        user_instance.gender = lst[int(gender) - 1]
        tel = form.data['tel']
        user_instance.tel = tel
        address = form.data['address']
        user_instance.address = address
        db.session.add(user_instance)
        db.session.commit()
    elif username != g.user.username:
        user01 = User.query.filter_by(username=username).first()
        if not user01:
            return "该用户不存在"
        status = Follow.query.filter_by(followed=username, follower=g.user.username, activation=True).first()
        reverse = Follow.query.filter_by(followed=g.user.username, follower=username, activation=True).first()
        if status and reverse:
            button = "互相关注"
        elif status:
            button = "已关注"
        else:
            button = "未关注"
        return render_template("profile_for_other.html", username=username, button=button)
    if request.args.get('edit'):
        return render_template('profile_edit.html', form=form)
    return render_template("profile_display.html", username=g.user.username, form=form)


# 更换头像处理
@user.route('/<string:username>/head', methods=['GET', 'POST'])
@user_login_req
def head(username):
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']
    from platform_take_out import forms
    from platform_take_out.models import User, db
    form = forms.ProfileForm(request.files)
    if request.method == 'POST':
        filename = secure_filename(form.photo.data.filename)
        if filename and allowed_file(filename):
            user_instance = User.query.filter_by(username=g.user.username).first()
            user_instance.head = filename
            db.session.add(user_instance)
            db.session.commit()
            form.photo.data.save('D:\\flaskProject\\platform_take_out\\static\\profile_picture\\' + filename)
            return redirect(url_for('user.profile', username=g.user.username))
        elif not allowed_file(filename):
            return "请上传正确格式"
    return render_template("head.html", username=g.user.username, form=form)


# 密码修改处理
@user.route('/<string:username>/reset', methods=['GET', 'POST'])
@user_login_req
def reset(username):
    from platform_take_out import forms
    from platform_take_out.models import User, db
    form = forms.PwdForm(request.form)
    if username != g.user.username:
        return "无此权限"
    if request.method == "POST":
        if form.validate_on_submit():
            old = form.data['old_pwd']
            new = form.data['new_pwd']
            user_instance = User.query.filter_by(username=username).first()
            if not user_instance.check_pwd(old):
                return "旧密码输入错误"
            user_instance.password = generate_password_hash(new)
            db.session.add(user_instance)
            db.session.commit()
            return redirect(url_for("user.profile", username=username))
    return render_template("pwd_reset.html", form=form, username=username)


# 用户关注处理
@user.route('/<string:username>/follow')
@user_login_req
def follow(username):
    from platform_take_out.models import User, db, Follow
    status1 = Follow.query.filter_by(followed=username, follower=g.user.username).first()
    status2 = Follow.query.filter_by(followed=username, follower=g.user.username, activation=True).first()
    # 曾经取关，再次关注
    if status1 and not status2:
        status1.activation = True
        db.session.add(status1)
        db.session.commit()
    # 已经关注，想要取关
    elif status2:
        status2.activation = False
        db.session.add(status2)
        db.session.commit()
    # 没有记录，且没有关注
    else:
        followed = User.query.filter_by(username=username).first().username
        follower = User.query.filter_by(username=g.user.username).first().username
        row = Follow(followed=followed, follower=follower, activation=True)
        db.session.add(row)
        db.session.commit()
    return redirect(url_for("user.profile", username=username))
