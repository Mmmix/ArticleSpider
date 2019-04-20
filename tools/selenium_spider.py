from selenium import webdriver

browser = webdriver.Chrome(executable_path="H:/毕业设计/chromedriver.exe")

browser.get("http://www.taobao.com")

print(browser.page_source)

# browser.quit()