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
            # Kiểm tra xem thành phố đã tồn tại chưa
            city, created = City.objects.get_or_create(
                name=city_data["name"],
                defaults={"code": city_code_counter},  # Tạo mã duy nhất cho mỗi City
            )
            if created:  # Chỉ tăng code nếu thành phố mới được tạo
                city_code_counter += 1

            # Duyệt qua các huyện/quận
            for district_data in city_data["districts"]:
                # Kiểm tra xem huyện/quận đã tồn tại chưa
                district, created = District.objects.get_or_create(
                    name=district_data["name"],
                    defaults={
                        "code": district_code_counter,
                        "city": city,
                    },  # Tạo mã duy nhất cho mỗi District
                )
                if created:  # Chỉ tăng code nếu huyện/quận mới được tạo
                    district_code_counter += 1

                # Duyệt qua các phường/xã
                for ward_data in district_data["wards"]:
                    # Kiểm tra xem phường/xã đã tồn tại chưa
                    ward, created = Ward.objects.get_or_create(
                        name=ward_data["name"],
                        defaults={
                            "code": ward_code_counter,
                            "district": district,
                        },  # Tạo mã duy nhất cho mỗi Ward
                    )
                    if created:  # Chỉ tăng code nếu phường/xã mới được tạo
                        ward_code_counter += 1

        self.stdout.write(self.style.SUCCESS("Successfully imported city data"))
