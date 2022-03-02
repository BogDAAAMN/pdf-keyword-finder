import os
import argparse

import pandas as pd

from tika import parser
from alive_progress import alive_it

# Return all the .pdf file paths from the `dir` directory
def extract_pdf_paths(dir):
    pdf_paths = []

    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith('.pdf'):
                pdf_paths.append(os.path.join(root, file))

    return pdf_paths

# Return the cleaned text, without all the white spaces, tabs and newlines from text
def clean_text(text):
    return ' '.join(text.split())

# Return all the sentences from `text` that contains the `keyword`
def find_sentence(text, keyword):
    sentences = []
    dot_split = text.split('.')

    # Return three sentences as context (one before, one after)
    # If the sentence is the first one, return first three
    # If the sentence is tha last one, return last three
    for index, sentence in enumerate(dot_split):
        if keyword.lower() in sentence.lower():
            if index == 0:
                sentences.append(". ".join([
                    dot_split[index].strip(),
                    dot_split[index+1].strip(),
                    dot_split[index+2].strip(),
                    ''
                ]))
            elif index == len(dot_split):
                sentences.append(". ".join([
                    dot_split[index-2].strip(),
                    dot_split[index-1].strip(),
                    dot_split[index].strip(),
                    ''
                ]))
            else:
                sentences.append(". ".join([
                    dot_split[index-1].strip(),
                    dot_split[index].strip(),
                    dot_split[index+1].strip(),
                    ''
                ]))
                
    return sentences

# Return directories and file name from `path`
def split_path(path):
    head_tail_path = os.path.split(path)
    return [part.replace('./', '') for part in head_tail_path]

# Return list of keywords from string
def split_keywords(input):
    return [keyword.strip() for keyword in input.split(',')]

# Create excel file with the findings
def export_lines(lines, filename):
    df = pd.DataFrame(lines)
    # df.to_excel(filename)

    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='keywords', index=False)
        
        workbook = writer.book
        center_format = workbook.add_format({'valign': 'vcenter'})
        wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'vcenter'})

        worksheet = writer.sheets['keywords']
        worksheet.set_column('A:C', 20, center_format)
        worksheet.set_column('D:D', 45, wrap_format)

    return df.shape

if __name__ == "__main__":
    # Create the CLI arguments
    arg_parser = argparse.ArgumentParser(description='Find keywords in a collection of PDF files.')
    arg_parser.add_argument('src', help='source directory with PDF files')
    arg_parser.add_argument('keywords', help='list of keyword separated by comma')
    arg_parser.add_argument('out', nargs='?', default='data.xlsx', help='name of the output xlsx file')
    args = arg_parser.parse_args()

    # Parse the CLI arguments
    source_path_input = args.src
    keywords_input = args.keywords
    out_path_input = args.out

    # Parse mock file to start the parser server and check status
    p = parser.from_file('start.pdf')
    print(f'Parser server status: {p["status"]}')

    # Extract the paths of all the .pdf files
    paths = extract_pdf_paths(source_path_input)
    print(f'Found {len(paths)} PDF files.')

    # Process the keywords
    # keywords_input = "referral, referral jurisdiction, Article 214 RTC, Caribbean Court of Justice, CCJ, reference, Article 214"
    print(f'Processing keywords: {len(split_keywords(keywords_input))}')

    # Init data structure
    lines = []

    for path in alive_it(paths): 
        # Extract and split the path of the pdf file
        path_directory = split_path(path)[0]
        path_file = split_path(path)[1]
        print(path_file)

        # Parse the pdf file
        text_parsed = parser.from_file(path)
        
        # Skip the processing if there is no content
        if text_parsed['content'] == None:
            print('NO_CONTENT')
            continue

        # Clean the content of the file
        text_raw = text_parsed["content"]
        text = clean_text(text_raw)

        # For each keyword find and log any finding
        for keyword in split_keywords(keywords_input):
            try:
                sentences = find_sentence(text, keyword)

                for sentence in sentences:
                    lines.append({
                        'keyword' : keyword,
                        'subdirectory': path_directory,
                        'file': path_file,
                        'context': sentence.strip()  
                    })
            except Exception as e:
                print(f'ERR {e}')

    # Export all the findings in an excel sheet
    print(export_lines(lines, out_path_input))