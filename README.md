# OdooUITest
odooUI自动化测试



## 目的

解决自测过程中重复填写数据的操作  →  自动化测试  →  免代码（只需配置json）自动化测试

odoo页面每次重新生成，页面id总是变化的，无法使用一些工具如：[Selenium IDE](https://www.selenium.dev/selenium-ide/)



## 环境

- Python 3.8
- Selenium 3.141.0
- Ubuntu
- Google Chrome



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



## 配置

- 流程（操作流程配置，比如登录-打开页面-填充内容-发起-换号-通过等流程）
- 工作流（工作流按钮配置，基本不需要修改）
- 账号密码（配置流程时只需填写用户名，不用每次填写账号密码）



## 待办

- [ ] 增加页面配置，减少流程配置量
- [ ] 重构流程配置中内容填充部分，减少流程配置量
- [ ] 适配多平台
- [ ] 适配多浏览器



