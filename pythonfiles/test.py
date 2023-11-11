import pandas as pd
import toml

from langchain.chains.openai_functions import create_structured_output_chain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage


with open("secrets.toml", "r") as file:
    secrets = toml.load(file)

openai_api_key = secrets["openai_api_key"]
llm_model = secrets["llm_model"]
langchain_verbose = str(secrets["langchain_verbose"])


def func_calling_chain():
    func_calling_json_schema = {
        "title": "get_structured_sources_to_list",
        "description": "Extract the source information from text and return it in a json.",
        "type": "object",
        "properties": {
            "sources": {
                "title": "sources",
                "description": """All sources information extracted from text, in a json format. Each source should be in a single string, including its title, publisher, and the year of publication if available. These details should be placed in an array named 'sources'. For instance, if I have two sources: "平成12年工業統計調査" published by "経済産業省" in 2002, and "素形材年鑑" published by "財団法人素形材センター", the JSON should look like this:
{
  "sources": [
    "平成12年工業統計調査 (経済産業省, 2002)",
    "素形材年鑑 (財団法人素形材センター)"
  ]
}""",
                "type": "string",
            },
        },
        "required": ["sources"],
    }

    prompt_func_calling_msgs = [
        SystemMessage(
            content="You are a world class algorithm for extracting the sources information from text. Make sure to answer in the correct structured format."
        ),
        HumanMessage(content="Text:"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]

    prompt_func_calling = ChatPromptTemplate(messages=prompt_func_calling_msgs)

    llm_func_calling = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name=llm_model,
        temperature=0,
        streaming=False,
    )

    func_calling_chain = create_structured_output_chain(
        output_schema=func_calling_json_schema,
        llm=llm_func_calling,
        prompt=prompt_func_calling,
        verbose=langchain_verbose,
    )

    return func_calling_chain


# 使用pandas读取Excel文件
df = pd.read_excel("data/idea-348.xlsx")
general_comment = df["GeneralComment"]

sources_function_calling_chain = func_calling_chain()

response = []
for comment in general_comment:
    func_calling_response = sources_function_calling_chain.run(comment)
    response.append(func_calling_response)

# 将结果添加到 DataFrame
df["Response"] = response

# 将修改后的 DataFrame 写回原 Excel 文件
df.to_excel("data/idea-348.xlsx", index=False)

# all_sources = []
# for item in response:
#     all_sources.extend(item['sources'])
