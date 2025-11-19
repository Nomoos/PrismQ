#!/usr/bin/env python3
"""
Layer Architecture - Proper Layer Separation Example

Demonstrates the 5-layer architecture with proper dependency flow.
Run this file to see layer interaction in action.
"""

from typing import Protocol, List, Optional
from dataclasses import dataclass
from datetime import datetime


# Layer 5: Infrastructure (lowest - no dependencies)
class ConfigLoader:
    def load(self): 
        print("[Infrastructure] Loading config")
        return {"db_path": "ideas.db"}

# Layer 4: Model
@dataclass
class IdeaInspiration:
    id: str
    title: str
    source: str
    category: Optional[str] = None

class IdeaRepository(Protocol):
    def save(self, idea: IdeaInspiration) -> str: ...

# Layer 3: Collection
class YouTubePlugin:
    def fetch(self, url: str) -> List[IdeaInspiration]:
        print(f"[Collection] Fetching from {url}")
        return [IdeaInspiration("1", "Python Tutorial", "youtube")]

# Layer 2: Processing
class CategoryClassifier:
    def classify(self, idea: IdeaInspiration) -> str:
        print(f"[Processing] Classifying: {idea.title}")
        return "programming"

# Layer 1: Application (highest - depends on all)
class IdeaService:
    def __init__(self, plugin, classifier, repository):
        self._plugin = plugin
        self._classifier = classifier
        self._repository = repository
    
    def collect(self, url: str):
        ideas = self._plugin.fetch(url)
        for idea in ideas:
            idea.category = self._classifier.classify(idea)
            self._repository.save(idea)
        return len(ideas)

if __name__ == "__main__":
    print("Demonstrating Layer Architecture\n")
    print("Dependencies flow DOWNWARD only:")
    print("Application → Processing → Collection → Model → Infrastructure\n")
