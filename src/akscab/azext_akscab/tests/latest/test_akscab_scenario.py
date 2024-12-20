# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AkscabScenarioTest(ScenarioTest):

    def test_akscab(self):

        self.kwargs.update({
            'role': 'pod-reader',
            'environment': 'nonprod'
        })

        self.cmd('az akscab create --role {role} --environment {environment} --dev', checks=[
            self.check('role', '{role}'),
            self.check('environment', '{environment}')
        ])

        self.cmd('az akscab create --role pod-reader --environment {environment} --expiration-seconds 600 --dev', checks=[
            self.check('role', '{role}'),
            self.check('environment', '{environment}'),
            self.check('expiration-seconds', '600')
        ])

        self.cmd('az akscab create --role pod-reader --environment {environment} --keysize 4096 --dev', checks=[
            self.check('role', '{role}'),
            self.check('environment', '{environment}'),
            self.check('keysize', '4096')
        ])
