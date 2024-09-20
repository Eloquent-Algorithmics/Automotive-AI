targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Flag to decide where to create OpenAI role for current user')
param createRoleForUser bool = true

param deployAzureOpenAi bool = true

param openAiResourceName string = ''
param openAiResourceGroupName string = ''

// https://learn.microsoft.com/azure/ai-services/openai/concepts/models#standard-deployment-model-availability
@description('Location for the OpenAI resource')
@allowed([ 'eastus', 'swedencentral' ])
@metadata({
  azd: {
    type: 'location'
  }
})
param openAiResourceLocation string
param openAiDeploymentName string = 'chatgpt'
param openAiSkuName string = ''
param openAiDeploymentCapacity int // Set in main.parameters.json
param openAiApiVersion string = ''

var openAiConfig = {
  modelName: 'gpt-4o-mini'
  modelVersion: '2024-07-18'
  deploymentName: !empty(openAiDeploymentName) ? openAiDeploymentName : 'chatgpt'
  deploymentCapacity: openAiDeploymentCapacity != 0 ? openAiDeploymentCapacity : 30
}

var resourceToken = toLower(uniqueString(subscription().id, name, location))

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup.name
}

module openAi 'core/ai/cognitiveservices.bicep' = if (deployAzureOpenAi) {
  name: 'openai'
  scope: openAiResourceGroup
  params: {
    name: !empty(openAiResourceName) ? openAiResourceName : '${resourceToken}-cog'
    location: openAiResourceLocation
    sku: {
      name: !empty(openAiSkuName) ? openAiSkuName : 'S0'
    }
    disableLocalAuth: true
    deployments: [
      {
        name: openAiConfig.deploymentName
        model: {
          format: 'OpenAI'
          name: openAiConfig.modelName
          version: openAiConfig.modelVersion
        }
        sku: {
          name: 'Standard'
          capacity: openAiConfig.deploymentCapacity
        }
      }
    ]
  }
}

module openAiRoleUser 'core/security/role.bicep' = if (createRoleForUser && deployAzureOpenAi) {
  scope: openAiResourceGroup
  name: 'openai-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: 'User'
  }
}


output AZURE_LOCATION string = location

output AZURE_OPENAI_CHATGPT_DEPLOYMENT string = deployAzureOpenAi ? openAiConfig.deploymentName : ''
output AZURE_OPENAI_API_VERSION string = deployAzureOpenAi ? openAiApiVersion : ''
output AZURE_OPENAI_ENDPOINT string = deployAzureOpenAi ? openAi.outputs.endpoint : ''
output AZURE_OPENAI_RESOURCE string = deployAzureOpenAi ? openAi.outputs.name : ''
output AZURE_OPENAI_RESOURCE_GROUP string = deployAzureOpenAi ? openAiResourceGroup.name : ''
output AZURE_OPENAI_RESOURCE_GROUP_LOCATION string = deployAzureOpenAi ? openAiResourceGroup.location : ''
output OPENAI_MODEL_NAME string = openAiConfig.modelName
