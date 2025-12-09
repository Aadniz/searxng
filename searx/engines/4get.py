# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=invalid-name
"""4get is a proxy search engine that doesn't suck."""

from json import loads
from urllib.parse import urlencode
from datetime import datetime

from searx.exceptions import SearxEngineCaptchaException

about = {
    "website": 'https://git.lolcat.ca/lolcat/4get',
    "wikidata_id": "Q122602765",
    "official_api_documentation": "https://git.lolcat.ca/lolcat/4get/src/branch/master/docs/",
    "use_official_api": False,
    "require_api_key": False,
    "results": 'JSON',
}

paging = True

base_url = "http://4get.localhost"
api_path = "/api/v1/web"
# Any of these https://git.lolcat.ca/lolcat/4get/src/branch/master/lib/frontend.php#L939-L960
# google, yandex, yahoo, qwant, yep etc...
scraper: str | None = None


def check_captcha(json_response):
    if "captcha" in json_response.get("status", '').lower():
        raise SearxEngineCaptchaException(suspended_time=1800)


def request(query, params):
    lang = "en"
    if params['language'] != 'all':
        lang = params['language'][:2]

    fp = {  # pylint: disable=invalid-name
        's': query,
        'scraper': scraper,
        'country': "en",
        'nsfw': "yes" if params['safesearch'] == 0 else "no",
        'lang': lang,
    }

    if params['pageno'] > 1:
        next_page_token = params['engine_data'].get('nextpage_token')
        if next_page_token:
            fp["npt"] = next_page_token

    params['url'] = base_url + api_path + '?' + urlencode(fp)

    return params


def response(resp):
    try:
        json_response = loads(resp.text)
    except ValueError:
        json_response = {}

    check_captcha(json_response)

    results = []

    for result in json_response.get('web', []):
        published_date = None
        if result.get('date') is not None:
            published_date = datetime.fromtimestamp(result['date'])

        results.append(
            {
                'url': result['url'],
                'title': result['title'],
                'content': result['description'],
                'publishedDate': published_date,
            }
        )

    results.extend({'suggestion': item} for item in json_response.get("related", []))
    next_page_token = json_response.get('npt')
    if next_page_token:
        results.append(
            {
                "engine_data": next_page_token,
                "key": "nextpage_token",
            }
        )
    return results
