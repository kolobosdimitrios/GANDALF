"""
GANDALF AI Agent Communication Module

This module provides the interface for communicating with the AI agent
running inside the GANDALF VM to perform intent analysis, gap detection,
and CTC generation.
"""

from .agent_client import AgentClient
from .ctc_orchestrator import CTCOrchestrator

__all__ = ['AgentClient', 'CTCOrchestrator']
