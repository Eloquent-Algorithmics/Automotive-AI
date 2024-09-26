param redisCacheName string

@description('Specify name of Built-In access policy to use as assignment.')
@allowed([
  'Data Owner'
  'Data Contributor'
  'Data Reader'
])
param builtInAccessPolicyName string = 'Data Contributor'

param principalId string

param accessPolicyAlias string

resource redisCache 'Microsoft.Cache/Redis@2023-08-01' existing = {
  name: redisCacheName
}

resource redisCacheBuiltInAccessPolicyAssignment 'Microsoft.Cache/redis/accessPolicyAssignments@2023-08-01' = {
  name: '${redisCacheName}-assignment-${uniqueString(principalId)}'
  parent: redisCache
  properties: {
    accessPolicyName: builtInAccessPolicyName
    objectId: principalId
    objectIdAlias: accessPolicyAlias
  }
}
