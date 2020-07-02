import base64
import logging
import os

import boto3

import glawit.core.main

boto3_session = boto3.session.Session(
)

logger = logging.getLogger(
)

# Top logger object based on whether everything should be logged
top_logger_names = {
    False: 'glawit',
    True: None,
}


def entry_point(context, event, handler):
    stage_variables = event['stageVariables']

    logging_level = getattr(
        logging,
        stage_variables['logging_level'],
    )

    set_up_logging(
        level=logging_level,
    )

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

    github_owner = os.environ['GITHUB_OWNER']
    github_repo = os.environ['GITHUB_REPO']

    logger.debug(
        'GitHub repository: %s/%s',
        github_owner,
        github_repo,
    )

    config = {
        'API': {
            'endpoint': api_endpoint,
        },
        'AWS': {
            'region': os.environ['AWS_REGION'],
        },
        'GitHub': {
            'owner': github_owner,
            'repo': github_repo,
        },
        'large_file_store': {
            'bucket_name': stage_variables['store_bucket'],
            'storage_class': stage_variables['storage_class'],
        },
    }

    body = event.get(
        'body',
    )
    headers = event['headers']
    is_base64_encoded = event['isBase64Encoded']
    path_variables = event.get(
        'pathParameters',
    )
    urlparams = event.get(
        'queryStringParameters',
    )

    if is_base64_encoded:
        logger.debug(
            'request body is Base64-encoded',
        )

        body = base64.b64decode(
            body,
            validate=True,
        )

    request = {
        'body': body,
        'headers': headers,
        'path_variables': path_variables,
        'urlparams': urlparams,
    }

    session = {
        'boto3': {
            'session': boto3_session,
        },
    }

    return_value = glawit.core.main.process_request(
        config=config,
        handler=handler,
        request=request,
        session=session,
    )

    return_value['isBase64Encoded'] = False

    return return_value


def set_up_logging(level):
    log_everything = True

    top_logger_name = top_logger_names[log_everything]

    top_logger = logging.getLogger(
        name=top_logger_name,
    )

    top_logger.setLevel(
        level,
    )


def decorator(handler):
    def entry_point_dfd(event, context):
        response = entry_point(
            context=context,
            event=event,
            handler=handler,
        )

        return response

    return entry_point_dfd
