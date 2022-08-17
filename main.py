import json
import random
import re
import time
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
}


def _write_html_code_to_file(driver: webdriver) -> None:
    with open("parse/source-page.html", "w") as file:
        file.write(driver.page_source)


def get_source_html(url: str) -> None:
    """Getting page html code"""

    driver = webdriver.Chrome(
        executable_path="driver_path"
    )

    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)

        while True:
            find_more_element = driver.find_element_by_class_name("catalog-button-showMore")

            if driver.find_element_by_class_name("hasmore-text"):
                _write_html_code_to_file(driver=driver)
                break
            else:
                action = ActionChains(driver)
                action.move_to_element(find_more_element).perform()
                time.sleep(3)
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

    def get_items_urls(file_path: str) -> str:
        with open(file_path) as file:
            scr = file.read()

        soup = BeautifulSoup(scr, "lxml")
        items_divs = soup.find_all("div", class_="service-description")

        urls = []
        for item in items_divs:
            item_url = item.find("div", class_="H3").find("a").get("href")
            urls.append(item_url)

        with open("parse/items_urls2.txt", "w") as file:
            for url in urls:
                file.write(f"{url}\n")

        return "[INFO] Urls collected successfully!"


def get_item_name(soup: BeautifulSoup) -> list:
    try:
        item_name = soup.find("span", {"itemprom": "name"}).text.strip()
    except Exception as _ex:
        item_name = None

    return item_name


def get_item_phones_list(soup: BeautifulSoup) -> list:
    item_phones_list: list = []
    try:
        item_phones = soup.find("div", class_="service-phones-list").find_all("a", class_="js-phone-number")

        for phone in item_phones:
            item_phone = phone.get("href").split(":")[-1].strip()
            item_phones_list.append(item_phone)
    except Exception as _ex:
        item_phones_list = None
    return item_phones_list


def get_item_address(soup: BeautifulSoup) -> list:
    try:
        item_address = soup.find("addres", class_="iblock").text.strip()
    except Exception as _ex:
        item_address = None
    return item_address


def get_item_site(soup: BeautifulSoup) -> list:
    try:
        item_site = soup.find(text=re.compile("Сайт|официальный сайт")).find_next().text.strip()
    except Exception as _ex:
        item_site = None
    return item_site


def get_social_networks_list(soup: BeautifulSoup) -> list:
    social_networks_list: list = []
    try:
        item_social_networks = soup.find(text=re.compile("Страница в соцсетях")).find_next().find_all("a")
        for sn in item_social_networks:
            sn_url = sn.get("href")
            sn_url = unquote(sn_url.split("?to=")[1].split("&")[0])
            social_networks_list.append(sn_url)
    except Exception as _ex:
        social_networks_list = None
    return social_networks_list


def writing_result_list_in_file(result_list: list, path: str, name_file: str) -> None:
    with open(f"{path}/{name_file}", "w") as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)


def get_data(file_path: str) -> str:
    with open(file_path) as file:
        url_list = [url.strip() for url in file.readlines()]

    result_list = []
    url_count = len(url_list)
    count = 1
    for url in url_list:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # try:
        #     item_name = soup.find("span", {"itemprom": "name"}).text.strip()
        # except Exception as _ex:
        #     item_name = None

        item_name = get_item_name(soup)

        # item_phones_list = []
        # try:
        #     item_phones = soup.find("div", class_="service-phones-list").find_all("a", class_="js-phone-number")
        #
        #     for phone in item_phones:
        #         item_phone = phone.get("href").split(":")[-1].strip()
        #         item_phones_list.append(item_phone)
        # except Exception as _ex:
        #     item_phones_list = None

        item_phones_list = get_item_phones_list(soup)

        # try:
        #     item_address = soup.find("addres", class_="iblock").text.strip()
        # except Exception as _ex:
        #     item_address = None

        item_address = get_item_address(soup)

        # try:
        #     item_site = soup.find(text=re.compile("Сайт|официальный сайт")).find_next().text.strip()
        # except Exception as _ex:
        #     item_site = None

        item_site = get_item_site(soup)

        # social_networks_list = []
        # try:
        #     item_social_networks = soup.find(text=re.compile("Страница в соцсетях")).find_next().find_all("a")
        #     for sn in item_social_networks:
        #         sn_url = sn.get("href")
        #         sn_url = unquote(sn_url.split("?to=")[1].split("&")[0])
        #         social_networks_list.append(sn_url)
        # except Exception as _ex:
        #     social_networks_list = None

        social_networks_list = get_social_networks_list(soup)

        result_list.append(
            {
                "item_name": item_name,
                "item_url": url,
                "item_phones_list": item_phones_list,
                "item_address": item_address,
                "item_site": item_site,
                "social_networks_list": social_networks_list,
            }
        )

        time.sleep(random.randrange(2, 5))

        if count % 10 == 0:
            time.sleep(random.randrange(5, 9))

        print(f"[+] Processed: {count}/{url_count}")

        count += 1

    # with open("parse/result.json", "w") as file:
    #     json.dump(result_list, file, indent=4, ensure_ascii=False)

    writing_result_list_in_file(path="parse", name_file="result.json", result_list=result_list)

    return "[INFO] Data collected successfully!"


def main():
    get_source_html(
        url="https://spb.zoon.ru/medical/?search_query_form=1&m%5B5200e522a0f302f066000055%5D=1&center%5B%5D=59."
            "91878264665887&center%5B%5D=30.342586983263384&zoom=10")


if __name__ == '__main__':
    main()
