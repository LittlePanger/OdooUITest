# -*- coding: utf-8 -*-
def login(driver, username, password):
    driver.get('http://127.0.0.1:8069/web')
    driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/a[1]').click()
    driver.find_element_by_xpath('/html/body/div/div[2]/a').click()
    driver.find_element_by_xpath('//*[@id="login"]').send_keys(username)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
    driver.find_element_by_xpath('/html/body/form/div[3]/button').click()
