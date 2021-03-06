#////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////
# script: s3_util.py
# author: James Webber
# date: 5.19 (made some mods -- LJH)
#
# Library of common functions used for s3 operations
#////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////
import csv
import os
import boto3
import botocore.exceptions

import itertools
import multiprocessing

from collections import defaultdict, Counter

def prefix_gen(bucket, prefix, fn=None):
    """Generic generator of fn(result) from an S3 paginator"""
    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects')

    response_iterator = paginator.paginate(
            Bucket=bucket, Prefix=prefix
    )

    for result in response_iterator:
        if 'Contents' in result:
            yield from (fn(r) for r in result['Contents'])

# changes in here -- LJH
def get_files(bucket=None, prefix=None):
    """Generator of keys for a given S3 prefix"""
    yield from prefix_gen(bucket, prefix, lambda r: r['Key'])


def get_size(bucket='czbiohub-seqbot', prefix=None):
    """Generator of (key,size) for a given S3 prefix"""
    yield from prefix_gen(bucket, prefix, lambda r: (r['Key'], r['Size']))


def get_status(file_list, bucket_name='czbiohub-seqbot'):
    """Print the storage/restore status for a list of keys"""
    s3r = boto3.resource('s3')

    for fn in file_list:
        obj = s3r.Object(bucket_name, fn)
        storage_class = obj.storage_class
        restore = obj.restore
        print(obj.key, obj.storage_class, obj.restore)


def restore_file(k):
    obj = s3r.Object('czbiohub-seqbot', k)
    storage_class = obj.storage_class
    restore = obj.restore
    if not obj.restore:
        resp = bucket.meta.client.restore_object(
            Bucket='czbiohub-seqbot',
            Key=k,
            RestoreRequest={'Days': 3}
        )


def restore_files(file_list, n_proc=16):
    """Restore a list of files from czbiohub-seqbot in parallel"""

    global s3r
    s3r = boto3.resource('s3')
    global bucket
    bucket = s3r.Bucket('czbiohub-seqbot')

    print('creating pool')

    p = multiprocessing.Pool(processes=n_proc)

    try:
        print('restoring files...')
        p.map(restore_file, file_list, chunksize=100)
    finally:
        p.close()
        p.join()


def copy_file(k):
    key, new_key = k
    try:
        s3c.head_object(Bucket=new_bucket, Key=new_key)
    except botocore.exceptions.ClientError:
        s3c.copy(CopySource={'Bucket': bucket, 'Key': key},
                 Bucket=new_bucket,
                 Key=new_key)


def copy_files(src_list, dest_list, b, nb, n_proc=16):
    """
    Copy a list of files from src_list to dest_list.
    b - original bucket
    nb - destination bucket
    """

    global s3c
    s3c = boto3.client('s3')

    global bucket
    bucket = b
    global new_bucket
    new_bucket = nb

    try:
        p = multiprocessing.Pool(processes=n_proc)
        p.map(copy_file, zip(src_list, dest_list), chunksize=100)
    finally:
        p.close()
        p.join()


def remove_file(k):
    s3c.delete_object(Bucket=bucket, Key=k)


def remove_files(file_list, *, b, really=False, n_proc=16):
    """Remove a list of file keys from S3"""

    assert really

    print("Removing {} files!".format(len(file_list)))

    global s3c
    s3c = boto3.client('s3')
    global bucket
    bucket = b

    try:
        p = multiprocessing.Pool(processes=n_proc)
        p.map(remove_file, file_list, chunksize=100)
    finally:
        p.close()
        p.join()

#////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////