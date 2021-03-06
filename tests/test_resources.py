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
import sys
import mock
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
from saws.saws import Saws


class ResourcesTest(unittest.TestCase):

    NUM_SAMPLE_INSTANCE_IDS = 7
    NUM_SAMPLE_INSTANCE_TAG_KEYS = 3
    NUM_SAMPLE_INSTANCE_TAG_VALUES = 6
    NUM_SAMPLE_BUCKET_NAMES = 16

    def setUp(self):
        self.create_resources()

    def create_resources(self):
        self.saws = Saws(refresh_resources=False)
        self.resources = self.saws.completer.resources
        self.resources._set_resources_path('data/RESOURCES_SAMPLE.txt')

    def verify_resources(self):
        assert len(self.resources.instance_ids.resources) == \
            self.NUM_SAMPLE_INSTANCE_IDS
        assert len(self.resources.instance_tag_keys.resources) == \
            self.NUM_SAMPLE_INSTANCE_TAG_KEYS
        assert len(self.resources.instance_tag_values.resources) == \
            self.NUM_SAMPLE_INSTANCE_TAG_VALUES
        assert len(self.resources.bucket_names.resources) == \
            self.NUM_SAMPLE_BUCKET_NAMES
        assert len(self.resources.bucket_uris.resources) == \
            self.NUM_SAMPLE_BUCKET_NAMES

    # TODO: Silence output
    @mock.patch('saws.resources.print')
    def test_refresh(self, mock_print):
        self.resources.refresh(force_refresh=False)
        self.verify_resources()
        mock_print.assert_called_with('Loaded resources from cache')

    # TODO: Silence output
    @mock.patch('saws.resources.print')
    def test_refresh_forced(self, mock_print):
        self.resources.clear_resources()
        self.resources.refresh(force_refresh=True)
        mock_print.assert_called_with('Done refreshing')

    # TODO: Fix mocks
    @unittest.skip('')
    @mock.patch('saws.resources.subprocess')
    def test_query_aws_instance_ids(self, mock_subprocess):
        self.resources.instance_ids._query_aws(
            self.resources.instance_ids.QUERY)
        mock_subprocess.check_output.assert_called_with(
            self.resources.instance_ids.QUERY,
            universal_newlines=True,
            shell=True)

    # TODO: Fix mocks
    @unittest.skip('')
    @mock.patch('saws.resources.subprocess')
    def test_query_aws_instance_tag_keys(self, mock_subprocess):
        self.resources.instance_tag_keys._query_aws(
            self.resources.instance_tag_keys.QUERY)
        mock_subprocess.check_output.assert_called_with(
            self.resources.instance_tag_keys.QUERY,
            universal_newlines=True,
            shell=True)

    # TODO: Fix mocks
    @unittest.skip('')
    @mock.patch('saws.resources.subprocess')
    def query_aws_instance_tag_values(self, mock_subprocess):
        self.resources.instance_tag_values._query_aws(
            self.resources.instance_tag_values.QUERY)
        mock_subprocess.check_output.assert_called_with(
            self.resources.instance_tag_values.QUERY,
            universal_newlines=True,
            shell=True)

    # TODO: Fix mocks
    @unittest.skip('')
    @mock.patch('saws.resources.subprocess')
    def test_query_aws_bucket_names(self, mock_subprocess):
        self.resources.bucket_names._query_aws(
            self.resources.bucket_names.QUERY)
        mock_subprocess.check_output.assert_called_with(
            self.resources.bucket_names.QUERY,
            universal_newlines=True,
            shell=True)

    def test_add_and_clear_bucket_name(self):
        BUCKET_NAME = 'test_bucket_name'
        self.resources.bucket_names.clear_resources()
        self.resources.bucket_names.add_bucket_name(BUCKET_NAME)
        assert BUCKET_NAME in self.resources.bucket_names.resources
        self.resources.bucket_uris.add_bucket_name(BUCKET_NAME)
        BUCKET_URI = self.resources.bucket_uris.PREFIX + BUCKET_NAME
        assert BUCKET_URI in self.resources.bucket_uris.resources
        self.resources.bucket_names.clear_resources()
        self.resources.bucket_uris.clear_resources()
        assert len(self.resources.bucket_names.resources) == 0
        assert len(self.resources.bucket_uris.resources) == 0
