param keyVaultName string

param clientSecretName string

@secure()
param clientSecretValue string

module clientSecretKVSecret 'core/security/keyvault-secret.bicep' = {
  name: 'clientsecret'
  params: {
    keyVaultName: keyVaultName
    name: clientSecretName
    secretValue: clientSecretValue
  }
}
