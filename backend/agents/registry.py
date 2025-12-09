
import os
import pkgutil
import inspect
import importlib
from typing import Dict, Type, List, Optional
from loguru import logger
from metagpt.roles import Role
from agents import roles

class AgentRegistry:
    """
    Dynamic registry for MetaGPT agents.
    Scans backend/agents/roles for subclasses of Role.
    """
    _agents: Dict[str, Type[Role]] = {}
    _initialized: bool = False

    @classmethod
    def initialize(cls):
        """Discover and register all agents"""
        if cls._initialized:
            return

        logger.info("🕵️ Discovering agents...")
        
        # Path to roles package
        package_path = os.path.dirname(roles.__file__)
        
        for _, name, _ in pkgutil.iter_modules([package_path]):
            if name == "base_role":
                continue
                
            try:
                module = importlib.import_module(f"agents.roles.{name}")
                
                # Find Role subclasses
                for attr_name, attr_value in inspect.getmembers(module):
                    if (inspect.isclass(attr_value) 
                        and issubclass(attr_value, Role) 
                        and attr_value is not Role
                        and attr_value.__module__ == module.__name__):
                        
                        # Use class name or a generic registry key
                        # Convention: ContractGuardian -> contract-guardian
                        # But for now, let's map by class name or explicit ID if available
                        # FlagPilot logic uses specific ID strings, we need to match that.
                        
                        # HACK: For now, map simple names. 
                        # In a real system, Agents should declare their 'name' property.
                        # We will store the class.
                        cls._agents[name] = attr_value
                        logger.debug(f"  - Registered: {name} -> {attr_name}")
                        
            except Exception as e:
                logger.error(f"Failed to load agent module {name}: {e}")

        cls._initialized = True
        logger.info(f"✅ Registered {len(cls._agents)} agents")

    @classmethod
    def get_agent_class(cls, name: str) -> Optional[Type[Role]]:
        if not cls._initialized:
            cls.initialize()
        return cls._agents.get(name)

    @classmethod
    def list_agents(cls) -> List[str]:
        if not cls._initialized:
            cls.initialize()
        return list(cls._agents.keys())

# Create a singleton-like access
registry = AgentRegistry
