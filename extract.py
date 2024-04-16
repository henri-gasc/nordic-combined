#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import pypdf

def is_date(text: str) -> bool:
    date = text.count(" ") == 2
    if date:
        try:
            # Try to convert the date
            int(text.split(" ")[0])
            int(text.split(" ")[2])
        except ValueError:
            date = False
    return date

def convert_to_list(text: str) -> list[dict[str, str]]:
    records = []
    end_index = text.find("Did not Finish")
    offset = text.find("TIME BEHIND\n")
    if end_index == -1:
        text += " "
    text_list = text[offset+12:end_index].split("\n")
    i = 0
    while (i < len(text_list)-11):
        athlete = {}
        athlete["name"]           = text_list[i]
        athlete["nationality"]    = text_list[i+1]
        # Sometimes an athlete does not have a team/club, and so
        if is_date(text_list[i+2]):
            athlete["team"]       = ""
            i -= 1
        else:
            athlete["team"]       = text_list[i+2]
        athlete["birthdate"]      = text_list[i+3]
        athlete["rank"]           = text_list[i+4]
        athlete["bib"]            = text_list[i+5]
        athlete["jump_points"]    = text_list[i+6]
        athlete["jump_rank"]      = text_list[i+7]
        athlete["jump_time_diff"] = text_list[i+8]
        athlete["cross_time"]     = text_list[i+9]
        athlete["cross_rank"]     = text_list[i+10]
        athlete["time_behind"]    = text_list[i+11]
        records.append(athlete.copy())
        i += 12
    return records

def write_to_csv(file_name: str, records: list[dict[str, str]]) -> None:
    with open(file_name, "w") as f:
        f.write(",".join(records[0].keys()) + "\n")
        for line in records:
            f.write(",".join(line.values()) + "\n")

pdfs_dir = "pdf_results"
csv_dir = "extracted"

l = os.listdir(pdfs_dir)
if len(l) == 0:
    printf("No pdf found. Put them in the results folder so they can be extracted")

for pdf_path in l:
    if ".pdf" != pdf_path[-4:]:
        continue
    print(f"Doing {pdf_path}")
    pdf = pypdf.PdfReader(os.path.join(pdfs_dir, pdf_path))
    records = []
    for i in range(pdf.get_num_pages()):
        page = pdf.get_page(i)
        text = page.extract_text()
        records += convert_to_list(text)
    os.makedirs(csv_dir, exist_ok=True)
    write_to_csv(os.path.join(csv_dir, f"{pdf_path[:-4]}.csv"), records)
