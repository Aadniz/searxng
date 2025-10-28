about = {
    "website": 'https://www.bing.com',
    "wikidata_id": 'Q182496',
    "official_api_documentation": 'https://www.microsoft.com/en-us/bing/apis/bing-web-search-api',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['general', 'web']
paging = True
max_page = 200
"""200 pages maximum (``&first=1991``)"""

time_range_support = True
safesearch = True
"""Bing results are always SFW.  To get NSFW links from bing some age
verification by a cookie is needed / thats not possible in SearXNG.
"""

def request(query, params):
    print("Sending")
    return params

def response(resp):
    print("Receiving")
    return []
