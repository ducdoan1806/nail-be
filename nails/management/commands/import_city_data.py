import json
from django.core.management.base import BaseCommand
from nails.models import City, District, Ward


class Command(BaseCommand):
    help = "Import city data from JSON file"

    def handle(self, *args, **kwargs):
        # Đường dẫn tới file JSON
        file_path = "data/vietnam_city_data.json"

        # Đọc file JSON
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        city_code_counter = 1  # Bắt đầu từ 1 để tạo mã duy nhất
        district_code_counter = 1  # Bắt đầu từ 1 để tạo mã duy nhất cho District
        ward_code_counter = 1  # Bắt đầu từ 1 để tạo mã duy nhất cho Ward

        # Duyệt qua các tỉnh/thành phố
        for city_data in data:
            city, created = City.objects.get_or_create(
                name=city_data["name"],
                code=city_code_counter,  # Tạo mã duy nhất cho mỗi City
            )
            city_code_counter += 1  # Tăng giá trị code lên sau mỗi lần tạo city

            # Duyệt qua các huyện/quận
            for district_data in city_data["districts"]:
                district, created = District.objects.get_or_create(
                    name=district_data["name"],
                    code=district_code_counter,  # Tạo mã duy nhất cho mỗi District
                    city=city,
                )
                district_code_counter += (
                    1  # Tăng giá trị code lên sau mỗi lần tạo district
                )

                # Duyệt qua các phường/xã
                for ward_data in district_data["wards"]:
                    Ward.objects.get_or_create(
                        name=ward_data["name"],
                        code=ward_code_counter,  # Tạo mã duy nhất cho mỗi Ward
                        district=district,
                    )
                    ward_code_counter += 1  # Tăng giá trị code lên sau mỗi lần tạo ward

        self.stdout.write(self.style.SUCCESS("Successfully imported city data"))
