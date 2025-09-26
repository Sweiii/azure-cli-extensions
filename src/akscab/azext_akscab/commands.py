# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

def load_command_table(self, _):

    with self.command_group('akscab') as g:
        g.custom_command('list', 'list_commands')

    with self.command_group('akscab create') as g:
        g.custom_command('csr', 'create_csr')
        g.custom_command('help', 'create_help')
