import pandas as pd
import re
import argparse
from string import digits, punctuation
from minhash import create_lsh_index, query_similar_documents

# Global variables
academic_fields = []
filled_academic_df = None
counter_keyword = 0
counter_minhash = 0
counter_wiki = 0


def read_raw_data(file_path):
    return pd.read_csv(file_path, header=0)


def clean_double_space(text):
    return re.sub(' +', ' ', text)


def remove_punctuation_digit(text):
    if isinstance(text, str):
        return clean_double_space(''.join([char for char in text if char not in digits and char not in punctuation]))


def lower_strip(df, columns_list):
    for column in columns_list:
        column_cleaned = column + '_cleaned'
        df[column_cleaned] = df[column].str.lower().apply(remove_punctuation_digit).str.strip()
    return df


def get_unique_values(df, column):
    df = df.dropna(subset=[column])
    df = df.groupby(column).size().reset_index(name='count').sort_values('count', ascending=False)
    return df[column].unique()


def find_academic_field_keyword(degree):
    global counter_keyword
    for field in academic_fields:
        if field in degree:
            counter_keyword += 1
            return field
    return None


def find_academic_fields_minhash(degree, lsh_index, ngram_range=(2, 2)):
    global filled_academic_df
    global counter_minhash
    similar_academic_fields = query_similar_documents(degree, lsh_index, filled_academic_df['academic_field_cleaned'],
                                                      ngram_range=ngram_range)
    if similar_academic_fields:
        doc_id, score = similar_academic_fields
        counter_minhash += 1
        return filled_academic_df.loc[doc_id, 'academic_field_cleaned']
    return None


def find_academic_field_wiki(degree, academic_fields_list):
    global counter_wiki
    for field in academic_fields_list:
        field = field.strip()
        if field in degree:
            counter_wiki += 1
            return field
    return None


def fill_missing_academic_fields(df, level, report_lines):
    global academic_fields
    global filled_academic_df

    # Level 1: Keyword matching
    report_lines.append(f"Number of missing academic fields: {df['academic_field_cleaned'].isnull().sum()}")
    missing_academic_df = df[df['academic_field_cleaned'].isnull()]
    df.loc[missing_academic_df.index, 'academic_field_cleaned'] = missing_academic_df['field_of_study_cleaned'].apply(find_academic_field_keyword)
    report_lines.append(f"Number of matches using keywords: {counter_keyword}")

    # Level 2: MinHash
    if level > 1:
        missing_academic_df = df[df['academic_field_cleaned'].isnull()]
        filled_academic_df = df.dropna(subset=['academic_field_cleaned'])
        lsh_index = create_lsh_index(filled_academic_df['academic_field_cleaned'], ngram_range=(2, 2))
        df.loc[missing_academic_df.index, 'academic_field_cleaned'] = missing_academic_df['field_of_study_cleaned'].apply(
            find_academic_fields_minhash, lsh_index=lsh_index, ngram_range=(2, 4))
        report_lines.append(f"Number of matches using MinHash: {counter_minhash}")

    # Level 3: Wikipedia matching
    if level > 2:
        missing_academic_df = df[df['academic_field_cleaned'].isnull()]
        with open('csv/wiki/academic_fields.txt', 'r') as file:
            academic_fields_list = file.readlines()
        df.loc[missing_academic_df.index, 'academic_field_cleaned'] = missing_academic_df['field_of_study_cleaned'].apply(
            find_academic_field_wiki, academic_fields_list=academic_fields_list)
        report_lines.append(f"Number of matches using Wiki: {counter_wiki}")

    filled_percentage = round((df['academic_field_cleaned'].count() / df.shape[0]), 4) * 100
    report_lines.append(f'Percentage of filled academic fields: {filled_percentage}')
    # Fill remaining missing values with 'Other'
    df['academic_field_cleaned'] = df['academic_field_cleaned'].fillna('other')
    return df


def fill_missing_academic_level(row):
    if pd.isnull(row['level_name']) and pd.notnull(row['level']):
        row['level_name'] = row['level']
    else:
        row['level_name'] = row['level_name'] if pd.notnull(row['level_name']) else 'unknown'
        row['level'] = row['level'] if pd.notnull(row['level']) else 'unknown'
    return row


def main(file_path, level, debug):
    global academic_fields
    columns_list = ['field_of_study', 'academic_field']
    report_lines = []

    # Read and clean data
    df = read_raw_data(file_path)
    df = lower_strip(df, columns_list)
    academic_fields = get_unique_values(df, 'academic_field_cleaned')

    # Fill missing academic fields
    df = fill_missing_academic_fields(df, level, report_lines)
    df = df.apply(fill_missing_academic_level, axis=1)

    # Save cleaned data
    if debug:
        df.to_csv('csv/stg/cleaned_field_of_study.csv', index=False)
    df = df[['level', 'level_name', 'field_of_study', 'academic_field_cleaned']]
    df.rename(columns={'academic_field_cleaned': 'academic_field'}, inplace=True)
    df.to_csv('csv/cleaned/cleaned_field_of_study.csv', index=False)

    # Write report to file
    with open('csv/report.txt', 'w') as report_file:
        report_file.write("\n".join(report_lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process academic field data.')
    parser.add_argument('file_path', type=str, help='Path to the input CSV file')
    parser.add_argument('--level', type=int, choices=[1, 2, 3], default=1, help='Level of processing (default: 1)')
    parser.add_argument('--debug', action='store_true', default=False, help='Save stg files for debugging')
    args = parser.parse_args()
    main(args.file_path, args.level, args.debug)
