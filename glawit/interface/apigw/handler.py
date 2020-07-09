import base64
import logging
import os

import boto3
import requests

import glawit.core.boto3
import glawit.core.main
import glawit.interface.apigw.logging

logger = logging.getLogger(
    __name__,
)

logging_level = logging.DEBUG

glawit.interface.apigw.logging.set_up(
    level=logging_level,
)

aws_region = os.environ['AWS_REGION']

config = {
}

config['AWS'] = {
    'region': aws_region,
}

api_pagination_max_str = os.environ['API_PAGINATION_MAX']
api_pagination_max = int(
    api_pagination_max_str,
)

logger.debug(
    'API pagination: maximum amount of objects to return: %i',
    api_pagination_max,
)

api_pagination_min_str = os.environ['API_PAGINATION_MIN']
api_pagination_min = int(
    api_pagination_min_str,
)

logger.debug(
    'API pagination: minimum amount of objects to return: %i',
    api_pagination_min,
)

config['API'] = {
    'pagination': {
        'max': api_pagination_max,
        'min': api_pagination_min,
    },
}

github_owner = os.environ['GITHUB_OWNER']
github_repo = os.environ['GITHUB_REPO']

logger.debug(
    'GitHub repository: %s/%s',
    github_owner,
    github_repo,
)

config['GitHub'] = {
    'owner': github_owner,
    'repo': github_repo,
}

lfs_bucket = os.environ['STORE_BUCKET']

logger.debug(
    'LFS bucket: %s',
    lfs_bucket,
)

lfs_storage_class = os.environ['STORAGE_CLASS']

logger.debug(
    'LFS storage class: %s',
    lfs_storage_class,
)

config['large_file_store'] = {
    'bucket_name': lfs_bucket,
    'storage_class': lfs_storage_class,
}

locktable = os.environ['LOCKTABLE']

logger.debug(
    'locktable: %s',
    locktable,
)

config['locktable'] = locktable

boto3_session = glawit.core.boto3.Session(
    clients=[
        'dynamodb',
        's3',
    ],
    region=aws_region,
    session=boto3.session.Session(
        region_name=aws_region,
    ),
)

requests_session = requests.Session(
)


def entry_point(
            context,
            event,
            handler,
        ):
    domain_name = event['requestContext']['domainName']

    logger.debug(
        'domain name: %s',
        domain_name,
    )

    api_endpoint = f'https://{domain_name}'

    logger.debug(
        'API endpoint: %s',
        api_endpoint,
    )

    config['API']['endpoint'] = api_endpoint

    headers = event['headers']
    is_base64_encoded = event['isBase64Encoded']

    request = {
        'headers': headers,
    }

    try:
        body = event['body']
    except KeyError:
        logger.debug(
            'request has no body',
        )
    else:
        logger.debug(
            'request has a body',
        )

        if is_base64_encoded:
            logger.debug(
                'request body is Base64-encoded',
            )

            body = base64.b64decode(
                body,
                validate=True,
            )

        request['body'] = body

    try:
        path_parameters = event['pathParameters']
    except KeyError:
        logger.debug(
            'request has no path parameters',
        )
    else:
        logger.debug(
            'request has path parameters',
        )

        request['path_variables'] = path_parameters

    try:
        query_string_parameters = event['queryStringParameters']
    except KeyError:
        logger.debug(
            'request has no query string parameters',
        )
    else:
        logger.debug(
            'request has query string parameters',
        )

        request['urlparams'] = query_string_parameters

    return_value = glawit.core.main.process_request(
        boto3_session=boto3_session,
        config=config,
        handler=handler,
        request=request,
        requests_session=requests_session,
    )

    return_value['isBase64Encoded'] = False

    return return_value


def bind_entry_point(
            handler,
        ):
    def bound_entry_point(
                event,
                context,
            ):
        response = entry_point(
            context=context,
            event=event,
            handler=handler,
        )

        return response

    return bound_entry_point
