# -*- coding: utf-8 -*-
import json
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class Driver:
    def __init__(self, url):
        self.url = url
        self.userInfo = self.load_json('./config/userInfo.json')

        self.model = ''
        self.id = ''

        self.driver = webdriver.Chrome(executable_path='./Driver/chromedriver')
        self.driver.get(self.url)

    def close(self):
        """
        关闭浏览器
        """
        self.driver.close()

    def choose_databases(self):
        """
        选择第一个数据库
        """
        databases = self.is_exist('/html/body/div[1]/div/div[3]/a[1]')
        if databases:
            databases.click()

    @staticmethod
    def load_json(path):
        """
        加载json
        :param path: json文件路径
        """
        with open(path)as f:
            return json.loads(f.read())

    def clickable(self, xpath):
        """
        等待直到按钮可点击, 超时报错
        :param xpath: xpath
        :return: 按钮
        """
        wait = WebDriverWait(self.driver, 5)  # 等待的最大时间
        try:
            # 判断该元素是否可点击
            return wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutException:
            print('加载超时')
            exit()

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

    def login(self, name):
        """
        选择登录方式 - 输入账号密码
        :param name: userInfo中配置名
        """
        # 选择数据库
        self.choose_databases()
        # 选择账户登录
        self.driver.find_element_by_xpath('/html/body/div/div[2]/a').click()
        # 账号密码登录
        self.driver.find_element_by_xpath('//*[@id="login"]').send_keys(self.userInfo[name]['username'])
        self.driver.find_element_by_xpath('//*[@id="password"]').send_keys(self.userInfo[name]['password'])
        self.driver.find_element_by_xpath('/html/body/form/div[3]/button').click()

    def open(self, name):
        """
        根据名字打开对应页面
        :param name: 页面名
        """
        if name != -1:
            # 获取页面url
            href = self.driver.find_element_by_xpath(f'//a[@data-menu-name="{name}"]').get_attribute('href')
            self.driver.get(href)
            sleep(1)
            # 有时跳转需要点击左上角Apps切换页面
            body = self.driver.find_element_by_tag_name('body')
            if 'drawer-open' in body.get_attribute('class'):
                self.driver.find_element_by_xpath('//a[@class="app-drawer-icon-close drawer-toggle"]').click()
            sleep(0.5)
        else:
            url = f'{self.url}#id={self.id}&view_type=form&model={self.model}'
            self.driver.get(url)

    def create(self):
        """
        点击创建
        """
        # 创建
        create_btn = self.clickable('/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/div/button')
        create_btn.click()
        sleep(1)
