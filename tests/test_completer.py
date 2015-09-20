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
import unittest
import mock
import re
from prompt_toolkit.document import Document
from awscli import completer as awscli_completer
from saws.completer import AwsCompleter
from saws.commands import AwsCommands
from saws.saws import Saws
from test_resources import ResourcesTest


class CompleterTest(unittest.TestCase):

    @mock.patch('saws.resources.print')
    def setUp(self, mock_print):
        self.saws = Saws()
        self.completer = self.create_completer()
        self.completer_event = self.create_completer_event()
        mock_print.assert_called_with('Loaded resources from cache')

    def create_completer(self):
        self.aws_commands = AwsCommands()
        self.commands, self.sub_commands, self.global_options, \
            self.resource_options, self.ec2_states = \
            self.aws_commands.generate_all_commands()
        return AwsCompleter(awscli_completer,
                            self.saws.config_obj,
                            self.saws.logger,
                            self.ec2_states)

    def create_completer_event(self):
        return mock.Mock()

    def _get_completions(self, command):
        position = len(command)
        result = set(self.completer.get_completions(
            Document(text=command, cursor_position=position),
            self.completer_event))
        return result

    def verify_completions(self, commands, expected):
        result = set()
        for command in commands:
            # Call the AWS CLI autocompleter
            result.update(self._get_completions(command))
        result_texts = []
        for item in result:
            # Each result item is a Completion object,
            # we are only interested in the text portion
            result_texts.append(item.text)
        assert result_texts
        if len(expected) == 1:
            assert expected[0] in result_texts
        else:
            for item in expected:
                assert item in result_texts

    def test_ec2_commands(self):
        commands = ['aws e']
        expected = ['ec2',
                    'ecs',
                    'efs',
                    'elasticache',
                    'elasticbeanstalk',
                    'elastictranscoder',
                    'elb',
                    'emr']
        self.verify_completions(commands, expected)

    def test_ec2_subcommands(self):
        commands = ['aws ec2 c']
        expected = ['cancel-bundle-task',
                    'cancel-conversion-task',
                    'cancel-export-task',
                    'cancel-import-task',
                    'cancel-reserved-instances-listing',
                    'cancel-spot-fleet-requests',
                    'cancel-spot-instance-requests']
        self.verify_completions(commands, expected)

    def test_ec2_state_completions(self):
        commands = ['ec2 ls --ec2-state pend']
        expected = ['pending']
        self.verify_completions(commands, expected)
        commands = ['ec2 ls --ec2-state run']
        expected = ['running']
        self.verify_completions(commands, expected)
        commands = ['ec2 ls --ec2-state shut']
        expected = ['shutting-down']
        self.verify_completions(commands, expected)
        commands = ['ec2 ls --ec2-state term']
        expected = ['terminated']
        self.verify_completions(commands, expected)
        commands = ['ec2 ls --ec2-state stop']
        expected = ['stopping',
                    'stopped']
        self.verify_completions(commands, expected)

    def test_aws_command_completion(self):
        commands = ['a', 'aw']
        expected = [AwsCommands.AWS_COMMAND]
        self.verify_completions(commands, expected)

    def test_global_options(self):
        commands = ['aws -', 'aws --']
        expected = self.saws.global_options
        self.verify_completions(commands, expected)

    def test_resource_options(self):
        commands = ['aws ec2 describe-instances --',
                    'aws s3api get-bucket-acl --']
        expected = self.saws.resource_options
        self.verify_completions(commands, expected)

    def test_simple_shortcuts(self):
        commands = ['aws ec2 ls',
                    'aws emr ls',
                    'aws elb ls',
                    'aws dynamodb ls']
        expected = ['aws ec2 describe-instances',
                    'aws emr list-clusters',
                    'aws elb describe-load-balancers',
                    'aws dynamodb list-tables']
        shortcuts = dict(zip(commands, expected))
        for command, expect in shortcuts.items():
            result = self.completer.replace_shortcut(command)
            assert result == expect

    def test_instance_ids(self):
        commands = ['aws ec2 ls --instance-ids i-a']
        expected = ['i-a875ecc3', 'i-a51d05f4', 'i-a3628153']
        self.completer.resources.instance_ids.extend(expected)
        self.verify_completions(commands, expected)

    def test_instance_keys(self):
        commands = ['aws ec2 ls --ec2-tag-key na']
        expected = ['name', 'namE']
        self.completer.resources.instance_tag_keys.update(expected)
        self.verify_completions(commands, expected)

    def test_instance_tag_values(self):
        commands = ['aws ec2 ls --ec2-tag-value prod']
        expected = ['production', 'production-blue', 'production-green']
        self.completer.resources.instance_tag_values.update(expected)
        self.verify_completions(commands, expected)

    def test_bucket_names(self):
        commands = ['aws s3pi get-bucket-acl --bucket web-']
        expected = ['web-server-logs', 'web-server-images']
        self.completer.resources.bucket_names.extend(expected)
        self.verify_completions(commands, expected)

    def test_s3_completion(self):
        commands = ['aws s3 ls s3:']
        expected = ['s3://web-server-logs', 's3://web-server-images']
        for s3_uri in expected:
            bucket_name = re.sub('s3://', '', s3_uri)
            self.completer.resources.add_bucket_name(bucket_name)
        self.verify_completions(commands, expected)
        commands = ['aws s3 ls s3://web']
        self.verify_completions(commands, expected)

    def test_fuzzy_instance_ids_matching(self):
        self.completer.fuzzy_match = True
        commands = ['aws ec2 ls --instance-ids a5']
        expected = ['i-a875ecc3', 'i-a41d55f4', 'i-a3628153']
        self.completer.resources.instance_ids.extend(expected)
        self.verify_completions(commands, expected)

    def test_fuzzy_shortcut_matching(self):
        self.completer.fuzzy_match = True
        self.completer.shortcut_match = True
        commands = ['aws ec2ls']
        expected = ['ec2 ls --instance-ids']
        self.verify_completions(commands, expected)
        commands = ['aws ec2start']
        expected = ['ec2 start-instances --instance-ids']
        self.verify_completions(commands, expected)
        commands = ['aws ec2stop']
        expected = ['ec2 stop-instances --instance-ids']
        self.verify_completions(commands, expected)
        commands = ['aws ec2tagk']
        expected = ['ec2 ls --ec2-tag-key']
        self.verify_completions(commands, expected)
        commands = ['aws ec2tagv']
        expected = ['ec2 ls --ec2-tag-value']
        self.verify_completions(commands, expected)

    def test_substitutions(self):
        command = 'aws ec2 ls --filters "Name=tag-key,Values=%s prod"'
        expected = 'aws ec2 ls --filters "Name=tag-key,Values=prod"'
        result = self.completer.replace_substitution(command)
        assert result == expected
        command = 'aws ec2 ls --ec2-tag-key Stack'
        expected = 'aws ec2 describe-instances --filters "Name=tag-key,Values=Stack"'
        result = self.completer.replace_shortcut(command)
        assert result == expected
        command = 'aws ec2 ls --ec2-tag-value prod'
        expected = 'aws ec2 describe-instances --filters "Name=tag-value,Values=prod"'
        result = self.completer.replace_shortcut(command)
        assert result == expected

    @mock.patch('saws.resources.print')
    def test_refresh_resources(self, mock_print):
        NUM_EC2_STATE = 6
        self.completer.resources.RESOURCE_FILE = \
            ResourcesTest.RESOURCES_SAMPLE
        self.completer.resource_map = None
        self.completer.refresh_resources(force_refresh=False)
        mock_print.assert_called_with('Loaded resources from cache')
        keys = [self.completer.resources.INSTANCE_IDS,
                self.completer.resources.EC2_TAG_KEY,
                self.completer.resources.EC2_TAG_VALUE,
                self.completer.resources.EC2_STATE,
                self.completer.resources.BUCKET,
                self.completer.resources.S3_URI]
        expected = [ResourcesTest.NUM_INSTANCE_IDS,
                    ResourcesTest.NUM_INSTANCE_TAG_KEYS,
                    ResourcesTest.NUM_INSTANCE_TAG_VALUES,
                    NUM_EC2_STATE,
                    ResourcesTest.NUM_BUCKET_NAMES,
                    ResourcesTest.NUM_BUCKET_NAMES]
        for i in range(len(keys)):
            assert len(self.completer.resource_map[keys[i]]) == expected[i]
