import time
import json
import os
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from NSM.src.utils import utils


class TaoBao:
    fileCWD = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        options = webdriver.ChromeOptions()
        self.get_user_info()
        if utils.is_windows():
            options.binary_location = self.chromepath

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("prefs", {"prfile.managed_default_content_setting.images": 2})
        self.browser = webdriver.Chrome(options=options, executable_path=self.get_chromedriver_exe_path())

        # 反爬设置  webdriver为 undefined
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
        			Object.defineProperty(navigator, 'webdriver', {
        			  get: () => undefined
        			})
        		  """
        })
        self.wait = WebDriverWait(self.browser, 10)
        self.loginurl = "https://login.taobao.com/member/login.jhtml"
        self.trytime = 0
        self.excelfile = "%s.xlsx" % self.keyword

    # 从config.json 文件中读取相关的配置
    def get_user_info(self):
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        self.username = config["username"]
        self.password = config["password"]
        self.keyword = config["keyword"]
        self.maxpage = config["maxpage"]
        self.chromepath = config["chromepath"]
        # print(self.password)

    # 获取不同平台的chromedriver的路径
    def get_chromedriver_exe_path(self):
        ret = "./bin/mac/chromedriver"
        if utils.is_windows():
            ret = "D:\Python\Python39\Scripts\chromedriver.exe"
        return ret

    def login(self):
        self.browser.get(self.loginurl)
        try:
            # 找到用户名输入框,输入账号密码并登录
            username_input = self.wait.until(EC.presence_of_element_located((By.ID, "fm-login-id")))
            username_input.send_keys(self.username)

            password_input = self.wait.until(EC.presence_of_element_located((By.ID, "fm-login-password")))
            password_input.send_keys(self.password)

            login_button = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fm-button")))
            login_button.click()
            time.sleep(5)
            # # 检查是否需要验证码登陆
            # while 1:
            #     try:
            #         self.browser.find_element_by_id('J_Phone_Checkcode')
            #     except:
            #         break
            # time.sleep(2)
            # ”site-nav-login-info-nick” 找到名字标签并打印内容
            taobao_name_tag = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "site-nav-login-info-nick ")))
            print(f"登录成功:{taobao_name_tag.text}")
        except Exception as e:
            print(e)
            self.browser.close()
            print("登录失败")

    # 爬取相关的内容
    def crawl(self):
        self.detail_page('600344949083')

    # 爬详情页面信息
    def detail_page(self, productId):
        print('detail_page start...')
        url = "https://detail.tmall.com/item.htm?id=" + productId
        self.browser.get(url)
        time.sleep(2)

        # 点击颜色分类小图，加载图片
        items = self.browser.find_elements_by_xpath('//*[@id="J_DetailMeta"]/div[1]/div[1]/div/div[4]/div/div/dl[1]/dd/ul/li')
        for item in items:
            item.click()
            time.sleep(1)

        # 滚动条操作
        new_height = self.browser.execute_script("return document.body.scrollHeight;")
        for i in range(math.ceil(new_height/500)):
            self.browser.execute_script('window.scrollTo(0, '+str(500*(i+1))+')')
            time.sleep(1)

        idx = 0
        items = self.browser.find_elements_by_xpath('/html/body/div/img')
        for item in items:
            pic = item.get_attribute("src")
            if "430x430q90" in pic:
                continue
            idx += 1
            utils.saveImg(pic, self.fileCWD + '\\pic\\' + productId, 'a'+str(idx) + '.jpg')
            print(pic)

        idx = 0
        items = self.browser.find_elements_by_xpath('//*[@id="description"]/div/p/img')
        for item in items:
            pic = item.get_attribute("src")
            idx += 1
            utils.saveImg(pic, self.fileCWD + '\\pic\\' + productId, 'b'+str(idx) + '.jpg')
            print(pic)


if __name__ == "__main__":
    tb = TaoBao()
    tb.login()
    tb.crawl()
