

# FlaskPlatform

用Flask构建一个外卖平台网站。

仅是本人学习所写，多有不足。

## 本项目采用的技术

* 使用整型、字符串型路由转换器；
* post、get请求、上传文件、session；
* 模板自定义转义、定义全局上下文处理器、Jinja2语法等；
* 使用Flask-wtf定义表单模型、字段类型、字段验证、视图处理表单、模板使用表单；
* Falsk-sqlalchemy定义数据库模型、添加数据、修改、查询；
* 蓝图优化项目结构，实现网站前台的业务逻辑；

**已完成的功能：**

1. 用户

> 注册、登录、注销
>
> 修改各类资料，头像上传
>
> 修改密码
>
> 用户间可以相互关注

2. 商家

> 上传物品信息，包括物品图片
>
> 商家标签分类

目前所遇到未解决的问题：用户的登录处理中，*session*和g对象在将数据从一个视图传到另一个视图的过程中会丢失，但找到的回答是数据内存过大，但所传递的只是一个小小的用户名字符串。<br/>而在商家的操作中无此问题。

## 数据库设计

数据库是开发的重点。

> 目前有以下几个表：

* 用户表（user）
* 关注表（follow）
* 商家表（merchant）
* 标签表（tag）
* 物品表（item）
* 评论（comment）

其中的关系：

| 用户表（user） |                      |
| -------------- | -------------------- |
| username       | 昵称，字符串型，主键 |
| password       | 密码，字符串型       |
| email          | 邮箱，字符串型       |
| head           | 头像，字符串型       |
| tel            | 手机号码，字符串型   |
| gender         | 性别，字符串型       |
| address        | 地址，字符串型       |

| 关注表（follow） |                            |
| ---------------- | -------------------------- |
| id               | 编号，整型，主键，自动递增 |
| folloewd         | 被关注者，字符串型         |
| follower         | 关注者，字符串型           |
| activation       | 状态，布尔型               |

| 商家表（merchant） |                      |
| ------------------ | -------------------- |
| username           | 昵称，字符串型，主键 |
| password           | 密码，字符串型       |
| email              | 邮箱，字符串型       |
| head               | 头像，字符串型       |
| tel                | 手机号码，字符串型   |
| address            | 地址，字符串型       |
| tag_id             | 标签id，整型，外键   |

| 标签表（tag） |                                |
| ------------- | ------------------------------ |
| tag_id        | 标签编号，整型，主键，自动递增 |
| name          | 标签名，字符串型               |

| 物品表（item） |                            |
| -------------- | -------------------------- |
| id             | 编号，整型，主键，自动递增 |
| name           | 物品名，字符串型           |
| price          | 物品价格，字符串型         |
| description    | 物品描述，字符串型         |
| picture        | 物品图片，字符串型         |
| username       | 所属商家，字符串型，外键   |

| 评论表（comment） |                            |
| ----------------- | -------------------------- |
| id                | 编号，整型，主键，自动递增 |
| comment           | 内容，字符串型             |
| user              | 发起者，字符串型           |
| merchant          | 被评论者，字符串型，外键   |



> 运行本项目

1. 用pycharm搭建好需要的环境，同时安装好mysql。

2. 需在MySQL中建立mydatabase数据库

3. 运行mysql数据库，在`config.py`里面配置数据库账号和密码

4. 先运行models.py进行表格创建

5. 再运行`__init__.py`即可