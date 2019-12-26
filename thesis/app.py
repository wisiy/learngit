from datetime import timedelta
from functools import wraps
from stu_forms import StudentForm
from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from sqlalchemy import or_
from decimal import *
import config
from models import db, User, StudentInfo, Province, Mission, Log, MajorDirection, Major, MajorList

app = Flask(__name__, static_url_path='')
app.config.from_object(config)
db.init_app(app)


def checking_login(f):
    """
    定义一个@checking_login登录装饰器，验证登录 ，如果未登录，重定向到‘login’
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def addlog(reason):
    """记录日志"""
    log = Log(
        user_id=session["user_id"],
        ip=request.remote_addr,
        reason=reason
    )
    db.session.add(log)
    db.session.commit()


@app.route('/index')
def hello_world():
    if session:
        session.clear()
    return "<script>alert('Hello You Guys!');location.href='/login/';</script>"


@app.route('/')
@checking_login
def index():
    """
    主页，计算数据量
    """
    user = User.query.count()
    student = StudentInfo.query.count()
    return render_template('index.html', total_user=user, total_student=student)


@app.route('/new/user/register/', methods=['POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        phone = request.form.get('phone')
        password = request.form.get('password')
        pass_confirm = request.form.get('password-confirm')
        user = User.query.filter(User.username == username).first()
        if user:
            flash('该用户名已存在')
        else:
            # 检查两次输入的密码是否相等
            if password != pass_confirm:
                flash('两次密码输入不一致！')
            else:
                # 写入数据库，数据库字段名=表单列名
                user = User(username=username, password=password, phone=phone, name=name)
                db.session.add(user)
                db.session.commit()
                flash('用户注册成功')
    return redirect(url_for('login'))


@app.route('/login/', methods=["GET", "POST"])
def login():
    """登录"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # 获取登录表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username == username).first()
        if not user:
            flash('该用户名不存在！')
            # end = time.time()
            # print(end-start)
            return redirect(url_for('login'))
        elif user.username == username and user.password == password:
            # 记录用户个人数据到session
            session['user_id'] = user.id
            session['username'] = user.username
            session['name'] = user.name
            session['is_admin'] = user.is_admin
            session['add_time'] = user.add_time
            session['is_input'] = user.is_input
            session['is_check'] = user.is_check
            session['can_add'] = user.can_add
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=2)  # session存活时间
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！')
            return redirect(url_for('login'))


@app.route('/log-out/')
@checking_login
def logout():
    """
    清除session，退出
    """
    session.clear()
    return redirect(url_for("login"))


@app.route('/reset/password/', methods=["GET", "POST"])
@checking_login
def reset_password():
    """修改密码"""
    if request.method == 'GET':
        return render_template("reset-password.html")
    else:
        ori_pass = request.form.get("ori-password")  # 原始密码
        new_pass = request.form.get("password")  # 新密码
        confirm = request.form.get("confirm")  # 确认
        user = User.query.filter_by(username=session["username"]).first()
        if ori_pass != user.password:
            flash('原密码不正确！')
            return redirect(url_for("reset_password"))
        elif new_pass != confirm:
            flash('两次输入的密码不一致')
            return redirect(url_for("reset_password"))
        elif new_pass == ori_pass:
            flash('新旧密码不能一样')
            return redirect(url_for("reset_password"))
        else:
            user.password = new_pass
            db.session.add(user)
            db.session.commit()
            session.clear()
            return "<script>alert('密码修改成功');location.href='/login/';</script>"


