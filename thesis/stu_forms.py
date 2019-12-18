from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, DecimalField, RadioField, SelectField
from wtforms.validators import DataRequired, ValidationError


class StudentForm(FlaskForm):
    ksh = StringField(
        label='考生号',
        description='考生号',
        render_kw={
            "class": "form-control",
        }
    )
    xm = StringField(
        label='姓名',
        description='姓名',
        render_kw={
            'class': 'form-control'
        }
    )
    bkh = StringField(
        label='报考号',
        description='报考号',
        render_kw={
            'class': 'form-control'
        }
    )
    gjztc = StringField(
        label='国际直通车',
        description='国际直通车',
        render_kw={
            'class': 'form-control'
        }
    )
    sfzh = StringField(
        label='身份证号',
        description='身份证号',
        render_kw={
            'class': 'form-control'
        }
    )
    sr = StringField(
        label='出生年月',
        description='出生年月',
        render_kw={
            'class': 'form-control'
        }
    )
    xb = RadioField(
        label='性别',
        description='性别',
        coerce=str,
        choices=[(1, '男'), (2, '女')],
        render_kw={
            'type': 'radio',
            'class': 'list-inline minimal',
        }
    )
    sg = StringField(
        label='身高',
        description='身高',
        render_kw={
            'class': 'form-control'
        }
    )
    gzxx = StringField(
        label='毕业院校',
        description='毕业院校',
        render_kw={
            'class': 'form-control'
        }
    )
    zy = SelectField(
        label='专业',
        description='专业',
        coerce=int,
        render_kw={
            'class': 'form-control select2'
        }
    )
    zyfx = SelectField(
        label='专业方向',
        description='专业方向',
        coerce=int,
        render_kw={
            'class': 'form-control select2'
        }
    )
    msbh = StringField(
        label='面试包号',
        description='笔试包号',
        render_kw={
            'class': 'form-control'
        }
    )
    bsbh = StringField(
        label='笔试包号',
        description='笔试包号',
        render_kw={
            'class': 'form-control'
        }
    )
    mscj = DecimalField(
        label='面试成绩',
        description='面试成绩',
        render_kw={
            'class': 'form-control'
        }
    )
    bscj = DecimalField(
        label='笔试成绩',
        description='笔试成绩',
        render_kw={
            'class': 'form-control'
        }
    )
    zcj = DecimalField(
        label='总成绩',
        description='总成绩',
        render_kw={
            'class': 'form-control'
        }
    )
    nffdxf = RadioField(
        label='经济状况',
        description='经济状况',
        coerce=str,
        choices=[(1, '能负担学费'), (2, '否负担学费'), (3, '有困难')],
        render_kw={
            'class': 'list-inline'
        }
    )
    wlk = RadioField(
        label='文/理科',
        description='文/理科',
        coerce=str,
        choices=[(1, '文'), (2, '理')],
        render_kw={
            'class': 'list-inline'
        }
    )
    hjlx = RadioField(
        label='户籍类型',
        description='户籍类型',
        coerce=str,
        choices=[(1, '城应'), (2, '城往'), (3, '农应'), (4, '农往')],
        render_kw={
            'class': 'list-inline'
        }
    )
    dh1 = StringField(
        label='电话1',
        description='电话1',
        render_kw={
            'class': 'form-control'
        }
    )
    dh2 = StringField(
        label='电话2',
        description='电话2',
        render_kw={
            'class': 'form-control'
        }
    )
    sf = SelectField(
        label='省份',
        description='省份',
        coerce=int,
        render_kw={
            'class': 'form-control select2'
        }
    )
    sjr = StringField(
        label='收件人',
        description='收件人',
        render_kw={
            'class': 'form-control'
        }
    )
    bz = StringField(
        label='备注',
        description='备注',
        render_kw={
            'class': 'form-control',
            'id': '24',
        }
    )
    yjdz = StringField(
        label='邮寄地址',
        description='邮寄地址',
        render_kw={
            'class': 'form-control'
        }
    )

