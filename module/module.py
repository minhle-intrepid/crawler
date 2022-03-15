import re
import os
import json
import requests

from typing import Tuple
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, shop_url):
        self.shop_url = shop_url


class ShopeeCrawler(Crawler):
    shop_id_api = "https://shopee.vn/api/v4/shop/get_shop_detail?username={}"
    product_id_api = "https://shopee.vn/api/v4/search/search_items?by=pop&entry_point=ShopBySearch&limit=30&match_id={}&newest={}&order=desc&page_type=shop&scenario=PAGE_OTHERS&version=2"
    product_info_api = "https://shopee.vn/api/v4/item/get?itemid={}&shopid={}"

    def get_shop_id(self, shop_url):
        """
        Get shop_id of shop
        :param shop_url:
        :return:
        """
        response = requests.get(self.shop_id_api.format(shop_url[18:])).json()
        shop_id = response["data"]["shopid"]
        return shop_id

    def get_product_ids(self, shop_id, newest=0):
        """
        Get product_id of all product
        :param shop_id:
        :param newest:
        :return:
        """
        item_ids = []
        while True:
            response = requests.get(self.product_id_api.format(shop_id, newest)).json()
            if len(response["items"]) > 0:
                for item in response["items"]:
                    item_ids.append(item["item_basic"]["itemid"])
                newest += 30
            else:
                return item_ids

    def get_product_info(self, item_id, shop_id):
        """
        Get product information
        :param item_id:
        :param shop_id:
        :return:
        """
        response = requests.get(self.product_info_api.format(item_id, shop_id)).json()
        product_name = response["data"]["name"]
        price_bf_discount = response["data"]["price_before_discount"] / 100000
        price = response["data"]["price"] / 100000
        sold = response["data"]["historical_sold"]
        rating_star = response["data"]["item_rating"]["rating_star"]
        description = response["data"]["description"]
        tier_variation = response["data"]["tier_variations"]
        return product_name, price_bf_discount, price, sold, rating_star, description, tier_variation

    def get_all_product_infor_by_shop(self):
        """
        Get all product information by the shop
        :param :
        :return: information of all product
        """
        data = []
        shop_id = self.get_shop_id(self.shop_url)
        item_ids = self.get_product_ids(shop_id)
        for item_id in item_ids:
            product_name, price_bf_discount, price, sold, rating_star, description, tier_variation = self.get_product_info(
                item_id, shop_id)
            product_info = {
                "platform": "shopee",
                "shop_id": shop_id,
                "item_id": item_id,
                "product_names": product_name,
                "price_before_discounts": price_bf_discount,
                "price_of_products": price,
                "historical_sold": sold,
                "rating_stars": rating_star,
                "descriptions": description,
                "tier_variations": tier_variation
            }
            data.append(product_info)
        return data


