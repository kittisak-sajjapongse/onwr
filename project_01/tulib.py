import json
import re
from datetime import datetime
from typing import Any, List, Tuple

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Change to keywords and phrases for searching
SEARCH_PHRASE = "จัดการ น้ำ"

# Change to desired ccollection for searching
SEARCH_COLLECTION = "NRCT"


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
    assert response.status_code == 200, "Unable to retrieve search results"
    resp_js = json.loads(response.text)
    return resp_js


def search_recur(obj: Any, search_type: str) -> List[str]:
    occurences = []
    assert search_type in ["LINK", "EMAIL"], "Unknown search type"
    link_pattern = r"https://\S+?(?=\s|$)"
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    pattern = link_pattern if search_type == "LINK" else email_pattern

    if isinstance(obj, dict):
        for _, value in obj.items():
            occurences.extend(search_recur(value, search_type))
    elif isinstance(obj, list):
        for item in obj:
            occurences.extend(search_recur(item, search_type))
    elif isinstance(obj, str):
        occurences.extend(re.findall(pattern, obj))
    else:
        return occurences
    return list(set(occurences))


def get_links(entry_resp: Any) -> List[str]:
    tu_dl_url = "https://digital.library.tu.ac.th/tu_dc/digital/api/DownloadDigitalFile/dowload/{}"

    links = search_recur(entry_resp["template_data"], "LINK")
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

    accpeted_description_fld = ["description", "TH Abstract", "Table of contents"]
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

        details["_doc_metadata_url"] = doc_url
        details["_doc_page_url"] = entry["link"]
        details["title"] = entry["title"]
        details["author"] = entry_resp["biblio_info"]["author"].split(";")
        details["email"] = search_recur(entry_resp, "EMAIL")
        details["keyword"] = [keyword for keyword in entry["keyword_full"]]
        details["organization"] = entry_resp["biblio_info"]["cat_name"]
        details["description"] = None
        for section in ["fld_name", "fld_tag"]:
            for fld in accpeted_description_fld:
                if fld in entry_resp["template_data"][section]:
                    details["description"] = entry_resp["template_data"][section][fld]
        details["created_date"] = (
            datetime.strptime(
                entry_resp["biblio_info"]["time_create"], "%Y-%m-%d %H:%M:%S"
            )
            .date()
            .strftime("%Y-%m-%d")
        )
        details["URL"] = get_links(entry_resp)
        details["authored_year"] = entry["pubyear_highlight"]
        result.append(details)

    return result, debug_doc


def get_num_results(phrase: str, collection: str) -> int:
    search_resp = search_from_phrase(SEARCH_PHRASE, page_size=1, collection=collection)
    assert search_resp["result"]["metadata"]["total"]["relation"] == "eq"
    return search_resp["result"]["metadata"]["total"]["value"]


if __name__ == "__main__":

    num_results = get_num_results(SEARCH_PHRASE, SEARCH_COLLECTION)
    print(f"Found {num_results} results")
    search_resp = search_from_phrase(
        SEARCH_PHRASE, page_size=num_results, collection=SEARCH_COLLECTION
    )
    result, debug_doc = extract_search_details(search_resp)
    with open("result.json", "w") as f:
        json.dump(result, f, indent=4)
    with open("debug_doc.json", "w") as f:
        json.dump(debug_doc, f, indent=4)
