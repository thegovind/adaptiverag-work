param documentIntelligenceName string
param principalId string

resource documentIntelligence 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: documentIntelligenceName
}

resource cognitiveServicesUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: documentIntelligence
  name: guid(documentIntelligence.id, principalId, subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908'))
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
    principalType: 'ServicePrincipal'
    principalId: principalId
  }
}