class LazadaCrawler(Crawler):

    def check_platform_response(self, platform_response: str, http_code: int) -> Tuple[bool, str]:
        """
        Check some error in response from platform
        @param platform_response:
        @param http_code:
        @return:
        @rtype [bool, str]:
        """

        if platform_response.find('punish-page') != -1 \
                or platform_response.find('bixi.alicdn.com/punish/') != -1 \
                or platform_response.find('slide to verify') != -1 \
                or platform_response.find('retcode.alicdn.com/retcode/bl.js') != -1 \
                or platform_response.find('_____tmd_____/punish') != -1 \
                or (platform_response.find("bar.tmall.com") != -1 and platform_response.find("cart.tmall.com") != -1) \
                or platform_response.find("http://www.airtel.in/dot/") != -1 \
                or platform_response.find("/act/common-error") != -1 \
                or platform_response.find("An error occurred while processing your request.") != -1 \
                or platform_response.find("The server is temporarily unable to service your request") != -1 \
                or platform_response.find("The service you requested does not exist") != -1 \
                or (http_code != 200 and platform_response.find("Whitelabel Error Page") != -1) \
                or (http_code != 200 and platform_response == ""):

            return False, "constants.ERROR_TYPE_CAPTCHA"
        elif platform_response.find('lazada-icon lazada-ic-404') != -1 or platform_response.find(
                "title = '500' === '404") != -1 \
                or platform_response.find("all skus are wrong") != -1 or platform_response.find("item not found") != -1:
            # global_logger.write_log('check_platform_response', f'product_is_not_exist', global_logger.LOG_WARNING)
            print("check_platform_response")
            return False, "constants.ERROR_TYPE_URL_DONT_EXIST"
        elif platform_response.find('?wh_errCode=404') != -1 or platform_response.find('Shop Enter Fail Page PC') != -1:
            return False, "constants.ERROR_TYPE_URL_DONT_EXIST"

        return True, platform_response

    def get_product_list(self, shop_url):
        """
        Get all product urls on a page
        :param shop_url:
        :return: url of products
        """
        product_urls = []
        shop_url = shop_url.split("/")
        product_page = os.path.join("https://", shop_url[-3], shop_url[-1],
                                    "?from=wangpu&langFlag=en&page=1&pageTypeId=2&q=All-Products")
        response = requests.get(product_page)
        check, platform_response = self.check_platform_response(response.text, response.status_code)
        if check:
            soup = BeautifulSoup(platform_response, features="html.parser")
            scripts = soup.find_all('script')
            jsonobj = None
            for script in scripts:
                if 'window.pageData =' in script.text:
                    jsonstr = script.text
                    jsonstr = jsonstr.split("window.pageData = ")[1][:-4]
                    jsonobj = json.loads(jsonstr)
            if "listItems" in jsonobj['mods'].keys():
                products = jsonobj['mods']['listItems']
                for product in products:
                    product_urls.append(product["productUrl"][2:])
            return product_urls
        return platform_response

    def get_product_infor(self, product_url):
        """
        Get product information
        :param product_url:
        :return: information of product
        """
        response = requests.get(product_url)
        check, platform_response = self.check_platform_response(response.text, response.status_code)
        if check:
            moduledata = re.findall(r'__moduleData__ = .*;', platform_response)
            moduledata = json.loads(moduledata[0][17:-1])
            shop_id = moduledata["data"]["root"]["fields"]["seller"]["shopId"]
            item_id = moduledata["data"]["root"]["fields"]["review"]["params"]["itemId"]
            product_name = moduledata["data"]["root"]["fields"]["tracking"]["pdt_name"]
            price_bf_discount = moduledata["data"]["root"]["fields"]["skuInfos"]["0"]["price"]["originalPrice"]["value"]
            price = moduledata["data"]["root"]["fields"]["skuInfos"]["0"]["price"]["salePrice"]["value"]
            rating_star = moduledata["data"]["root"]["fields"]["review"]["ratings"]["average"]
            if "highlights" in moduledata["data"]["root"]["fields"]["product"].keys():
                description = moduledata["data"]["root"]["fields"]["product"]["highlights"]
                description = BeautifulSoup(description, features="html.parser").get_text()
            else:
                description = moduledata["data"]["root"]["fields"]["product"]["desc"]
                description = BeautifulSoup(description, features="html.parser").get_text()
            tier_variation = moduledata["data"]["root"]["fields"]["productOption"]["skuBase"]["properties"]
            return shop_id, item_id, product_name, price_bf_discount, price, rating_star, description, tier_variation
        return platform_response

    def get_all_product_infor_by_shop(self):
        """
        Get all product information by the shop
        :param :
        :return: information of all product
        """
        data = []
        product_urls = self.get_product_list(self.shop_url)
        for product_url in product_urls:
            product_url = os.path.join("https://", product_url)
            try:
                shop_id, item_id, product_name, price_bf_discount, price, rating_star, description, tier_variation = self.get_product_infor(
                    product_url)
                product_info = {
                    "platform": "lazada",
                    "shop_id": shop_id,
                    "item_id": item_id,
                    "product_names": product_name,
                    "price_before_discounts": price_bf_discount,
                    "price_of_products": price,
                    "historical_sold": "NA",
                    "rating_stars": rating_star,
                    "descriptions": description,
                    "tier_variations": tier_variation
                }
                data.append(product_info)
            except:
                print(product_url)
        return data

