"""
This module defines a class GStorageJSON inherited from _TerminalDict
that implements methods for saving and loading dictionary to/from Google
Cloud Storage in JSON format.
"""

import json
from io import BytesIO
from tempfile import NamedTemporaryFile

from google.cloud import storage

from ...tools.dict import enrich_dict
from .terminal import _TerminalDict

__all__ = ['GStorageJSON']


def get_bucket_and_object_names(place: str) -> tuple[str, str]:
    """
    Extracts the bucket name and object name from a given place string.

    Args:
        place (str): A string representing the Google Cloud Storage location, in the format
            "gs://bucket-name/object-name".

    Returns:
        A tuple containing the bucket name and object name.
    """
    if not place.startswith("gs://"):
        raise ValueError("Invalid GCS location. It should start with 'gs://'")
    place = place[5:]
    parts = place.split('/')
    if len(parts) < 1 or not parts[0]:
        raise ValueError("Invalid GCS location. Bucket name is missing.")
    bucket_name = parts[0]
    object_name = '/'.join(parts[1:])
    return bucket_name, object_name


def get_gcs_client(options: dict) -> storage.Client:
    """
    Creates a Google Cloud Storage client object.

    Args:
        options (dict): A dictionary containing the options for creating the client.

    Returns:
        A storage.Client object.
    """
    if 'key_file' in options:
        with NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(json.dumps(options['key_file']))
            # json.dump(options['key_file'], temp_file)
            key_file = temp_file.name
        client = storage.Client.from_service_account_json(key_file)
        return client

    else:
        return storage.Client()


class GStorageJSON(_TerminalDict.Gate):
    """
    A class for loading and saving JSON data to/from Google Cloud Storage.
    """

    @classmethod
    def arriving(cls, place: str, **options):
        """
        Loads JSON data from Google Cloud Storage.

        Args:
            place (str): A string representing the Google Cloud Storage location, in the format
                "gs://bucket-name/object-name".
            options (dict): A dictionary containing the options for loading the JSON data.

        Returns:
            The loaded JSON data as a dictionary or string.
        """
        # Parse JSON options
        json_params = [
            'object_name', 'download_as_string', 'content_type', 'key_file'
        ]
        json_options = {}
        for k in json_params:
            json_options = enrich_dict(json_options, options, k)

        # Extract bucket name and object name from place
        bucket_name, object_name = get_bucket_and_object_names(place)

        # Create Google Cloud Storage client
        client = get_gcs_client(json_options)

        # Retrieve bucket and blob
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(json_options.get('object_name', object_name))

        # Download JSON data
        data = BytesIO()
        blob.download_to_file(data)
        data.seek(0)

        # Load JSON data and return
        if json_options.get('download_as_string', False):
            return data.read().decode()
        else:
            return json.load(data)

    @classmethod
    def departure(cls, parcel, place: str, **options):
        """
        Saves JSON data to Google Cloud Storage.

        Args:
            parcel (dict): A dictionary representing the JSON data to be saved.
            place (str): A string representing the Google Cloud Storage location, in the format
                "gs://bucket-name/object-name".
            options (dict): A dictionary containing the options for saving the JSON data.

        Returns:
            None.
        """
        # Parse JSON options
        json_params = [
            'content_type', 'key_file'
        ]
        json_options = {}
        for k in json_params:
            json_options = enrich_dict(json_options, options, k)

        # Extract bucket
        bucket_name, object_name = get_bucket_and_object_names(place)

        # Create Google Cloud Storage client
        client = get_gcs_client(json_options)

        # Serialize data to JSON
        json_data = json.dumps(parcel)

        # Upload JSON data to Google Cloud Storage
        blob = client.bucket(bucket_name).blob(object_name)
        blob.upload_from_string(json_data, content_type=json_options.get('content_type', 'application/json'))
