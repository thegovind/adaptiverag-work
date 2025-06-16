from typing import Optional
from semantic_kernel.kernel import Kernel

kernel: Optional[Kernel] = None
agent_registry = None

def initialize_kernel() -> Kernel:
    """Initialize and return the global kernel instance"""
    global kernel
    if kernel is None:
        kernel = Kernel()
    return kernel

def set_agent_registry(registry):
    """Set the global agent registry"""
    global agent_registry
    agent_registry = registry

def get_agent_registry():
    """Get the global agent registry"""
    return agent_registry
