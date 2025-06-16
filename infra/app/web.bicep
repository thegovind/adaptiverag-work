param name string
param location string = resourceGroup().location
param tags object = {}

param apiBaseUrl string

resource web 'Microsoft.Web/staticSites@2022-03-01' = {
  name: name
  location: location
  tags: union(tags, { 'azd-service-name': 'web' })
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    repositoryUrl: ''
    branch: ''
    buildProperties: {
      appLocation: '/frontend'
      apiLocation: ''
      outputLocation: 'dist'
    }
  }
}

resource webConfig 'Microsoft.Web/staticSites/config@2022-03-01' = {
  parent: web
  name: 'appsettings'
  properties: {
    VITE_API_BASE_URL: apiBaseUrl
  }
}

output SERVICE_WEB_NAME string = web.name
output SERVICE_WEB_URI string = 'https://${web.properties.defaultHostname}'
