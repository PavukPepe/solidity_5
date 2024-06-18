from web3 import Web3
from web3.middleware import geth_poa_middleware
from contractinfo import abi, contract_adress
from time import time

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=contract_adress, abi=abi)


def auth():
    public_key = input("Введите логин")
    password = input("Введите пароль: ")
    try:
        w3.geth.personal.unlock_account(public_key, password)
        print("Вы успешно авторизировались")
        return public_key
    except Exception as e:
        print(e)
        return None


def registration():
    password = input("Введите пароль: ")
    password2 = input("Повторите пароль: ")
    if password2 == password:
        address = w3.geth.personal.new_account(password)
        print(f"Адрес нового аккаунта: {address}")
    else:
        print("Пароли не совпадают повторите попытку регистрации")


def create_estate(account: str):
    size = int(input("Введите размер недвижимости: "))
    photo = input("Введите хеш изображения: ")
    rooms = int(input("Введите кол-во комнат: "))
    est = int(input("Выберите тип недвижимости:\n1. Дом\n2. Квартира\n3. Лофт\n")) - 1
    estate = contract.functions.createEstate(size, photo, rooms, est).transact({
        "from": account
    })


def create_add(account: str):
    estate = contract.functions.getEstates().call({
        "from": account
    })
    print(*list(filter((lambda tup: tup[4] == account), estate)))
    est = input("Введите ID вашей недвижимости: ")
    price = int(input("Введите стоимость недвижимости: "))
    date = time()
    estate = contract.functions.createAdd(price, date, est).transact({
        "from": account
    })


def transh(account: str):
    amount = int(input("Введите сумму к пополнению"))
    try:
        tx_hash = contract.functions.Transh().transact({
            "from": account,
            "value": amount
        })
        print("Баланс успешно пополнен. Хеш транзакции ", tx_hash)
    except Exception as e:
        print(f"Ошибка при отправке эфира: {e}")


def output_money(account: str):
    get_balance(account)
    amount = int(input("Сумма к выводу: "))
    tx_hash = contract.functions.Output_MY_MONEY(amount).transact({
        "from": account
    })
    print("Успешно!")


def get_balance(account: str):
    tx_hash = contract.functions.GetBalance().call({
        "from": account
    })
    print(f"Ваш баланс {tx_hash}")


def update_est(account: str):
    estate = contract.functions.getEstates().call({
        "from": account
    })
    print(*list(filter((lambda tup: tup[4] == account), estate)), sep="\n")
    cur = input("Введите ID недвижимости которой хотите изменить статус: ")
    tx_hash = contract.functions.updateEstateStatus(cur).transact({
        "from": account
    })
    estate = contract.functions.getEstates().call({
        "from": account
    })
    print(*list(filter((lambda tup: tup[4] == account), estate)), sep="\n")


def update_add(account: str):
    estate = contract.functions.getAdds().call({
        "from": account
    })
    print(*list(filter((lambda tup: tup[4] == account), estate)), sep="\n")
    cur = input("Введите ID объявления которому хотите изменить статус: ")
    tx_hash = contract.functions.updateAddStatus(cur).transact({
        "from": account
    })
    estate = contract.functions.getAdds().call({
        "from": account
    })
    print(*list(filter((lambda tup: tup[4] == account), estate)), sep="\n")


def main():
    account = ""
    is_auth = False
    while True:
        try:
            if not is_auth:
                choice = input("Выберете: \n1. Авторизация\n2. Регистрация\n")
                match choice:
                    case "1":
                        account = auth()
                        if account is not None:
                            is_auth = True
                    case "2":
                        registration()
            else:
                с = input(
                    "Выберите:\n1. Пополнить баланс контракта\n2. Вывод денег с контракта\n3. Узнать баланс\n4. Добавить недвижимость\n5. Создать объявление\n6. Изменить статус недвижимости\n7. Изменить статус объявления\n8. Выход")
                match с:
                    case "1":
                        transh(account)
                    case "2":
                        output_money(account)
                    case "3":
                        get_balance(account)
                    case "4":
                        create_estate(account)
                    case "5":
                        create_add(account)
                    case "6":
                        update_est(account)
                    case "7":
                        update_add(account)
                    case "8":
                        is_auth = False
                    case _:
                        print("Некорректное значение")
        except:
            print("Ошибка при транзакции(((")
            continue


if __name__ == '__main__':
    main()
