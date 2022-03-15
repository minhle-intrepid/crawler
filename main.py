import itertools
from module.module import *

if __name__ == '__main__':
    meta_data = []
    shop_urls = ["https://www.lazada.vn/shop/samsung-flagship-store",
                 "https://www.lazada.vn/shop/apple-flagship-store",
                 "https://www.lazada.vn/shop/xiaomi-flagship-store",
                 "https://www.lazada.vn/shop/hogoto-shopp",
                 "https://www.lazada.vn/shop/sdvn-streetwear"]
    for shop_url in shop_urls:
        lazada_crawler = LazadaCrawler(shop_url)
        data = lazada_crawler.get_all_product_infor_by_shop()
        list(itertools.chain(meta_data, data))
    shop_url = "https://shopee.vn/samsung_official_store"
    shopee_crawler = ShopeeCrawler(shop_url)
    data = shopee_crawler.get_all_product_infor_by_shop()
    with open('./data/data.json', 'w', encoding='utf-8') as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=4)
