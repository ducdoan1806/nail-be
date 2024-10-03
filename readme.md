1. Tạo môi trường ảo  
`python -m venv venv`  
`venv\Scripts\activate`  
2. Tạo file requirements.txt  
`pip freeze > requirements.txt`
`pip install -r requirements.txt`
3. Hủy môi trường ảo  
`deactivate`
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
4. Deploy docker
    `https://github.com/DanielArian/django-mysql-docker/blob/main/READme.md`
    `docker compose --env-file .env.dev up --build`
    `docker exec -it django-web python manage.py createsuperuser`