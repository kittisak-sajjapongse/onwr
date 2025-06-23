import json

import ollama


def relevance_check(title: str, lang: str) -> bool:
    persona_th = "คุณคือข้าราชการทำงานเกี่ยวกับการวางแผนการจัดการน้ำเพื่อป้องกันน้ำท่วมและเพื่อจัดสรรหาน้ำให้เกษตรกร"
    prompt_th = (
        f"หัวเรื่อง: '{title}'\n"
        "จากหัวเรื่องจงตอบว่าหัวเรื่องดังกล่าวเกี่ยวข้องโดยตรงกับการจัดการน้ำหรือไม่"
        "ให้ตอบ 'True' หากหัวเรื่องเกี่ยวกับหนึ่งในหัวข้อ แต่ถ้าไม่เกี่ยวให้ตอบ 'False'"
        "ตอบ 'True' หรือ 'False' เท่านั้น โดยห้ามใส่คำอื่นเข้ามาโดยเด็ดขาด"
    )

    persona_en = (
        "You are a civil servance working in the area of water management."
        "Your main responsibility is to prevent flooding and irrigation for argriculture."
    )
    prompt_en = (
        f"Title: '{title}'\n"
        "Determine if the given title is directly related to water management or irrigation"
        "You must mention 'True' if the title is directly related and 'False' otherwise"
        "Your response must not include other words."
    )

    persona = persona_th if lang == "TH" else persona_en
    prompt = prompt_th if lang == "TH" else prompt_en

    true_cnt = 0
    false_cnt = 0
    for _ in range(0, 10):
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": prompt},
            ],
        )
        if response["message"]["content"].lower() == "true":
            true_cnt += 1
        elif response["message"]["content"].lower() == "false":
            false_cnt += 1
    final_tf = True if true_cnt > false_cnt else False
    print(f"\tAnswer: {final_tf} ({true_cnt}/{false_cnt})\n\n")
    return final_tf


def language_check(title: str) -> str:
    persona = "You are a language experts who knows English and Thai languages"
    prompt = (
        f"Title: '{title}'\n"
        "Determine the langage of the given title by mentioning "
        "'EN' if the title is in English language, "
        "'TH' if the title is in Thai language"
        "Do not include other word in your response."
    )

    th_cnt = 0
    en_cnt = 0
    for _ in range(0, 3):
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": prompt},
            ],
        )
        if response["message"]["content"] == "TH":
            th_cnt += 1
        elif response["message"]["content"] == "EN":
            en_cnt += 1
        final_lang = "TH" if th_cnt > en_cnt else "EN"
    print(f"\tLang: {final_lang}")
    return final_lang


if __name__ == "__main__":
    with open("merged.json") as f:
        js = json.load(f)

    related = []
    unrelated = []
    total_docs = len(js)
    for i, entry in enumerate(js):
        title = entry["title"]
        print(f"({i}/{total_docs}) Title: {title}")
        lang = language_check(title)
        is_related = relevance_check(title, lang)
        if is_related:
            related.append(entry)
        else:
            unrelated.append(entry)

    with open("related.json", "w") as f:
        json.dump(related, f)
    with open("unrelated.json", "w") as f:
        json.dump(unrelated, f)
