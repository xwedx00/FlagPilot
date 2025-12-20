
import os
import pkgutil
import inspect
import importlib
from typing import Dict, Type, List, Optional, Any
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

    @classmethod
    def get_agent_info(cls, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get descriptive info about an agent from its class attributes"""
        if not cls._initialized:
            cls.initialize()
            
        role_cls = cls._agents.get(agent_id)
        if not role_cls:
            return None
            
        # Extract metadata from MetaGPT Role class
        # (Using getattr/default because Pydantic models in MetaGPT 0.8.1 might store them in different places)
        profile = getattr(role_cls, "profile", f"FlagPilot {agent_id} specialist")
        goal = getattr(role_cls, "goal", f"Help users with {agent_id.replace('_', ' ')}")
        
        # MetaGPT 0.8.1 often stores these as default values in Pydantic fields
        if hasattr(role_cls, "__fields__"):
             if "profile" in role_cls.__fields__:
                 profile = role_cls.__fields__["profile"].default
             if "goal" in role_cls.__fields__:
                 goal = role_cls.__fields__["goal"].default

        return {
            "id": agent_id,
            "name": agent_id,
            "description": f"FlagPilot {agent_id} agent",
            "profile": profile,
            "goal": goal
        }

# Create a singleton-like access
registry = AgentRegistry
