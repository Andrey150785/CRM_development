from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests, lxml, csv, itertools

headers = {'User-Agent': UserAgent().random}
# ==========================================
'''Для уменьшения кода, применим бесконечный итератор для цикла 
по карточкам товаров(часы), на итерациях будем проверять значение "response.status_code",
прерывая цикл, если отклик будет отличен от [Response 200]'''

with open('info.csv', 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Наименование', 'Артикул', 'Бренд', 'Модель', 'Тип', 'Технология экрана',
                     'Материал корпуса', 'Материал браслета', 'Размер', 'Сайт производителя',
                     'Наличие', 'Цена', 'Старая цена', 'Ссылка на карточку с товаром'])

    for i in itertools.count(1):  # Бесконечный цикл по карточкам товаров(часы).
        url = f'https://parsinger.ru/html/watch/1/1_{i}.html'
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            product_info = soup.find('div', {'class': 'description'})
            writer.writerow([i.split(':')[-1].strip() for i in product_info.text.split('\n') if i][:-1] + [url])
        else:
            break
