import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import dotenv_values


def downLoadImage():

    return True


def uploadImageToAzure(self, imgFileName, imageObjects, caseNumber):
    print("Upload to Azure storage serivce")
    config = dotenv_values(".env")
    # Define connection string and container name
    connect_str = config["AZURE_CON_STRING"]
    container_name = config["AZURE_CONTAINER_IMAGE"]

    try:
        config = dotenv_values(".env")
        # Define connection string and container name
        connect_str = config["AZURE_CON_STRING"]
        container_name = config["AZURE_CONTAINER_IMAGE"]

        # Create a BlobServiceClient object using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(
            connect_str)

        # Create a ContainerClient object for the container
        container_client = blob_service_client.get_container_client(
            container_name)

        # Define the path to the local file to upload
        local_path = imgFileName

        # Define the name for the blob in Azure Storage
        blob_name = imgFileName.split('/')[1]

        # Create a BlobClient object for the blob
        blob_client = container_client.get_blob_client(blob_name)

        # Upload the file to Azure Storage
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data)

        imageObjects.append(
            {"caseNumber": caseNumber, "imgSrc": blob_client.url, "cloudflareImgId": ""})

        print(blob_client.url)

    except Exception as ex:
        print('Exception:')
        print(ex)


def upload_image_to_azure_container(fileName, blobName, container_name):
    try:
        config = dotenv_values(".env")
        # Define connection string and container name
        connect_str = config["AZURE_CON_STRING"]
        container_name = config[container_name]

        # Create a BlobServiceClient object using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(
            connect_str, max_block_size=4*1024*1024,  # Note: This is the default value
            max_single_put_size=16*1024*1024)

        # Create a ContainerClient object for the container
        container_client = blob_service_client.get_container_client(
            container_name)

        # Define the path to the local file to upload
        local_path = fileName

        # Define the name for the blob in Azure Storage
        blob_name = blobName

        # Create a BlobClient object for the blob
        blob_client = container_client.get_blob_client(blob_name)

        # Upload the file to Azure Storage
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data)

        print(blob_client.url)

        return blob_client.url

    except Exception as ex:
        print('Exception:')
        print(ex)
        return "none"
