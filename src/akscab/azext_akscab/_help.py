# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['akscab'] = """
    type: group
    short-summary: Commands to manage Akscabs.
"""

helps['akscab create'] = """
    type: command
    short-summary: Creates an CSR.
    long-summary: "Generate a CSR with a specified role."
    parameters:
        - name: --role
          type: string
          short-summary: The name of the AKS role to use.
        - name: --environment
          type: string
          short-summary: Then environment to use.
        - name: --expiration-seconds
          type: int
          short-summary: The number of seconds the certificate is valid for.
        - name: --keysize
          type: string
          short-summary: The size of the rsa key to generate.
        - name: --dev
          type: bool
          short-summary: If true, don't use the graph client to get the username.
    examples:
      - name: Get the pod-reader role.
        text: az akscab create --role pod-reader --environment nonprod
      - name: Get the pod-reader role with 600 second lifetime for certificate.
        text: az akscab create --role pod-reader --environment nonprod --expiration-seconds 600
      - name: Get the pod-reader role with RSA:4096 key.
        text: az akscab create --role pod-reader --environment nonprod --keysize 4096
"""

