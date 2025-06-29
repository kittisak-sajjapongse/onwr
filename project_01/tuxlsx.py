import json
import re
import sys

import pandas as pd


def remove_illegal_chars(value):
    if isinstance(value, str):
        # Excel allows characters: 0x09 (tab), 0x0A (LF), 0x0D (CR), and 0x20-0xD7FF, 0xE000-0xFFFD, 0x10000-0x10FFFF
        return re.sub(
            r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\uF8FF\uFFFE\uFFFF]", "", value
        )
    return value


def main(result_file: str):
    with open(result_file) as f:
        result = json.load(f)

    csv_data = []

    for entry in result:
        author_str = None
        if len(entry["author"]) > 1:
            author_str = f"{entry["author"][0]} และคณะ"
        else:
            authors = entry["author"][0].split(",")
            if len(authors) > 1:
                author_str = f"{authors[0]} และคณะ"
            else:
                author_str = entry["author"][0]

        description = ""
        if isinstance(entry["description"], list):
            description = ",".join(entry["description"])
        elif isinstance(entry["description"], str):
            description = entry["description"]

        keyword = ""
        if isinstance(entry["keyword"], list):
            keyword = ",".join(entry["keyword"])
        elif isinstance(entry["keyword"], str):
            keyword = entry["keyword"]

        url = ""
        if isinstance(entry["URL"], list):
            url = ",".join(entry["URL"])
        elif isinstance(entry["URL"], str):
            url = entry["URL"]

        email = ""
        if isinstance(entry["email"], list):
            email = ",".join(entry["email"])
        elif isinstance(entry["email"], str):
            email = entry["email"]

        csv_data.append(
            [
                "",
                "",
                "",
                entry["title"],
                entry["organization"],
                "",
                "",
                keyword,
                description,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                entry["created_date"],
                "",
                url,
                "",
                "",
                "",
                "",
                entry["authored_year"],
                email,
                author_str,
            ]
        )
    df = pd.DataFrame(
        csv_data,
        columns=[
            "Timestamp",
            "รหัสชุดข้อมูลตามที่กำหนด (เว้นว่างไม่ต้องใส่)",
            "ประเภทข้อมูล",
            "ชื่อชุดข้อมูล",  ##
            "องค์กร",  ##
            "ชื่อฝ่ายงานสำหรับติดต่อ",
            "อีเมลสำหรับติดต่อ",
            "คำสำคัญ",  ##
            "รายละเอียด",  ##
            "วัตถุประสงค์ (เลือกได้มากกว่า 1 ข้อ)",
            "หน่วยความถี่ของการปรับปรุงข้อมูล",
            "ขอบเขตเชิงภูมิศาสตร์หรือเชิงพื้นที่",
            "รูปแบบการเก็บข้อมูล [รูปแบบ]",
            "หมวดหมู่ข้อมูลตามธรรมาภิบาลข้อมูลภาครัฐ (เลือกได้มากกว่า 1 ข้อ)",
            "ชั้นความลับของข้อมูลภาครัฐ",
            "เงื่อนไขในการเข้าถึงข้อมูล",
            "วันที่เริ่มต้นสร้าง",  ##
            "วันที่ปรับปรุงข้อมูลล่าสุด",
            "URL",  ##
            "ชุดข้อมูลที่มีคุณค่าสูง",
            "ความสอดคล้องแผนแม่บทการบริหารจัดการทรัพยากรน้ำ 20 ปี",
            "ประเภทการจัดกลุ่มตามลักษณะงาน",
            "ประเภทการจัดกลุ่มตามหมวดหมู่",
            "ปีที่แต่ง",  ##
            "Email Address",  ##
            "ผู้แต่ง",  ##
        ],
    )

    # df.to_csv('result.csv', mode='a', index=False, header=True, encoding='utf-8-sig')
    df.to_excel("result.xlsx", index=False, engine="xlsxwriter")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [RESULT_FILE]")
        sys.exit(-1)
    result_file = sys.argv[1]
    main(result_file)
