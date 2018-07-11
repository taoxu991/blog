"""
使用方法：

from utils.page import Pagination
def users(request):
    current_page = int(request.GET.get('page',1))

    total_item_count = models.UserInfo.objects.all().count()
    # page_obj = Pagination(current_page,total_item_count,request.path_info)
    page_obj = Pagination(current_page,total_item_count,'/users.html')

    user_list = models.UserInfo.objects.all()[page_obj.start:page_obj.end]

    return render(request,'users.html',{'user_list':user_list,'page_html':page_obj.page_html()})


"""

from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class Pagination(object):

    def __init__(self,current_page,total_item_count,base_url,per_page_count=10,show_pager_count=11):
        """
        :param current_page:  当前页
        :param total_item_count: 数据库数据总条数
        :param base_url: 分页前缀URL
        :param per_page_count:   每页显示数据条数
        :param show_pager_count: 对多显示的页码
        """
        self.current_page = current_page
        self.total_item_count = total_item_count
        self.base_url = base_url
        self.per_page_count = per_page_count
        self.show_pager_count = show_pager_count

        max_pager_num, b = divmod(total_item_count, per_page_count)
        if b:
            max_pager_num += 1
        self.max_pager_num = max_pager_num

    @property
    def start(self):
        """

        :return:
        """
        return (self.current_page-1)* self.per_page_count

    @property
    def end(self):
        """

        :return:
        """
        return self.current_page * self.per_page_count

    def page_html(self):
        """

        :return:
        """
        page_list = []

        if self.current_page == 1:
            prev = ' <li><a href="#">上一页</a></li>'
        else:
            prev = ' <li><a href="%s?page=%s">上一页</a></li>' % (self.base_url,self.current_page - 1,)
        page_list.append(prev)

        half_show_pager_count = int(self.show_pager_count / 2)

        # 数据特别少，15条数据=2页
        if self.max_pager_num < self.show_pager_count:
            # 页码小于11
            pager_start = 1
            pager_end = self.max_pager_num + 1
        else:
            if self.current_page <= half_show_pager_count:
                pager_start = 1
                pager_end = self.show_pager_count + 1
            else:
                if self.current_page + half_show_pager_count > self.max_pager_num:
                    pager_start = self.max_pager_num - self.show_pager_count + 1
                    pager_end = self.max_pager_num + 1
                else:
                    pager_start = self.current_page - half_show_pager_count
                    pager_end = self.current_page + half_show_pager_count + 1

        for i in range(pager_start, pager_end):
            if i == self.current_page:
                tpl = ' <li class="active"><a href="%s?page=%s">%s</a></li>' % (self.base_url,i, i,)
            else:
                tpl = ' <li><a href="%s?page=%s">%s</a></li>' % (self.base_url,i, i,)
            page_list.append(tpl)

        if self.current_page == self.max_pager_num:
            nex = ' <li><a href="#">下一页</a></li>'
        else:
            nex = ' <li><a href="%s?page=%s">下一页</a></li>' % (self.base_url,self.current_page + 1,)
        page_list.append(nex)

        return mark_safe(''.join(page_list))


class CustomPagination(Paginator):

    def __init__(self, current_page, base_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_page = current_page
        self.base_url = base_url
        self.res_list = None
        self.html = self.page_html()

    def page_html(self):
        """
        :return:
        """
        page_list = []

        if self.num_pages > 11:

            if self.current_page - 5 < 1:
                page_range = range(1, 12)
            elif self.current_page + 5 > self.num_pages:
                page_range = range(self.num_pages - 10, self.num_pages + 1)

            else:
                page_range = range(self.current_page - 5, self.current_page + 6)
        else:
            page_range = self.page_range

        try:
            self.res_list = self.page(self.current_page)
        except EmptyPage:
            self.current_page = self.num_pages
            self.res_list = self.page(self.current_page)
        except PageNotAnInteger:
            self.res_list = self.page(1)
            self.current_page = 1

        if self.res_list.has_previous():
            prev = '''<li><a href="%s?page=%s" aria-label="Previous">
            <span aria-hidden="true">上一页</span></a></li>
            ''' %(self.base_url, self.res_list.previous_page_number())
        else:
            prev = '''
            <li class="disabled"><a href="#" aria-label="Previous">
            <span aria-hidden="true">上一页</span></a></li>
            '''
        page_list.append(prev)

        for num in page_range:
            if num == self.current_page:
                content = '''
                <li class="item active"><a href="%s?page=%s">%s</a></li>
                ''' % (self.base_url, num, num)
            else:
                content = '''
                <li class="item"><a href="%s?page=%s">%s</a></li>
                ''' % (self.base_url, num, num)
            page_list.append(content)

        if self.res_list.has_next():
            has_next = '''<li><a href="%s?page=%s" aria-label="Previous">
            <span aria-hidden="true">下一页</span></a></li>
            ''' % (self.base_url, self.res_list.next_page_number())
        else:
            has_next = '''
            <li class="disabled"><a href="#" aria-label="Previous">
            <span aria-hidden="true">下一页</span></a></li>
            '''
        page_list.append(has_next)

        return mark_safe(''.join(page_list))
