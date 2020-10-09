# -*- coding: utf-8 -*-
import json
import re
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import ActionChains  # 动作
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from login import login


# executor_url = driver.command_executor._url
# session_id = driver.session_id
# print(session_id)
# print(executor_url)

def is_exist(xpath):
    try:
        flag = driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        flag = False
    return True if flag else False


def in_create(menu):
    sleep(1)
    driver.find_element_by_xpath('//*[@id="appDrawerAppPanelBody"]/ul/li[2]').click()
    # index = int(input('input:')) + 2
    index = menu["first"] + 2
    driver.find_element_by_xpath(f'//*[@id="odooMenuBarNav"]/div/div[1]/ul[2]/li[{index}]/a').click()
    index2 = menu["second"]
    url = driver.find_element_by_xpath(
        f'//*[@id="odooMenuBarNav"]/div/div[1]/ul[2]/li[{index}]//li[{index2}]/a').get_attribute('href')
    driver.get(url)
    sleep(2)
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/div/button').click()


def table_add(i):
    sleep(1)
    # 添加项目
    add_btn = driver.find_element_by_xpath(
        '//div[@class="o_form_field o_form_field_one2many o_view_manager_content"]//a')
    add_btn.click()
    # 表格中的input
    input_xpath = f'//div[@class="o_form_field o_form_field_one2many o_view_manager_content"]//input'
    inputs = driver.find_elements_by_xpath(input_xpath)
    for row in i['row']:
        for step in row:
            inputs[step['index'] - 1].click()
            if step.get('content'):
                inputs[step['index'] - 1].clear()
                # clear float时会弹窗,点击取消
                if is_exist('//*[@class="modal-footer"]//button[2]'):
                    driver.find_element_by_xpath('//*[@class="modal-footer"]//button[2]').click()
                inputs[step['index'] - 1].send_keys(step['content'])
                sleep(0.5)
        else:
            add_btn.click()
            sleep(1)


def input_content(content):
    labels = driver.find_elements_by_tag_name('label')
    sleep(1)
    for i in content:
        sleep(1)
        if i.get('type') == 'tableAdd':
            table_add(i)
        elif i.get('type') == 'tableEdit':
            driver.find_element_by_xpath('//ol[@class="breadcrumb"]/li[@class="active"]').click()

        else:
            for label in labels:
                if i['name'] in re.sub(r'\s+', '', label.text).strip():
                    # 如果字段没有id属性,则利用js通过层级关系找
                    try:
                        ele_list = driver.find_elements_by_id(label.get_attribute('for'))
                        for e in ele_list:
                            if 'o_form_invisible' in e.get_attribute('class'):
                                ele_list.remove(e)
                        ele = ele_list[0]
                    except NoSuchElementException:
                        js = "return arguments[0].parentNode.nextElementSibling.getElementsByTagName('input')[0];"
                        ele = driver.execute_script(js, label)
                    if ele.tag_name == 'select':
                        # selection字段
                        Select(ele).select_by_visible_text(i['content'])
                    elif 'ui-autocomplete-input' in ele.get_attribute('class'):
                        # m2o字段
                        ele.send_keys(i['content'])
                        sleep(0.5)
                        ele.send_keys(Keys.ENTER)
                    elif 'o_datepicker_input' in ele.get_attribute('class'):
                        # date字段
                        ele.click()
                    else:
                        # char和float等
                        ele.clear()
                        ele.send_keys(i['content'])
                    break


if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path='./chromedriver')
    username = 'admin@meow.com'
    pwd = 'admin'
    login(driver, username, pwd)
    filename = 'test.json'
    with open(filename)as f:
        file = json.loads(f.read())
    in_create(file["menu"])
    input_content(file["content"])
    # sleep(5)
    #
