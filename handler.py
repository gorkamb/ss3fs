#!/usr/bin/env python

import boto3
import os

s3 = boto3.client('s3')
source_bucket = os.getenv("SOURCE_BUCKET")
source_folder = os.getenv("SOURCE_FOLDER") + '/'
destination_bucket = os.getenv("DESTINATION_BUCKET")
destination_folder = os.getenv("DESTINATION_FOLDER") + '/'
create_empty_files = os.getenv("CREATE_EMPTY_FILES")
image_or_vide_file_extensions = os.getenv('IMAGE_VIDEO_EXTENSIONS')


def do_delete(source_key):
    destination_key = source_key.replace(source_folder, destination_folder)
    s3.delete_object(Bucket=destination_bucket, Key=destination_key)
    print('Deleting...' + destination_bucket + '/' + destination_key)


def do_copy(source_key):
    destination_key = source_key.replace(source_folder, destination_folder)
    if is_image_or_video(source_key):
        copy_image(source_key, destination_key)
    else:
        copy_file(source_key, destination_key)

    set_acl(source_key, destination_key)
    print('Copying from '
          + source_bucket
          + '/'
          + source_key
          + ' to '
          + destination_bucket
          + '/'
          + destination_key
          )


def is_image_or_video(file):
    if not image_or_vide_file_extensions:
        return False

    valid_extensions = image_or_vide_file_extensions.strip(' ').split(',')
    ext = file.rpartition('.')[-1]
    if ext.lower() in valid_extensions:
        return True

    return False


def copy_image(source_key, destination_key):
    s3.copy_object(
        Bucket=destination_bucket,
        CopySource={
            'Bucket': destination_bucket,
            'Key': source_key
        },
        Key=destination_key
    )
    print('Copying (image) from '
          + source_bucket
          + '/'
          + source_key
          + ' to '
          + destination_bucket
          + '/'
          + destination_key
          )


def copy_file(source_key, destination_key):
    if create_empty_files.lower() in ['true', '1', 'yes']:
        head_object = s3.head_object(Bucket=source_bucket, Key=source_key)
        s3.put_object(
            Bucket=destination_bucket,
            Body=b'Empty file. ;)',
            Key=destination_key,
            Metadata=head_object.get('Metadata'),
            ContentDisposition=head_object.get('ContentDisposition') or 'inline',
            ContentType=head_object.get('ContentType') or 'text/plain'
        )
    else:
        s3.copy_object(
            Bucket=destination_bucket,
            CopySource={
                'Bucket': destination_bucket,
                'Key': source_key
            },
            Key=destination_key
        )

    print('Copying (file) from '
          + source_bucket
          + '/'
          + source_key
          + ' to '
          + destination_bucket
          + '/'
          + destination_key
          )


def set_acl(source_key, destination_key):
    object_acl = s3.get_object_acl(Bucket=source_bucket, Key=source_key)
    data = {
        'AccessControlPolicy': {
            'Owner': object_acl['Owner'],
            'Grants': object_acl['Grants']
        }
    }
    s3.put_object_acl(**data, Bucket=destination_bucket, Key=destination_key)


def sync(event, context):
    if source_bucket == destination_bucket and source_folder == destination_folder:
        return False

    source_key = event['Records'][0]['s3']['object']['key']
    event_name = event['Records'][0]['eventName']
    if event_name == 'ObjectRemoved:Delete':
        do_delete(source_key)
    else:
        do_copy(source_key)

    return True
