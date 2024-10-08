from time import sleep

import pytest
from selenium.webdriver.remote.webelement import WebElement
from pages.order_received_page import OrderReceivedPage
from pages.checkout_page import CheckoutPage, NAME_FIELD, LAST_NAME_FIELD, ADDRESS_FIELD, CITY_FIELD


# @pytest.mark.usefixtures('chrome_browser')
# @pytest.mark.usefixtures('edge_browser')
# @pytest.mark.usefixtures('firefox_browser')
@pytest.mark.usefixtures('browsers')
class TestsCheckoutPage:

    # -------------------------------------------------
    # Страница оформления заказа
    @pytest.mark.parametrize('coupon', ['GIVEMEHALYAVA', 'SERT500'])
    def test_apply_coupon(self, checkout_page: CheckoutPage, coupon: str):
        """
        :param checkout_page: object
        :param coupon: str
        """
        if checkout_page.is_coupon_already_applied():
            checkout_page.removed_applied_coupon()

        checkout_page.apply_coupon(coupon)
        success_message: str = checkout_page.get_success_message_by_apply_coupon()

        assert success_message == "Купон успешно добавлен.", checkout_page.logger.log(30, "Couldn't apply coupon", exc_info=True)

    @pytest.mark.parametrize('coupon', ['GIVEMEHALYAVA', 'SERT500'])
    def test_remove_added_coupon(self, checkout_page: CheckoutPage, coupon: str):
        """
        :param checkout_page: object
        :param coupon: str
        """
        if checkout_page.is_coupon_already_applied():
            checkout_page.removed_applied_coupon()
        else:
            checkout_page.apply_coupon(coupon)
            _ = checkout_page.get_success_message_by_apply_coupon()
            checkout_page.removed_applied_coupon()

        assert checkout_page.is_coupon_removed(), checkout_page.logger.log(30, "Couldn't removed coupon on checkout page", exc_info=True)

    @pytest.mark.parametrize("field, filling_value", [
        (NAME_FIELD, "Faridun"),
        (LAST_NAME_FIELD, "Hushang-Mirzo"),
        (ADDRESS_FIELD, "Tashkent, Bobojon Gafurov str."),
        (CITY_FIELD, "Tashkent")
    ])
    def test_place_order_with_empty_mandatory_field(self, checkout_page: CheckoutPage, filling_value: str, field: tuple[str, str]):
        """
        :param checkout_page: object
        :param filling_value: str, value which should be filled after the test
        :param field: locator, is a selector and his value
        """
        checkout_page.clear_fields(field)
        checkout_page.waiting_load_block_invisible()
        checkout_page.ordering_products()

        assert "обязательное поле" in checkout_page.get_text_of_element(checkout_page.ERROR_ALERT), \
            checkout_page.logger.log(30, "Client can manage to place an order with an empty field that was mandatory", exc_info=True)

        checkout_page.filling_fields(**{filling_value: field})

    def test_place_order_with_some_empty_mandatory_fields(self, checkout_page: CheckoutPage):
        """
        :param checkout_page: object
        """
        checkout_page.clear_fields(LAST_NAME_FIELD, ADDRESS_FIELD, CITY_FIELD)
        checkout_page.ordering_products()

        for element in checkout_page.wait_for_elements(checkout_page.ERROR_ALERTS):
            assert "обязательное поле" in element.text, checkout_page.logger.log(30, "We can ordering product with empty mandatory fields", exc_info=True)

        checkout_page.filling_fields(**{"Hushang-Mirzo": LAST_NAME_FIELD,
                                        "Tashkent, Bobojon Gafurov str.": ADDRESS_FIELD,
                                        "Tashkent": CITY_FIELD})

    @pytest.mark.parametrize("payment_method", ["Прямой банковский перевод", "Оплата при доставке"])
    def test_place_order_via_direct_bank_transfer(self, checkout_page: CheckoutPage, payment_method: str):
        """
        :param checkout_page: object
        :param payment_method: str, we have 2 choices
        """
        payment_variants: list[WebElement] = checkout_page.get_payment_variants()
        checkout_page.scroll_to(payment_variants[0])
        checkout_page.select_payment_method(payment_method)
        checkout_page.waiting_load_block_invisible()
        checkout_page.ordering_products()

        order_received_page: OrderReceivedPage = OrderReceivedPage(checkout_page.driver)

        assert payment_method in order_received_page.get_payment_method(), checkout_page.logger.log(30, "Could not ordering product", exc_info=True)
