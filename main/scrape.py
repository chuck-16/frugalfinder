import bs4 as bs
import requests, re
from pprint import pprint
from time import time
from thefuzz import fuzz

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

class Product:
    def __init__(self, name, url, img_url, price, brand_img):
        self.name = name
        self.url = url 
        self.img_url = img_url
        self.price = price
        self.brand_img = brand_img

    def __str__(self):
        return f"\nname: {self.name}\nurl: {self.url}\nimage: {self.img_url}\nprice: {self.price}"

def scrape_amazon(product, top_count):
    shorturl = "https://www.amazon.com"
    url = f'{shorturl}/s?k="{product}"'

    website = requests.get(url, headers=HEADERS)

    soup = bs.BeautifulSoup(website.content, "lxml")
    product_elements = []
    product_elements = product_elements + soup.find_all("div", {"class": "s-card-container"}, limit=top_count)

    products = []
    for product_element in product_elements:
        link = product_element.find("a", {"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
        name =  link.span.text.replace('"', '')
        img_link = product_element.find("img", {"class": "s-image"}).get("src")
        if product_element.find("span", {"class": "a-offscreen"}) == None:
            continue
        price = float(product_element.find("span", {"class": "a-offscreen"}).text.replace("$", "").replace(",", ""))

        products.append(Product(name, shorturl+link.get("href"), img_link, price, 'https://cdn3.iconfinder.com/data/icons/popular-services-brands/512/amazon-512.png'))

    return products

def scrape_ebay(product, top_count, allow_used):
    shorturl = "https://www.ebay.com/"
    url = f'{shorturl}sch/i.html?_nkw={product}&rt=nc&LH_BIN=1&LH_ItemCondition=1000'
    if allow_used:
        url = f'{shorturl}/sch/i.html?_nkw={product}&rt=nc&LH_BIN=1'

    website = requests.get(url, headers=HEADERS)

    soup = bs.BeautifulSoup(website.content, "lxml")
    product_elements = []
    product_elements = product_elements + soup.find_all("div", {"class": "s-item__wrapper clearfix"}, limit=top_count)

    products = []
    for product_element in product_elements:
        price = product_element.find("span", {"class": "s-item__price"}).text
        link = product_element.find("a", {"class": "s-item__link"})
        name =  link.div.span.text.replace('"', '')

        if re.search('[a-zA-Z]', price.lower()) != None or "ebay" in name.lower():
            continue

        price = float(price.replace("$", "").replace(",", "").split(' ')[0])
        
        img_link = product_element.find("div", {"class": "s-item__image-wrapper image-treatment"}).img.get("src")

        products.append(Product(name, link.get("href"), img_link, price, 'https://cdn3.iconfinder.com/data/icons/popular-services-brands/512/ebay-512.png'))

    return products

def get_products(product, limit, sort_method, allow_used):
    products = scrape_amazon(product, limit)
    products = products + scrape_ebay(product, limit, allow_used)

    match sort_method:
        case 'lth':
            products = sorted(products, key=lambda x: x.price, reverse=False)
        case 'htl':
            products = sorted(products, key=lambda x: x.price, reverse=True)
        case 'bm':
            products = sorted(products, key=lambda x: fuzz.ratio(product, x.name), reverse=True)
            
    return products

