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
            existing_request_ids = set(Calls.objects.filter(request_number__in=batch_request_numbers).values_list("request_number", flat=True))

            batch_requests = {row.get('service_request'): row.get('date_modified') for row in data}
            existing_requests = {
                request_number: date_modified 
                for request_number, date_modified in Calls.objects.filter(
                    request_number__in=batch_requests.keys()
                ).values_list("request_number", "date_modified")
            }
            updated_requests = {
                req_num: batch_requests[req_num] 
                for req_num in batch_requests
                if req_num in existing_requests and batch_requests[req_num] != existing_requests[req_num]
            }
            
            new_rows = []
            updated_rows = []

            for row in data:
                service_request = row.get('service_request')
                
                if service_request not in existing_request_ids:
                    new_rows.append(
                        Calls(
                            request_number=service_request,
                            request_type=row.get('request_type', 'Unknown'),
                            reason=row.get('request_reason', 'Unknown'),
                            date_created=row.get('date_created', 'Unknown'),
                            date_modified=row.get('date_modified', 'Unknown'),
                            date_closed=row.get('case_close_date', 'Unknown'),
                            request_status=row.get('request_status', 'Unknown'),
                            agency=row.get('responsible_agency', 'Unknown'),
                            address=row.get('final_address', 'Unknown'),
                            council_district=row.get('address_councildis', 'Unknown'),
                            status=row.get('status', 'Unknown'),
                            contractor=row.get('contractor', 'Unknown'),
                            contractor_action=row.get('contractor_action', 'Unknown'),
                            longitude=row.get('longitude', 'Unknown'),
                            latitude=row.get('latitude', 'Unknown'),
                            location=row.get('geocoded_column', 'Unknown')
                        )
                    )
                elif service_request in updated_requests:
                    updated_rows.append(row)

            if new_rows:
                Calls.objects.bulk_create(new_rows)
                self.stdout.write(f"Inserted {len(new_rows)} rows")

            for row in updated_rows:
                service_request = row.get('service_request')
                
                existing_row = Calls.objects.filter(request_number=service_request).first()
                
                if existing_row:
                    existing_row.request_type = row.get('request_type', existing_row.request_type)
                    existing_row.reason = row.get('request_reason', existing_row.reason)
                    existing_row.date_created = row.get('date_created', existing_row.date_created)
                    existing_row.date_modified = row.get('date_modified', existing_row.date_modified)
                    existing_row.date_closed = row.get('case_close_date', existing_row.date_closed)
                    existing_row.request_status = row.get('request_status', existing_row.request_status)
                    existing_row.agency = row.get('responsible_agency', existing_row.agency)
                    existing_row.address = row.get('final_address', existing_row.address)
                    existing_row.council_district = row.get('address_councildis', existing_row.council_district)
                    existing_row.status = row.get('status', existing_row.status)
                    existing_row.contractor = row.get('contractor', existing_row.contractor)
                    existing_row.contractor_action = row.get('contractor_action', existing_row.contractor_action)
                    existing_row.longitude = row.get('longitude', existing_row.longitude)
                    existing_row.latitude = row.get('latitude', existing_row.latitude)
                    existing_row.location = row.get('geocoded_column', existing_row.location)
                    
                    existing_row.save()
                    self.stdout.write(f"Updated row with request number {service_request}")
            self.stdout.write(f"Updated database with offset={offset}")
            offset += query_size
        print("Success")
        #return