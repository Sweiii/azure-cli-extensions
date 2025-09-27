from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from string import Template
import asyncio
import subprocess
import os
import base64
import yaml
import json
from azext_akscab._helpers import (
    get_output,
    print_or_merge_credentials,
)


def update_akscab(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance


def list_commands():
    print("Available commands for 'az akscab':")
    print("  create    Commands to create CSRs")
    print("  list      Lists available commands")
    print("  help      Shows general help")
    print()
    print("For help with a specific command, use:")
    print("  az akscab <command> --help")


def general_help():
    print("akscab extension commands:")
    print("  az akscab create - Commands to create CSRs")
    print("  az akscab list - Lists available commands")
    print("  az akscab help - Show this help")


def create_group_help():
    print("Available subcommands for 'az akscab create':")
    print("  csr    Create a Certificate Signing Request")
    print()
    print("For help with a specific subcommand, use:")
    print("  az akscab create <subcommand> --help")


def create_help():
    print("To use the create csr command:")
    print("1. Specify the role with --role (required)")
    print("2. Specify the environment with --environment (default: nonprod)")
    print("3. Optionally set expiration seconds with --expiration-seconds (default: 1800)")
    print("4. Optionally set keysize with --keysize (default: 3072)")
    print("6. Optionally specify kubeconfig path with --kubeconfig-path (default: ~/.kube/config)")
    print("Example: az akscab create csr --role pod-reader --environment nonprod")


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


def check_dependencies():
    """Check if required external tools are installed."""
    required_tools = ['openssl', 'kubectl']
    missing_tools = []
    for tool in required_tools:
        try:
            if tool == 'kubectl':
                subprocess.run([tool, 'version'], capture_output=True, check=True)
            else:
                subprocess.run([tool, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
    if missing_tools:
        # pylint: disable=line-too-long
        raise SystemExit(f"Error: Required tools are not installed: {', '.join(missing_tools)}. Please install them and try again.")


def create_csr(role=None, environment='nonprod', keysize=3072,
               expiration_seconds=1800, dev=False, kubeconfig_path='~/.kube/config'):
    # pylint: disable=unused-argument
    if role is None:
        print("Parameters for 'az akscab create csr':")
        print()
        print("Required:")
        print("  --role                      The name of the AKS role to use")
        print()
        print("Optional:")
        print("  --environment               The environment to use (default: nonprod)")
        print("  --expiration-seconds        The number of seconds the certificate is valid for (default: 1800)")
        print("  --keysize                   The size of the rsa key to generate (default: 3072)")
        print("  --kubeconfig-path           Path to the kubeconfig file (default: ~/.kube/config)")
        print("  --dev                       Optional flag to indicate development mode with minikube (default: False)")
        print()
        print("Example:")
        print("  az akscab create csr --role pod-reader --environment nonprod")
        return

    check_dependencies()

    # get_base_kubeconfig(environment)
    if dev:
        username = "minikube-user"
        data = generate_key("minikube-user", role, keysize)
        encoded = base64.b64encode(bytes(data, "utf-8")).decode('utf-8')
    else:
        user = asyncio.run(getCurrentUsername())
        username = user.split("@")[0]
        data = generate_key(username, role, keysize)
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
    # create_kubeconfig(username, environment, kubeconfig_path)


def generate_key(username, role, keysize):
    subject = f"/CN={username}/O={role}"
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
    process = subprocess.Popen(['kubectl', 'apply', '-f', '/dev/stdin'], stdin=subprocess.PIPE, text=True)
    process.communicate(input=csr_yaml)
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, process.args)


def create_kubeconfig(username, environment='nonprod', kubeconfig_path='~/.kube/config_new'):
    key_name = f"{username}.key"
    dirname = os.path.split(os.path.abspath(__file__))[0]
    keyPath = os.path.join(dirname, key_name)

    config = load_kubeconfig(kubeconfig_path)
    current_context = get_current_context_from_config(config)
    current_cluster = get_cluster_for_context_from_config(config, current_context)
    cluster_info = get_cluster_info_from_config(config, current_cluster)
    client_certificate_data = get_certificate_signing_request(username)
    delete_certificate_signing_request(username)
    with open(keyPath, 'rb') as key_file:
        client_key_data = base64.b64encode(key_file.read()).decode('utf-8')

    os.remove(keyPath)

    # Generate cluster info as JSON string for flow style insertion
    cluster_yaml = json.dumps(cluster_info)

    kubeconfig_content = f"""apiVersion: v1
kind: Config
current-context: {current_cluster}
clusters:
- {cluster_yaml}
users:
- name: {current_cluster}
  user:
    client-certificate-data: "{client_certificate_data}"
    client-key-data: "{client_key_data}"
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


def set_context(context_name):
    command = ['kubectl', 'config', 'use-context', context_name]
    result = subprocess.run(command, capture_output=True, text=True)
    result.check_returncode()


def get_clustername_for_context(context_name):
    command = ['kubectl', 'config', 'view', '-o',
               f'jsonpath={{.contexts[?(@.name == "{context_name}")].context.cluster}}']
    return get_output(command)


def get_cluster_info(current_cluster):
    command = ['kubectl', 'config', 'view', '--raw', '-o',
               f'jsonpath={{.clusters[?(@.name == "{current_cluster}")]}}']
    return get_output(command)


def get_certificate_signing_request(username):
    command = ['kubectl', 'get', 'csr', username, '-o', 'jsonpath={.status.certificate}']
    return get_output(command)


def delete_certificate_signing_request(username):
    command = ['kubectl', 'delete', 'csr', username]
    return get_output(command)


def load_kubeconfig(kubeconfig_path):
    """Load and parse the kubeconfig file."""
    path = os.path.expanduser(kubeconfig_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Kubeconfig file not found: {path}")
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def get_current_context_from_config(config):
    """Get the current context from kubeconfig."""
    return config.get('current-context')


def get_cluster_for_context_from_config(config, context_name):
    """Get the cluster name for a given context."""
    for context in config.get('contexts', []):
        if context['name'] == context_name:
            return context['context']['cluster']
    return None


def get_cluster_info_from_config(config, cluster_name):
    """Get the cluster info for a given cluster."""
    for cluster in config.get('clusters', []):
        if cluster['name'] == cluster_name:
            # Ensure certificate-authority-data is a string
            if 'cluster' in cluster and 'certificate-authority-data' in cluster['cluster']:
                cad = cluster['cluster']['certificate-authority-data']
                if isinstance(cad, list):
                    cluster['cluster']['certificate-authority-data'] = ''.join(cad)
            return cluster
    return None


def get_base_kubeconfig(environment='nonprod'):
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
