from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# 考生信息表
class StudentInfo(db.Model):
    __tablename__ = 'studentinfo'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    examinee_number = db.Column(db.String(30))  # 考生号
    name = db.Column(db.String(100))  # 姓名
    registration_number = db.Column(db.String(30))  # 报考号
    international = db.Column(db.String(10))  # 国际直通车
    id_number = db.Column(db.String(20))  # 身份证号
    birthday = db.Column(db.String(30))  # 出生年月
    sex = db.Column(db.String(10))  # 性别
    height = db.Column(db.Float(10))  # 身高
    high_school = db.Column(db.String(100))  # 高中院校
    major_id = db.Column(db.Integer, db.ForeignKey('major.id'))  # 报考专业外键联系
    major_direction_id = db.Column(db.Integer, db.ForeignKey("majordirection.id"))  # 二级专业外键联系
    view_package = db.Column(db.String(20))  # 面试所在包号
    test_package = db.Column(db.String(20))  # 笔试所在包号
    view_score = db.Column(db.Float(20), default=0)  # 面试成绩
    test_score = db.Column(db.Float(20), default=0)  # 笔试成绩
    final_score = db.Column(db.Float(20), default=0)  # 总成绩
    afford_fee = db.Column(db.String(20))  # 能否负担学费/经济状况
    art_science = db.Column(db.String(20))  # 高中学科类
    household_type = db.Column(db.String(50))  # 户籍类别
    phone_1 = db.Column(db.String(30))  # 联系电话1
    phone_2 = db.Column(db.String(30))  # 联系电话2
    province_id = db.Column(db.Integer, db.ForeignKey("province.id"))  # 省份外键联系
    recipient = db.Column(db.String(100))  # 收件人
    note = db.Column(db.String(200))  # 备注
    post_address = db.Column(db.String(200))  # 邮寄地址
    input = db.Column(db.String(100))  # 输机人
    checker = db.Column(db.String(100))  # 复查人
    input_time = db.Column(db.DateTime)  # 修改时间
    check_time = db.Column(db.DateTime)  # 复查时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 新增时间

    def __repr__(self):
        return '<Studentinfo %r>' % self.examinee_number


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100))
    name = db.Column(db.String(100))
    password = db.Column(db.String(32))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.String(20))  # 是否为管理员
    can_add = db.Column(db.String(20))  # 能否新增学生
    # set_user = db.Column(db.String(20))  # 编辑用户
    # set_mission = db.Column(db.String(20))  # 设置任务
    is_input = db.Column(db.String(20))  # 输机
    is_check = db.Column(db.String(20))  # 复查
    view_log = db.Column(db.String(20))  # 查看输机/复查人
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)

    logs = db.relationship('Log', backref='user')

    def __repr__(self):
        return '<User %r>' % self.id


class Log(db.Model):
    __tablename__ = "log"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属人
    ip = db.Column(db.String(100))  # 操作IP
    reason = db.Column(db.String(600))  # 操作原因
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间

    def __repr__(self):
        return "<Log %r>" % self.id


# 省份列表
class Province(db.Model):
    __tablename__ = 'province'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)  # 省份代码
    name = db.Column(db.String(50))  # 省份名称
    studentinfo = db.relationship("StudentInfo", backref='province')  # 外键关系关联

    def __repr__(self):
        return "<Province %r>" % self.name


# 专业列表
class Major(db.Model):
    __tablename__ = 'major'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    code_major = db.Column(db.Integer)  # 专业代码
    name_major = db.Column(db.String(100))  # 专业名称
    major_direction = db.relationship("MajorDirection", backref='major')  # 外键关系关联
    studentinfo = db.relationship("StudentInfo", backref='major')  # 外键关系关联

    def __repr__(self):
        return "<Major %r>" % self.name_major


# 专业方向
class MajorDirection(db.Model):
    __tablename__ = 'majordirection'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    name_direction = db.Column(db.String(100))  # 专业名称
    major_id = db.Column(db.Integer, db.ForeignKey('major.id'))  # 所属大分类
    studentinfo = db.relationship("StudentInfo", backref='majordirection')  # 外键关系关联

    def __repr__(self):
        return "<MajorDirection %r>" % self.name_direction


# 任务
class Mission(db.Model):
    __tablename__ = 'mission'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(40))  # 任务执行者
    type = db.Column(db.String(60))  # 任务类型
    begin_time = db.Column(db.DateTime, default=datetime.now)  # 开始时间
    end_time = db.Column(db.DateTime)  # 结束时间
    quantity = db.Column(db.Integer)  # 任务量
    completed = db.Column(db.Integer)  # 完成量
    major = db.Column(db.String(100))  # 任务专业
    province = db.Column(db.String(100))  # 任务省份
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Mission %r>" % self.id


class MajorList(db.Model):
    __tablename__ = 'majorlist'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    code_majorlist = db.Column(db.Integer)  # 代码
    name_majorlist = db.Column(db.String(60))  # 名称

    def __repr__(self):
        return "<MajorList %r>" % self.id
