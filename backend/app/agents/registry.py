import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.kernel import Kernel
from ..core.config import settings
from .tools import SearchTools

class AgentRegistry:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.agents = {}
        self.orchestration_configs = {}
        self.search_tools = SearchTools()
        
        try:
            self.chat_completion_service = AzureChatCompletion(
                deployment_name=settings.openai_chat_deployment,
                endpoint=settings.openai_endpoint.split('/openai/deployments')[0],
                api_key=settings.openai_key,
                api_version="2025-01-01-preview"
            )
        except Exception as e:
            print(f"Warning: Could not initialize SK chat completion service in registry: {e}")
            self.chat_completion_service = None
    
    @classmethod
    async def create_from_yaml(cls, kernel: Kernel, config_path: str) -> "AgentRegistry":
        """Create agent registry from YAML configuration"""
        registry = cls(kernel)
        await registry.load_config(config_path)
        return registry
    
    async def load_config(self, config_path: str):
        """Load agent configurations from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Agent config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.orchestration_configs = config.get('orchestration', {})
        
        self.kernel.add_plugin(self.search_tools, plugin_name="search_tools")
        
        for agent_id, agent_config in config.get('agents', {}).items():
            agent = await self._create_agent_from_config(agent_id, agent_config)
            if agent:
                self.agents[agent_id] = agent
    
    async def _create_agent_from_config(self, agent_id: str, config: Dict[str, Any]) -> Optional[ChatCompletionAgent]:
        """Create a ChatCompletionAgent from configuration"""
        if not self.chat_completion_service:
            print(f"Warning: Chat completion service not available for agent {agent_id}")
            return None
            
        agent_type = config.get('type', 'chat_completion_agent')
        
        if agent_type == 'chat_completion_agent':
            agent = ChatCompletionAgent(
                kernel=self.kernel,
                name=config.get('name', agent_id),
                instructions=config.get('instructions', ''),
                service=self.chat_completion_service
            )
            
            tools = config.get('tools', [])
            if 'search_documents' in tools:
                pass
                
            return agent
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")
    
    def get_agent(self, agent_id: str) -> Optional[ChatCompletionAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> Dict[str, ChatCompletionAgent]:
        """Get all agents"""
        return self.agents.copy()
    
    def get_orchestration_config(self, orchestration_name: str) -> Optional[Dict[str, Any]]:
        """Get orchestration configuration by name"""
        return self.orchestration_configs.get(orchestration_name)
