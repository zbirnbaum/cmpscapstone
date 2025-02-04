from django.core.management.base import BaseCommand
import requests
from capstone_frontend.cap_frontend.models import Calls


class Command(BaseCommand):
    help = "Fetches data from NOLA Open Data and updates the database"
    
    def handle(self, *args, **options):

        original_url = "https://data.nola.gov/resource/2jgv-pqrq.json"
        query_size = 500
        offset = 0

        self.stdout.write("Fetching the data")
        while True:
            url = f"{original_url}?$limit={query_size}&$offset={offset}"
            response = requests.get(url)

            if response.status_code!=200:
                self.stderr.write("Failed to retrieve data")
                return

            data = response.json()
            if not data:
                self.stdout.write("Done! All records have been fetched.")
                break

            batch_request_numbers = [row.get('service_request') for row in data]
            existing_requests = set(Calls.objects.filter(request_number__in=batch_request_numbers).values_list("request_number", flat=True))
            
            transformed_data = [
                Calls(
                    request_number= row.get('service_request', 'Unknown'),
                    request_type = row.get('request_type', 'Unknown'),
                    reason= row.get('request_reason', 'Unknown'),
                    date_created= row.get('date_created', 'Unknown'),
                    date_modified= row.get('date_modified', 'Unknown'),
                    date_closed= row.get('case_close_date', 'Unknown'),
                    request_status= row.get('request_status', 'Unknown'),
                    agency= row.get('responsible_agency', 'Unknown'),
                    address= row.get('final_address', 'Unknown'),
                    council_district= row.get('address_councildis', 'Unknown'),
                    status= row.get('status', 'Unknown'),
                    contractor= row.get('contractor', 'Unknown'),
                    contractor_action= row.get('contractor_action', 'Unknown'),
                    longitude= row.get('longitude', 'Unknown'),
                    latitude= row.get('latitude', 'Unknown'),
                    location= row.get('geocoded_column', 'Unknown')
                )
                for row in data if row.get('service_request') not in existing_requests
            ]
            
            if transformed_data:
                Calls.objects.bulk_create(transformed_data)
                self.stdout.write(f"Inserted {len(transformed_data)} rows with offset={offset}")
     
            
            offset += query_size
        print("Success")
        #return