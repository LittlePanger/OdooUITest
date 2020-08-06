# -*- coding: utf-8 -*-
import os
import sys

from OdooTest import OdooTest

if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = './TestCase/subcontract/外协分包合同扣款登记表site.json'
    if not os.path.exists(path):
        print('文件路径错误')
        exit()
    o = OdooTest('http://127.0.0.1:8069/web')
    o.execute(path)
