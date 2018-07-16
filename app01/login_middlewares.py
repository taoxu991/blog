from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect,HttpResponse

class LoginMD(MiddlewareMixin):
    """
    登录需求验证中间件
    """
    # 白名单
    white_list = [
        '/login/',
        '/register/',
        '/',
    ]
    # 黑名单
    black_list = []
    def process_request(self, request):
        next_url = request.path_info
        if next_url in self.white_list or request.session.get('user'):
            return
        elif next_url in self.black_list:
            return HttpResponse('这是一个非法路径！')
        else:
            return redirect('/login/?next={}'.format(next_url))
