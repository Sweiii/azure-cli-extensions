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

    @unittest.skip('Requires authentication and file system access')
    def test_akscab_create_csr_parameters(self):
        """Test akscab create csr parameter display (skipped due to auth requirements)"""
        # This would test the parameter display when no role is provided
        # But it requires the extension to be loaded and would try to authenticate
        pass

    @unittest.skip('Requires authentication and file system access')
    def test_akscab_create_csr_with_minimal_params(self):
        """Test akscab create csr with minimal parameters (skipped due to auth requirements)"""
        # This would test actual CSR creation but requires:
        # - Azure authentication
        # - File system access for templates
        # - OpenSSL for key generation
        pass