# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azext_akscab.tests import try_manual
from azure.cli.testsdk import ScenarioTest


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


# Test class for Scenario
@try_manual
class AkscabScenarioTest(ScenarioTest):

    def test_akscab_list(self):
        """Test akscab list command"""
        self.cmd('akscab list')

    def test_akscab_help(self):
        """Test akscab help command"""
        self.cmd('akscab help')

    def test_akscab_create_help(self):
        """Test akscab create help command"""
        self.cmd('akscab create help')

    def test_akscab_create_csr_parameter_validation(self):
        """Test akscab create csr parameter validation"""
        # Test that the command shows parameter help when --role is missing
        # This tests the parameter validation logic without requiring authentication
        # The command should execute successfully and show parameter help
        self.cmd('akscab create csr')

    def test_akscab_create_csr_with_role_parameter(self):
        """Test akscab create csr with --role parameter"""
        # Test that the command accepts the --role parameter
        # It may fail due to authentication/file access, but parameter validation should pass
        try:
            self.cmd('akscab create csr --role test-role --dev')
        except Exception as e:
            # The command may fail due to missing files/auth, but not due to parameter validation
            # We just want to ensure the parameters are accepted
            self.assertNotIn("unrecognized arguments", str(e))
            self.assertNotIn("the following arguments are required", str(e))

    def test_akscab_create_csr_all_parameters(self):
        """Test akscab create csr with all parameters"""
        # Test that all parameters are accepted
        try:
            self.cmd('akscab create csr --role test-role --environment dev --expiration-seconds 600 --keysize 2048 --dev --kubeconfig-path /tmp/kubeconfig')
        except Exception as e:
            # Command may fail due to file/auth issues, but parameters should be valid
            self.assertNotIn("unrecognized arguments", str(e))
            self.assertNotIn("the following arguments are required", str(e))

