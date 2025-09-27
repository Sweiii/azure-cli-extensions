# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['akscab'] = """
    type: group
    short-summary: Commands to manage Akscabs.
    long-summary: This extension provides commands to manage Akscabs, including creating CSRs and listing available commands.
    examples:
      - name: List available commands
        text: az akscab list
      - name: Show general help
        text: az akscab help
      - name: Create a CSR
        text: az akscab create csr --role pod-reader --environment nonprod
"""

helps['akscab help'] = """
    type: command
    short-summary: Shows general help for the akscab extension.
    examples:
      - name: Show general help
        text: az akscab help
"""

helps['akscab create'] = """
    type: group
    short-summary: Commands to create CSRs.
    long-summary: |
        Commands to create Certificate Signing Requests (CSRs) for AKS access.

        Available subcommands:
          csr    Create a Certificate Signing Request
"""

helps['akscab create csr'] = """
    type: command
    short-summary: Creates a CSR.
    long-summary: "Generate a CSR with a specified role."
    parameters:
        - name: --role
          type: string
          short-summary: The name of the AKS role to use.
        - name: --environment
          type: string
          short-summary: The environment to use.
        - name: --expiration-seconds
          type: int
          short-summary: The number of seconds the certificate is valid for.
        - name: --keysize
          type: int
          short-summary: The size of the rsa key to generate.
        - name: --dev
          type: bool
          short-summary: If true, don't use the graph client to get the username.
        - name: --kubeconfig-path
          type: string
          short-summary: Path to the kubeconfig file to parse for cluster, context, and user info.
    examples:
      - name: Get the pod-reader role.
        text: az akscab create csr --role pod-reader --environment nonprod
      - name: Get the pod-reader role with 600 second lifetime for certificate.
        text: az akscab create csr --role pod-reader --environment nonprod --expiration-seconds 600
      - name: Get the pod-reader role with RSA:4096 key.
        text: az akscab create csr --role pod-reader --environment nonprod --keysize 4096
"""

helps['akscab create help'] = """
    type: command
    short-summary: Shows help for the create csr command.
    examples:
      - name: Show help for create csr command
        text: az akscab create help
"""

helps['akscab list'] = """
    type: command
    short-summary: Lists available commands in the akscab extension.
    examples:
      - name: List available commands
        text: az akscab list
"""
