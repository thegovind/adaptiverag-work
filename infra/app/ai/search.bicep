param name string
param location string = resourceGroup().location
param tags object = {}

param sku object = {
  name: 'basic'
}

param semanticSearch string = 'free'

resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []
    }
    disableLocalAuth: false
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    semanticSearch: semanticSearch
  }
  sku: sku
}

output id string = search.id
output endpoint string = 'https://${search.name}.search.windows.net/'
output name string = search.name
output key string = search.listAdminKeys().primaryKey
