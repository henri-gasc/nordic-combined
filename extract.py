#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pypdf


def is_date(text: str) -> bool:
    """Return true if text is of the format '%d %s %d'"""
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
    """Convert the text to a list of dict.
    This may not work for other format. If it is the case, send me the pdf"""
    records = []
    end_index = text.find("Did not Finish")
    offset = text.find("TIME BEHIND\n")
    if end_index == -1:
        text += " "
    text_list = text[offset + 12 : end_index].split("\n")
    i = 0
    while i < len(text_list) - 11:
        athlete = {}
        athlete["name"] = text_list[i]
        athlete["nationality"] = text_list[i + 1]
        # Sometimes an athlete does not have a team/club, and so
        if is_date(text_list[i + 2]):
            athlete["team"] = ""
            i -= 1
        else:
            athlete["team"] = text_list[i + 2]
        athlete["birthdate"] = text_list[i + 3]
        athlete["rank"] = text_list[i + 4]
        athlete["bib"] = text_list[i + 5]
        athlete["jump_points"] = text_list[i + 6]
        athlete["jump_rank"] = text_list[i + 7]
        athlete["jump_time_diff"] = text_list[i + 8]
        athlete["cross_time"] = text_list[i + 9]
        athlete["cross_rank"] = text_list[i + 10]
        athlete["time_behind"] = text_list[i + 11]
        records.append(athlete.copy())
        i += 12
    return records


def write_to_csv(file_name: str, records: list[dict[str, str]]) -> None:
    """Write the records to a csv file"""
    with open(file_name, "w") as f:
        f.write(",".join(records[0].keys()) + "\n")
        for line in records:
            f.write(",".join(line.values()) + "\n")


def get_distance(text: str) -> float:
    """Return the distance in kilometers of the track or 0 if it was not found"""
    for line in text.split("\n"):
        # Got distance ?
        if line[-2:] == "km":
            return float(line.split("/")[1][:-2])
    return 0


def extract(path_file_in: str, dir_file_out: str) -> None:
    """Use the other function in this file to extract all text from a pdf and write it to file having the name name as the pdf with _[distance] added at the end"""
    base = os.path.basename(path_file_in)
    base = ".".join(base.split(".")[:-1])  # Remove last .* (extension)
    pdf = pypdf.PdfReader(path_file_in)
    records = []
    distance = get_distance(pdf.get_page(0).extract_text())
    for i in range(pdf.get_num_pages()):
        page = pdf.get_page(i)
        text = page.extract_text()
        records += convert_to_list(text)
    os.makedirs(csv_dir, exist_ok=True)
    path_out = os.path.join(dir_file_out, f"{base}_{distance}.csv")
    write_to_csv(path_out, records)


pdfs_dir = "pdf_results"
csv_dir = "extracted"

if __name__ == "__main__":
    l = os.listdir(pdfs_dir)
    if len(l) == 0:
        print("No pdf found. Put them in the results folder so they can be extracted")

    for pdf_path in l:
        if ".pdf" != pdf_path[-4:]:
            continue
        print(f"Doing {pdf_path}")
        extract(os.path.join(pdfs_dir, pdf_path), csv_dir)
