# -*- coding: utf-8 -*-
import json

from driver import Driver


class Case(Driver):
    def __init__(self, url, page):
        self.res = []
        self.user = {}
        self.page = page
        self.fp = open(f'{page.replace("/", "")}.json', 'w', encoding='utf8')

        super(Case, self).__init__(url)

    def __del__(self):
        """
        写入json,关闭文件句柄和浏览器
        """
        self.fp.write(json.dumps(self.res, ensure_ascii=False, indent=2))
        self.fp.close()
        self.driver.close()

    def add_login(self, name='admin', user=False):
        if user:
            self.user['login'] = name
        else:
            self.res.append({'login': name})

    def add_logout(self, user=False):
        if user:
            self.user['logout'] = None
        else:
            self.res.append('logout')

    def add_open(self, user=False):
        if user:
            self.user['open'] = self.page
        else:
            self.res.append({'open': self.page})

    def add_close(self, user=False):
        if user:
            self.user['close'] = None
        else:
            self.res.append('close')

    def add_choose(self, index=1, user=False):
        if user:
            self.user['choose'] = index
        else:
            self.res.append({'choose': index})

    def add_create(self, user=False):
        if user:
            self.user['create'] = None
        else:
            self.res.append('create')

    def add_save(self, user=False):
        if user:
            self.user['save'] = None
        else:
            self.res.append('save')

    def add_wait(self, second, user=False):
        if user:
            self.user['wait'] = second
        else:
            self.res.append({'wait': second})

    def add_wkf(self, button, user=False):
        if user:
            self.user['wkf'] = button
        else:
            self.res.append({'wkf': button})

    def add_fill(self, user=False):
        self.login_open()
        fill = {}
        labels = self.driver.find_elements_by_tag_name('label')
        for label in labels:
            js = """
            let label = arguments[0];
            if (label.parentNode.nextElementSibling !== null){
                return label.parentNode.nextElementSibling.firstElementChild
            }else{
                return label.parentNode.parentNode.nextElementSibling.firstElementChild.firstElementChild
            }
            """
            ele = self.driver.execute_script(js, label)
            if ele.tag_name not in ['a', 'span'] and label.text:
                fill[label.text] = ''
        if user:
            self.user['fill'] = fill
        else:
            self.res.append({'fill': fill})

    def login_open(self):
        self.login('admin')
        self.open(self.page)
        self.create()

    def add_login_wkf_logout(self, name, button, index=1):
        self.user.clear()
        self.add_login(name, user=True)
        self.add_open(user=True)
        self.add_choose(index, user=True)
        self.add_wkf(button, user=True)
        self.add_logout(user=True)
        self.res.append(self.user)

    def add_login_create_logout(self, name):
        self.user.clear()
        self.add_login(name, user=True)
        self.add_open(user=True)
        self.add_create(user=True)
        self.add_fill(user=True)
        self.add_save(user=True)
        self.add_wkf('发起', user=True)
        self.add_logout(user=True)
        self.res.append(self.user)


if __name__ == '__main__':
    c = Case('http://127.0.0.1:8069/web', '还款/费用报销单(项目部及采购)')
    # c.add_login('test')
    # c.add_open()
    # c.add_create()
    # c.add_fill()
    # c.add_save()
    c.add_login_create_logout("test")
    # c.add_login_wkf_logout('采购', '通过')
    # c.add_login_wkf_logout('财务', '通过')
    # c.add_login_wkf_logout('工厂', '通过')
    # c.add_login_wkf_logout('控股', '通过')
    # c.add_login_wkf_logout('test', '通过')
    # # c.add_login_wkf_logout('财务', '通过')
    # c.add_login_wkf_logout('工厂出纳', '通过')
