# SPDX-License-Identifier: AGPL-3.0-or-later
"""Yandex (Web, images)"""

from json import loads
from urllib.parse import urlencode, quote
from html import unescape
from lxml import html
from searx.exceptions import SearxEngineCaptchaException
from searx.utils import humanize_bytes, eval_xpath, extract_text, extr


# Engine metadata
about = {
    "website": 'https://yandex.ru/',
    "wikidata_id": 'Q5281',
    "official_api_documentation": "?",
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# Engine configuration
categories = ['general', 'web']
paging = False
search_type = ""

# Search URL
base_url_web = 'https://yandex.ru/search/'
base_url_images = 'https://yandex.ru/images/search'

# Search xPath
results_xpath = '//li[contains(@class, "serp-item")]'
url_xpath = './/a[contains(@class, "OrganicTitle-Link organic__url")]/@href'
title_xpath = './/h2[contains(@class, "OrganicTitle-LinkText")]/span'
content_xpath = './/span[@class="OrganicTextContentSpan"]'


# Proxy URL
etools_proxy = False
etools_url_web = "https://www.etools.ch"
etools_search_path = (
    # fmt: off
    '/searchAdvancedSubmit.do'
    '?query={search_term}'
    '&pageResults=20'
    '&safeSearch={safesearch}'
    '&dataSources=mySettings'
    # fmt: on
)

# Proxy xPath
etools_results_xpath = '//table[@class="result"]//td[@class="record"]'
etools_url_xpath = './a/@href'
etools_title_xpath = './a//text()'
etools_content_xpath = './/div[@class="text"]//text()'
etools_cookie = "-".join(
    [
        'VER_3.3',
        'autocomplete_true',
        'country_web',
        'customerId_',
        'dataSourceResults_20',
        'dataSources_mySettings',
        'excludeQuery_',
        'language_all',
        'markKeyword_false',
        'openNewWindow_true',
        'pageResults_20',
        'queryAutoFocus_true',
        "_".join(
            [
                'rankCalibration',
                '%28Base',
                '0%29%28Bing',
                '0%29%28Brave',
                '0%29%28DuckDuckGo',
                '0%29%28Google',
                '0%29%28Lilo',
                '0%29%28Mojeek',
                '0%29%28Qwant',
                '0%29%28Search',
                '0%29%28Tiger',
                '0%29%28Wikipedia',
                '0%29%28Yahoo',
                '0%29%28Yandex',
                '4%29',
            ]
        ),
        'redirectLinks_false',
        'safeSearch_false',
        'showAdvertisement_true',
        'showSearchStatus_true',
        'timeout_4000',
        'usePost_false',
    ]
)


def catch_bad_response(resp):
    if resp.url.path.startswith('/showcaptcha'):
        raise SearxEngineCaptchaException()


def yandex_request(query, params):
    query_params_web = {
        "lr": "175",
        "text": query,
    }

    if params['pageno'] > 1:
        query_params_web.update({"p": params["pageno"] - 1})

    params['url'] = base_url_web + "?" + urlencode(query_params_web)

    return params


def yandex_request_images(query, params):
    query_params_images = {
        "text": query,
        "uinfo": "sw-1920-sh-1080-ww-1125-wh-999",
    }

    params['url'] = f"{base_url_images}?{urlencode(query_params_images)}"
    return params


def etools_request(query, params):
    if params['safesearch']:
        safesearch = 'true'
    else:
        safesearch = 'false'

    # Settings set to only allow Yandex, and some other stuff
    params['cookies']['searchSettings'] = etools_cookie

    params['url'] = etools_url_web + etools_search_path.format(search_term=quote(query), safesearch=safesearch)

    return params


def request(query, params):
    if search_type == 'web' and etools_proxy:
        return etools_request(query, params)
    if search_type == 'web' and not etools_proxy:
        return yandex_request(query, params)
    if search_type == 'images':
        return yandex_request_images(query, params)

    return params


def yandex_response(resp):

    catch_bad_response(resp)

    dom = html.fromstring(resp.text)

    results = []
    for result in eval_xpath(dom, results_xpath):
        url_list = eval_xpath(result, url_xpath)
        if not url_list:
            continue  # Likely hit a node that is an ad
        url = url_list[0]
        title = extract_text(eval_xpath(result, title_xpath))
        content = extract_text(eval_xpath(result, content_xpath))

        results.append({'url': url, 'title': title, 'content': content})

    return results


def yandex_response_images(resp):
    catch_bad_response(resp)

    html_data = html.fromstring(resp.text)
    html_sample = unescape(html.tostring(html_data, encoding='unicode'))

    content_between_tags = extr(
        html_sample, '{"location":"/images/search/', 'advRsyaSearchColumn":null}}', default="fail"
    )
    json_data = '{"location":"/images/search/' + content_between_tags + 'advRsyaSearchColumn":null}}'

    if content_between_tags == "fail":
        content_between_tags = extr(html_sample, '{"location":"/images/search/', 'false}}}')
        json_data = '{"location":"/images/search/' + content_between_tags + 'false}}}'

    json_resp = loads(json_data)

    results = []
    for _, item_data in json_resp['initialState']['serpList']['items']['entities'].items():
        title = item_data['snippet']['title']
        source = item_data['snippet']['url']
        thumb = item_data['image']
        fullsize_image = item_data['viewerData']['dups'][0]['url']
        height = item_data['viewerData']['dups'][0]['h']
        width = item_data['viewerData']['dups'][0]['w']
        filesize = item_data['viewerData']['dups'][0]['fileSizeInBytes']
        humanized_filesize = humanize_bytes(filesize)

        results.append(
            {
                'title': title,
                'url': source,
                'img_src': fullsize_image,
                'filesize': humanized_filesize,
                'thumbnail_src': thumb,
                'template': 'images.html',
                'resolution': f'{width} x {height}',
            }
        )

    return results


def etools_response(resp):
    dom = html.fromstring(resp.text)

    results = []
    for result in eval_xpath(dom, etools_results_xpath):
        # Check if the result contains an affiliate link
        if eval_xpath(result, './/span[@class="affiliate"]'):
            continue  # Likely hit a node that is an ad
        url_list = eval_xpath(result, etools_url_xpath)
        if not url_list:
            continue  # Likely hit a node that is an ad
        url = url_list[0]
        title = extract_text(eval_xpath(result, etools_title_xpath))
        content = extract_text(eval_xpath(result, etools_content_xpath))

        results.append({'url': url, 'title': title, 'content': content})

    return results


def response(resp):
    if search_type == 'web':
        if etools_proxy:
            return etools_response(resp)
        return yandex_response(resp)
    if search_type == 'images':
        return yandex_response_images(resp)

    return []
