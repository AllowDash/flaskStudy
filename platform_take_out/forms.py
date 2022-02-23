from flask import Flask
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, FileField, PasswordField, SubmitField, SelectField, EmailField, TelField, TextAreaField
from wtforms.validators import DataRequired, Email
import config

app = Flask(__name__)
app.config.from_object(config)


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired(), Email(message="Please input valid email")])
    tel = TelField(label='电话号码：', validators=[DataRequired(), ])
    address = StringField(label='店面地址：', validators=[DataRequired(), ])
    submit = SubmitField('submit')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('submit')


class ProfileForm(FlaskForm):
    photo = FileField(label='image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'],  'Images only!'),
    ])
    gender = SelectField(label='性别：', choices=[(1, '男'), (2, '女'), (3, '/')], default=3,
                         coerce=int, validators=[DataRequired(), ])
    tel = TelField(label='电话号码：', validators=[DataRequired(), ])
    address = StringField(label='住址：', validators=[DataRequired(), ])
    tag = StringField(label='标签：', validators=[DataRequired(), ])
    submit = SubmitField('提交')


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码！")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！",
        }
    )
    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary",
        }
    )


class ItemForm(FlaskForm):
    picture = FileField(label='物品图片', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!'),
    ])
    name = StringField('物品名', validators=[DataRequired()])
    price = StringField('价格', validators=[DataRequired()])
    description = TextAreaField('物品描述', validators=[DataRequired()])
    submit = SubmitField('提交')
