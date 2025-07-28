"""
🧠 Intelligent LLM Router - The Brain of NuiFlo's Hybrid AI System

This module implements smart routing between:
- Ollama/Mistral (FREE) - For simple tasks, orchestration, analysis
- Commercial LLMs (PAID) - For complex reasoning, specialized tasks

Key Features:
- Real-time complexity analysis
- Cost optimization
- Automatic fallback
- Performance tracking
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from decimal import Decimal
from dataclasses import dataclass
import re
import json

# import ollama  # Temporarily disabled due to dependency conflicts
from openai import OpenAI
import anthropic
import httpx

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ComplexityLevel(Enum):
    """Task complexity levels for routing decisions"""
    SIMPLE = "simple"        # Ollama can handle
    MEDIUM = "medium"        # GPT-3.5 recommended  
    COMPLEX = "complex"      # GPT-4 required
    SPECIALIZED = "specialized"  # Domain-specific models


class LLMProvider(Enum):
    """Available LLM providers in our hybrid system"""
    OLLAMA_MISTRAL = "ollama_mistral"
    OPENAI_GPT_35 = "openai_gpt_3.5_turbo"  
    OPENAI_GPT_4 = "openai_gpt_4"
    ANTHROPIC_CLAUDE = "anthropic_claude_3_haiku"


@dataclass
class RoutingDecision:
    """Decision made by the intelligent router"""
    provider: LLMProvider
    model: str
    estimated_cost: Decimal
    reasoning: str
    complexity: ComplexityLevel
    confidence: float


@dataclass 
class ExecutionResult:
    """Result from LLM execution with tracking"""
    content: str
    provider: LLMProvider
    actual_tokens: int
    actual_cost: Decimal
    duration_seconds: float
    success: bool
    error: Optional[str] = None


class ComplexityAnalyzer:
    """Analyzes task complexity to determine optimal LLM routing"""
    
    def __init__(self):
        self.ollama_available = False
        self._initialize_ollama()
    
    def _initialize_ollama(self):
        """Initialize connection to local Ollama via HTTP API"""
        try:
            # Check if Ollama is available via HTTP
            response = httpx.get('http://localhost:11434/api/version', timeout=5.0)
            if response.status_code == 200:
                self.ollama_available = True
                logger.info("🧠 Ollama HTTP API connection established")
            else:
                logger.warning("⚠️ Ollama HTTP API not responding")
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
            self.ollama_available = False
    
    def analyze_complexity(self, prompt: str, context: Optional[str] = None) -> ComplexityLevel:
        """
        Analyze task complexity using multiple heuristics
        
        Args:
            prompt: The task prompt to analyze
            context: Optional context information
            
        Returns:
            ComplexityLevel: Recommended complexity level
        """
        # Quick heuristic analysis (fast, no LLM needed)
        heuristic_score = self._heuristic_complexity_score(prompt)
        
        # If Ollama is available, use it for deeper analysis
        if self.ollama_available and heuristic_score > 0.3:
            try:
                llm_score = self._llm_complexity_analysis(prompt, context)
                # Combine scores (weighted average)
                final_score = (heuristic_score * 0.4) + (llm_score * 0.6)
            except Exception as e:
                logger.warning(f"LLM analysis failed, using heuristic: {e}")
                final_score = heuristic_score
        else:
            final_score = heuristic_score
        
        # Map score to complexity level
        if final_score < 0.2:
            return ComplexityLevel.SIMPLE
        elif final_score < 0.5:
            return ComplexityLevel.MEDIUM
        elif final_score < 0.8:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.SPECIALIZED
    
    def _heuristic_complexity_score(self, prompt: str) -> float:
        """Fast heuristic-based complexity scoring"""
        score = 0.0
        prompt_lower = prompt.lower()
        
        # Length factor
        if len(prompt) > 1000:
            score += 0.2
        elif len(prompt) > 500:
            score += 0.1
        
        # Complexity keywords
        complex_keywords = [
            'analyze', 'design', 'architect', 'optimize', 'algorithm',
            'machine learning', 'deep learning', 'neural network',
            'research', 'scientific', 'mathematical', 'statistical',
            'reasoning', 'logic', 'proof', 'theorem', 'philosophy'
        ]
        
        simple_keywords = [
            'list', 'summarize', 'translate', 'format', 'convert',
            'extract', 'find', 'search', 'basic', 'simple'
        ]
        
        # Score based on keyword presence
        for keyword in complex_keywords:
            if keyword in prompt_lower:
                score += 0.15
        
        for keyword in simple_keywords:
            if keyword in prompt_lower:
                score -= 0.1
        
        # Code-related tasks (medium complexity)
        if any(lang in prompt_lower for lang in ['python', 'javascript', 'sql', 'code', 'programming']):
            score += 0.2
        
        # Creative tasks (can be simple or complex)
        if any(word in prompt_lower for word in ['write', 'create', 'generate', 'story']):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _llm_complexity_analysis(self, prompt: str, context: Optional[str] = None) -> float:
        """Use Ollama/Mistral to analyze complexity (free analysis!)"""
        analysis_prompt = f"""
        Analyze the complexity of this task on a scale of 0-1:
        
        0.0-0.2: Simple (basic formatting, simple questions, extraction)
        0.2-0.5: Medium (analysis, coding, research with clear scope)  
        0.5-0.8: Complex (deep reasoning, multi-step problems, design)
        0.8-1.0: Specialized (expert domain knowledge, advanced math/science)
        
        Task: {prompt}
        Context: {context or 'None'}
        
        Respond with just a number between 0 and 1:
        """
        
        try:
            response = httpx.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'mistral:7b-instruct',
                    'prompt': analysis_prompt,
                    'options': {'temperature': 0.1, 'num_predict': 10}
                },
                timeout=10.0
            )
            
            response.raise_for_status() # Raise an exception for HTTP errors
            
            # Extract numeric score from response
            text = response.json()['response'].strip()
            score_match = re.search(r'([0-1]?\.?\d+)', text)
            
            if score_match:
                score = float(score_match.group(1))
                return max(0.0, min(1.0, score))
            else:
                logger.warning(f"Could not parse complexity score: {text}")
                return 0.5  # Default to medium
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP API complexity analysis failed with status {e.response.status_code}: {e}")
            raise
        except Exception as e:
            logger.error(f"Ollama HTTP API complexity analysis failed: {e}")
            raise


class IntelligentLLMRouter:
    """
    🚀 The Heart of NuiFlo's Hybrid AI System
    
    Routes requests to the most cost-effective LLM based on:
    - Task complexity
    - User budget preferences  
    - Model availability
    - Performance requirements
    """
    
    def __init__(self):
        self.complexity_analyzer = ComplexityAnalyzer()
        self.ollama_client = None
        self.openai_client = None
        self.anthropic_client = None
        
        self._initialize_clients()
        
        # Pricing per 1K tokens (approximate)
        self.pricing = {
            LLMProvider.OLLAMA_MISTRAL: Decimal("0.0000"),     # FREE! 🎉
            LLMProvider.OPENAI_GPT_35: Decimal("0.0015"),      # $0.0015/1K
            LLMProvider.OPENAI_GPT_4: Decimal("0.03"),         # $0.03/1K  
            LLMProvider.ANTHROPIC_CLAUDE: Decimal("0.0008"),   # $0.0008/1K
        }
    
    def _initialize_clients(self):
        """Initialize all LLM clients"""
        # Ollama (local)
        try:
            self.ollama_client = httpx.Client(base_url='http://localhost:11434')
            logger.info("🧠 Ollama client initialized")
        except Exception as e:
            logger.warning(f"Ollama initialization failed: {e}")
        
        # OpenAI  
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("🤖 OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
        
        # Anthropic
        if hasattr(settings, 'anthropic_api_key') and settings.anthropic_api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                logger.info("🧠 Anthropic client initialized") 
            except Exception as e:
                logger.warning(f"Anthropic initialization failed: {e}")
    
    def route_request(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        max_budget: Optional[Decimal] = None,
        preferred_quality: str = "balanced"  # "fast", "balanced", "premium"
    ) -> RoutingDecision:
        """
        🎯 Make intelligent routing decision
        
        Args:
            prompt: The task prompt
            context: Optional context
            max_budget: Maximum cost user wants to spend
            preferred_quality: User's quality preference
            
        Returns:
            RoutingDecision: Where to route the request
        """
        # Analyze complexity
        complexity = self.complexity_analyzer.analyze_complexity(prompt, context)
        
        # Estimate token usage (rough approximation)
        estimated_tokens = len(prompt.split()) * 1.3  # Words to tokens ratio
        
        # Generate routing options
        options = self._generate_routing_options(complexity, estimated_tokens, preferred_quality)
        
        # Filter by budget if specified
        if max_budget:
            options = [opt for opt in options if opt.estimated_cost <= max_budget]
        
        if not options:
            # Fallback to cheapest option
            options = [self._create_fallback_option(complexity, estimated_tokens)]
        
        # Select best option (first is highest priority)
        selected = options[0]
        
        logger.info(f"🎯 Routing decision: {selected.provider.value} for {complexity.value} task")
        
        return selected
    
    def _generate_routing_options(
        self, 
        complexity: ComplexityLevel, 
        estimated_tokens: float,
        preferred_quality: str
    ) -> List[RoutingDecision]:
        """Generate prioritized routing options"""
        options = []
        
        if complexity == ComplexityLevel.SIMPLE:
            # Try Ollama first (FREE!)
            if self.ollama_client:
                options.append(RoutingDecision(
                    provider=LLMProvider.OLLAMA_MISTRAL,
                    model="mistral:7b-instruct",
                    estimated_cost=Decimal("0.0000"),
                    reasoning="Simple task, Ollama can handle efficiently",
                    complexity=complexity,
                    confidence=0.9
                ))
            
            # Backup: GPT-3.5
            if self.openai_client:
                cost = (estimated_tokens / 1000) * self.pricing[LLMProvider.OPENAI_GPT_35]
                options.append(RoutingDecision(
                    provider=LLMProvider.OPENAI_GPT_35,
                    model="gpt-3.5-turbo",
                    estimated_cost=cost,
                    reasoning="Backup for simple task",
                    complexity=complexity,
                    confidence=0.8
                ))
        
        elif complexity == ComplexityLevel.MEDIUM:
            if preferred_quality == "fast" and self.ollama_client:
                # Try Ollama first for speed
                options.append(RoutingDecision(
                    provider=LLMProvider.OLLAMA_MISTRAL,
                    model="mistral:7b-instruct", 
                    estimated_cost=Decimal("0.0000"),
                    reasoning="Fast processing requested, Ollama is instant",
                    complexity=complexity,
                    confidence=0.7
                ))
            
            # GPT-3.5 is sweet spot for medium tasks
            if self.openai_client:
                cost = (estimated_tokens / 1000) * self.pricing[LLMProvider.OPENAI_GPT_35]
                options.append(RoutingDecision(
                    provider=LLMProvider.OPENAI_GPT_35,
                    model="gpt-3.5-turbo",
                    estimated_cost=cost,
                    reasoning="Good balance of cost and capability for medium tasks",
                    complexity=complexity,
                    confidence=0.9
                ))
        
        elif complexity == ComplexityLevel.COMPLEX:
            # GPT-4 for complex reasoning
            if self.openai_client:
                cost = (estimated_tokens / 1000) * self.pricing[LLMProvider.OPENAI_GPT_4]
                options.append(RoutingDecision(
                    provider=LLMProvider.OPENAI_GPT_4,
                    model="gpt-4",
                    estimated_cost=cost,
                    reasoning="Complex reasoning requires GPT-4 capabilities",
                    complexity=complexity,
                    confidence=0.95
                ))
            
            # Claude as alternative
            if self.anthropic_client:
                cost = (estimated_tokens / 1000) * self.pricing[LLMProvider.ANTHROPIC_CLAUDE]
                options.append(RoutingDecision(
                    provider=LLMProvider.ANTHROPIC_CLAUDE,
                    model="claude-3-haiku-20240307",
                    estimated_cost=cost,
                    reasoning="Claude alternative for complex reasoning",
                    complexity=complexity,
                    confidence=0.9
                ))
        
        return options
    
    def _create_fallback_option(self, complexity: ComplexityLevel, estimated_tokens: float) -> RoutingDecision:
        """Create fallback option when no suitable routes found"""
        if self.ollama_client:
            return RoutingDecision(
                provider=LLMProvider.OLLAMA_MISTRAL,
                model="mistral:7b-instruct",
                estimated_cost=Decimal("0.0000"),
                reasoning="Fallback to free local model",
                complexity=complexity,
                confidence=0.5
            )
        else:
            raise Exception("No available LLM providers!")
    
    def execute_request(self, decision: RoutingDecision, prompt: str, **kwargs) -> ExecutionResult:
        """
        🚀 Execute the LLM request using the routed provider
        
        Args:
            decision: Routing decision from route_request()
            prompt: The actual prompt to execute
            **kwargs: Additional parameters for the LLM
            
        Returns:
            ExecutionResult: Result with tracking data
        """
        start_time = time.time()
        
        try:
            if decision.provider == LLMProvider.OLLAMA_MISTRAL:
                result = self._execute_ollama(decision.model, prompt, **kwargs)
            elif decision.provider == LLMProvider.OPENAI_GPT_35:
                result = self._execute_openai(decision.model, prompt, **kwargs)
            elif decision.provider == LLMProvider.OPENAI_GPT_4:
                result = self._execute_openai(decision.model, prompt, **kwargs)
            elif decision.provider == LLMProvider.ANTHROPIC_CLAUDE:
                result = self._execute_anthropic(decision.model, prompt, **kwargs)
            else:
                raise ValueError(f"Unknown provider: {decision.provider}")
            
            duration = time.time() - start_time
            
            # Calculate actual cost
            actual_cost = (result['tokens'] / 1000) * self.pricing[decision.provider]
            
            return ExecutionResult(
                content=result['content'],
                provider=decision.provider,
                actual_tokens=result['tokens'],
                actual_cost=actual_cost,
                duration_seconds=duration,
                success=True
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"LLM execution failed: {e}")
            
            return ExecutionResult(
                content="",
                provider=decision.provider,
                actual_tokens=0,
                actual_cost=Decimal("0.0000"),
                duration_seconds=duration,
                success=False,
                error=str(e)
            )
    
    def _execute_ollama(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute request using Ollama (FREE!)"""
        response = self.ollama_client.post(
            '/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'options': kwargs.get('options', {'temperature': 0.7})
            },
            timeout=10.0
        )
        
        response.raise_for_status() # Raise an exception for HTTP errors
        
        # Estimate tokens (Ollama doesn't provide exact count)
        estimated_tokens = len(response.json()['response'].split()) * 1.3
        
        return {
            'content': response.json()['response'],
            'tokens': int(estimated_tokens)
        }
    
    def _execute_openai(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute request using OpenAI"""
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 2000)
        )
        
        return {
            'content': response.choices[0].message.content,
            'tokens': response.usage.total_tokens
        }
    
    def _execute_anthropic(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute request using Anthropic Claude"""
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=kwargs.get('max_tokens', 2000),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get('temperature', 0.7)
        )
        
        return {
            'content': response.content[0].text,
            'tokens': response.usage.input_tokens + response.usage.output_tokens
        }


# Global router instance
_router_instance = None

def get_intelligent_router() -> IntelligentLLMRouter:
    """Get singleton instance of the intelligent router"""
    global _router_instance
    if _router_instance is None:
        _router_instance = IntelligentLLMRouter()
    return _router_instance 