@app.route('/new/user/', methods=['GET', 'POST'])
@checking_login
def new_user():
    """新增用户"""
    if request.method == 'GET':
        return render_template('new-user.html')
    else:
        # 新增用户获取表单数据
        username = request.form.get('username')
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        password_sure = request.form.get('confirm')
        is_admin = request.form.get('is_admin')
        add_user = request.form.get('add_user')
        can_input = request.form.get('input')
        check = request.form.get('check')
        log = request.form.get('log')
        # 如果用户名被用了，就不能新增
        user = User.query.filter(User.username == username).first()
        if user:
            flash('该用户名已存在')
            return redirect(url_for('new_user'))
        else:
            # 检查两次输入的密码是否相等
            if password != password_sure:
                flash('两次密码输入不一致！')
                return redirect(url_for('new_user'))
            else:
                # 写入数据库，数据库字段名=表单列名
                user = User(username=username, password=password, phone=phone, name=name, is_admin=is_admin,
                            can_add=add_user, is_check=check, is_input=can_input, view_log=log)
                db.session.add(user)
                db.session.commit()
                return "<script>alert('添加成功！');location.href='/new/user/';</script>"


@app.route('/user/list/')
@checking_login
def user_list():
    """用户列表"""
    count = User.query.count()
    # 计算管理员数量
    count_admin = User.query.filter(User.is_admin == '1').count()
    user = User.query.order_by(User.add_time.desc()).all()
    return render_template('user-list.html', users=user, count=count, count_admin=count_admin)


@app.route('/user/detail/<int:uid>', methods=['GET', 'POST'])
@checking_login
def user_detail(uid=None):
    """
    获取用户的详细信息,进行修改
    :param uid: user id
    """
    user = User.query.get_or_404(int(uid))
    if request.method == 'GET':
        return render_template("user-detail.html", user=user)
    else:
        user.is_admin = request.form.get('is_admin')
        user.can_add = request.form.get('add_user')
        user.is_input = request.form.get('input')
        user.is_check = request.form.get('check')
        user.view_log = request.form.get('log')
        user.username = request.form.get('username')
        user.name = request.form.get('name')
        user.phone = request.form.get('phone')
        db.session.add(user)
        db.session.commit()
        return render_template("user-detail.html", user=user)


@app.route('/user/del/<int:udid>')
@checking_login
def user_del(udid=None):
    """
    删除用户
    :param udid: user deleted id
    """
    user = User.query.get_or_404(udid)
    db.session.delete(user)
    db.session.commit()
    flash('用户删除成功')
    return redirect(url_for('user_list'))


@app.route('/mission/setting/', methods=['GET', 'POST'])
@checking_login
def set_mission():
    """设置任务"""
    name = User.query.order_by(User.id.asc()).all()
    province = Province.query.order_by(Province.code.asc()).all()
    mis = Mission.query.order_by(Mission.add_time.asc()).all()
    major = MajorList.query.order_by(MajorList.id.asc()).all()
    if request.method == 'GET':
        return render_template("mission-set.html", name=name, province=province, mis=mis, major=major)
    else:
        import time
        user = request.form.get('name')
        province = request.form.get('province')
        major = request.form.get('major')
        op_type = request.form.get('type')
        quantity = request.form.get('quantity')
        begin_time = time.strftime('%Y-%m-%d %H:%M:%S')
        # 从所有学生信息中检索input和任务完成人进行比对，该任务被删除时，下次任务数量不为0，输机与复查完成量问题
        completed = StudentInfo.query.filter(StudentInfo.input == Mission.user).count()
        mission = Mission(user=user, province=province, major=major, type=op_type, quantity=quantity,
                          begin_time=begin_time, completed=completed)
        db.session.add(mission)
        db.session.commit()
        flash('任务添加成功！')
        return redirect(url_for("set_mission"))


@app.route('/mission/list/')
@checking_login
def mission_list():
    """任务列表"""
    mission = Mission.query.order_by(Mission.add_time.asc()).all()
    count = Mission.query.count()  # 计算任务数量
    return render_template('mission-list.html', mis=mission, count=count)


@app.route('/mission/del/<int:mdid>')
@checking_login
def mission_del(mdid=None):
    """
    删除任务
    :param mdid: mission deleted id
    """
    mis = Mission.query.get_or_404(mdid)
    db.session.delete(mis)
    db.session.commit()
    flash('任务删除成功')
    return redirect(url_for('mission_list'))


