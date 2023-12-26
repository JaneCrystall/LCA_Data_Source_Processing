from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer


# Get the total number of pages
total_pages = sum(1 for _ in extract_pages("3.8-cutoff-25104.pdf"))

# Specify the pages you want to extract. In this case, the first page and the last two pages.
pages_to_extract = {0, total_pages - 1, total_pages - 2}

text = extract_text("3.8-cutoff-25104.pdf", page_numbers=pages_to_extract)
print(text)

for i, page_layout in enumerate(extract_pages("3.8-cutoff-25104.pdf")):
    if i in pages_to_extract:
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                print(f"Page {i+1}:\n{element.get_text()}\n")


# print(repr(text))

"<table><thead><th>Established report panel and commenced training sessions for the CSR report</th></thead><tr><td>Initiated key interviews and stakeholder research</td></tr><tr><td>Finalized report structure and content for each section, and started to collect material</td></tr><tr><td>In preparation of report, as well as report content review and confirmation</td></tr><tr><td>Approved and issued by BYD CSR management committee and board of directors</td></tr></table>"
