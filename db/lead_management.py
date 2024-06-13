import asyncio
import argparse
from uuid import uuid4
from typing import Optional, Dict, List
import json
from enum import Enum
from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field, ValidationError


class CompanyType(str, Enum):
    STARTUP = "Startup"
    MID_MARKET = "Mid Market"
    MULTI_NATIONAL_COMPANY = "Multi National Company"


class Lead(Document):
    id: str = Field(default_factory=lambda: uuid4().hex)
    status: int = 0
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None
    academic_field: Optional[str] = None
    company_type: Optional[CompanyType] = None


async def init():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = client["aipiping2"]
    await init_beanie(database, document_models=[Lead])


async def populate_data(file_path: str, error_file_path: str):
    with open(file_path, 'r') as file, open(error_file_path, 'w') as error_file:
        for line in file:
            try:
                lead_data = json.loads(line.strip())
                lead = Lead(**lead_data)
                await lead.insert()
            except (ValidationError, ValueError) as e:
                print(f"Error inserting record: {lead_data}, Error: {e}")
                error_file.write(json.dumps(lead_data) + "\n")


async def select_lead_persona(query_params: Dict):
    query = {k: v for k, v in query_params.items() if v is not None}
    leads = await Lead.find(query).to_list()
    return leads


async def update_lead(lead_id: str, update_data: Dict):
    lead = await Lead.get(lead_id)
    if lead:
        for key, value in update_data.items():
            setattr(lead, key, value)
        await lead.save()
        return lead
    return None


async def delete_lead(lead_id: str):
    lead = await Lead.get(lead_id)
    if lead:
        await lead.delete()
        return True
    return False


def format_lead_persona(lead):
    return {
        "id": lead.id,
        "status": lead.status,
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "email": lead.email,
        "photo_url": lead.photo_url,
        "academic_field": lead.academic_field,
        "company_type": lead.company_type
    }


async def main(args):
    await init()

    if args.populate:
        await populate_data(args.file_path, args.error_file_path)
        print("Sample data populated.")

    if args.query_params:
        query_params = json.loads(args.query_params)
        lead_personas = await select_lead_persona(query_params)
        for lead in lead_personas:
            print(format_lead_persona(lead))

    if args.update_lead_id and args.update_data:
        update_data = json.loads(args.update_data)
        updated_lead = await update_lead(args.update_lead_id, update_data)
        if updated_lead:
            print("Lead updated:", format_lead_persona(updated_lead))
        else:
            print("Lead not found.")

    if args.delete_lead_id:
        success = await delete_lead(args.delete_lead_id)
        if success:
            print(f"Lead with ID {args.delete_lead_id} deleted.")
        else:
            print(f"Lead with ID {args.delete_lead_id} not found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query lead personas from the database.")
    parser.add_argument("--lead_id", type=str, help="Lead ID to query.")
    parser.add_argument("--query_params", type=str, help="JSON string of query parameters to filter leads.")
    parser.add_argument("--populate", action="store_true", help="Populate the database with sample data.")
    parser.add_argument("--file_path", type=str, help="Path to the file containing lead data.",
                        default="raw/leads.txt")
    parser.add_argument("--error_file_path", type=str, help="Path to the file to save error records.",
                        default="db/error_leads.txt")
    parser.add_argument("--update_lead_id", type=str, help="Lead ID to update.")
    parser.add_argument("--update_data", type=str, help="JSON string of the data to update the lead with.")
    parser.add_argument("--delete_lead_id", type=str, help="Lead ID to delete.")

    args = parser.parse_args()
    asyncio.run(main(args))
