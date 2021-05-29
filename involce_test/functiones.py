from hashlib import sha256
from const import SHOPID, SECRETKEY, PAYWAY, URL_PAY, URL_INVOICE, URL_BILL
from flask import render_template, redirect
from database import write, get_conn
import requests
import logging


logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


def get_payment(payment_amount):
    payment_amount = float(payment_amount)
    return "%.2f" % payment_amount


def get_html_eur(sign, amount, currency, shop_id, id_order, link):
    html = f"""<form name="Pay" method="post" action='{link}' accept-charset="UTF-8"> 
     <input type="hidden" name="amount" value='{amount}'/>
     <input type="hidden" name="currency" value='{currency}'/> 
     <input type="hidden" name="shop_id" value='{shop_id}'/> 
     <input type="hidden" name="sign" value='{sign}'/> 
     <input type="hidden" name="shop_order_id" value='{id_order}'/>
     <input type="submit"/> <input type="hidden" name="description" value="Test invoice"/>
     </form>""".format(link=link, amount=amount, currency=currency, shop_id=shop_id, id_order=id_order, sign=sign)
    return html


def get_referer_html_rub(method, url, data, description):
    html = """
    <!--Fragment of HTML page with the payment request form-->
        <form method='{method}' action='{url}'>
        <input type="hidden" name="ac_account_email" value='{email}'>
        <input type="hidden" name="ac_sci_name" value='{name}'>
        <input type="hidden" name="ac_amount" value='{amount}'>
        <input type="hidden" name="ac_currency" value='{currency}'>
        <input type="hidden" name="ac_order_id" value='{order_id}'>
        <input type="hidden" name="ac_sub_merchant_url" value= '{sub_url}' >
        <input type="hidden" name="ac_sign" value='{sign}'>
        <input type="submit">
        <input type="hidden" name="ac_comments" value='{description}'>
        <!-- Merchant custom fields -->
        </form>
        <!--Fragment of HTML page with the payment request form-->
    """.format(method=method,
               url=url,
               email=data['ac_account_email'],
               name=data['ac_sci_name'],
               amount=data['ac_amount'],
               currency=data['ac_currency'],
               order_id=data['ac_order_id'],
               sub_url=data['ac_sub_merchant_url'],
               sign=data['ac_sign'],
               description=description)
    return html


def get_sign_decorator(func):
    def return_func(*args, **kwargs):
        return sha256(func(*args, **kwargs).encode('utf-8')).hexdigest()
    return return_func


@get_sign_decorator
def get_sign_eur(payment_amount, currency, shop_id, id_order):
    return ":".join([payment_amount, currency, shop_id, id_order]) + SECRETKEY


@get_sign_decorator
def get_sign_rub(amount, currency, payway, shop_id, shop_order_id):
    return ":".join([amount, currency, payway, shop_id, shop_order_id]) + SECRETKEY


@get_sign_decorator
def get_sign_usd(payment_amount, currency_payer, shop_id, id_order):
    return ":".join([currency_payer, payment_amount, currency_payer, shop_id, id_order]) + SECRETKEY


def get_id_order(cursor):
    cursor.execute("SELECT MAX(id) FROM orders")
    return cursor.fetchall()[0][0]


def pay_rub(payment_amount, product_description):
    currency = 643
    conn = get_conn()
    cursor = conn.cursor()
    write(payment_amount, currency, product_description, conn)
    id_order = get_id_order(cursor)
    sign = get_sign_rub(payment_amount, str(currency), PAYWAY, str(SHOPID), str(id_order))
    piastrix_request_data = {
        "currency": str(currency),
        "sign": sign,
        "payway": PAYWAY,
        "amount": str(payment_amount),
        "shop_id": str(SHOPID),
        "shop_order_id": str(id_order),
        "description": product_description
    }
    try:
        response = requests.post(URL_INVOICE, json=piastrix_request_data)
        if response.json()['data'] is None:
            conn.rollback()
            return render_template("index.html", mes=response.json()['message'])
        data = response.json()['data']['data']
    except Exception as e:
        logging.exception(f'error: {e}'.format(e=e))
        conn.rollback()
        return render_template("index.html", mes="Please try later")
    method = response.json()['data']['method']
    url = response.json()['data']['url']
    conn.commit()
    logging.info(f'Form submitted successfully id_order:{id_order} curency:{currency} amount{payment_amount}'.format(
        id_order=str(id_order),
        currency=str(currency),
        payment_amount=payment_amount))
    return get_referer_html_rub(method, url, data, product_description)


def pay_eur(payment_amount, product_description):
    currency = 978
    conn = get_conn()
    cursor = conn.cursor()
    write(payment_amount, currency, product_description, conn)
    id_order = get_id_order(cursor)
    sign = get_sign_eur(payment_amount, str(currency), str(SHOPID), str(id_order))
    try:
        html = get_html_eur(sign, payment_amount, currency, SHOPID, id_order, URL_PAY)
    except Exception as e:
        logging.exception(f'error: {e}'.format(e=e))
        conn.rollback()
        return render_template("index.html", mes="Please try later")
    logging.info(f'Form submitted successfully id_order:{str(id_order)} curency:{str(currency)} amount:{payment_amount}')
    return html


def pay_usd(payment_amount, product_description):
    currency = 840
    conn = get_conn()
    cursor = conn.cursor()
    write(payment_amount, currency, product_description, conn)
    id_order = get_id_order(cursor)
    sign = get_sign_usd(payment_amount, str(currency), str(SHOPID), str(id_order))
    piastrix_request_data = {
        "description": product_description,
        "payer_currency": currency,
        "shop_amount": payment_amount,
        "shop_currency": currency,
        "shop_id": SHOPID,
        "shop_order_id": id_order,
        "sign": sign
    }
    try:
        json = requests.post(URL_BILL, json=piastrix_request_data).json()
        if json["data"] is None:
            conn.rollback()
            if json['message']:
                e = json['message']
                logging.warning(f'error: {e}'.format(e=e))
            return render_template("index.html", mes=json['message'])
    except Exception as e:
        logging.exception(f'error: {e}'.format(e=e))
        return render_template("index.html", mes="Please try later")
    conn.commit()
    logging.info(f'Form submitted successfully id_order:{id_order} curency:{currency} amount{payment_amount}'.format(
        id_order=str(id_order),
        currency=str(currency),
        payment_amount=payment_amount))
    return redirect(json['data']['url'])
