import os
from openai import OpenAI
from langchain.text_splitter import CharacterTextSplitter


client = OpenAI(base_url="https://api-obon.conf.in.th/team14/v1", api_key="0000")

summarize_prompt = "You are an expert in text summarization. Your task is to read and condense the given text so that the main points can be understood quickly and comprehensively.\
            Please summarize the received text appropriately with the same language as article, retaining the meaning and key information. If there are major points, important numbers, or specific information that needs emphasis,\
            please include them. Additionally, use clear and concise language to ensure the summary is highly effective."

bullet_summarize_prompt = """
You are an AI assistant specialized in summarizing text into concise bullet points. Follow these guidelines:

1.Analyze the input text and identify the main ideas and key points.
2.Create a bullet-point summary, with each point capturing a distinct main idea or important detail.
3.Use clear, concise language for each bullet point.
4.Maintain the original meaning and intent of the text.
5.Organize bullet points in a logical order, following the structure of the original text when appropriate.
6.Aim for 3-7 bullet points for most texts, adjusting based on length and complexity.
7.Start each bullet point with a dash (-) for consistency.
8.Avoid redundancy between bullet points.
9.Do not include minor details or examples unless crucial to understanding.
10.If the text contains numerical data or statistics, include the most significant ones in your summary.

Your goal is to provide a clear, concise summary that captures the essence of the original text in an easily digestible format.
"""

list_making_prompt = """ 
Analyze the given article and:

1.Identify the article's language and use it for your response.
2.Extract all mentioned tasks or action items.
3.Categorize each task as "To Do", "Doing", or "Done".
4.Present results in three lists: To Do, Doing, Done.
5.Use clear, concise language matching the article's style.
6.Include category headers even if empty.

I will give you a sample article to practice on.
Input:
    - สปรินท์หกสัปดาห์ผ่านไปสองสัปดาห์, ฟังก์ชันหลักเช่นแคตตาล็อกสินค้าและฟีเจอร์การค้นหามีความคืบหน้า 70%
    - ทีมพัฒนาพิจารณาสถาปัตยกรรมแบ็กเอนด์ระหว่างไมโครเซอร์วิสและโมโนลิธิก, มีแนวโน้มเลือกโมโนลิธิกแบบโมดูลาร์
    - ผู้เชี่ยวชาญ QA เห็นด้วยกับการผสมผสาน: ใช้โมโนลิธิกแบบโมดูลาร์ในตอนแรก, แล้วออกแบบให้มีขอบเขตชัดเจนเพื่อแยกเป็นไมโครเซอร์วิสในภายหลัง
    - ลูกค้าต้องการโฟกัสที่ตะกร้าสินค้าและกระบวนการชำระเงินเป็นลำดับถัดไป
    - สำเร็จการล็อคแบบ optimistic ในฐานข้อมูลเพื่อจัดการธุรกรรมที่เกิดขึ้นพร้อมกันได้
Output:
    To Do:
    1. พิจารณาสถาปัตยกรรมแบ็กเอนด์: ไมโครเซอร์วิส vs โมโนลิธิก
    2. พัฒนาโครงสร้างตะกร้าสินค้าและกระบวนการชำระเงิน

    Doing:
    1. ปรับปรุงแคตตาล็อกสินค้าและฟีเจอร์การค้นหา (70% เสร็จ)
    2. พิจารณาการผสมผสานสถาปัตยกรรมแบ็กเอนด์: โมโนลิธิกแบบโมดูลาร์และไมโครเซอร์วิส

    Done:
    1. จัดการล็อคแบบ optimistic ในฐานข้อมูล

Keep output brief, relevant, and in the same language as the input article. """


text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    separator=" ",
    chunk_size=700,
    chunk_overlap=100,
    is_separator_regex=False,
    model_name="text-embedding-3-small",
    encoding_name="text-embedding-3-small",
)


def get_response(task, message):
    completion = client.chat.completions.create(
        model="scb10x/llama-3-typhoon-v1.5x-70b-instruct-awq",
        # model="typhoon-v1.5-instruct",
        messages=[
            {"role": "system", "content": task},
            {"role": "user", "content": message},
        ],
        stop="<|eot_id|>",
        temperature=0,
    )
    return completion.choices[0].message.content


if __name__ == "__main__":
    with open("raw_text.txt", "r") as file:
        text = file.read()

    print("chunking texts...")
    doc_list = text_splitter.create_documents([text])

    sum_list = []
    print("Summarizing meeting...")
    for i in range(len(doc_list)):
        sum = get_response(summarize_prompt, doc_list[i].page_content)
        sum_list.append(sum)
    print("Tasks summarized...")
    bullet_summarize = get_response(bullet_summarize_prompt, "\n".join(sum_list))

    print("convert to Trello...")
    trello = get_response(list_making_prompt, bullet_summarize)

    print("saving results...")
    with open("summary.txt", "w") as file:
        file.write("\n".join(sum_list))
    with open("bullet_summary.txt", "w") as file:
        file.write(bullet_summarize)
    with open("trello.txt", "w") as file:
        file.write(trello)
    print("Done!")
