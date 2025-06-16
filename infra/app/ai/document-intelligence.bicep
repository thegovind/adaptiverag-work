param name string
param location string = resourceGroup().location
param tags object = {}

param sku object = {
  name: 'S0'
}

resource documentIntelligence 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: 'FormRecognizer'
  properties: {
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
  sku: sku
}

output endpoint string = documentIntelligence.properties.endpoint
output id string = documentIntelligence.id
output name string = documentIntelligence.name
output key string = documentIntelligence.listKeys().key1
