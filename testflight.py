import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
from multiprocessing import Process

app_mapping = {}
with open('testflight.txt', 'r') as file:
    for line in file:
        app, code = line.strip().split(':')
        app_mapping[app] = code

config = {}
with open('config.txt', 'r') as file:
    for line in file:
        key, value = line.strip().split('=')
        config[key] = value

telegram_token = config['telegram_token']
chat_id = config['chat_id']

def send_telegram_message(message):
    send_text = 'https://api.telegram.org/bot' + telegram_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + message
    response = requests.get(send_text)
    return response.json()

def check_beta(app_name):
    id = app_mapping.get(app_name)
    if id:
        url = "https://testflight.apple.com/join/" + id
        beta_available = False

        with requests.Session() as s:
            while True:
                response = s.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')

                beta_message = soup.find('span', string=lambda text: 'beta, open the link on your iPhone, iPad, or Mac after you install TestFlight.' in str(text))
                if beta_message is not None and not beta_available:
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    print(current_time + " Đã tìm thấy bản beta " + app_name + " " + url)
                    send_telegram_message(current_time + " Đã tìm thấy bản beta " + app_name + " " + url)
                    beta_available = True
                elif beta_message is None and beta_available:
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    print(current_time + " Bản beta đã hết " + app_name + " " + url)
                    send_telegram_message(current_time + " Bản beta đã hết " + app_name + " " + url)
                    beta_available = False
                time.sleep(1)  # Dừng 1 giây trước khi kiểm tra lại

if __name__ == "__main__":
    print('Tool bắt đầu chạy...')
    # Create processes for each app
    processes = []
    for app_name in app_mapping.keys():
        process = Process(target=check_beta, args=(app_name,))
        processes.append(process)

    # Start all processes
    for process in processes:
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()