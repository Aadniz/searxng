from urllib.parse import urlencode

about = {
    "website": "https://www.google.com",
    "wikidata_id": "Q9366",
    "official_api_documentation": "https://developers.google.com/custom-search/",
    "use_official_api": "false",
    "require_api_key": "false",
    "results": "JSON",
}

def request(query: str, params: "OnlineParams"):
    params["url"] = "https://www.google.com/search?" + urlencode({'q': query})
    return params

def response(resp: "SXNG_Response"):
    print(resp.text)
    with open("/tmp/google_test_2.html", "w") as f:
        f.write(resp.text)
    return []
