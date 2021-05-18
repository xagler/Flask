from flask import Flask, render_template, request
import xmltodict
import requests
from bs4 import BeautifulSoup as bs
import json
from multiprocessing import Pool
import sendgrid
import threading
from sendgrid.helpers.mail import *
import xlsxwriter
import base64



app = Flask(__name__)



@app.route('/')
def hello_world():
    # price_name = get_xml()
    # process(price_name)
    return render_template('index.html')


@app.route('/handle_data', methods=['POST'])
def handle_data():
    email = request.form['email']
    password = request.form['password']
    if password != '228899':
        return '<h1>Не правильный пароль</h1>'
    else:
        threading.Thread(target=process, args=(email,)).start()
        return f'<h1>Парсинг успешно запущен, ждите письмо через час на {email}</h1>'


def get_xml():
    res = []
    url = 'https://tralivali.ua/yandex_market.xml?hash_tag=73182ed29583ac4c82e3edb89ad9894e&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=0&yandex_cpa=&process_presence_sure=&export_lang=ru&languages=&group_ids='
    while True:
        try:
            with requests.get(url, stream=True, timeout=5000) as f:
                doc = xmltodict.parse(f.content.decode('utf-8'))
                break
        except:
            pass

    # with open('tralivali.xml',encoding='utf-8') as f:
    #     doc = xmltodict.parse(f.read())
    for offer in doc['yml_catalog']['shop']['offers']['offer']:
        try:
            for key in offer['param']:
                if key['@name'] == 'Артикул':
                    off = []
                    off.append(offer['name'])
                    off.append(offer['price'])
                    off.append(key['#text'])
                    off.append(offer['vendorCode'])
                    res.append(off)
        except:
            pass
    print('Скачали xml')
    return res




def process(email):
    print(email)
    price_name = get_xml()
    rozetka_list = []
    antoshka_list = []
    babyshop_list = []
    panama_list = []
    bi_list = []
    header = ['VendorCode','Артикул',	'Tralivali',	'Tralivali Цена',	'Rozetka',	'Rozetka Цена',	'Antoshka',	'Antoshka Цена',	'Babyshop',	'Babyshop Цена',	'Panama',	'Panama Цена',	'Bi',	'Bi Цена']
    new_list = []
    new_list.append(header)

    print('Parsing Panama')
    pool = Pool(5)
    rez = (pool.map(panama, price_name))
    for line in rez:
        if line != None:
            panama_list.append(line)



    print('Parsing ROZETKA')
    pool = Pool(5)
    rez = (pool.map(rozetka,price_name))
    for line in rez:
        if line != None:
            rozetka_list.append(line)


    print('Parsing ANTOSHKA')
    pool = Pool(5)
    rez = (pool.map(antushka, price_name))
    for line in rez:
        if line != None:
            antoshka_list.append(line)

    print('Parsing BABYSHOP')
    pool = Pool(5)
    rez = (pool.map(babyshop, price_name))
    for line in rez:
        if line != None:
            babyshop_list.append(line)
    print('Parsing Panama')
    pool = Pool(5)
    rez = (pool.map(panama, price_name))
    for line in rez:
        if line != None:
            panama_list.append(line)
    print('Parsing bi')
    pool = Pool(5)
    rez = (pool.map(bi_ua, price_name))
    for line in rez:
        if line != None:
            bi_list.append(line)


    for line in price_name:
        temp_list = []
        temp_list.append(line[-1])
        a = 0
        temp_list.append(line[2])
        temp_list.append(line[0])
        temp_list.append(line[1])
        for el in rozetka_list:
            if line[2] == el[0]:
                temp_list.append(el[4])
                temp_list.append(el[3])
                a = 1
        if a == 0:
            temp_list.append('')
            temp_list.append('')

        a = 0

        for el in antoshka_list:
            if line[2] == el[0]:

                temp_list.append(el[4])
                temp_list.append(el[3])
                a = 1
        if a == 0:
            temp_list.append('')
            temp_list.append('')
        a = 0

        for el in babyshop_list:
            if line[2] == el[0]:
                temp_list.append(el[4])
                temp_list.append(el[3])
                a = 1
        if a == 0:
            temp_list.append('')
            temp_list.append('')
        a = 0

        for el in panama_list:
            if line[2] == el[0]:
                temp_list.append(el[4])
                temp_list.append(el[3])
                a = 1
        if a == 0:
            temp_list.append('')
            temp_list.append('')

        a = 0

        for el in bi_list:
            if line[2] == el[0]:
                temp_list.append(el[4])
                temp_list.append(el[3])
                a = 1
        if a == 0:
            temp_list.append('')
            temp_list.append('')
        if len(temp_list) < 15:
            new_list.append(temp_list)




    with xlsxwriter.Workbook('test.xlsx') as workbook:
        worksheet = workbook.add_worksheet()

        for row_num, data in enumerate(new_list):
            worksheet.write_row(row_num, 0, data)

    send_mail(email,'test.xlsx')






