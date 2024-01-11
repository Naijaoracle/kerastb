from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Authenticate to your Azure Key Vault using DefaultAzureCredential
credential = DefaultAzureCredential()

# Replace 'your-key-vault-url' with the URL of your Azure Key Vault
keyvault_url = "https://kerastbkeys.vault.azure.net/"
secret_client = SecretClient(vault_url=keyvault_url, credential=credential)

# Create secrets in Azure Key Vault
# Blob URL
blob_url_secret = secret_client.set_secret("BlobURL", "https://daviddasaprojects.blob.core.windows.net/kerastb/model_weights.h5")

# SAS Token
sas_token_secret = secret_client.set_secret("SASToken", "?sv=2023-01-03&ss=btqf&srt=sco&st=2024-01-06T00%3A30%3A38Z&se=2025-01-07T00%3A30%3A00Z&sp=rwlacu&sig=3JxRMqFMQJZAUz9brTwaXphU1RaF6o0PYMjdKFravTQ%3D")

# Container
container_secret = secret_client.set_secret("Container", "daviddasaprojects")

# Connection String
connection_string_secret = secret_client.set_secret("ConnectionString", "SharedAccessSignature=sv=2023-01-03&ss=btqf&srt=sco&st=2024-01-06T00%3A30%3A38Z&se=2025-01-07T00%3A30%3A00Z&sp=rwlacu&sig=3JxRMqFMQJZAUz9brTwaXphU1RaF6o0PYMjdKFravTQ%3D;BlobEndpoint=https://daviddasaprojects.blob.core.windows.net;FileEndpoint=https://daviddasaprojects.file.core.windows.net;QueueEndpoint=https://daviddasaprojects.queue.core.windows.net;TableEndpoint=https://daviddasaprojects.table.core.windows.net;")

# SAS Token
sas_token_secret = secret_client.set_secret("SASToken", "?sv=2023-01-03&ss=btqf&srt=sco&st=2024-01-06T00%3A30%3A38Z&se=2025-01-07T00%3A30%3A00Z&sp=rwlacu&sig=3JxRMqFMQJZAUz9brTwaXphU1RaF6o0PYMjdKFravTQ%3D")

# Create a key
# Replace 'your-key-name' with the desired key name
rsa_key = key_client.create_rsa_key("kerastbkey", size=2048)
print(rsa_key.name)
print(rsa_key.key_type)
