import ccxt
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.exchange = ccxt.bybit({
            'apiKey': 'CXP7kBL0o9TLW7WwLB',
            'secret': 'Hk7l78twJdytHRuSZ2ieqLWhKWxYpp8Xhvog',
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            }
        })

        self.assets = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'EOS', 'TRX', 'ETC', 'LINK', 'ADA']
        self.selected_asset = None
        self.capital = 1000  # Увеличим стартовый капитал для более реалистичной модели
        self.position_size = self.capital / 10
        self.buy_threshold = 0.05  # 5% падения цены для покупки
        self.sell_threshold = 0.05  # 5% роста цены для продажи
        self.current_price = 0
        self.last_buy_price = 0
        self.positions = []

    def select_asset(self):
        print("Доступные активы:")
        for i, asset in enumerate(self.assets):
            print(f"{i + 1}. {asset}")
        choice = input("Выберите актив (введите номер): ")
        self.selected_asset = self.assets[int(choice) - 1]
        print(f"Выбран актив: {self.selected_asset}")

    def get_current_price(self):
        try:
            ticker = self.exchange.fetch_ticker(f'{self.selected_asset}/USDT')
            return ticker['last']
        except Exception as e:
            print(f"Ошибка при получении текущей цены: {str(e)}")
            return None

        def display_status(self):
            try:
                balance = self.exchange.fetch_balance()
                logger.info(f"Balance structure: {balance}")

                usdt_free = balance.get('USDT', {}).get('free', 0)
                print("\nТекущее состояние:")
                print(f"Актив: {self.selected_asset}")
                print(f"Текущая цена: ${self.get_current_price():.2f}")
                print(f"Баланс USDT: ${usdt_free:.2f}")
                print(f"Капитал: ${self.capital:.2f}")
                print(f"Позиции: {len(self.positions)}")
                print("")
            except Exception as e:
                logger.error(f"Ошибка при отображении статуса: {str(e)}")

        def buy(self):
            if len(self.positions) < 10:
                price = self.get_current_price()
                if price <= self.current_price * (1 - self.buy_threshold):
                    try:
                        balance = self.exchange.fetch_balance()
                        usdt_free = balance.get('USDT', {}).get('free', 0)
                        logger.info(f"Available USDT balance: {usdt_free}")

                        quantity = min(self.position_size / price, usdt_free / price)
                        if quantity > 0:
                            try:
                                order = self.exchange.create_market_buy_order(f'{self.selected_asset}/USDT', quantity)
                                self.positions.append((price, quantity))
                                self.last_buy_price = price
                                logger.info(f"Покупка {quantity} {self.selected_asset} по цене {price}")
                                return True
                            except Exception as e:
                                logger.error(f"Ошибка при покупке: {str(e)}")
                        else:
                            logger.warning("Недостаточно средств для покупки")
                    except Exception as e:
                        logger.error(f"Ошибка при получении баланса или выполнении покупки: {str(e)}")
                return False

    def buy(self):
        if len(self.positions) < 10:
            price = self.get_current_price()
            if price <= self.current_price * (1 - self.buy_threshold):
                quantity = min(self.position_size / price, self.exchange.fetch_balance()['USDT']['free'] / price)
                if quantity > 0:
                    try:
                        order = self.exchange.create_market_buy_order(f'{self.selected_asset}/USDT', quantity)
                        self.positions.append((price, quantity))
                        self.last_buy_price = price
                        print(f"Покупка {quantity} {self.selected_asset} по цене {price}")
                        return True
                    except Exception as e:
                        print(f"Ошибка при покупке: {str(e)}")
                else:
                    print("Недостаточно средств для покупки")
            return False

    def sell(self):
        if self.positions:
            price = self.get_current_price()
            if price >= self.last_buy_price * (1 + self.sell_threshold):
                bought_price, quantity = self.positions.pop(0)
                try:
                    order = self.exchange.create_market_sell_order(f'{self.selected_asset}/USDT', quantity)
                    profit = (price - bought_price) * quantity
                    self.capital += profit
                    self.last_buy_price = 0
                    print(f"Продажа {quantity} {self.selected_asset} по цене {price}, прибыль: {profit}")
                    return True
                except Exception as e:
                    print(f"Ошибка при продаже: {str(e)}")
        return False

    def display_status(self):
        balance = self.exchange.fetch_balance()
        print("\nТекущее состояние:")
        print(f"Актив: {self.selected_asset}")
        print(f"Текущая цена: ${self.get_current_price():.2f}")
        print(f"Баланс USDT: ${balance['USDT']['free']:.2f}")
        print(f"Капитал: ${self.capital:.2f}")
        print(f"Позиции: {len(self.positions)}")
        print("")

    def run(self):
        self.select_asset()
        while True:
            try:
                self.current_price = self.get_current_price()
                self.display_status()

                if not self.buy():
                    self.sell()

                time.sleep(60)  # Обновление каждую минуту
            except Exception as e:
                print(f"Ошибка: {str(e)}")
                time.sleep(60)


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
