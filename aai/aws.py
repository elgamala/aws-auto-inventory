# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
  
#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
  
#       http://www.apache.org/licenses/LICENSE-2.0
  
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import boto3
import logging

from aai import config as _config

# import utils.aws as aws

log = logging.getLogger('aai.aws')

def fetch(region_name, service, function, result_key, parameters):
    log.info('Started: {}:{}:{}:{}:{}'.format(region_name, service, function, result_key, parameters))
    response = ""

    try:
        session = get_session()
        client = session.client(service, region_name=region_name)
    
        if parameters is not None:
            if result_key:
                response = client.__getattribute__(function)(**parameters).get(result_key)
            else:
                response = client.__getattribute__(function)(**parameters)
        elif result_key:
            response = client.__getattribute__(function)().get(result_key)
        else:
            response = client.__getattribute__(function)()
            # Remove ResponseMetadata as it's not useful
            response.pop('ResponseMetadata', None)

    except Exception as e:
        log.error("Error while processing {}, {}.\n{}".format(service, region_name, e))

    
    log.info('Finished:{}:{}:{}:{}'.format(service, region_name, function, result_key))
    return response

def get_methods(client):
    methods = dir(client)
    return methods

def get_read_methods(client):
    l=[]
    methods = get_methods(client)
    for method in methods:
        if 'describe' in method or 'list' in method:
            l.append(method)
    return l

def get(region_name, inventory):
    # results = []
    
    for key, value in inventory.items():
        service = value['service']
        function = value['function']
        
        if 'result_key' in value:
            result_key = value['result_key']
        else:
            result_key = None   

        if 'parameters' in value:
            parameters = value['parameters']
        else:
            parameters=None

    log.info('Started:{}:{}:{}:{}'.format(region_name, service, function, result_key))
    result = fetch(region_name=region_name, service=service, function=function, result_key=result_key, parameters=parameters)
    # results.append(result)
    log.info('Result:{{{}}}'.format(result))
    log.info('Finished:{}:{}:{}:{}'.format(region_name, service, function, result_key))

    return result

def get_session():
    profile_name = _config.settings.get_aws_profile()
    session = boto3.Session(profile_name=profile_name)
    return session

def get_account_id():
    log.info('Started: get_caller_identity')
    
    client = aws.get_session().client('sts')
    response = client.get_caller_identity()
    account = response['Account']
    user_id = response['UserId']
    arn = response['Arn']
    
    log.info('Account: {}'.format(account))
    log.info('UserId: {}'.format(user_id))
    log.info('Arn: {}'.format(arn))
    
    log.info('Finished: get_caller_identity')
    return account