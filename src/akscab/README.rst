Microsoft Azure CLI 'akscab' Extension
==========================================

This package provides the 'akscab' extension for Azure CLI, enabling the creation of Certificate Signing Requests (CSRs) for AKS clusters in CAB (Cluster API Bootstrap) environments.

Usage:
- az akscab create --role <role> [--environment <env>] [--keysize <size>] [--expiration-seconds <secs>] [--dev]

This extension automates the process of generating RSA keys, creating CSRs, and configuring kubeconfig for authenticated access to AKS clusters.