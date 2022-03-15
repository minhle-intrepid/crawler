import time
import itertools
from module.module import *

if __name__ == '__main__':
    meta_data = []
    # shop_urls = ["https://www.lazada.vn/shop/samsung-flagship-store",
    #              "https://www.lazada.vn/shop/apple-flagship-store",
    #              "https://www.lazada.vn/shop/xiaomi-flagship-store",
    #              "https://www.lazada.vn/shop/hogoto-shopp",
    #              "https://www.lazada.vn/shop/sdvn-streetwear"]
    # for index, shop_url in enumerate(shop_urls):
    #     lazada_crawler = LazadaCrawler(shop_url)
    #     data = lazada_crawler.get_all_product_infor_by_shop()
    #     meta_data = list(itertools.chain(meta_data, data))
    #     print("Done: ", index+1, "/", len(shop_urls))
    #     if index+1 != len(shop_urls):
    #         time.sleep(120)
    shop_urls = ["https://shopee.vn/samsung_official_store",
                 "https://shopee.vn/apple_flagship_store"]
    for index, shop_url in enumerate(shop_urls):
        shopee_crawler = ShopeeCrawler(shop_url)
        data = shopee_crawler.get_all_product_infor_by_shop()
        meta_data = list(itertools.chain(meta_data, data))
        print("Done: ", index+1, "/", len(shop_urls))
        if index+1 != len(shop_urls):
            time.sleep(120)
    with open('data/data_shopee.json', 'w', encoding='utf-8') as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=4)
