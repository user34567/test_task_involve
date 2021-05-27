from flask import Flask, render_template, request
from functiones import eur_pay, usd_pay, rub_pay, get_payment, db


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "GET":
        return render_template("index.html", mes="")
    else:
        payment_amount = request.form["payment_amount"]
        currency = request.form["currency"]
        product_description = request.form["product_description"]
        if currency == "Выберите валюту":
            return render_template("index.html", mes="Выберите валюту")
        else:
            payment_amount = get_payment(payment_amount)
            id_order = db.get_last_id()
            if id_order is None:
                id_order = 1
            else:
                id_order = id_order + 1
            if currency == "eur":
                return eur_pay(payment_amount, id_order, product_description)
            if currency == "usd":
                return usd_pay(payment_amount, id_order, product_description)
            if currency == "rub":
                return rub_pay(payment_amount, id_order, product_description)


if __name__ == "__main__":
    app.run()
