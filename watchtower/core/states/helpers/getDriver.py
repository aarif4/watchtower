from core.states.helpers._common_imports import *

def getDriver(want_js=False, executable=''):
    # TODO: Maybe you can search for it
    # - look up user's name
    # - search in the following paths using os or sys depending on platform: (dir "----")
    #   - C:\Users\%username%\AppData\Local\Mozilla Firefox\firefox.exe
    #   - C:\Program Files\Mozilla Firefox\firefox.exe
    #   - C:\Program Files (x86)\Mozilla Firefox\firefox.exe
    #   - /usr/bin/firefox
    profile = webdriver.FirefoxProfile()
    cap = webdriver.common.desired_capabilities.DesiredCapabilities().FIREFOX
    cap["marionette"] = True #optional
    options = Options()
    options.preferences.update({"javascript.enabled": want_js})
    options.binary = executable
    driver = webdriver.Firefox(options=options, capabilities=cap, executable_path=GeckoDriverManager().install(), firefox_profile=profile)

    return driver