@app.route('/mission/reset/<int:mid>', methods=['GET', 'POST'])
@checking_login
def mission_reset(mid=None):
    """
    编辑、修改任务
    :param mid: user mission id
    """
    mis = Mission.query.get_or_404(mid)  # 获取任务
    user = User.query.order_by(User.add_time.asc()).all()  # 获取用户
    province = Province.query.order_by(Province.id.asc()).all()  # 获取省份
    major = MajorList.query.order_by(MajorList.id.asc()).all()  # 获取专业
    if request.method == 'GET':
        return render_template('mission-reset.html', mission=mis, name=user, province=province, major=major)
    else:
        import time
        mis.user = request.form.get('name')
        mis.type = request.form.get('type')
        mis.major = request.form.get("major")
        mis.province = request.form.get('province')
        mis.quantity = request.form.get('quantity')
        mis.begin_time = time.strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(mis)
        db.session.commit()
        flash('修改成功！', 'ok')
        return render_template('mission-reset.html', mission=mis, name=user, province=province, major=major)


@app.route('/mission/self/')
@checking_login
def mission_self():
    """
    用户自己的任务
    """
    mission = Mission.query.filter(Mission.user == session['name']).all()
    if mission is None:
        flash('用户当前没有任务！')
        return render_template('mission-self.html', mis=mission)
    else:
        return render_template('mission-self.html', mis=mission)


@app.route('/student/information/list/', methods=['POST', 'GET'])
@checking_login
def studentinfo_list():
    """查询到的学生信息列表"""
    mis = Mission.query.order_by(Mission.id.asc()).all()
    keywords = request.form.get('keywords', type=str)
    data = StudentInfo.query.filter(
        or_(StudentInfo.examinee_number.like("%" + keywords + "%"),
            StudentInfo.name.like("%" + keywords + "%"),
            StudentInfo.registration_number.like("%" + keywords + "%"),
            StudentInfo.id_number.like("%" + keywords + "%"),
            StudentInfo.id.like("%" + keywords + "%"))
    ).order_by(StudentInfo.add_time.desc()).all()
    count = len(data)
    return render_template("studentinfo-list.html", data=data, count=count, mis=mis)


