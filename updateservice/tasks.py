from minio import Minio
import pyshorteners
from datetime import datetime
import os
from updateservice.models.backup import Backup
from asgiref.sync import async_to_sync
from updateservice.connection_db import celery_async_session
import re
from updateservice.settings import setting
from updateservice.celeryapp import app


endpoint = setting["endpoint"]
access_key = setting["my_access_key"]
secret_key = setting["my_secret_key"]
bucket_name = setting["bucket_name"]


def short_url(url): 
    shortener = pyshorteners.Shortener() 
    tiny_url = shortener.tinyurl.short(url) 
    return tiny_url 


async def upload_to_minio():

    client = Minio(endpoint, access_key, secret_key, secure=False)
    print(endpoint)
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    package_folders = [f for f in os.listdir('updateservice/backup_storage') if f.startswith('Package_')]
    tiny_list = []
    package_numbers = []

    for package_folder in package_folders:
        package_path = f'updateservice/backup_storage/{package_folder}'
        files = os.listdir(package_path)
        uploaded_files = []
        skipped_files = []
        object_prefix = f"{package_folder}/"
        objects = client.list_objects(bucket_name, prefix=object_prefix, recursive=True)
        uploaded_object_names = [obj.object_name for obj in objects]

        for filename in files:
            object_name = f"{package_folder}/{filename}"
            if object_name in uploaded_object_names:
                skipped_files.append(filename)
                continue

            file_path = f"{package_path}/{filename}"
            client.fput_object(bucket_name, object_name, file_path)
            url = client.presigned_get_object(bucket_name, object_name)
            uploaded_files.append((filename, url))

        if uploaded_files:
            for filename, url in uploaded_files:
                print(f'Uploaded file URL for {filename}: {url}')
                tiny_url = short_url(url=url)
                print(f"tiny url is : {tiny_url}")
                tiny_list.append(tiny_url)
        
            package_number = re.findall(r'\d+', package_folder)
            if package_number:
                package_number = int(package_number[0])
                package_numbers.append(package_number)
        else:
            package_numbers.append(None)

        if skipped_files:
            skipped_files_str = ", ".join(skipped_files)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timestamp}: Skipped already uploaded files for {package_folder}: {skipped_files_str}")
    return tiny_list, [n for n in package_numbers if n is not None]


async def insert_to_db():

    async with celery_async_session() as session:
        tiny_urls, numbers = await upload_to_minio()      
        for i in range(len(tiny_urls)):
            url = tiny_urls[i]
            number = numbers[i]
            new_backup = Backup(backup_path=url, package_id=number)
            session.add(new_backup)
        await session.commit()


@app.task(name='tasks.backup_task')
def backup_task():
    async_to_sync(insert_to_db)()




