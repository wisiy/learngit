from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FormField, DateField, FieldList


class ItemForm(FlaskForm):
    zy = StringField('日期')
    content = StringField("内容")
    delete = SubmitField("删除")


# 自定义表单类
class AddForm(FlaskForm):
    item_list = FieldList(FormField(ItemForm), min_entries=1)  # min_entries =3表示有三个同样的ItemForm
    submit = SubmitField("再加一行")
