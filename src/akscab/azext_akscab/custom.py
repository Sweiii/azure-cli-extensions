from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from string import Template
import asyncio
import subprocess
import os
import base64
from azext_akscab._helpers import (
    get_output,
    must,
    print_or_merge_credentials,
)


def update_akscab(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance


def list_commands():
    print("Available commands:")
    print("  create - Commands to create CSRs")


def create_help():
    print("To use the create csr command:")
    print("1. Specify the role with --role (required)")
    print("2. Specify the environment with --environment (default: nonprod)")
    print("3. Optionally set expiration seconds with --expiration-seconds (default: 1800)")
    print("4. Optionally set keysize with --keysize (default: 3072)")
    print("5. Use --dev if not using graph client (default: False)")
    print("Example: az akscab create csr --role pod-reader --environment nonprod --dev")


async def create_graphclient():
    scopes = ['User.Read']
    tenant_id = os.getenv('AKSCAB_TENANT_ID', '581d5615-1943-4c5a-a95b-58136824cee7')
    client_id = os.getenv('AKSCAB_CLIENT_ID', '4ee02bc2-ed8c-43b0-89bc-e35afacee3e0')

    credential = DeviceCodeCredential(
        tenant_id=tenant_id,
        client_id=client_id)

    graph_client = GraphServiceClient(credential, scopes)
    username = await graph_client.me.get()
    return username


async def getCurrentUsername():
    user = await create_graphclient()
    return user.user_principal_name


def create_csr(role, environment='nonprod', keysize=3072, expiration_seconds=1800, dev=False):
    # get_base_kubeconfig(environment)
    if dev is False:
        user = asyncio.run(getCurrentUsername())
        username = user.split("@")[0]
        data = generate_key(username, role, keysize)
        encoded = base64.b64encode(bytes(data, "utf-8")).decode('utf-8')
    else:
        username = "minikube-user"
        data = generate_key("minikube-user", role, keysize)
        encoded = base64.b64encode(bytes(data, "utf-8")).decode('utf-8')
    substitute = {
        'user': username,
        'request': encoded,
        'expirationSeconds': expiration_seconds
    }
    dirname = os.path.split(os.path.abspath(__file__))[0]
    templatePath = os.path.join(dirname, 'templates/certificatesigningrequest')
    with open(templatePath, 'r') as f:
        src = Template(f.read())
        result = src.substitute(substitute)
    apply_certificate_signing_request(result)
    create_kubeconfig(username, environment)


def generate_key(username, role, keysize):
    subject = f"/CN={username}/O={role}/O=csrdefault"
    key_size = f"rsa:{keysize}"
    key_name = f"{username}.key"
    dirname = os.path.split(os.path.abspath(__file__))[0]
    keyPath = os.path.join(dirname, key_name)

    cmd = [
        "openssl", "req", "-newkey", key_size, "-nodes", "-keyout", keyPath, "-subj", subject
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    result.check_returncode()
    return result.stdout


def apply_certificate_signing_request(csr_yaml):
    process = subprocess.Popen(['kubectl', 'apply', '-f', '-'], stdin=subprocess.PIPE, text=True)
    process.communicate(input=csr_yaml)
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, process.args)


def create_kubeconfig(username, environment='nonprod', dev=False):
    key_name = f"{username}.key"
    dirname = os.path.split(os.path.abspath(__file__))[0]
    keyPath = os.path.join(dirname, key_name)

    if dev is True:
        get_output('kubectl config use-context minikube')

    current_context = get_output('kubectl config current-context')
    current_cluster = get_clustername_for_context(current_context)
    cluster_info = get_cluster_info(current_cluster)
    client_certificate_data = get_certificate_signing_request(username)
    delete_certificate_signing_request(username)
    with open(keyPath, 'rb') as key_file:
        client_key_data = base64.b64encode(key_file.read()).decode('utf-8')

    os.remove(keyPath)

    kubeconfig_content = f"""
apiVersion: v1
kind: Config
current-context: {current_cluster}
clusters:
- {cluster_info}
users:
- name: {current_cluster}
  user:
    client-certificate-data: {client_certificate_data}
    client-key-data: {client_key_data}
contexts:
- name: {current_cluster}
  context:
    cluster: {current_cluster}
    user: {current_cluster}
"""

    home_directory = os.getenv('HOME')
    output_path_merge = os.path.join(home_directory, '.kube/config')
    print_or_merge_credentials(output_path_merge, kubeconfig_content, True, current_cluster)
    context_name = f"{current_cluster}-admin" if environment == 'nonprod' else current_cluster
    set_context(context_name)


def set_context(context_name, dev=False):
    command = ['kubectl', 'config', 'use-context', context_name]
    result = subprocess.run(command, capture_output=True, text=True)
    result.check_returncode()


def get_clustername_for_context(context_name):
    command = ['kubectl', 'config', 'view', '-o', f'jsonpath={{.contexts[?(@.name == "{context_name}")].context.cluster}}']
    return get_output(command)


def get_cluster_info(current_cluster):
    command = ['kubectl', 'config', 'view', '--raw', '-o', f'jsonpath={{.clusters[?(@.name == "{current_cluster}")]}}']
    return get_output(command)


def get_certificate_signing_request(username):
    command = ['kubectl', 'get', 'csr', username, '-o', 'jsonpath={.status.certificate}']
    return get_output(command)


def delete_certificate_signing_request(username):
    command = ['kubectl', 'delete', 'csr', username]
    return get_output(command)


def get_base_kubeconfig(environment='nonprod', dev=False):
    if dev is True:
        return
    clustername = f'corehosting-aks-{environment}'
    subscription = f'cab-automotive-corehosting-{environment}'
    command = [
        'az', 'aks', 'get-credentials',
        '--name', clustername,
        '--resource-group', clustername,
        '--overwrite-existing',
        '--admin',
        '--subscription', subscription
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    result.check_returncode()
