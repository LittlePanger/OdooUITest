# -*- coding: utf-8 -*-

import re
from time import sleep

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from driver import Driver


class OdooTest(Driver):
    def __init__(self, url):
        self.button_box = self.load_json('./config/wkf_button.json')
        super(OdooTest, self).__init__(url)

    @staticmethod
    def wait(second):
        """
        延时
        :param second: 秒
        """
        sleep(second)

    def execute(self, path):
        """
        执行json, 步骤不存在中断
        :param path: json文件路径
        """
        steps = self.load_json(path)
        for step in steps:
            # 判断步骤是字典还是字符串
            if isinstance(step, dict):
                name, content = step.popitem()
            else:
                name, content = step, None
            if hasattr(self, name):
                # 判断是否有参数
                if content:
                    getattr(self, name)(content)
                else:
                    getattr(self, name)()
            else:
                print(f'步骤 {name} 不存在')
                return

    def is_exist(self, xpath):
        """
        判断元素是否存在
        :return: 存在返回元素,否则返回Flase
        """
        try:
            flag = self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            flag = False
        return flag

    def click_blank(self):
        """
        点击空白处(其实是breadcrumb的标题)
        """
        self.driver.find_element_by_xpath('//ol[@class="breadcrumb"]/li[@class="active"]').click()

    def dialog_button(self, index):
        """
        若弹窗, 点击确定/取消
        :param index: 1确定,2取消
        """
        button = self.is_exist(f'//*[@class="modal-footer"]//button[{index}]')
        if button:
            button.click()

    def logout(self):
        """
        退出账号
        """
        if self.is_exist('//div[contains(@class,"modal-dialog")]'):
            self.dialog_button(1)
        self.driver.find_element_by_xpath('//header//li[@class="o_user_menu"]/a').click()
        self.driver.find_element_by_xpath('//header//ul[@class="dropdown-menu"]//a[@data-menu="logout"]').click()
        if self.is_exist('//div[contains(@class,"modal-dialog")]'):
            return

    def logout_login(self, name):
        """
        退出账号并登录
        :param name: ./config/userInfo.json中的名字
        """
        self.logout()
        self.login(name)

    def choose(self, index):
        """
        根据索引打开对应页面并点击对应的kanban or tree
        :param index: 索引
        """
        kanban = self.is_exist(f'//div[contains(@class,"o_kanban_view")]/div[{index}]')
        tree = self.is_exist(f'//table[contains(@class,"o_list_view")]/tbody/tr[{index}]')
        if kanban:
            kanban.click()
        elif tree:
            tree.click()
        else:
            raise IndexError('fourth超出范围')

    def save(self):
        """
        保存
        """
        self.driver.find_element_by_xpath('//div[@class="o_form_buttons_edit"]/button[1]').click()

    def wkf(self, button):
        """
        工作流操作
        :param button: ./config/wkf_button.json中的按钮名
        """
        index = self.button_box[button]
        sleep(1)
        try:
            self.driver.find_element_by_xpath(f'//div[@name="button_box"]/button[{index}]').click()
        except ElementNotInteractableException:
            print('按钮无法点击,可能是没有权限')
            exit()
        # 除了[发起,挂起],其他需要填写内容
        if index not in [1, 7]:
            self.driver.find_element_by_id('description').send_keys('1')
            self.dialog_button(1)
        sleep(1)

    def fill(self, contents):
        """
        填写内容
        :param contents: {'name1':'content1','name2':'content2','tableAdd/tableEdit/tableM2M':[]}
        """
        for name, content in contents.items():
            if content:
                if name == 'tableAdd':
                    self.table_add(content)
                elif name == 'tableEdit':
                    self.click_blank()
                    self.table_edit(content)
                elif name == 'tableM2M':
                    self.table_m2m(content)
                # elif content.get('type') == 'file':
                #     self.file(content)
                else:
                    self.general_content('tag', 'label', name, content)

    def general_content(self, find_type, label_name, name, content):
        """
        常规内容: 根据名字找到对应输入框后输入内容
        :param find_type: 标签查找类型
        :param label_name: 对应类型的查找条件
        :param name: 标题, 即<label>
        :param content: 填写内容
        """
        if find_type == 'tag':
            labels = self.driver.find_elements_by_tag_name(label_name)
        else:
            labels = self.driver.find_elements_by_xpath(label_name)
        for label in labels:
            if name == re.sub(r'\s+', '', label.text).strip():
                # 如果字段没有id属性,则利用js通过层级关系找
                ele_list = self.driver.find_elements_by_id(label.get_attribute('for'))
                if ele_list:
                    # 存在相同id的情况,移除隐藏的
                    for e in ele_list:
                        if 'o_form_invisible' in e.get_attribute('class'):
                            ele_list.remove(e)
                    ele = ele_list[0]
                else:
                    # 日期的input/textarea/m2m都没有id
                    js = "let father = arguments[0].parentNode.nextElementSibling;" \
                         "return father.getElementsByClassName('o_form_input_file')[0]" \
                         "|| father.getElementsByClassName('o_datepicker_input')[0]" \
                         "|| father.getElementsByClassName('ui-autocomplete-input')[0]" \
                         "|| father.getElementsByTagName('textarea')[0];"
                    ele = self.driver.execute_script(js, label)
                if ele:
                    if ele.tag_name == 'select':
                        # selection字段
                        Select(ele).select_by_visible_text(content)
                    elif 'ui-autocomplete-input' in ele.get_attribute('class'):
                        # m2o/m2m字段
                        ele.clear()
                        ele.send_keys(content)
                        sleep(0.5)
                        ele.send_keys(Keys.ENTER)
                    elif 'o_datepicker_input' in ele.get_attribute('class'):
                        # date字段
                        ele.clear()
                        ele.send_keys(content)
                        # 解决前端报错弹窗
                        self.click_blank()
                        self.dialog_button(1)
                    elif 'o_form_input_file' in ele.get_attribute('class'):
                        # 文件
                        ele.send_keys(content)
                    else:
                        # char和float等
                        ele.clear()
                        ele.send_keys(content)
                break

    def table_add(self, rows):
        """
        表格底部追加: 添加项目 - 按照表格填写顺序填写内容
        :param rows: [{index1:content1,index2:content2},{index1:content1,index2:content2}]
        """
        # 添加项目
        add_btn = self.clickable('//div[@class="o_form_field o_form_field_one2many o_view_manager_content"]//a')
        add_btn.click()
        # 表格中的input
        input_xpath = f'//div[@class="o_form_field o_form_field_one2many o_view_manager_content"]//input'
        inputs = []
        for inp in self.driver.find_elements_by_xpath(input_xpath):
            if not inp.get_attribute('type') == 'hidden':
                inputs.append(inp)
        # 按照顺序填写内容
        for row in rows:
            for index, content in row.items():
                inp = inputs[int(index) - 1]
                if inp.get_attribute('type') != 'file':
                    inp.click()
                    inp.clear()
                    # clear float时会弹窗,点击取消
                    self.dialog_button(2)
                inp.send_keys(content)
                sleep(0.5)
            else:
                add_btn.click()
                sleep(1)

    def table_edit(self, rows):
        """
        o2m 编辑table: 点击对应行 -
                弹窗: 和填写普通表单一样 - 确定
                直接编辑: 根据表头找到对应的输入框 - 输入内容 - 点击空白处使表格回到未选中状态
        :param rows: [{name1:content1,name2:content2},{name1:content1,name2:content2}]
        """
        for index, row in enumerate(rows):
            if row:
                # 如果row不是None,则点击对应行
                table_rows = self.driver.find_elements_by_xpath(
                    '//div[@class="o_form_field o_form_field_one2many o_view_manager_content"]//table//tr[@data-id]')
                table_rows[index].click()
                sleep(1)
                if self.is_exist('//div[contains(@class,"modal-dialog")]'):
                    # 弹窗和普通表单一样
                    for name, content in row.items():
                        self.general_content('xpath', '//div[contains(@class,"modal-dialog")]//label', name, content)
                    self.dialog_button(1)
                else:
                    # table直接编辑
                    # 表头
                    heads = self.driver.find_elements_by_xpath(
                        f'//div[@class="o_form_field o_form_field_one2many o_view_manager_content"]//table//th[@data-id]')
                    # 点击表格出现的所有输入框
                    tables_old = self.driver.find_elements_by_xpath(
                        '//div[contains(@class,"o_form_view o_list_editable_form o_form_nosheet o_cannot_create '
                        'o_form_editable")]/*')
                    # 过滤隐藏的
                    tables = []
                    for table in tables_old:
                        if 'o_form_invisible' not in table.get_attribute('class'):
                            tables.append(table)

                    for name, content in row.items():
                        # 找到name对应table的索引
                        for head_index, head in enumerate(heads):
                            if head.text == name:
                                table_index = head_index

                                # 判断是否是m2o字段
                                if tables[table_index].tag_name == 'input':
                                    table_input = tables[table_index]
                                    m2o = False
                                else:
                                    # m2o字段
                                    table_input = tables[table_index].find_element_by_tag_name('input')
                                    m2o = True
                                # 清空,若出现弹窗则点击取消
                                table_input.clear()
                                self.dialog_button(2)
                                sleep(0.5)

                                table_input.send_keys(content)
                                # 如果是m2o,则回车
                                if m2o:
                                    sleep(0.5)
                                    table_input.send_keys(Keys.ENTER)
                                self.dialog_button(2)
                                break
                    # 点击空白处,使表格回到未选中状态
                    self.click_blank()

    def table_m2m(self, content):
        """
        m2m表: 添加项目 - 点击选项前面的input - 确定
        :param content: [index1,index2]
        """
        sleep(1)
        self.clickable('//td[@class="o_form_field_x2many_list_row_add"]/a').click()
        sleep(1)
        if self.is_exist('//div[contains(@class,"modal-dialog")]'):
            inputs = self.driver.find_elements_by_xpath(
                '//div[contains(@class,"modal-dialog")]//tbody//input[@name="radiogroup"]')
            for index in content:
                inputs[index - 1].click()
            self.dialog_button(1)
        sleep(1)
