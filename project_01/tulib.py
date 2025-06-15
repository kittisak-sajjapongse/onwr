import json
import re
from typing import Any, List, Tuple

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


collections = {
    "ALL": {"id": "all"},
    "TDRI": {"id": "57"},
    "NRCT": {"id": "61"},
    "TSDI": {"id": "16"},
}


def search_from_phrase(phrase: str, collection="TDRI", page=1, page_size=10) -> Any:
    assert collections[collection] is not None, "Unknown collection specified"
    search_url = f"https://digital.library.tu.ac.th/tu_dc/frontend/Search/find/{(page - 1) * page_size}/0"
    search_settings = {
        "main": phrase,
        "option": "all",
        "collection_id": collections[collection]["id"],
        "main_collection_id": "all",
        "pubyear_start": None,
        "pubyear_end": None,
        "filter": {
            "main_collection_id": [],
            "collection_id": [],
            "keyword_full": [],
            "author_data_full": [],
            "pubyear": [],
        },
        "filter_include": True,
        "aggregate": True,
        "sort": "_score",
        "per_page": page_size,
        "like_search": 0,
    }
    form_data = {
        "data": json.dumps(search_settings),
    }
    response = requests.post(search_url, data=form_data, verify=False)
    resp_js = json.loads(response.text)
    return resp_js


def search_for_links(obj: Any) -> List[str]:
    links = []
    pattern = r"https://\S+?(?=\s|$)"
    if isinstance(obj, dict):
        for _, value in obj.items():
            links.extend(search_for_links(value))
    elif isinstance(obj, list):
        for item in obj:
            links.extend(search_for_links(item))
    elif isinstance(obj, str):
        links.extend(re.findall(pattern, obj))
    else:
        return links
    return list(set(links))


def get_links(entry_resp: Any) -> List[str]:
    tu_dl_url = "https://digital.library.tu.ac.th/tu_dc/digital/api/DownloadDigitalFile/dowload/{}"

    links = search_for_links(entry_resp["template_data"])
    if len(links) == 0:
        if not "digital" in entry_resp:
            return links
        if len(entry_resp["digital"]) == 0:
            return links
        dl_link = tu_dl_url.format(entry_resp["digital"][0]["doc_id"])
        # response = requests.head(dl_link, allow_redirects=True, verify=False)
        # if response.status_code // 100 != 2:
        #     return links
        return [dl_link]
    return links


def extract_search_details(search_resp: Any) -> Tuple[Any, Any]:

    detail_url = (
        "https://digital.library.tu.ac.th/tu_dc/digital/api/Biblio/detailData/{}"
    )
    debug_doc = []
    result = []

    accpeted_description_fld = ["description", "Table of contents"]
    for entry in search_resp["result"]["result"]:
        details = {}
        bibid = entry["bibid"]
        doc_url = detail_url.format(bibid)
        print("=" * 80)
        print(doc_url)
        response = requests.get(doc_url, verify=False)
        if response.status_code != 200:
            continue
        entry_resp = json.loads(response.text)
        debug_doc.append(entry_resp["template_data"])

        details["_doc_url"] = doc_url
        details["title"] = entry["title"]
        details["keywords"] = [keyword for keyword in entry["keyword_full"]]
        details["organization"] = entry_resp["biblio_info"]["cat_name"]
        details["description"] = None
        for section in ["fld_name", "fld_tag"]:
            for fld in accpeted_description_fld:
                if fld in entry_resp["template_data"][section]:
                    details["description"] = entry_resp["template_data"][section][fld]
        details["created_date"] = entry_resp["biblio_info"]["time_create"]
        details["URL"] = get_links(entry_resp)
        details["authored_year"] = entry["pubyear_highlight"]
        result.append(details)

    return result, debug_doc


if __name__ == "__main__":
    search_resp = search_from_phrase("น้ำ", page_size=10)
    result, debug_doc = extract_search_details(search_resp)
    with open("result.json", "w") as f:
        json.dump(result, f, indent=4)
    with open("debug_doc.json", "w") as f:
        json.dump(debug_doc, f, indent=4)

    # resp = search_from_phrase('น้ำ', page_size=1000)
    # print(json.dumps(resp, indent=4))

    # for page in range(1,3):
    #     resp = search_from_phrase('น้ำ', page=page)
    #     for entry in resp["result"]["result"]:
    #         print(entry["title"])
