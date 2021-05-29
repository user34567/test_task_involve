from flask import Flask, request
from functiones import *


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "GET":
        return render_template("index.html", mes="")
    else:
        try:
            payment_amount = request.form["payment_amount"]
            currency = request.form["currency"]
            product_description = request.form["product_description"]
            if currency == "Выберите валюту":
                return render_template("index.html", mes="Выберите валюту")
            else:
                payment_amount = get_payment(payment_amount)
                if currency == "eur":
                    return pay_eur(payment_amount, product_description)
                if currency == "usd":
                    return pay_usd(payment_amount, product_description)
                if currency == "rub":
                    return pay_rub(payment_amount, product_description)
        except Exception as e:
            logging.exception(f'error: {e}'.format(e=e))
            return render_template("index.html", mes=e)


if __name__ == "__main__":
    app.run(debug=True)
