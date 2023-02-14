from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import dotenv_values
try:
    config = dotenv_values(".env")
    # Define connection string and container name
    connect_str = config["AZURE_CON_STRING"]
    container_name = config["AZURE_CONTAINER_IMAGE"]

    # Create a BlobServiceClient object using the connection string
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a ContainerClient object for the container
    container_client = blob_service_client.get_container_client(container_name)

    # Define the path to the local file to upload
    local_path = "azure_test/2019타경5285_1.png"

    # Define the name for the blob in Azure Storage
    blob_name = ""

    # Create a BlobClient object for the blob
    blob_client = container_client.get_blob_client(blob_name)

    # Upload the file to Azure Storage
    with open(local_path, "rb") as data:
        blob_client.upload_blob(data)

    print(blob_client.url)

except Exception as ex:
    print('Exception:')
    print(ex)
