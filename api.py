import requests
from environs import Env

env = Env()
env.read_env()
BASE_URL = env.str('BASE_URL')


def check_phone(phone_number: str, tg_user_id):
    data = {
        'phone_number': phone_number,
        'tg_user_id': tg_user_id
    }
    response = requests.post(f"{BASE_URL}/auth/check-phone/", json=data)
    return response


def get_company(tg_user_id):
    data = {
        'tg_user_id': tg_user_id,
    }
    response = requests.get(
        f'{BASE_URL}/bot/companies?tg_user_id={tg_user_id}')
    return response


def create_company_api(tg_user_id, name, address, phone_number, stir):
    is_active = True
    data = {
        'name': name,
        'address': address,
        'phone_number': phone_number,
        'stir': stir,
        'is_active': is_active,
    }
    response = requests.post(
        f'{BASE_URL}/bot/companies/?tg_user_id={tg_user_id}', json=data)
    return response


def delete_company_api(id, tg_user_id):
    response = requests.delete(f"{BASE_URL}/bot/{id}?tg_user_id={tg_user_id}")
    return response
# print(delete_company_api(3,'994276762'))


def get_orders_acceptet_api(tg_user_id):
    data = {
        'tg_user_id': tg_user_id,
    }
    response = requests.get(
        f'{BASE_URL}/bot/orders/accepted/?tg_user_id={tg_user_id}')
    return response


def get_order_id_api(id):
    """
        detail olish
    """
    data = {
        'id': id
    }
    response = requests.get(f'{BASE_URL}/orders/{id}')
    return response


def get_order_accepted_api(tg_user_id):
    data = {
        'tg_user_id': tg_user_id,
    }
    response = requests.get(
        f'{BASE_URL}/bot/orders/accepted/?tg_user_id={tg_user_id}')
    return response


def get_order_rejected_api(tg_user_id):
    data = {
        'tg_user_id': tg_user_id,
    }
    response = requests.get(
        f'{BASE_URL}/bot/orders/rejected/?tg_user_id={tg_user_id}')
    return response

# fol buyurtmalarni olish


def get_order_inprogress_api(tg_user_id):
    data = {
        'tg_user_id': tg_user_id,
    }
    response = requests.get(
        f'{BASE_URL}/bot/orders/in-progress/?tg_user_id={tg_user_id}')
    return response


def get_order_pending_api(tg_user_id):
    data = {
        'tg_user_id': tg_user_id,
    }
    response = requests.get(
        f'{BASE_URL}/bot/orders/pending/?tg_user_id={tg_user_id}')
    return response


def post_order_in_progress_api(order_id: str, tg_user_id):
    params = {
        'order_id': order_id,
        'tg_user_id': tg_user_id
    }
    response = requests.post(
        f"{BASE_URL}/bot/orders/in-progress/", params=params)
    return response


def post_order_in_accepted_api(order_id: str, tg_user_id):
    params = {
        'order_id': order_id,
        'tg_user_id': tg_user_id
    }
    response = requests.post(f"{BASE_URL}/bot/orders/accepted/", params=params)
    return response


def post_order_rejected_api(order_id: str, tg_user_id):
    params = {
        'order_id': order_id,
        'tg_user_id': tg_user_id
    }
    response = requests.post(f"{BASE_URL}/bot/orders/rejected/", params=params)
    return response
