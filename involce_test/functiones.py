from hashlib import sha256
from const import *
from flask import render_template, redirect
from database import Database
import requests
from datetime import datetime
import logging

db = Database()
logging.basicConfig(filename='test.log',level=logging.INFO)


def log(message, id_order, amount, currency, error=None):
    message = message + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message = message + " id_order=" + str(id_order) + " amount=" + str(amount) + " currency=" + str(currency)
    if error is not None:
        message = message + " error='" + error + "'"
    logging.info(message)


def get_payment(payment_amount):
    if len(payment_amount) == 1:
        payment_amount = payment_amount + ".00"
    if payment_amount[len(payment_amount) - 3] != "." and len(payment_amount) != 1:
        if payment_amount[len(payment_amount) - 2] == ".":
            payment_amount = payment_amount + "0"
        else:
            payment_amount = payment_amount + ".00"
    return payment_amount


def get_sign_rub(amount, currency, payway, shop_id, shop_order_id):
    sign = str(amount) + ":" + str(currency) + ":" + str(payway) + ":" + str(shop_id) + ":" + str(shop_order_id)
    sign = sign + SECRETKEY
    sign = sha256(sign.encode('utf-8')).hexdigest()
    return sign


def get_html_eur(sign, amount, currency, shop_id, id_order, link):
    html = """<form name="Pay" method="post" action='""" + link + """' accept-charset="UTF-8"> 
     <input type="hidden" name="amount" value='""" + str(amount) + """'/>
     <input type="hidden" name="currency" value='""" + str(currency) + """'/> 
     <input type="hidden" name="shop_id" value='""" + str(shop_id) + """'/> 
     <input type="hidden" name="sign" value='""" + sign + """'/> 
     <input type="hidden" name="shop_order_id" value='""" + str(id_order) + """'/>
     <input type="submit"/> <input type="hidden" name="description" value="Test invoice"/> </form>"""
    return html


def get_referer_html_rub(method, url, data, description):
    html = """
    <!--Fragment of HTML page with the payment request form-->
        <form method='""" + method + """' action='""" + url + """'>
        <input type="hidden" name="ac_account_email" value='""" + data['ac_account_email'] + """'>
        <input type="hidden" name="ac_sci_name" value='""" + data['ac_sci_name'] + """'>
        <input type="hidden" name="ac_amount" value='""" + data['ac_amount']+"""'>
        <input type="hidden" name="ac_currency" value='""" + data['ac_currency'] + """'>
        <input type="hidden" name="ac_order_id" value='""" + data['ac_order_id']+"""'>
        <input type="hidden" name="ac_sub_merchant_url" value= '""" + data['ac_sub_merchant_url'] + """' >
        <input type="hidden" name="ac_sign" value='"""+data['ac_sign'] + """'>
        <input type="submit">
        <input type="hidden" name="ac_comments" value='""" + description + """'>
        <!-- Merchant custom fields -->
        </form>
        <!--Fragment of HTML page with the payment request form-->
    """
    return html


def get_sign_eur(payment_amount, currency, shop_id, id_order):
    sign = payment_amount + ":" + str(currency) + ":" + str(shop_id) + ":" + str(id_order) + SECRETKEY
    sign = sha256(sign.encode('utf-8')).hexdigest()
    return sign


def get_sign_usd(payment_amount, currency_payer, shop_id, id_order):
    sign = str(currency_payer) + ":" + str(payment_amount) + ":" + str(currency_payer) + ":" + str(shop_id) + ":"
    sign = sign + str(id_order) + SECRETKEY
    sign = sha256(sign.encode('utf-8')).hexdigest()
    return sign


def rub_pay(payment_amount, id_order, product_description):
    currency = 643
    log("Try to execute", id_order, payment_amount, currency)
    sign = get_sign_rub(payment_amount, currency, PAYWAY, SHOPID, id_order)
    piastrix_request_data = {
        "currency": str(currency),
        "sign": sign,
        "payway": PAYWAY,
        "amount": str(payment_amount),
        "shop_id": str(SHOPID),
        "shop_order_id": str(id_order),
        "description": product_description
    }
    response = requests.post(URL_INVOICE, json=piastrix_request_data)
    if response.json()['data'] is None:
        log("Execute error", id_order, payment_amount, currency, error=response.json()['message'])
        return render_template("index.html", mes=response.json()['message'])
    data = response.json()['data']['data']
    method = response.json()['data']['method']
    url = response.json()['data']['url']
    db.write(payment_amount, currency, product_description)
    log("Successfully execute", id_order, payment_amount, currency)
    return get_referer_html_rub(method, url, data, product_description)


def eur_pay(payment_amount, id_order, product_description):
    currency = 978
    log("Try to execute", id_order, payment_amount, currency)
    sign = get_sign_eur(payment_amount, currency, SHOPID, id_order)
    db.write(payment_amount, currency, product_description)
    log("Successfully execute", id_order, payment_amount, currency)
    return get_html_eur(sign, payment_amount, currency, SHOPID, id_order, URL_PAY)


def usd_pay(payment_amount, id_order, product_description):
    currency = 840
    log("Try to execute", id_order, payment_amount, currency)
    sign = get_sign_usd(payment_amount, currency, SHOPID, id_order)
    piastrix_request_data = {"description": product_description,
                             "payer_currency": currency,
                             "shop_amount": payment_amount,
                             "shop_currency": currency,
                             "shop_id": SHOPID,
                             "shop_order_id": id_order,
                             "sign": sign
                             }
    json = requests.post(URL_BILL, json=piastrix_request_data).json()
    if json["data"] is None:
        log("Execute error", id_order, payment_amount, currency, error=json['message'])
        return render_template("index.html", mes=json['message'])
    db.write(payment_amount, currency, product_description)
    log("Successfully execute", id_order, payment_amount, currency)
    return redirect(json['data']['url'])
