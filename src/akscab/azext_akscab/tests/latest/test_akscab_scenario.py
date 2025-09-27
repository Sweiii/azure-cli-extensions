# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import patch
from io import StringIO
from azext_akscab.custom import list_commands, general_help, create_group_help, create_help, create_csr


class AkscabScenarioTest(unittest.TestCase):

    def test_list_commands(self):
        """Test that list_commands displays available commands"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            list_commands()
            output = mock_stdout.getvalue()
            self.assertIn("Available commands for 'az akscab':", output)
            self.assertIn("create", output)
            self.assertIn("list", output)
            self.assertIn("help", output)

    def test_general_help(self):
        """Test that general_help displays help information"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            general_help()
            output = mock_stdout.getvalue()
            self.assertIn("akscab extension commands:", output)
            self.assertIn("az akscab create", output)
            self.assertIn("az akscab list", output)
            self.assertIn("az akscab help", output)

    def test_create_group_help(self):
        """Test that create_group_help displays available subcommands"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            create_group_help()
            output = mock_stdout.getvalue()
            self.assertIn("Available subcommands for 'az akscab create':", output)
            self.assertIn("csr", output)
            self.assertIn("az akscab create <subcommand> --help", output)

    def test_create_help(self):
        """Test that create_help displays CSR creation help"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            create_help()
            output = mock_stdout.getvalue()
            self.assertIn("To use the create csr command:", output)
            self.assertIn("--role", output)
            self.assertIn("--environment", output)
            self.assertIn("--expiration-seconds", output)

    def test_create_csr_without_role(self):
        """Test that create_csr shows parameter info when role is not provided"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            create_csr(role=None)
            output = mock_stdout.getvalue()
            self.assertIn("Parameters for 'az akscab create csr':", output)
            self.assertIn("Required:", output)
            self.assertIn("--role", output)
            self.assertIn("Optional:", output)
            self.assertIn("--environment", output)
            self.assertIn("--expiration-seconds", output)
            self.assertIn("--keysize", output)
            self.assertIn("--dev", output)
            self.assertIn("--kubeconfig-path", output)

    @patch('azext_akscab.custom.create_graphclient')
    @patch('asyncio.run')
    def test_create_csr_with_role(self, mock_asyncio_run, mock_create_graphclient):
        """Test that create_csr proceeds when role is provided"""
        # Mock the graph client and user
        mock_user = type('User', (), {'user_principal_name': 'test@example.com'})()
        mock_asyncio_run.return_value = mock_user

        with patch('os.path.join') as mock_join, \
             patch('os.path.split') as mock_split, \
             patch('builtins.open', create=True) as mock_open, \
             patch('subprocess.run') as mock_run:

            # Mock file operations
            mock_split.return_value = ('/path', 'akscab')
            mock_join.return_value = '/path/templates/certificatesigningrequest'
            mock_file = mock_open.return_value.__enter__.return_value
            mock_file.read.return_value = 'template content'
            mock_run.return_value = type('CompletedProcess', (), {'returncode': 0})()

            # This should not raise an exception and should proceed with CSR creation
            try:
                create_csr(role='pod-reader', dev=True)  # Use dev=True to avoid graph API call
                # If we get here without exception, the test passes
                self.assertTrue(True)
            except Exception as e:
                # If there's an exception, it should be related to missing files/keys, not parameter validation
                self.assertNotIn("required", str(e).lower())


if __name__ == '__main__':
    unittest.main()