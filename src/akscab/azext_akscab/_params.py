# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

def load_arguments(self, _):

    with self.argument_context('akscab create csr') as c:
        c.argument('role', type=str, help='The name of the AKS role to use.', required=False)
        c.argument('environment', type=str, help='The environment to use.', default='nonprod')
        c.argument('expiration_seconds', type=int, help='The number of seconds the certificate is valid for.', default=1800)
        c.argument('keysize', type=int, help='The size of the rsa key to generate.', default=3072)
        c.argument('dev', action='store_true', help='If true, don\'t use the graph client to get the username.')
        c.argument('kubeconfig_path', type=str, help='Path to the kubeconfig file to parse for cluster, context, and user info.', default='~/.kube/config')
