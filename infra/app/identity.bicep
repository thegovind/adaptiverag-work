param name string
param location string = resourceGroup().location
param tags object = {}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: name
  location: location
  tags: tags
}

output identityId string = identity.id
output identityName string = identity.name
output identityPrincipalId string = identity.properties.principalId
output identityClientId string = identity.properties.clientId
