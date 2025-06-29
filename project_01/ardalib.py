import json
import requests

from typing import Any, List, Set, Tuple


def get_total_docs(phrase: str) -> Tuple[int, int]:
    search_url = "https://tarr.arda.or.th/api/searchResearch"
    form_data = {
        "pagingButton": 1,
        "pageNo": 1,
        "sort[]": None,
        "keyword": phrase,
        "via": "web",
        "cats[]": "-งานวิจัยและวิชาการ",
        "cats[]": "-สิทธิบัตร",
    }
    response = requests.post(search_url, data=form_data, verify=False)
    assert response.status_code == 200, "Unable to retrieve search results"
    resp_js = json.loads(response.text)
    total_docs = int(resp_js["data"]["total"])
    page_size = int(resp_js["data"]["size"])
    return total_docs, page_size


def search_from_phrase(phrase: str, page: int, total_pages: int) -> Any:
    search_url = "https://tarr.arda.or.th/api/searchResearch"
    form_data = {
        "pagingButton": total_pages,
        "pageNo": page,
        "sort[]": None,
        "keyword": phrase,
        "via": "web",
        "cats[]": "-งานวิจัยและวิชาการ",
        "cats[]": "-สิทธิบัตร",
    }
    response = requests.post(search_url, data=form_data, verify=False)
    assert response.status_code == 200, "Unable to retrieve search results"
    resp_js = json.loads(response.text)
    return resp_js


def extract_search_details(search_resp: Any, result: List, doc_ids: Set) -> Any:

    # Build a dictionary of extended details
    ext_details = {}
    for item in search_resp["data"]["converted"]:
        ext_details[item["id"]] = item

    link_base = "https://tarr.arda.or.th/preview/item/{}"
    for item in search_resp["data"]["data"]:
        if item["id"] in doc_ids:
            continue
        details = {}

        doc_id = item["id"]
        link = link_base.format(doc_id)
        title = item["dc.title.th"] if "dc.title.th" in item else item["dc.title.en"]
        details["_doc_metadata_url"] = link
        details["_doc_page_url"] = link
        details["title"] = title
        details["author"] = ext_details[doc_id]["author"]
        details["email"] = []
        details["keyword"] = ext_details[doc_id]["keyword"]
        details["organization"] = ext_details[doc_id]["org"]
        details["description"] = ext_details[doc_id]["description"]
        details["created_date"] = ext_details[doc_id]["date"]
        details["URL"] = link
        details["authored_year"] = None
        result.append(details)
        doc_ids.add(doc_id)


if __name__ == "__main__":
    result = []
    doc_ids = set()
    phrase = "จัดการ น้ำ"

    # total_docs, page_size = get_total_docs(phrase=phrase)
    # pages = int(total_docs/page_size) + (1 if total_docs%page_size > 0 else 0)
    # print(f"total docs:  {total_docs}")
    # print(f"total pages: {pages}")
    # print(f"page size:   {page_size}")

    # for i in range(1, pages+1):
    #     print(f"page: {i}")
    #     resp_js = search_from_phrase(phrase=phrase, page=i, total_pages=1)
    #     with open(f"arda_resp_{i:03d}.json", "w") as f:
    #         json.dump(resp_js, f, ensure_ascii=False, indent=4)

    pages = 129
    for i in range(1, pages + 1):
        with open(f"arda_resp_{i:03d}.json") as f:
            resp_js = json.load(f)
        extract_search_details(resp_js, result, doc_ids)
        print(f"{len(result)}/{len(doc_ids)}")
    with open("result.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
