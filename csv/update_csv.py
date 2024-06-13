import pandas as pd
import argparse
import os


def read_existing_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=['level', 'level_name', 'field_of_study', 'academic_field'])


def update_data(existing_df, new_entry):
    new_df = pd.DataFrame([new_entry], columns=['level', 'level_name', 'field_of_study', 'academic_field'])
    combined_df = pd.concat([existing_df, new_df]).drop_duplicates().reset_index(drop=True)
    return combined_df


def save_data(df, file_path):
    df.to_csv(file_path, index=False)


def main(file_path, field_of_study, academic_field, level, level_name):
    existing_df = read_existing_data(file_path)
    new_entry = {
        'level': level.lower().strip() if level is not None else 'unknown',
        'level_name': level_name.lower().strip() if level_name is not None else 'unknown',
        'field_of_study': field_of_study,
        'academic_field': academic_field.lower().strip()
    }
    updated_df = update_data(existing_df, new_entry)
    save_data(updated_df, file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update academic field data.')
    parser.add_argument('field_of_study', type=str, help='Field of study to add')
    parser.add_argument('academic_field', type=str, help='Academic field to add')
    parser.add_argument('--level', type=str, default=None, help='Level of study (default: unknown)')
    parser.add_argument('--level_name', type=str, default=None, help='Level name (default: unknown)')
    parser.add_argument('--file_path', type=str, default='csv/cleaned/cleaned_field_of_study.csv',
                        help='Path to the CSV file to update')

    args = parser.parse_args()

    main(args.file_path, args.field_of_study, args.academic_field, args.level, args.level_name)
