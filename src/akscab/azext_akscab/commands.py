# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_akscab._client_factory import cf_akscab


def load_command_table(self, _):

    with self.command_group('akscab') as g:
        g.custom_command('create', 'create_csr')

    with self.command_group('akscab', is_preview=True):
        pass