@app.route('/student/information/details/<int:sid>', methods=['GET', 'POST'])
@checking_login
def student_info(sid=None):
    """
    学生的详细信息，编辑，复查，输机信息，复查信息
    """
    form = StudentForm()
    student = StudentInfo.query.get_or_404(int(sid))
    form.zy.choices = [(v.id, v.name_major) for v in Major.query.all()]
    form.zyfx.choices = [(
        v.id, v.name_direction
    ) for v in MajorDirection.query.filter_by(major_id=student.major.id).all()]
    form.sf.choices = [(v.id, v.name) for v in Province.query.all()]
    if request.method == 'GET':
        form.ksh.data = student.examinee_number  # 考生号
        form.xm.data = student.name  # 报考号
        form.bkh.data = student.registration_number  # 报考号
        form.sfzh.data = student.id_number  # 身份证号
        form.gjztc.data = student.international  # 国际直通车
        form.sr.data = student.birthday  # 生日
        form.xb.data = student.sex  # 性别
        form.sg.data = student.height  # 身高
        form.gzxx.data = student.high_school  # 高中学校
        form.zy.data = student.major_id  # 专业
        form.zyfx.data = student.major_direction_id  # 专业方向
        form.msbh.data = student.view_package  # 面试包号
        form.bsbh.data = student.test_package  # 笔试包号
        form.nffdxf.data = student.afford_fee  # 能否负担学费
        form.wlk.data = student.art_science  # 文理科
        form.hjlx.data = student.household_type  # 户籍类型
        form.dh1.data = student.phone_1  # 电话1
        form.dh2.data = student.phone_2  # 电话2
        form.sf.data = student.province_id  # 省份
        form.sjr.data = student.recipient  # 收件人
        form.bz.data = student.note  # 备注
        form.yjdz.data = student.post_address  # 邮寄地址
    else:
        student.examinee_number = form.data['ksh']
        student.name = form.data['xm']
        student.registration_number = form.data['bkh']
        student.id_number = form.data['sfzh']
        student.international = form.data['gjztc']
        # 如果身份证号满足18位，就从身份证号获取生日
        if len(student.id_number) == 18:
            student.birthday = student.id_number[6:10] + ' - ' + student.id_number[10:12] + ' - ' + student.id_number[12:14]
        else:  # 如果不满足18位，就按照输入的生日来存储
            student.birthday = form.data["sr"]
        student.sex = int(form.data['xb'])
        student.height = form.data['sg']
        student.high_school = form.data['gzxx']
        student.major_id = int(form.data['zy'])
        student.major_direction_id = int(form.data['zyfx'])
        student.view_package = form.data['msbh']
        student.test_package = form.data['bsbh']
        if not request.form.get('mscj'):
            student.view_score = 0
        else:
            student.view_score = Decimal(request.form.get('mscj')).quantize(Decimal('0.00'))
        if not request.form.get('bscj'):
            student.test_score = 0
        else:
            student.test_score = Decimal(request.form.get('bscj')).quantize(Decimal('0.00'))
        if not request.form.get('zcj'):
            student.final_score = 0
        else:
            student.final_score = Decimal(request.form.get('zcj')).quantize(Decimal('0.00'))
        student.afford_fee = int(form.data['nffdxf'])
        student.art_science = int(form.data['wlk'])
        student.household_type = int(form.data['hjlx'])
        student.phone_1 = form.data['dh1']
        student.phone_2 = form.data['dh2']
        student.province_id = int(form.data['sf'])
        student.recipient = form.data['sjr']
        student.note = form.data['bz']
        student.post_address = form.data['yjdz']
        alter = request.form.get('alter')
        check = request.form.get('check')
        import time
        import datetime
        if alter is not None:
            addlog('alter:' + student.name + "、" + student.examinee_number)
            student.input = session['name']
            student.input_time = time.strftime('%Y-%m-%d %H:%M:%S')
        elif check is not None:
            addlog("check:" + student.name + "、" + student.examinee_number)
            student.checker = session['name']
            student.check_time = datetime.datetime.now()
        db.session.add(student)
        db.session.commit()
        return "<script>location.href='';</script>"
    return render_template('studentinfo-details.html', form=form, student=student)


@app.route('/delete/alter/information/<int:acdid>')
@checking_login
def alter_clear(acdid=None):
    """
    清除输机信息
    acdid: alter clear delete id
    """
    import time
    student = StudentInfo.query.get_or_404(acdid)
    student.input_time = time.strftime("1970-01-01 00:00:00")
    student.input = None
    db.session.add(student)
    db.session.commit()
    flash('输机信息清除成功！')
    return redirect(url_for('student_info', sid=acdid))


@app.route('/delete/checker/information/<int:ccdid>')
@checking_login
def check_clear(ccdid=None):
    """
    清除复查信息
    ccdid: checker clear delete id
    """
    import time
    student = StudentInfo.query.get_or_404(ccdid)
    student.check_time = time.strftime("1970-01-01 00:00:00")
    student.checker = None
    db.session.add(student)
    db.session.commit()
    flash('复查信息清除成功！')
    return redirect(url_for('student_info', sid=ccdid))


@app.route("/major/select/major/direction/", methods=["GET"])
@checking_login
def select_major_direction():
    """查找子分类"""
    ma_id = request.args.get("ma_id", "")  # 接收传递的参数ma_id
    majordirection = MajorDirection.query.filter_by(major_id=ma_id).all()
    result = {}
    if majordirection:
        data = []
        for item in majordirection:
            data.append({'id': item.id, 'name_direction': item.name_direction})
        result['status'] = 1
        result['message'] = 'ok'
        result['data'] = data
    else:
        result['status'] = 0
        result['message'] = 'error'
    return jsonify(result)  # 返回json数据


