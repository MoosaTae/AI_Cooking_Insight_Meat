import gradio as gr
import os
from openai import OpenAI
from langchain.text_splitter import CharacterTextSplitter

import re
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENTYPHOON_API_KEY = os.getenv("OPENTYPHOON_API_KEY")
client = OpenAI(
    base_url="https://api.opentyphoon.ai/v1",
    api_key=OPENTYPHOON_API_KEY,
)

# client = OpenAI(base_url="https://api-obon.conf.in.th/team14/v1", api_key="0000")

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_API_TOKEN = os.getenv("TRELLO_API_TOKEN")

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

# Text splitter
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
        # model="scb10x/llama-3-typhoon-v1.5x-70b-instruct-awq",
        model="typhoon-v1.5-instruct",
        messages=[
            {"role": "system", "content": task},
            {"role": "user", "content": message},
        ],
        # stop="<|eot_id|>",
        temperature=0,
    )
    return completion.choices[0].message.content


def parse_tasks(text):
    sections = re.split(r"\n(?=To Do:|Doing:|Done:)", text.strip())
    tasks = {"To Do": [], "Doing": [], "Done": []}

    for section in sections:
        if section.startswith("To Do:"):
            tasks["To Do"] = re.findall(r"\d+\.\s(.+)", section)
        elif section.startswith("Doing:"):
            tasks["Doing"] = re.findall(r"\d+\.\s(.+)", section)
        elif section.startswith("Done:"):
            tasks["Done"] = re.findall(r"\d+\.\s(.+)", section)

    return tasks


def upload_to_trello(tasks):
    url = "https://api.trello.com/1/cards"
    headers = {"Accept": "application/json"}

    idList = {
        "To Do": "66774c5dcebc33d490f463fd",
        "Doing": "66774cb80a97a9f6a3a77b1e",
        "Done": "66774cbcb80d5f2a51abb4d9",
    } # get from trello board

    results = []
    for status, task_list in tasks.items():
        for task in task_list:
            data = {
                "name": task,
                "desc": f"Task: {task}\nStatus: {status}",
            }
            query = {"key": TRELLO_API_KEY, "token": TRELLO_API_TOKEN, "idList": idList[status]}
            query.update(data)

            response = requests.request("POST", url, headers=headers, params=query)
            results.append(f"Uploaded task: {task}\nResponse: {response.text}\n")

    return "\n".join(results)


def process_text(input_text):
    doc_list = text_splitter.create_documents([input_text])

    print("Summarizing meeting...")
    sum_list = [get_response(summarize_prompt, doc.page_content) for doc in doc_list]
    summary = "\n".join(sum_list)

    print("Summarizing tasks...")
    bullet_summary = get_response(bullet_summarize_prompt, summary)

    print("Creating Trello-style list...")
    trello_list = get_response(list_making_prompt, bullet_summary)

    print("Parsing tasks...")
    tasks = parse_tasks(trello_list)

    print("Uploading to Trello...")
    trello_response = upload_to_trello(tasks)

    return summary, bullet_summary, trello_list, trello_response


# Gradio interface
def gradio_interface(input_text):

    if not input_text:
        return (
            "No input provided. Please select an example or enter custom text.",
            "",
            "",
            "",
            "",
        )

    summary, bullet_summary, trello_list, trello_response = process_text(input_text)
    return summary, bullet_summary, trello_list, trello_response


iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(
            lines=10,
            label="Or enter your own text here",
        ),
    ],
    outputs=[
        gr.Textbox(label="Summary"),
        gr.Textbox(label="Bullet Summary"),
        gr.Textbox(label="Trello-style List"),
        gr.Textbox(label="Trello Upload Response"),
    ],
    title="Text Summarization and Trello Integration",
    description="Enter text to summarize, create bullet points, generate Trello-style lists, and upload tasks to Trello.",
    cache_examples=True,
)

iface.launch(share=True)
