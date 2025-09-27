# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azext_akscab.tests import try_manual
from azure.cli.testsdk import ScenarioTest


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

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

    def test_akscab_create_list(self):
        """Test akscab create list command"""
        self.cmd('akscab create list')

    def test_akscab_create_csr_parameter_validation(self):
        """Test akscab create csr parameter validation"""
        self.cmd('akscab create csr')