@app.route('/student/information/all/', methods=["GET", "POST"])
@checking_login
def student_all():
    """
    所有考生,筛选考生
    """
    # 先从数据库读取必要的内容
    province = Province.query.order_by(Province.id.asc()).all()
    major = Major.query.order_by(Major.id.asc()).all()
    majorlist = MajorList.query.order_by(MajorList.id.asc()).all()
    direction = MajorDirection.query.order_by(MajorDirection.id.asc()).all()
    count = StudentInfo.query.count()  # 计算学生总数
    # 判断获取方式get与post，如果是get方法，返回所有学生的数据
    if request.method == 'GET':
        student = StudentInfo.query.order_by(StudentInfo.id.asc()).all()  # 直接数据库获取所有学生，返回到页面模板
        return render_template('studentinfo-all.html', student=student, count_all=count, pro=province, major=major,
                               dirc=direction, majorlist=majorlist)
    else:
        # 否则就获取筛选表数据
        status = request.form.get('screen-status')  # 在库状态
        province_post = request.form.get('screen-province')  # 省份
        major = request.form.get('screen-major')  # 专业
        print(status, type(status), major, type(major))
        # 判断筛选项
        if province_post is not None:  # 如果选择了省份，则有4种情况，不考虑三个条件全选有三种
            if major and status is None:  # 只选择了省份的情况
                student = StudentInfo.query.filter(
                    StudentInfo.province_id == Province.query.filter(
                        Province.name == province_post
                    ).first().id
                ).all()
                return render_template("studentinfo-all.html", pro=province, student=student, count=len(student),
                                       count_all=count, major=major, direction=direction, majorlist=majorlist)
            elif major is not None and status is None:  # 选择了省份和专业的情况
                student = StudentInfo.query.filter(
                    or_(
                        StudentInfo.major_id == Major.query.filter(
                            Major.name_major.like("%" + major + "%")
                        ).first().id,
                        StudentInfo.major_direction_id == MajorDirection.query.filter(
                            MajorDirection.name_direction.like("%" + major + "%")
                        ).first().id
                    )
                ).all()
                return render_template("studentinfo-all.html", pro=province, student=student, count=len(student),
                                       count_all=count, major=major, direction=direction, majorlist=majorlist)
            else:  # 在库状态不为空
                student = [1, 2]
                return render_template("studentinfo-all.html", pro=province, student=student, count=len(student),
                                       count_all=count, major=major, direction=direction, majorlist=majorlist)
        else:
            return redirect(url_for('student_all'))


@app.route('/all/major/list/')
@checking_login
def major_list():
    """专业列表"""
    major = MajorList.query.order_by(MajorList.code_majorlist.aszc()).all()
    return render_template("major-list.html", major=major)


@app.route('/major/list/delete/', methods=["POST"])
@checking_login
def major_del():
    """专业列表批量删除"""
    if request.method == 'POST':
        major_ids = request.form.getlist("delid")  # cat_ids 是一个列表
        # 如果没有专业可以删除。或者未删除任何专业
        if not major_ids:
            flash('未选择专业或者没有可以删除的专业！')
            return redirect(url_for("major_list"))
        else:
            # 使用in_ 方式批量删除，需要设置synchronize_session为False
            db.session.query(MajorList).filter(MajorList.id.in_(major_ids)).delete(synchronize_session=False)
            db.session.commit()
            flash('删除成功！')
            return redirect(url_for("major_list"))


