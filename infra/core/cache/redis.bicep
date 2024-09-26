param name string
param location string = resourceGroup().location
param tags object = {}

resource redisCache 'Microsoft.Cache/Redis@2023-08-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    sku: {
      capacity: 1
      family: 'C'
      name: 'Basic'
    }
    redisConfiguration: {
      'aad-enabled': 'true'
    }
  }
}

output name string = redisCache.name
output id string = redisCache.id
output hostName string = redisCache.properties.hostName
