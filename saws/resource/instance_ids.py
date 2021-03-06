# -*- coding: utf-8 -*-

# Copyright 2015 Donne Martin. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from __future__ import unicode_literals
from __future__ import print_function
import re
from .resource import Resource


class InstanceIds(Resource):
    """Encapsulates the EC2 instance ids resources.

    Attributes:
        * OPTION: A string representing the option for instance ids.
        * QUERY: A string representing the AWS query to list all instance ids.
        * resources: A list of instance ids.
        * log_exception: A callable log_exception from SawsLogger.
    """

    OPTION = '--instance-ids'
    QUERY = 'aws ec2 describe-instances --query "Reservations[].Instances[].[InstanceId]" --output text'

    def __init__(self, log_exception):
        """Initializes InstanceIds.

        Args:
            * log_exception: A callable log_exception from SawsLogger.

        Returns:
            None.
        """
        self.resources = []
        self.log_exception = log_exception

    def query_resource(self):
        """Queries and stores instance ids from AWS.

        Args:
            * None.

        Returns:
            The list of resources.
        """
        print('  Refreshing instance ids...')
        output = self._query_aws(self.QUERY)
        if output is not None:
            output = re.sub('\n', ' ', output)
            self.resources = output.split()