def bi_ua(line):
    rez = []
    name = line[0]
    our_price = line[1].strip()
    art = line[2]
    r = requests.get('https://bi.ua/ukr/gsearch/?search=' + art)
    soup = bs(r.text, 'html.parser')
    try:
        site_price = soup.find('div', 'goodsItem p01').find('a', 'goodsItemLink').find('p', 'costIco').getText().replace(' ','').replace('грн','')
        site_name = soup.find('span','itemDes').getText().strip()
        if int(site_price) != int(our_price):
            rez.append(art)
            rez.append(name)
            rez.append(our_price)
            rez.append(site_price)
            rez.append(site_name)
            rez.append('BI.UA')
            print(rez)
            return rez
    except:
        pass

def antushka(line):
    rez = []
    name = line[0]
    our_price = line[1].strip()
    art = line[2]
    r = requests.get('https://antoshka.ua/catalogsearch/result/?q=' + art)
    soup = bs(r.text,'html.parser')
    try:
        site_price = soup.find('div','item-content-block').find('div','price').getText().strip().replace('грн','').replace(' .','').replace(' ','')
        site_name = soup.find('p','h2 goods-name').getText().strip()
        if int(site_price) != int(our_price):
            rez.append(art)
            rez.append(name)
            rez.append(our_price)
            rez.append(site_price)
            rez.append(site_name)
            rez.append('ANTOSHKA.UA')
            print(rez)
            return rez
    except:
        pass

def babyshop(line):
    name = line[0]
    our_price = line[1].strip()
    art = line[2]
    rez = []
    headers = {
        'Accept': 'application / json, text / plain, * / *',
        'Project': 'bbs',
        'Referer': 'https://babyshop.ua/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'

    }
    r = requests.get(f'https://babyshop.ua/api/search/public/products?title={art}&hasImage=1&limit=10&page=0&withPrice=1&v=5485ee98&locale=ru',headers=headers)
    y = json.loads(r.text)
    try:
        price = y['items'][0]['probablyPriceSelling']
        site_name = y['items'][0]['title']
        if int(price) != int(our_price):
            rez.append(art)
            rez.append(name)
            rez.append(our_price)
            rez.append(price)
            rez.append(site_name)
            rez.append('BABYSHOP.UA')
            print(rez)
            return rez
    except:
        pass

def panama(line):
    name = line[0]
    our_price = line[1].strip()
    art = line[2]
    rez = []
    try:
        r = requests.get('https://panama.ua/suggest/?q='+name)
        print(r.status_code)
        y = json.loads(r.text)
        r = requests.get('https://panama.ua'+y['list'][0]['link'])
        print(r.status_code)

        soup = bs(r.text,'html.parser')
        site_price = soup.find('div','product__price').getText().replace('грн.','')
        site_name = soup.find('span','product-item__name').getText()
        if art in r.text:
            if int(our_price) != int(site_price):
                rez.append(art)
                rez.append(name)
                rez.append(our_price)
                rez.append(site_price)
                rez.append(site_name)
                rez.append('PANAMA.UA')
                print(rez)
                return rez
    except:
        pass

def epicentr(line):
    name = line[0]
    our_price = line[1].strip()
    art = line[2]
    rez = []
    r = requests.get(f'https://epicentrk.ua/search/?q={name}')
    print(r.status_code)
    try:
        soup = bs(r.text, 'html.parser')
        site_name = soup.find('div','card__name').getText().strip()

        if site_name == name:
            site_price = soup.find('span','card__price-sum').getText().strip().replace('₴','')
            if site_price == our_price:
                return False
            else:
                rez.append(art)
                rez.append(name)
                rez.append(our_price)
                rez.append(site_price)
                rez.append('EPICENTR.UA')
                print(rez)
                return rez
        else:
            return False
    except:
        return False

def rozetka(line):
    rez = []
    name = line[0]
    our_price = line[1].strip()
    art = line[2]
    r = requests.get(f'https://search.rozetka.com.ua/search/api/v4/autocomplete/?front-type=xl&country=UA&lang=ru&text={art}')
    if r.status_code == 200:
        try:
            doc = json.loads(r.text)
            site_price = doc['data']['content']['records']['goods'][0]['price']
            site_name = doc['data']['content']['records']['goods'][0]['title']
            if str(our_price) != str(site_price):
                rez.append(art)
                rez.append(name)
                rez.append(our_price)
                rez.append(site_price)
                rez.append(site_name)
                rez.append('ROZETKA.COM.UA')
                print(rez)
                return rez
        except:
            pass

    else:
        print('ЗАБАНИЛИ!!!!!!')


def send_mail(to_mail,filename):
    message = Mail(
        from_email='vladislav.bbad@gmail.com',
        to_emails=to_mail,
        subject='Результат парсинга!',
        html_content='<strong>Результат парсинга!</strong>'
    )

    with open(filename, 'rb') as f:
        data = f.read()
        f.close()
    encoded_file = base64.b64encode(data).decode()

    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName('Результат.xlsx'),
        FileType('application/xlsx'),
        Disposition('attachment')
    )
    message.attachment = attachedFile

    sg = sendgrid.SendGridAPIClient('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')
    response = sg.send(message)
    print(response.status_code, response.body, response.headers)


if __name__ == '__main__':
    app.run()
