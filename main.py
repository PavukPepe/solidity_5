import re
from flask import *
from web3 import Web3
from web3.middleware import geth_poa_middleware
from contractinfo import abi, contract_adress
from time import time


app = Flask(__name__)
app.secret_key = 'key'

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=contract_adress, abi=abi)
accounts = w3.eth.accounts

login = None

def errors(e):
    if "У вас недостаточно средств" in str(e):
        flash("У вас недостаточно средств", "error")
    elif "Вы не владелец недвижимости" in str(e):
        flash("Вы не владелец недвижимости", "error")
    elif "Недвижимость недоступна" in str(e):
        flash("Недвижимость недоступна", "error")
    elif "Данное объявление закрыто" in str(e):
        flash("Данное объявление закрыто", "error")
    elif "Владелец не может купить свою недвижимость" in str(e):
        flash("Владелец не может купить свою недвижимость", "error")


@app.route('/', methods=['GET', 'POST'])
def index():
    global login
    if request.method == 'POST':
        login = request.form.get("username")
        password = request.form.get("password")
        try:
            w3.geth.personal.unlock_account(login, password)
            # return render_template('mainpage.html')
            return redirect(url_for('main_page'))
        except:
            flash("Неверный логин или пароль", "error")
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/mainpage')
def main_page():
    ads = contract.functions.getEstates().call()
    return render_template("mainpage.html", ads=ads)


@app.route('/createpage', methods=['GET', 'POST'])
def create_es():
    if request.method == 'POST':
        size = request.form.get("size")
        photo = request.form.get("picture")
        rooms = request.form.get("rooms")
        est = request.form.get("type")

        try:
            contract.functions.createEstate(int(size), str(photo), int(rooms), int(est)).transact({'from': login})
            return redirect(url_for('main_page'))
        except ValueError as e:
            errors(e)
            return render_template("createpage.html")
    return render_template("createpage.html")


@app.route('/create_ad', methods=['GET', 'POST'])
def create_ad():
    if request.method == 'POST':
        est = request.form.get("es_id")
        price = request.form.get("price")
        date = time()
        try:
            contract.functions.createAdd(price, int(date), est).transact({
        "from": login
    })
            return redirect(url_for('main_page'))
        except ValueError as e:
            errors(e)
    return render_template("create_ad.html")


@app.route('/changepage', methods=['GET', 'POST'])
def change_es():
    if request.method == 'POST':
        es_id = request.form.get("es_id")
        is_active = request.form.get("is_active")
        try:
            contract.functions.updateEstateStatus(int(es_id)).transact({'from': login})
            return redirect(url_for('main_page'))
        except ValueError as e:
            errors(e)
    return render_template("changepage.html")


@app.route('/change_ad', methods=['GET', 'POST'])
def change_ad():
    if request.method == 'POST':
        ad_id = request.form.get("ad_id")
        try:
            contract.functions.updateAddStatus(int(ad_id)).transact({'from': login})
            return redirect(url_for('main_page'))
        except ValueError as e:
            errors(e)
    return render_template("change_ad.html")


@app.route('/buypage', methods=['GET', 'POST'])
def buy():
    global login
    if request.method == 'POST':
        ad_id = request.form.get("ad_id")
        value = request.form.get("value")
        value = w3.to_wei(value, 'ether')

        try:
            contract.functions.BuyEstates(int(ad_id)).transact(
                {'from': login, 'value': value, 'gasPrice': w3.to_wei('10', 'ether')})
            return redirect(url_for('main_page'))
        except ValueError as e:
            errors(e)
    return render_template("buypage.html")


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)


