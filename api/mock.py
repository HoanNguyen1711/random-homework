import boto3
import json
import argparse

s3_client = boto3.client('s3')
bucket_name = 'hoan-test-bucket'


def mock_get_linkedin_data(email: str):
    with open('raw/api_json_exercise.json', 'r') as file:
        json_data = json.load(file)
    return json_data


def etl_linkedin_data(email: str):
    response = mock_get_linkedin_data(email)
    if not response['success']:
        raise ValueError("API call failed")

    person = response['person']
    company = response['company']

    educations = person.get("schools", {}).get("educationHistory", [])
    degrees = [{
        "degreeName": education.get("degreeName"),
        "schoolName": education.get("schoolName"),
        "fieldOfStudy": education.get("fieldOfStudy")
    } for education in educations]

    company_info = {
        "company_name": company.get("name"),
        "employee_count": company.get("employeeCount")
    }

    return degrees, company_info, response


def write_json_to_s3(email: str, data: dict):
    file_name = f"{email.replace('@', '_at_').replace('.', '_')}.json"
    s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(data))
    print(f"Data written to S3 bucket {bucket_name} with key {file_name}")


def read_json_from_s3(email: str) -> dict:
    file_name = f"{email.replace('@', '_at_').replace('.', '_')}.json"
    response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
    data = json.loads(response['Body'].read().decode('utf-8'))
    return data


def main():
    parser = argparse.ArgumentParser(description="Extract, transform, and load LinkedIn data.")
    parser.add_argument('email', type=str, help='The email address to get LinkedIn data for')
    args = parser.parse_args()

    email = args.email
    degrees, company_info, original_data = etl_linkedin_data(email)

    write_json_to_s3(email, original_data)

    # Display the extracted data
    print("Degrees:")
    for degree in degrees:
        print(f"School: {degree['schoolName']}, Degree: {degree['degreeName']}, Field of Study: {degree['fieldOfStudy']}")

    print("\nCompany Information:")
    print(f"Company Name: {company_info['company_name']}")
    print(f"Employee Count: {company_info['employee_count']}")

    # Read back the data from S3 to verify
    retrieved_data = read_json_from_s3(email)
    print("\nRetrieved JSON data from S3:")
    print(json.dumps(retrieved_data, indent=4))


if __name__ == "__main__":
    main()
