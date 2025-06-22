import json
import ollama

model = 'llama3.2:3b'
with open("merged.json") as f:
    js = json.load(f)

for entry in js:
    title = entry["title"]
    prompt = (
        f"หัวเรื่อง: '{title}'\n"
        "จากหัวเรื่องจงตอบว่าหัวเรื่องดังกล่าวเกี่ยวข้องโดยตรงกับการจัดการน้ำหรือไม่"
        "ให้ตอบ 'True' หากหัวเรื่องเกี่ยวกับหนึ่งในหัวข้อ แต่ถ้าไม่เกี่ยวให้ตอบ 'False'"
        "ตอบ 'True' หรือ 'False' เท่านั้น โดยห้ามใส่คำอื่นเข้ามาโดยเด็ดขาด"
    )

    true_cnt = 0
    false_cnt = 0
    for _ in range(0, 10):
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': 'คุณคือข้าราชการทำงานเกี่ยวกับการวางแผนการจัดการน้ำเพื่อป้องกันน้ำท่วมและเพื่อจัดสรรหาน้ำให้เกษตรกร'},
                {'role': 'user', 'content': f'{prompt}'}
            ]
        )
        if response['message']['content'].lower() == 'true':
            true_cnt += 1
        elif response['message']['content'].lower() == 'false':
            false_cnt += 1
    final_tf = True if true_cnt > false_cnt else False
    print(f"Title:{title}")
    print(f"\tAnswer: {final_tf} ({true_cnt}/{false_cnt})\n\n")
