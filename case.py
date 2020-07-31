# -*- coding: utf-8 -*-
import json

from driver import Driver


class Case(Driver):
    def __init__(self, url, page):
        self.res = []
        self.page = page
        self.fp = open(f'{page.replace("/","")}.json', 'w', encoding='utf8')

        super(Case, self).__init__(url)

    def __del__(self):
        """
        写入json,关闭文件句柄和浏览器
        """
        self.fp.write(json.dumps(self.res, ensure_ascii=False, indent=2))
        self.fp.close()
        self.driver.close()

    def add_login(self, name='admin'):
        self.res.append({'login': name})

    def add_logout(self):
        self.res.append('logout')

    def add_open(self):
        self.res.append({'open': self.page})

    def add_close(self):
        self.res.append('close')

    def add_choose(self, index=1):
        self.res.append({'choose': index})

    def add_create(self):
        self.res.append('create')

    def add_save(self):
        self.res.append('save')

    def add_wait(self, second):
        self.res.append({'wait': second})

    def add_wkf(self, button):
        self.res.append({'wkf': button})

    def add_fill(self):
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
        self.res.append({'fill': fill})

    def login_open(self):
        self.login('admin')
        self.open(self.page)
        self.create()

    def add_login_wkf_logout(self, name, button, index=1):
        self.add_login(name)
        self.add_open()
        self.add_choose(index)
        self.add_wkf(button)
        self.add_logout()

    def add_login_create_logout(self, name):
        self.add_login(name)
        self.add_open()
        self.add_create()
        self.add_fill()
        self.add_save()
        self.add_wkf('发起')
        self.add_logout()


if __name__ == '__main__':
    c = Case('http://127.0.0.1:8069/web', '用款/借款/押金申请单(项目部及采购)')
    c.add_login('test')
    c.add_open()
    c.add_create()
    c.add_fill()
    c.add_save()
    # c.add_login_create_logout("test")
    # c.add_login_wkf_logout('采购', '通过')
    # c.add_login_wkf_logout('财务', '通过')
    # c.add_login_wkf_logout('工厂', '通过')
    # c.add_login_wkf_logout('控股', '通过')
    # c.add_login_wkf_logout('test', '通过')
    # # c.add_login_wkf_logout('财务', '通过')
    # c.add_login_wkf_logout('工厂出纳', '通过')
