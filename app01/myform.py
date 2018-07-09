from django import forms
from django.core.exceptions import  ValidationError
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator
from app01.models import UserInfo

class RegForm(forms.Form):
    user = fields.CharField(
        required=True,
        widget=widgets.TextInput(attrs={'class': "form-control" ,'placeholder': '用户名为2-12个字符'}),
        min_length=2,
        max_length=12,
        strip=True,
        error_messages={'required': '用户名不能为空',
                        'min_length': '用户名最少为2个字符',
                        'max_length': '用户名最不超过为12个字符'},
    )
    email = fields.EmailField(
        required=True,
        widget=widgets.TextInput(attrs={'class': "form-control" ,'placeholder': '请输入邮箱'}),
        # strip=True,
        error_messages={'required': '邮箱不能为空',
                        'invalid' :'请输入正确的邮箱格式'},
    )

    valid_code = fields.CharField(
        required=True,
        widget=widgets.TextInput(attrs={'class':'form-control','placeholder':'请输入验证码'}),
        strip=True,
        error_messages={
            'required': '验证码不能为空',
        }
    )

    pwd = fields.CharField(
        widget=widgets.PasswordInput(attrs={'class': "form-control" ,'placeholder': '请输入密码，必须包含数字,字母'}
                                     ,render_value=True),
        required=True,
        min_length=2,
        max_length=12,
        strip=True,
        # validators=[
        #     # 下面的正则内容一目了然，我就不注释了
        #     RegexValidator(r'((?=.*\d))^.{6,12}$', '必须包含数字'),
        #     RegexValidator(r'((?=.*[a-zA-Z]))^.{6,12}$', '必须包含字母'),
        #     # RegexValidator(r'((?=.*[^a-zA-Z0-9]))^.{6,12}$', '必须包含特殊字符'),
        #     RegexValidator(r'^.(\S){6,10}$', '密码不能包含空白字符'),
        # ],  # 用于对密码的正则验证
        error_messages={'required': '密码不能为空!',
                        'min_length': '密码最少为2个字符',
                        'max_length': '密码最多不超过为12个字符!' ,},
    )
    repeat_pwd = fields.CharField(
        # render_value会对于PasswordInput，错误是否清空密码输入框内容，默认为清除，我改为不清楚
        widget=widgets.PasswordInput(attrs={'class': "form-control" ,'placeholder': '请再次输入密码!'} ,render_value=True),
        required=True,
        strip=True,
        error_messages={'required': '请再次输入密码!' ,}

    )

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    def clean_user(self):
        # 对username的扩展验证，查找用户是否已经存在
        username = self.cleaned_data.get('user')
        user = UserInfo.objects.filter(username=username)
        if user.exists():
            # self.errors['user'] = '用户已经存在！'
            raise ValidationError('用户已经存在！')
        return username

    def clean_email(self):
        # 对email的扩展验证，查找用户是否已经存在
        email = self.cleaned_data.get('email')
        email_obj = UserInfo.objects.filter(email=email)  # 从数据库中查找是否用户已经存在
        if email_obj.exists():
            # self.errors['user'] = '该邮箱已经注册！'
            raise ValidationError('该邮箱已经注册！')
        return email

    def _clean_repeat_pwd(self):  # 查看两次密码是否一致
        password1 = self.cleaned_data.get('pwd')
        password2 = self.cleaned_data.get('repeat_pwd')
        if password1 and password2:
            if password1 != password2:
                self.errors['repeat_pwd'] = ['两次密码不匹配']
                # raise ValidationError('密码不一致！')
        return password2

    def clean_valid_code(self):
        val = self.cleaned_data.get('valid_code')

        if val.upper() == self.request.session.get('valid_code_str').upper():
            return self.cleaned_data.get('valid_code')
        else:
            raise ValidationError('验证码错误！')

    def clean(self):
        # 是基于form对象的验证，字段全部验证通过会调用clean函数进行验证
        # self._clean_new_password2()  # 简单的调用而已
        self._clean_repeat_pwd()


class LoginForm(forms.Form):
    user = fields.CharField(
        required=True,
        widget=widgets.TextInput(attrs={'class': "form-control",'placeholder': '请输入用户名'}),
        min_length=2,
        max_length=12,
        strip=True,
        error_messages={'required': '用户名不能为空',}
    )

    pwd = fields.CharField(
        widget=widgets.PasswordInput(attrs={'class': "form-control",'placeholder': '请输入密码'}),
        required=True,
        min_length=2,
        max_length=12,
        strip=True,
        error_messages={'required': '密码不能为空!',}
    )

    valid_code = fields.CharField(
        required=True,
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入验证码'}),
        strip=True,
        error_messages={
          'required': '验证码不能为空',
        }
    )

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    def clean_user(self):
        # 对username的扩展验证，查找用户是否已经存在
        user = self.cleaned_data.get('user')
        user_obj = UserInfo.objects.filter(username=user)
        if not user_obj.exists():
          # self.errors['user'] = '用户不存在！'
          raise ValidationError('用户不存在！')
        return user

    def clean_pwd(self):
        pwd = self.cleaned_data.get('pwd')
        return pwd

    def clean_valid_code(self):
        val = self.cleaned_data.get('valid_code')

        if val.upper() == self.request.session.get('valid_code_str').upper():
          return self.cleaned_data.get('valid_code')
        else:
          raise ValidationError('验证码错误！')

    def clean(self):
        pass