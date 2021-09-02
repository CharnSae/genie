import os
import time

import chromedriver_autoinstaller as installer
import selenium.common.exceptions
from selenium import webdriver as wd


class GenieAutoSignIn:
    def __init__(self):
        self.password = ''
        self.download_folder = os.getcwd()
        self.driver = self.install_or_get_chrome_driver()
        self.URL = 'https://www.genie.co.kr/search/searchMain?query=talk%2520%2526%2520talk'
        self.file_name = '프로미스나인_Talk & Talk.mp3'
        self.main_window = None

    def set_password(self):
        self.password = input("공용 비밀번호를 입력해주세요.\n>>")

    def install_or_get_chrome_driver(self):
        chrome_version = installer.get_chrome_version().split('.')[0]
        options = wd.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('prefs', {
            'download.default_directory': self.download_folder,
        })

        try:
            driver = wd.Chrome(f'./{chrome_version}/chromedriver.exe', options=options)
        except:
            installer.install(True)
            driver = wd.Chrome(f'./{chrome_version}/chromedriver.exe', options=options)

        driver.implicitly_wait(3)
        return driver

    def open_genie_web(self):
        self.driver.get(self.URL)
        self.main_window = self.driver.current_window_handle

    def toggle_genie_account_form(self):
        sign_in_toggle_button = self.driver.find_element_by_class_name('btn')
        sign_in_toggle_button.click()

    def sign_in(self, user_id: str):
        self.toggle_genie_account_form()
        sign_in_button = self.driver.find_element_by_class_name('btn-login')
        sign_in_button.click()

        windows = self.driver.window_handles
        sign_in_popup_window = windows[1]
        self.driver.switch_to.window(sign_in_popup_window)

        id_form = self.driver.find_element_by_id('gnb_uxd')
        password_form = self.driver.find_element_by_id('gnb_uxx')
        submit_button = self.driver.find_element_by_class_name('btn-submit')

        id_form.send_keys(user_id)
        password_form.send_keys(self.password)
        submit_button.click()

        time.sleep(0.3)  # due to network delay
        sign_in_message = self.driver.find_element_by_id('signinMessage')
        if len(sign_in_message) > 0 and len(self.driver.window_handles) > 1:
            print(f'에러: {sign_in_message.text}, 직접 로그인하세요.')

        while True:
            if len(self.driver.window_handles) == 1:
                self.driver.switch_to.window(self.main_window)
                self.driver.get(self.URL)
                break

    def delete_mp3_file(self):
        try:
            os.remove(f'{self.download_folder}\\{self.file_name}')
        except FileNotFoundError as e:
            print(e, '\n이미 삭제되었거나 경로에 음원이 없습니다.\n다른 경로에 있을 경우 음원을 직접 삭제해주세요')
            print(f'음원 저장경로는 {os.getcwd()}입니다.\n')

    def sign_out(self):
        self.toggle_genie_account_form()
        try:
            sign_out_button = self.driver.find_element_by_class_name('btn-logout')
            sign_out_button.click()
        except selenium.common.exceptions.NoSuchElementException:
            self.toggle_genie_account_form()
            return

    def get_command(self):
        print('좋아요/음원 다운로드를 진행해주세요.')
        print('완료 후 결제 및 음원 다운로드 창이 켜져있다면 종료한뒤 선택해주세요')
        return input('[1]: 로그아웃 후 다른 아이디로 로그인하기, [2]: 종료\n>>')

    def get_user_id(self):
        return input('로그인할 아이디를 입력하고 엔터를 누르세요\n>>').strip()

    def run(self):
        genie.open_genie_web()
        genie.sign_out()
        genie.set_password()

        while True:
            user_id = self.get_user_id()
            if not user_id or user_id == '\n':
                continue
            genie.sign_in(user_id)

            command = self.get_command()
            while command not in {'1', '2'}:
                command = self.get_command()

            genie.delete_mp3_file()

            if command == '1':
                genie.sign_out()
                continue
            if command == '2':
                self.driver.close()
                return


if __name__ == '__main__':
    genie = GenieAutoSignIn()
    genie.run()