@app.route('/log/all/record/')
def log_list():
    """日志列表"""
    log_count = Log.query.count()  # 日志计数
    # print(log_count)
    page = request.args.get('page', type=int)  # 日志分页
    page_data = Log.query.order_by(Log.add_time.desc()).paginate(page=page, per_page=10)  # 每页十条日志
    return render_template('log-list.html', log=page_data, count=log_count)


@app.route('/option/log/list/delete', methods=["POST"])
@checking_login
def log_del():
    """
    日志列表批量删除
    """
    if request.method == 'POST':
        log_ids = request.form.getlist("ldid")  # log_ids是从表单获取的一个列表
        # 如果没有日志可以删除。或者未选择任何日志
        if not log_ids:
            flash('未选择或者没有可以删除的！')
        else:
            # 使用in_ 方式批量删除，需要设置synchronize_session为False
            db.session.query(Log).filter(Log.id.in_(log_ids)).delete(synchronize_session=False)
            db.session.commit()
            flash('删除成功！')
        return redirect(url_for("log_list"))


@app.route('/from/excel/import/', methods=['POST', 'GET'])
def import_excel():
    """
    从excel导入专业
    """
    import pandas as pd
    import os
    major = request.form.get('major')
    student = request.form.get("student")
    if request.method == 'GET':
        return render_template("import-excel.html")
    else:
        if major is not None:
            file = request.files['file-upload']  # 获取上传的文件
            file_basename = os.path.basename(file.filename)
            filepath = os.path.abspath(file_basename)
            if not file:
                flash('请选择需要上传的文件！')
            else:
                # 利用pandas库读取major.xlsx中的数据，只读取第一列和第二列，第一行不做处理，读取完成将读取到的值转化为一个list
                list_major = pd.read_excel(file, usecols=[0, 1], names=None).values.tolist()
                for lm in list_major:  # for循环来遍历list中的每一项
                    major = MajorList(code_majorlist=lm[0], name_majorlist=lm[1])
                    db.session.add(major)  # 在for循环中添加到数据库，每循环一次添加一次，但不提交
                db.session.commit()  # 所有事务一次提交到数据库
                addlog('导入专业列表 :' + file.filename)  # 增加日志
                flash('专业导入成功！导入路径：%s' % filepath)
        elif student is not None:
            file = request.files['file-upload-student']
            file_basename = os.path.basename(file.filename)
            filepath = os.path.abspath(file_basename)
            if not file:
                flash('请选择需要上传的文件！')
            else:
                list_student = pd.read_excel(
                    file,
                    usecols=[0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 16, 17, 18, 19, 20, 21, 24, 25],
                    names=None
                ).values.tolist()  # 选择性读取excel文件中的某一些列作为一个新列表
                for ls in list_student:
                    import datetime
                    studentinfo = StudentInfo(
                        # 新列表从第一行开始遍历
                        examinee_number=ls[0],
                        name=ls[1],
                        registration_number=ls[2],
                        international=ls[3],
                        id_number=ls[4],
                        # birthday=ls[5],
                        sex=ls[5],
                        height=ls[6],
                        high_school=ls[7],
                        major_id=ls[8],
                        major_direction_id=ls[9],
                        afford_fee=ls[10],
                        art_science=ls[11],
                        household_type=ls[12],
                        phone_1=ls[13],
                        phone_2=ls[14],
                        province_id=ls[15],
                        # recipient=ls[22],
                        # note=ls[23],
                        post_address=ls[16],
                        add_time=datetime.datetime.now(),
                    )
                    db.session.add(studentinfo)
                db.session.commit()
                addlog('导入学生信息：%s' % file.filename)  # 增加日志
                flash('学生信息导入成功！路径：%s' % filepath)
        return render_template("import-excel.html")


@app.route('/500')
def err():
    return render_template("500.html")


@app.route('/permission/denied/403/')
def forbidden():
    """权限不足，权限受限403"""
    return render_template('403.html')


@app.errorhandler(404)
def page_not_found(error):
    """访问到未注册的路由时返回404"""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(thread=True)
