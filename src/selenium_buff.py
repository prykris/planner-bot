import pyperclip
from selenium.webdriver import Keys, ActionChains


def paste_content(driver, el, content):
    el.click()
    pyperclip.copy(content)
    act = ActionChains(driver)
    act.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
