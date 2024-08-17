import requests
from environs import Env

env = Env()
env.read_env()
BASE_URL = env.str('BASE_URL')


class ApiClient:
    def __init__(self):
        """
        ApiClient klassi bilan ishlash uchun asosiy konstruktori.

        :param base_url: APIning bazaviy URL manzili.
        """
        self.base_url = BASE_URL

    def _post(self, endpoint, data=None, params=None):
        """
        POST so'rovini yuborish uchun yordamchi funksiya.

        :param endpoint: API endpoint manzili.
        :param data: Yuboriladigan JSON ma'lumotlar.
        :param params: URL parametrlar.
        :return: JSON javobi.
        """
        response = requests.post(
            f"{self.base_url}{endpoint}", json=data, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def _get(self, endpoint, params=None):
        """
        GET so'rovini yuborish uchun yordamchi funksiya.

        :param endpoint: API endpoint manzili.
        :param params: URL parametrlar.
        :return: JSON javobi.
        """
        response = requests.get(f"{self.base_url}{endpoint}", params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def _delete(self, endpoint, params=None):
        """
        DELETE so'rovini yuborish uchun yordamchi funksiya.

        :param endpoint: API endpoint manzili.
        :param params: URL parametrlar.
        :return: JSON javobi.
        """
        response = requests.delete(f"{self.base_url}{endpoint}", params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return {}


class CompanyClient(ApiClient):
    def check_phone(self, phone_number: str, tg_user_id):
        """
        Telefon raqamini tekshirish.

        :param phone_number: Telefon raqami.
        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        data = {
            'phone_number': phone_number,
            'tg_user_id': tg_user_id
        }
        return self._post("/auth/check-phone/", data=data)

    def get_company(self, tg_user_id):
        """
        Kompaniyalar ro'yxatini olish.

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {'tg_user_id': tg_user_id}
        return self._get('/bot/companies', params=params)

    def create_company(self, tg_user_id, name, address, phone_number, stir):
        """
        Yangi kompaniya yaratish.

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :param name: Kompaniya nomi.
        :param address: Kompaniya manzili.
        :param phone_number: Kompaniya telefon raqami.
        :param stir: Kompaniya STIR.
        :return: JSON javobi.
        """
        data = {
            'name': name,
            'address': address,
            'phone_number': phone_number,
            'stir': stir,
            'is_active': True
        }
        return self._post(f'/bot/companies/?tg_user_id={tg_user_id}', data=data)

    def delete_company(self, company_id, tg_user_id):
        """
        Kompaniyani o'chirish.

        :param company_id: Kompaniya identifikatori.
        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        return self._delete(f"/bot/companies/{company_id}", params={'tg_user_id': tg_user_id})


class OrderClient(ApiClient):
    def get_orders_accepted(self, tg_user_id):
        """
        Qabul qilingan buyurtmalarni olish.

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {'tg_user_id': tg_user_id}
        return self._get('/bot/orders/accepted/', params=params)

    def get_order_by_id(self, order_id):
        """
        Buyurtma tafsilotlarini olish.

        :param order_id: Buyurtma identifikatori.
        :return: JSON javobi.
        """
        return self._get(f'/orders/{order_id}')

    def get_orders_rejected(self, tg_user_id):
        """
        Rad etilgan buyurtmalarni olish.

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {'tg_user_id': tg_user_id}
        return self._get('/bot/orders/rejected/', params=params)

    def get_orders_in_progress(self, tg_user_id):
        """F
        Jarayonda bo'lgan buyurtmalarni olish.

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {'tg_user_id': tg_user_id}
        return self._get('/bot/orders/in-progress/', params=params)

    def get_factura_doc(self, tg_user_id):
        """
        Jarayonda bo'lgan buyurtmalarni olish.

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {'tg_user_id': tg_user_id}
        return self._post('/bot/factura/', params=params)

    def get_factura_doc_without_price(self, tg_user_id):
        """
        Jarayonda bo'lgan buyurtmalarni olish.

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {'tg_user_id': tg_user_id}
        return self._post('/bot/factura-without-price/', params=params)

    def get_orders_pending(self, tg_user_id):
        """
        Kutayotgan buyurtmalarni olish.

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {'tg_user_id': tg_user_id}
        return self._get('/bot/orders/pending/', params=params)

    def set_order_in_progress(self, order_id: str, tg_user_id):
        """
        Buyurtmani jarayonda deb belgilash.

        :param order_id: Buyurtma identifikatori.
        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {
            'order_id': order_id,
            'tg_user_id': tg_user_id
        }
        return self._post("/bot/orders/in-progress/", params=params)

    def accept_order(self, order_id: str, tg_user_id):
        """
        Buyurtmani qabul qilingan deb belgilash.

        :param order_id: Buyurtma identifikatori.
        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {
            'order_id': order_id,
            'tg_user_id': tg_user_id
        }
        return self._post("/bot/orders/accepted/", params=params)

    def reject_order(self, order_id: str, tg_user_id):
        """
        Buyurtmani rad etilgan deb belgilash.

        :param order_id: Buyurtma identifikatori.
        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {
            'order_id': order_id,
            'tg_user_id': tg_user_id
        }
        return self._post("/bot/orders/rejected/", params=params)

    def get_product_prices(self, tg_user_id):
        """
        Mahsulot narxlarini olish.

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {'tg_user_id': tg_user_id}
        return self._get("/bot/products-prices", params=params)


class LimitClient(ApiClient):
    def get_factura_data(self, contract_id, telegram_id):
        """
        Factura uchun to'liq datani olish

        :param contract_id: Shartnomi raqami
        :return: JSON javobi.
        """
        params = {'contract_id': contract_id, 'tg_user_id': telegram_id}
        return self._get('/limit-factura', params=params)

    def get_contracts(self, tg_user_id):
        """
        user uchun hamm shartnomalarni olish

        :param tg_user_id: Telegram foydalanuvchi identifikatori.
        :return: JSON javobi.
        """
        params = {'tg_user_id': tg_user_id}
        return self._get('/contracts', params=params)
