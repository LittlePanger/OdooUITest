# -*- coding: utf-8 -*-
import json
import os

from driver import Driver


class Case(Driver):
    def __init__(self, url, page, name=''):
        self.res = []
        self.page = page
        case_path = self.load_json('./config/case_path.json')['path']
        self.path = os.path.join(case_path, f'{page.replace("/", "")}{name}.json')
        if os.path.exists(self.path):
            print('文件名已存在,为防覆盖请加name参数')
            exit()
        self.fp = open(self.path, 'w', encoding='utf8')

        super(Case, self).__init__(url)

    def __del__(self):
        """
        写入json,关闭文件句柄和浏览器
        """
        if getattr(self, "fp", False):
            self.fp.write(json.dumps(self.res, ensure_ascii=False, indent=2))
            self.fp.close()
            if not self.res:
                os.remove(self.path)
            self.driver.close()

    def add_login(self, name='admin'):
        self.res.append({'login': name})

    def add_logout(self):
        self.res.append('logout')

    def add_open(self):
        self.res.append({'open': self.page})

    def add_close(self):
        self.res.append('close')

    def add_choose(self, model, model_id):
        self.res.append({'choose': {model: model_id}})

    def add_create(self):
        self.res.append('create')

    def add_save(self):
        self.res.append('save')

    def add_wait(self, second):
        self.res.append({'wait': second})

    def add_wkf(self, button):
        self.res.append({'wkf': button})

    def add_fill(self):
        self.res.append({'fill': self.label_fill()})

    def label_fill(self):
        self.login('admin')
        self.open(self.page)
        self.create()
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
        return fill

    def add_login_wkf_logout(self, username, button):
        """
        wkf流程:登录-打开-选择-通过/拒绝等-退出
        :param username: userinfo.json中的用户名
        :param button: wkf_button.json中的按键名
        """
        self.res.append({
            "login": username,
            "open": -1,
            "wkf": button,
            "logout": None
        })

    def add_login_create_logout(self, username):
        """
        登录-打开-创建-填充内容-保存-发起-退出
        """
        self.res.append({
            "login": username,
            "open": self.page,
            "create": None,
            "fill": self.label_fill(),
            "save": None,
            "wkf": "发起",
            "logout": None
        })


if __name__ == '__main__':
    c = Case('http://127.0.0.1:8069/web', page='外协分包合同扣款登记表', name='factory')
    # c.add_login('test')
    # c.add_open()
    # c.add_create()
    # c.add_fill()
    # c.add_save()
    c.add_login_create_logout(username="成本管理员")
    # c.add_login_wkf_logout('生产', '通过')

    c.add_login_wkf_logout(username='采购', button='通过')
    # c.add_login_wkf_logout('财务', '通过')
    # c.add_login_wkf_logout('工厂', '通过')
    # c.add_login_wkf_logout('控股', '通过')
    c.add_login_wkf_logout('成本管理员', '通过')
    # c.add_login_wkf_logout('test', '通过')
    # # c.add_login_wkf_logout('财务', '通过')
    # c.add_login_wkf_logout('工厂出纳', '通过')
