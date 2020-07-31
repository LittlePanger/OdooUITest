# OdooUITest
odooUI自动化测试



## 目的

解决自测过程中重复填写数据的操作  →  自动化测试  →  免代码（只需配置json）自动化测试

odoo页面每次重新生成，页面id总是变化的，无法使用一些工具如：[Selenium IDE](https://www.selenium.dev/selenium-ide/)



## 环境

- Python 3.8
- Selenium 3.141.0
- Ubuntu 18.04.3 LTS
- Google Chrome 79.0.3945.88（正式版本）（64 位）



## 启动

pycharm : 修改path变量, 改为所需json路径

命令行 : python main.py path                 eg :  `python3.8 main.py ./TestCase/picihuafen.json`



## 功能

- 登录、登出
- 打开页面
- 新建、保存
- 工作流
- 内容填充
  - 基础字段填充 eg: Char;Integer;Float;Text;Selection
  - 关系字段填充 eg: Many2one;One2many;Many2many
  - One2many支持底部新增、弹窗新增、直接编辑、弹窗编辑
  - 附件上传
- 生成测试用例



## 配置

- TestCase
    - 测试用例（操作流程配置，比如登录-打开页面-填充内容-发起-换号-通过等流程）
- config
    - wkf_button.json : 工作流按钮配置，基本不需要修改
    - userInfo.json : TestCase配置时只需填写用户名
    - ~~page.json : 页面索引,减少TestCase配置~~



## 待办

- [x] 增加页面配置，减少流程配置量
- [x] 重构流程配置中内容填充部分，减少流程配置量
- [x] 打开页面不能按照索引,角色不一样看到的索引不同,只能按照标签名
- [x] 自动生成case, 减少json的修改
- [ ] m2o字段有个bug,比如下拉框是[1,test11]时,输入1时默认选择第一个,可能选不到1,而选到test11
- [ ] 适配多平台
- [ ] 适配多浏览器



