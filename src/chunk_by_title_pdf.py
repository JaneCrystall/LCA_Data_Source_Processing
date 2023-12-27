import json
import os
import tempfile

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader, PdfWriter
from tenacity import retry
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean, group_broken_paragraphs
from unstructured.documents.elements import (
    CompositeElement,
    Footer,
    Header,
    Image,
    NarrativeText,
    Table,
)
from unstructured.partition.auto import partition
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)


load_dotenv()
openai_client = OpenAI()

pdf_name = "3.8-cutoff-25104.pdf"

min_image_width = 250
min_image_height = 270


def extract_pages(filename):
    # 获取文件名（不包括扩展名）
    base_name = os.path.splitext(filename)[0]
    # 创建新的文件名
    output_filename = "pdfs/" + base_name + "_new.pdf"

    pdf_reader = PdfReader(filename)
    pdf_writer = PdfWriter()

    total_pages = len(pdf_reader.pages)

    # 提取第一页
    first_page = pdf_reader.pages[0]
    pdf_writer.add_page(first_page)

    # 提取最后两页
    for page_number in range(total_pages - 2, total_pages):
        page = pdf_reader.pages[page_number]
        pdf_writer.add_page(page)

    with open(output_filename, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

    return output_filename


new_pdf_name = extract_pages(pdf_name)

elements = partition(
    filename=new_pdf_name,
    pdf_extract_images=False,
    pdf_image_output_dir_path=tempfile.gettempdir(),
    skip_infer_table_types=["jpg", "png", "xls", "xlsx"],
    # strategy="hi_res",
)

filtered_elements = [
    element
    for element in elements
    if not (
        isinstance(element, Header)
        or isinstance(element, Footer)
        or isinstance(element, NarrativeText)
    )
]

for element in filtered_elements:
    if element.text != "":
        element.text = group_broken_paragraphs(element.text)
        element.text = clean(
            element.text,
            bullets=False,
            extra_whitespace=True,
            dashes=False,
            trailing_punctuation=False,
        )
    # elif isinstance(element, Image):
    #     point1 = element.metadata.coordinates.points[0]
    #     point2 = element.metadata.coordinates.points[2]
    #     width = abs(point2[0] - point1[0])
    #     height = abs(point2[1] - point1[1])
    #     if width >= min_image_width and height >= min_image_height:
    #         element.text = vision_completion(element.metadata.image_path)

chunks = chunk_by_title(
    elements=filtered_elements,
    multipage_sections=True,
    combine_text_under_n_chars=0,
    new_after_n_chars=None,
    max_characters=4096,
)

text_list = []
for chunk in chunks:
    if isinstance(chunk, CompositeElement):
        text = chunk.text
        text_list.append(text)
    elif isinstance(chunk, Table):
        if text_list:
            text_list[-1] = text_list[-1] + "\n\n" + chunk.metadata.text_as_html
        else:
            text_list.append(chunk.metadata.text_as_html)

# result_list = []

# for text in text_list:
#     split_text = text.split("\n\n", 1)
#     if len(split_text) == 2:
#         title, body = split_text
#         result_list.append({"title": title, "body": body})


# msgs = [
#     SystemMessage(
#         content="Generate JSON based on the text below."
#     ),
#     HumanMessage(content="Text:"),
#     HumanMessagePromptTemplate.from_template("{result_list}"),
# ]

@retry(stop_max_attempt_number=5)
def create_completion(**kwargs):
    return openai_client.chat.completions.create(**kwargs)

response = create_completion(
    model="gpt-4-1106-preview",
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant designed to output JSON with the key name of CSV_Content.",
        },
        {
            "role": "user",
            "content": f"""从下面信息中仔细分辨并提取信息: First Author, Additional Author(s), Title, Year, Volume Number, Issue Number, Journal，输出为csv格式：\n\n{text_list}""",
        },
    ],
)


result = response.choices[0].message.content
dict_data = json.loads(result)

with open("test.csv", "a+") as f:
    f.write(dict_data["CSV_Content"])



df = pd.DataFrame(result_list)
print(df)
df.to_excel("output.xlsx", index=True, header=True)


# for result in result_list:
#     print(result)
#     print("\n\n" + "-" * 80)
#     input()
