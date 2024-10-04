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

param speechServiceResourceGroupName string = ''
param speechServiceLocation string = ''
param speechServiceName string = ''
param speechServiceSkuName string // Set in main.parameters.json

@description('Use Azure speech service for reading out text')
param useSpeechOutputAzure bool = true

@description('Flag to decide where to create OpenAI role for current user')
param createRoleForUser bool = true

param deployAzureOpenAi bool = true

param openAiResourceName string = ''
param openAiResourceGroupName string = ''


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
param openAiDeploymentCapacity int
param openAiApiVersion string = ''

var openAiConfig = {
  modelName: 'gpt-4o-mini'
  modelVersion: '2024-07-18'
  deploymentName: !empty(openAiDeploymentName) ? openAiDeploymentName : 'chatgpt'
  deploymentCapacity: openAiDeploymentCapacity != 0 ? openAiDeploymentCapacity : 30
}

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var abbrs = loadJsonContent('abbreviations.json')

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup.name
}

resource speechResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(speechServiceResourceGroupName)) {
  name: !empty(speechServiceResourceGroupName) ? speechServiceResourceGroupName : resourceGroup.name
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

module speech 'br/public:avm/res/cognitive-services/account:0.5.4' = if (useSpeechOutputAzure) {
  name: 'speech-service'
  scope: speechResourceGroup
  params: {
    name: !empty(speechServiceName) ? speechServiceName : '${abbrs.cognitiveServicesSpeech}${resourceToken}'
    kind: 'SpeechServices'
    networkAcls: {
      defaultAction: 'Allow'
    }
    customSubDomainName: !empty(speechServiceName)
      ? speechServiceName
      : '${abbrs.cognitiveServicesSpeech}${resourceToken}'
    location: !empty(speechServiceLocation) ? speechServiceLocation : location
    sku: speechServiceSkuName
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

module speechRoleUser 'core/security/role.bicep' = {
  scope: speechResourceGroup
  name: 'speech-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'f2dc8367-1007-4938-bd23-fe263f013447'
    principalType: 'User'
  }
}



output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = resourceGroup.name
output AZURE_OPENAI_CHATGPT_DEPLOYMENT string = deployAzureOpenAi ? openAiConfig.deploymentName : ''
output AZURE_OPENAI_API_VERSION string = deployAzureOpenAi ? openAiApiVersion : ''
output AZURE_OPENAI_ENDPOINT string = deployAzureOpenAi ? openAi.outputs.endpoint : ''
output AZURE_OPENAI_RESOURCE string = deployAzureOpenAi ? openAi.outputs.name : ''
output AZURE_OPENAI_RESOURCE_GROUP string = deployAzureOpenAi ? openAiResourceGroup.name : ''
output AZURE_OPENAI_RESOURCE_GROUP_LOCATION string = deployAzureOpenAi ? openAiResourceGroup.location : ''
output OPENAI_MODEL_NAME string = openAiConfig.modelName
output AZURE_SPEECH_SERVICE_ID string = useSpeechOutputAzure ? speech.outputs.resourceId : ''
output AZURE_SPEECH_SERVICE_LOCATION string = useSpeechOutputAzure ? speech.outputs.location : ''