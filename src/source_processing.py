import pandas as pd
import json

# 使用pandas读取Excel文件
df = pd.read_excel("data/test.xlsx")

# 使用apply函数将sources列中的每个条目转换为有效的JSON对象
df['sources'] = df['Sources'].apply(lambda x: json.loads(x[x.index('['):x.rindex(']')+1]))

# 初始化一个空的DataFrame，用于存储解析后的JSON数据
df_parsed = pd.DataFrame()
parsed_data = []

# 遍历df的每一行
for idx, row in df.iterrows():
    # 使用json_normalize函数解析sources列中的JSON数据，并将id列的值添加到解析后的数据中
    df_temp = pd.json_normalize(row['sources'])
    df_temp['GlobalId'] = row['GlobalId']
    parsed_data.append(df_temp)

df_parsed = pd.concat(parsed_data, ignore_index=True)

print(df_parsed)



# 展开 sources 列
expanded_rows = []
for _, row in df.iterrows():
    for source in row['sources']:
        new_row = {'id': row['id'], 'name': row['name'], **source}
        expanded_rows.append(new_row)

expanded_df = pd.DataFrame(expanded_rows)

# 保存处理后的数据到新的 Excel 文件
expanded_df.to_excel('expanded_data.xlsx', index=False)

# all_sources = []
# for item in response:
#     all_sources.extend(item['sources'])
