# -*- coding: utf-8 -*-

import json
import re
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait


class Driver:
    def __init__(self, url):
        self.url = url
        self.button_box = self.load_json('./config/button_box.json')
        self.userInfo = self.load_json('./config/userInfo.json')

        self.driver = webdriver.Chrome(executable_path='./WebDriver/chromedriver')
        self.driver.get(self.url)
        self.choose_databases()

    def close(self):
        """
        关闭浏览器
        """
        self.driver.close()

    @staticmethod
    def load_json(filename):
        """
        加载json
        """
        with open(filename)as f:
            return json.loads(f.read())

    def execute(self, filename):
        """
        执行json, 步骤不存在中断
        """
        file = self.load_json(filename)
        for f in file:
            step, content = f.popitem()
            if hasattr(self, step):
                if content:
                    getattr(self, step)(content)
                else:
                    getattr(self, step)()
            else:
                print(f'步骤 {step} 不存在')
                return

    def clickable(self, xpath):
        """
        等待直到按钮可点击, 超时报错
        :return: 按钮
        """
        wait = WebDriverWait(self.driver, 5)  # 等待的最大时间
        try:
            # 判断该元素是否可点击
            return wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutException:
            print('加载超时')

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

    def choose_databases(self):
        """
        选择第一个数据库
        """
        self.driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/a[1]').click()

    def login(self, info):
        """
        选择数据库 - 选择登录方式 - 输入账号密码
        """
        # 选择账户登录
        self.driver.find_element_by_xpath('/html/body/div/div[2]/a').click()
        # 账号密码登录
        self.driver.find_element_by_xpath('//*[@id="login"]').send_keys(self.userInfo[info]['username'])
        self.driver.find_element_by_xpath('//*[@id="password"]').send_keys(self.userInfo[info]['password'])
        self.driver.find_element_by_xpath('/html/body/form/div[3]/button').click()

    def logout(self, is_pass):
        """
        退出账号,弹窗时pass = True跳过直接退出,否则不退出
        """
        self.driver.find_element_by_xpath('//header//li[@class="o_user_menu"]/a').click()
        self.driver.find_element_by_xpath('//header//ul[@class="dropdown-menu"]//a[@data-menu="logout"]').click()
        if self.is_exist('//div[contains(@class,"modal-dialog")]'):
            # 不保存退出
            if is_pass['pass']:
                self.dialog_button(1)
            else:
                self.dialog_button(2)

    def open_page(self, menu):
        """
        根据索引打开对应页面
        """
        first = menu.get("first")
        second = menu.get('second') + 2
        third = menu.get('third')

        # 首页按钮
        home_btn = self.clickable(f'//*[@id="appDrawerAppPanelBody"]/ul/li[{first}]')
        home_btn.click()
        sleep(0.5)
        # 顶部导航栏
        self.driver.find_element_by_xpath(
            f'//*[@id="odooMenuBarNav"]/div/div[1]/ul[{first}]/li[{second}]/a').click()
        # 顶部导航栏下按钮
        if third:
            # page_url = self.driver.find_element_by_xpath(
            #     f'//*[@id="odooMenuBarNav"]/div/div[1]/ul[{first}]/li[{second}]//li[{third}]/a').get_attribute('href')
            # self.driver.get(page_url)
            self.driver.find_element_by_xpath(
                f'//*[@id="odooMenuBarNav"]/div/div[1]/ul[{first}]/li[{second}]//li[{third}]/a').click()
            sleep(0.5)

    def open_page_and_create(self, menu):
        """
        根据索引打开对应页面并点击创建
        """
        self.open_page(menu)
        # 创建
        create_btn = self.clickable('/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/div/button')
        create_btn.click()
        sleep(1)

    def open_page_and_choose(self, menu):
        """
        根据索引打开对应页面并点击对应的kanban or tree
        """
        self.open_page(menu)
        index = menu.get("fourth")
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
        :param button: 按钮名
        """
        index = self.button_box[button]
        self.clickable(f'//div[@name="button_box"]/button[{index}]').click()
        # 除了[发起,挂起],其他需要填写内容
        if index not in [1, 7]:
            self.driver.find_element_by_id('description').send_keys('1')
            self.dialog_button(1)

    def fill_in(self, contents):
        """
        填写内容
        """
        for content in contents:
            if content.get('type') == 'tableAdd':
                self.table_add(content)
            elif content.get('type') == 'tableEdit':
                self.click_blank()
                self.table_edit(content)
            elif content.get('type') == 'tableM2M':
                self.table_m2m(content)
            # elif content.get('type') == 'file':
            #     self.file(content)
            else:
                self.general_content('tag', 'label', content)

    def general_content(self, find_type, label_name, content):
        """
        常规内容: 根据名字找到对应输入框后输入内容
        :param find_type: 标签查找类型
        :param label_name: 对应类型的查找条件
        :param content: 填写内容
        """
        if find_type == 'tag':
            labels = self.driver.find_elements_by_tag_name(label_name)
        else:
            labels = self.driver.find_elements_by_xpath(label_name)
        for label in labels:
            if content['name'] in re.sub(r'\s+', '', label.text).strip():
                # 如果字段没有id属性,则利用js通过层级关系找
                ele_list = self.driver.find_elements_by_id(label.get_attribute('for'))
                if ele_list:
                    # 存在相同id的情况,移除隐藏的
                    for e in ele_list:
                        if 'o_form_invisible' in e.get_attribute('class'):
                            ele_list.remove(e)
                    ele = ele_list[0]
                else:
                    # 日期的input和textarea都没有id
                    js = "let father = arguments[0].parentNode.nextElementSibling;" \
                         "return father.getElementsByClassName('o_form_input_file')[0]" \
                         "|| father.getElementsByClassName('o_datepicker_input')[0]" \
                         "|| father.getElementsByTagName('textarea')[0];"
                    ele = self.driver.execute_script(js, label)
                if ele.tag_name == 'select':
                    # selection字段
                    Select(ele).select_by_visible_text(content['content'])
                elif 'ui-autocomplete-input' in ele.get_attribute('class'):
                    # m2o字段
                    ele.clear()
                    ele.send_keys(content['content'])
                    sleep(0.5)
                    ele.send_keys(Keys.ENTER)
                elif 'o_datepicker_input' in ele.get_attribute('class'):
                    # date字段
                    if content['content']:
                        ele.clear()
                        ele.send_keys(content['content'])
                    else:
                        ele.click()
                    # 解决前端报错弹窗
                    self.click_blank()
                    self.dialog_button(1)
                elif 'o_form_input_file' in ele.get_attribute('class'):
                    # 文件
                    ele.send_keys(content['content'])
                else:
                    # char和float等
                    ele.clear()
                    ele.send_keys(content['content'])
                break

    def table_add(self, content):
        """
        表格底部追加: 添加项目 - 按照表格填写顺序填写内容
        """
        # 添加项目
        add_btn = self.is_exist('//div[@class="o_form_field o_form_field_one2many o_view_manager_content"]//a')
        add_btn.click()
        # 表格中的input
        input_xpath = f'//div[@class="o_form_field o_form_field_one2many o_view_manager_content"]//input'
        inputs = self.driver.find_elements_by_xpath(input_xpath)
        # 按照顺序填写内容
        for row in content['row']:
            for step in row:
                inputs[step['index'] - 1].click()
                if step.get('content'):
                    inputs[step['index'] - 1].clear()
                    # clear float时会弹窗,点击取消
                    self.dialog_button(2)
                    inputs[step['index'] - 1].send_keys(step['content'])
                    sleep(0.5)
            else:
                add_btn.click()
                sleep(1)

    def table_edit(self, content):
        """
        o2m 编辑: 点击对应行 -
                弹窗: 和填写普通表单一样 - 确定
                直接编辑: 根据表头找到对应的输入框 - 输入内容 - 点击空白处使表格回到未选中状态
        """
        for index, row_contents in content["row"].items():
            index = int(index) - 1
            rows = self.driver.find_elements_by_xpath(
                '//div[@class="o_form_field o_form_field_one2many o_view_manager_content"]//table//tr[@data-id]')
            rows[index].click()
            sleep(1)
            if self.is_exist('//div[contains(@class,"modal-dialog")]'):
                # 弹窗
                for row_content in row_contents:
                    self.general_content('xpath', '//div[contains(@class,"modal-dialog")]//label', row_content)
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

                for row_content in row_contents:
                    # 找到name对应table的索引
                    for head_index, head in enumerate(heads):
                        if head.text == row_content["name"]:
                            table_index = head_index
                            break
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

                    table_input.send_keys(row_content["content"])
                    # 如果是m2o,则回车
                    if m2o:
                        sleep(0.5)
                        table_input.send_keys(Keys.ENTER)
                    self.dialog_button(2)
                # 点击空白处,使表格回到未选中状态
                self.click_blank()

    def table_m2m(self, content):
        """
        m2m表: 添加项目 - 点击选项前面的input - 确定
        """
        sleep(1)
        self.clickable('//td[@class="o_form_field_x2many_list_row_add"]/a').click()
        sleep(1)
        if self.is_exist('//div[contains(@class,"modal-dialog")]'):
            inputs = self.driver.find_elements_by_xpath('//div[contains(@class,"modal-dialog")]//tbody//input')
            for index in content['content']:
                inputs[index - 1].click()
            self.dialog_button(1)
        sleep(1)

    def file(self, content):
        pass


if __name__ == '__main__':
    d = Driver('http://127.0.0.1:8069/web')
    d.execute('./factory_erp/test.json')
