import os
import subprocess
import shutil
import typesense
from datetime import datetime
from cloudpathlib import CloudPath, S3Client


def create_snapshot():
    client = typesense.Client({
        'nodes': [{
            'host': "typesense-svc",
            'port': "8108",
            'protocol': 'http'
        }],
        'api_key': os.environ.get("TYPESENSE_API_KEY"),
        'connection_timeout_seconds': 600
    })

    client.operations.perform('snapshot', {'snapshot_path': '/usr/share/typesense/data/typesense-data-snapshot'})


def upload_snapshot():
    compress_backup_result = subprocess.run(['tar', '-czvf', 'typesense-data-snapshot.tar.gz', 'typesense-data-snapshot'], capture_output=True, cwd="/usr/share/typesense/data")
    print(compress_backup_result.stdout.decode('utf-8'))
    if compress_backup_result.returncode != 0:
        raise Exception("Fehler beim Aufruf von '{}': {}".format(" ".join(compress_backup_result.args), compress_backup_result.stderr.decode('utf-8')))

    shutil.rmtree("/usr/share/typesense/data/typesense-data-snapshot")

    os.environ["AWS_ACCESS_KEY_ID"] = os.environ.get("MINIO_ROOT_USER")
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ.get("MINIO_ROOT_PASSWORD")
    s3_endpoint_url = "http://minio:9000"
    s3_bucket_url = "s3://dpt-backup-typesense/typesense-data-snapshot.tar.gz"

    client = S3Client(endpoint_url=s3_endpoint_url)
    s3_path = CloudPath(s3_bucket_url, client=client)
    s3_path.upload_from("/usr/share/typesense/data/typesense-data-snapshot.tar.gz", force_overwrite_to_cloud=True)



if __name__ == "__main__":
    print(f"Running backup script at {datetime.now()}")
    create_snapshot()
    upload_snapshot()