"""
Advanced User Experience Module

This module implements Phase 3 of the Bot Logic Enhancement: Advanced User Experience.
It focuses on conversational interface improvements, workflow intelligence, and enhanced
user interaction patterns.

Key Components:
- ConversationalInterface: Natural language interaction layer
- WorkflowIntelligence: Pattern recognition and workflow optimization  
- UserExperienceEnhancer: Proactive guidance and experience optimization
- SessionManager: Advanced session and state management
"""

import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from .context_manager import ConversationContext, OperationInfo
from .response_intelligence import ResponseIntelligence, ResponseContext
from .exceptions import WorkspaceAIError

logger = logging.getLogger(__name__)


class InteractionMode(Enum):
    """Different modes of user interaction"""
    EXPLORATORY = "exploratory"  # User is exploring/learning
    FOCUSED = "focused"          # User has clear goals
    COLLABORATIVE = "collaborative"  # Multi-step workflow
    TROUBLESHOOTING = "troubleshooting"  # Problem-solving mode


class UserSkillLevel(Enum):
    """User skill level assessment"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class UserProfile:
    """User profile for personalized experience"""
    skill_level: UserSkillLevel = UserSkillLevel.INTERMEDIATE
    preferred_interaction_mode: InteractionMode = InteractionMode.FOCUSED
    preferred_verbosity: str = "balanced"  # "minimal", "balanced", "verbose"
    tool_preferences: Dict[str, float] = field(default_factory=dict)
    domain_expertise: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_skill_assessment(self, interaction_data: Dict[str, Any]):
        """Update skill level based on interaction patterns"""
        success_rate = interaction_data.get("success_rate", 0.5)
        complexity_handled = interaction_data.get("avg_complexity", 0.5)
        
        if success_rate > 0.9 and complexity_handled > 0.8:
            if self.skill_level == UserSkillLevel.BEGINNER:
                self.skill_level = UserSkillLevel.INTERMEDIATE
            elif self.skill_level == UserSkillLevel.INTERMEDIATE:
                self.skill_level = UserSkillLevel.ADVANCED
        elif success_rate < 0.6:
            if self.skill_level == UserSkillLevel.ADVANCED:
                self.skill_level = UserSkillLevel.INTERMEDIATE
            elif self.skill_level == UserSkillLevel.INTERMEDIATE:
                self.skill_level = UserSkillLevel.BEGINNER


@dataclass  
class ConversationState:
    """Current state of the conversation"""
    current_task: Optional[str] = None
    active_context: Optional[str] = None
    pending_clarifications: List[str] = field(default_factory=list)
    workflow_stage: str = "initial"
    user_mood: str = "neutral"  # "frustrated", "confident", "exploratory"
    interaction_mode: InteractionMode = InteractionMode.FOCUSED
    last_activity: datetime = field(default_factory=datetime.now)


class ConversationalInterface:
    """
    Natural language interaction layer that adapts to user communication style
    and provides conversational responses with appropriate tone and verbosity.
    """
    
    def __init__(self, context: ConversationContext, response_intelligence: ResponseIntelligence):
        self.context = context
        self.response_intelligence = response_intelligence
        self.user_profile = UserProfile()
        self.conversation_state = ConversationState()
        self.interaction_patterns = {}
        
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input with conversational awareness
        
        Args:
            user_input: Raw user input
            
        Returns:
            Processed input with conversational context
        """
        try:
            # Analyze communication style
            communication_analysis = self._analyze_communication_style(user_input)
            
            # Detect conversation state changes
            state_changes = self._detect_state_changes(user_input)
            
            # Identify interaction mode
            interaction_mode = self._identify_interaction_mode(user_input, communication_analysis)
            
            # Update conversation state
            self._update_conversation_state(user_input, state_changes, interaction_mode)
            
            # Generate conversational metadata
            conversational_context = {
                "communication_style": communication_analysis,
                "interaction_mode": interaction_mode,
                "conversation_state": self.conversation_state,
                "user_profile": self.user_profile,
                "processing_timestamp": datetime.now().isoformat()
            }
            
            return {
                "processed_input": user_input,
                "conversational_context": conversational_context,
                "suggested_tone": self._suggest_response_tone(communication_analysis),
                "verbosity_level": self._determine_verbosity_level(),
                "needs_clarification": len(self.conversation_state.pending_clarifications) > 0
            }
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return {
                "processed_input": user_input,
                "conversational_context": {},
                "error": str(e)
            }
    
    def generate_conversational_response(
        self, 
        operation_result: Dict[str, Any], 
        response_context: ResponseContext
    ) -> str:
        """
        Generate conversational response adapted to user preferences
        
        Args:
            operation_result: Result of the operation
            response_context: Context for response generation
            
        Returns:
            Conversational response string
        """
        try:
            # Get base intelligent response
            base_response = self.response_intelligence.generate_contextual_response(response_context)
            
            # Adapt tone and style based on user profile and conversation state
            adapted_response = self._adapt_response_style(base_response, response_context)
            
            # Add conversational elements based on context
            enhanced_response = self._add_conversational_elements(adapted_response, operation_result)
            
            # Include proactive guidance if appropriate
            final_response = self._add_proactive_guidance(enhanced_response, operation_result)
            
            # Update interaction history
            self._record_interaction(response_context.user_input, final_response, operation_result)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error generating conversational response: {e}")
            # Fallback to basic response
            return "I've completed your request."
    
    def _analyze_communication_style(self, user_input: str) -> Dict[str, Any]:
        """Analyze user's communication style"""
        analysis = {
            "formality": "neutral",
            "directness": "moderate",
            "detail_preference": "balanced",
            "urgency": "normal",
            "confidence": "moderate"
        }
        
        input_lower = user_input.lower()
        
        # Analyze formality
        formal_indicators = ["please", "could you", "would you", "kindly"]
        informal_indicators = ["hey", "yo", "sup", "can you just"]
        
        if any(indicator in input_lower for indicator in formal_indicators):
            analysis["formality"] = "formal"
        elif any(indicator in input_lower for indicator in informal_indicators):
            analysis["formality"] = "informal"
        
        # Analyze directness
        direct_indicators = ["do this", "make", "create", "run", "execute"]
        indirect_indicators = ["maybe", "perhaps", "could", "might"]
        
        if any(indicator in input_lower for indicator in direct_indicators):
            analysis["directness"] = "direct"
        elif any(indicator in input_lower for indicator in indirect_indicators):
            analysis["directness"] = "indirect"
        
        # Analyze urgency
        urgent_indicators = ["quickly", "asap", "urgent", "now", "immediately"]
        if any(indicator in input_lower for indicator in urgent_indicators):
            analysis["urgency"] = "high"
        
        # Analyze detail preference
        if len(user_input.split()) > 20 or "explain" in input_lower or "details" in input_lower:
            analysis["detail_preference"] = "high"
        elif len(user_input.split()) < 5:
            analysis["detail_preference"] = "low"
        
        return analysis
    
    def _detect_state_changes(self, user_input: str) -> List[str]:
        """Detect changes in conversation state"""
        changes = []
        input_lower = user_input.lower()
        
        # Detect frustration
        frustration_indicators = ["not working", "failed", "error", "broken", "frustrated"]
        if any(indicator in input_lower for indicator in frustration_indicators):
            changes.append("frustration_detected")
        
        # Detect task switching
        switch_indicators = ["instead", "actually", "never mind", "change", "different"]
        if any(indicator in input_lower for indicator in switch_indicators):
            changes.append("task_switch")
        
        # Detect exploration mode
        exploration_indicators = ["what can", "how do", "show me", "example", "demo"]
        if any(indicator in input_lower for indicator in exploration_indicators):
            changes.append("exploration_mode")
        
        return changes
    
    def _identify_interaction_mode(self, user_input: str, communication_analysis: Dict[str, Any]) -> InteractionMode:
        """Identify the current interaction mode"""
        input_lower = user_input.lower()
        
        # Check for troubleshooting mode
        if any(word in input_lower for word in ["error", "problem", "not working", "failed", "fix"]):
            return InteractionMode.TROUBLESHOOTING
        
        # Check for exploratory mode
        if any(word in input_lower for word in ["what", "how", "show", "example", "explain"]):
            return InteractionMode.EXPLORATORY
        
        # Check for collaborative mode
        if any(word in input_lower for word in ["we", "us", "together", "step by step", "guide"]):
            return InteractionMode.COLLABORATIVE
        
        # Default to focused mode
        return InteractionMode.FOCUSED
    
    def _update_conversation_state(
        self, 
        user_input: str, 
        state_changes: List[str], 
        interaction_mode: InteractionMode
    ):
        """Update the conversation state"""
        self.conversation_state.interaction_mode = interaction_mode
        self.conversation_state.last_activity = datetime.now()
        
        # Update mood based on state changes
        if "frustration_detected" in state_changes:
            self.conversation_state.user_mood = "frustrated"
        elif "exploration_mode" in state_changes:
            self.conversation_state.user_mood = "exploratory"
        else:
            self.conversation_state.user_mood = "confident"
        
        # Handle task switching
        if "task_switch" in state_changes:
            self.conversation_state.current_task = None
            self.conversation_state.workflow_stage = "initial"
    
    def _suggest_response_tone(self, communication_analysis: Dict[str, Any]) -> str:
        """Suggest appropriate response tone"""
        if self.conversation_state.user_mood == "frustrated":
            return "supportive"
        elif communication_analysis["formality"] == "formal":
            return "professional"
        elif communication_analysis["formality"] == "informal":
            return "friendly"
        else:
            return "balanced"
    
    def _determine_verbosity_level(self) -> str:
        """Determine appropriate verbosity level"""
        # Check user preference first
        if self.user_profile.preferred_verbosity != "balanced":
            return self.user_profile.preferred_verbosity
        
        # Adapt based on interaction mode and skill level
        if self.conversation_state.interaction_mode == InteractionMode.EXPLORATORY:
            return "verbose"
        elif self.user_profile.skill_level == UserSkillLevel.EXPERT:
            return "minimal"
        else:
            return "balanced"
    
    def _adapt_response_style(self, base_response: str, response_context: ResponseContext) -> str:
        """Adapt response style based on user preferences"""
        # For now, return base response - can be enhanced with style adaptation
        return base_response
    
    def _add_conversational_elements(self, response: str, operation_result: Dict[str, Any]) -> str:
        """Add conversational elements to response"""
        # Add empathy for failed operations
        if not operation_result.get("success", True) and self.conversation_state.user_mood == "frustrated":
            response = "I understand this can be frustrating. " + response
        
        # Add encouragement for exploratory users
        if self.conversation_state.interaction_mode == InteractionMode.EXPLORATORY:
            response += "\n\n🌟 Feel free to ask if you'd like to explore more options!"
        
        return response
    
    def _add_proactive_guidance(self, response: str, operation_result: Dict[str, Any]) -> str:
        """Add proactive guidance based on context"""
        # Add workflow suggestions for collaborative mode
        if self.conversation_state.interaction_mode == InteractionMode.COLLABORATIVE:
            response += "\n\n🤝 What would you like to work on next?"
        
        return response
    
    def _record_interaction(self, user_input: str, response: str, operation_result: Dict[str, Any]):
        """Record interaction for learning and adaptation"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input[:100],  # Truncate for privacy
            "response_length": len(response),
            "operation_success": operation_result.get("success", True),
            "interaction_mode": self.conversation_state.interaction_mode.value,
            "user_mood": self.conversation_state.user_mood
        }
        
        self.user_profile.interaction_history.append(interaction)
        
        # Keep only recent history (last 50 interactions)
        if len(self.user_profile.interaction_history) > 50:
            self.user_profile.interaction_history = self.user_profile.interaction_history[-50:]


class WorkflowIntelligence:
    """
    Pattern recognition and workflow optimization for enhanced user experience.
    Learns from user patterns to suggest improvements and automate common workflows.
    """
    
    def __init__(self, context: ConversationContext):
        self.context = context
        self.workflow_patterns = {}
        self.optimization_suggestions = []
        
    def analyze_workflow_patterns(self) -> Dict[str, Any]:
        """
        Analyze user workflow patterns to identify optimization opportunities
        
        Returns:
            Analysis of workflow patterns and suggestions
        """
        try:
            recent_operations = self.context.get_recent_operations(20)
            
            # Identify common operation sequences
            sequences = self._identify_operation_sequences(recent_operations)
            
            # Find repetitive patterns
            repetitive_patterns = self._find_repetitive_patterns(recent_operations)
            
            # Analyze efficiency metrics
            efficiency_metrics = self._calculate_efficiency_metrics(recent_operations)
            
            # Generate optimization suggestions
            optimizations = self._generate_optimization_suggestions(sequences, repetitive_patterns)
            
            return {
                "operation_sequences": sequences,
                "repetitive_patterns": repetitive_patterns,
                "efficiency_metrics": efficiency_metrics,
                "optimization_suggestions": optimizations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing workflow patterns: {e}")
            return {"error": str(e)}
    
    def suggest_workflow_automation(self, current_task: str) -> Optional[Dict[str, Any]]:
        """
        Suggest automation opportunities for current workflow
        
        Args:
            current_task: Description of current task
            
        Returns:
            Automation suggestions if applicable
        """
        try:
            # Check if current task matches known patterns
            similar_patterns = self._find_similar_workflow_patterns(current_task)
            
            if similar_patterns:
                automation_suggestion = {
                    "automation_type": "workflow_template",
                    "confidence": self._calculate_automation_confidence(similar_patterns),
                    "suggested_steps": self._generate_automation_steps(similar_patterns),
                    "estimated_time_saved": self._estimate_time_savings(similar_patterns),
                    "risk_level": "low"  # Conservative approach
                }
                
                return automation_suggestion
            
            return None
            
        except Exception as e:
            logger.error(f"Error suggesting workflow automation: {e}")
            return None
    
    def _identify_operation_sequences(self, operations: List[OperationInfo]) -> List[Dict[str, Any]]:
        """Identify common sequences of operations"""
        sequences = []
        
        # Look for sequences of 2-5 operations
        for seq_length in range(2, 6):
            for i in range(len(operations) - seq_length + 1):
                sequence = operations[i:i + seq_length]
                pattern = [op.tool_name for op in sequence]
                
                # Check if this pattern appears multiple times
                pattern_count = self._count_pattern_occurrences(operations, pattern)
                if pattern_count >= 2:
                    # Calculate duration as time between operations (rough estimate)
                    if i < len(operations) - 1:
                        duration = operations[i + 1].timestamp - operations[i].timestamp
                    else:
                        duration = 0.5  # Default duration for last operation
                    
                    sequences.append({
                        "pattern": pattern,
                        "frequency": pattern_count,
                        "avg_duration": duration,
                        "success_rate": sum(1 for op in sequence if op.success) / len(sequence)
                    })        # Sort by frequency
        sequences.sort(key=lambda x: x["frequency"], reverse=True)
        return sequences[:10]  # Top 10 sequences
    
    def _find_repetitive_patterns(self, operations: List[OperationInfo]) -> List[Dict[str, Any]]:
        """Find repetitive patterns that could be optimized"""
        patterns = []
        
        # Group operations by tool
        tool_groups = {}
        for op in operations:
            if op.tool_name not in tool_groups:
                tool_groups[op.tool_name] = []
            tool_groups[op.tool_name].append(op)
        
        # Find tools used repeatedly
        for tool_name, tool_ops in tool_groups.items():
            if len(tool_ops) >= 3:  # Used at least 3 times
                patterns.append({
                    "tool": tool_name,
                    "usage_count": len(tool_ops),
                    "avg_success_rate": sum(1 for op in tool_ops if op.success) / len(tool_ops),
                    "total_time": tool_ops[-1].timestamp - tool_ops[0].timestamp if len(tool_ops) > 1 else 0,
                    "optimization_potential": "high" if len(tool_ops) >= 5 else "medium"
                })
        
        return patterns
    
    def _calculate_efficiency_metrics(self, operations: List[OperationInfo]) -> Dict[str, float]:
        """Calculate efficiency metrics for operations"""
        if not operations:
            return {}
        
        total_operations = len(operations)
        successful_operations = sum(1 for op in operations if op.success)
        
        # Calculate total time as span from first to last operation
        if len(operations) > 1:
            total_time = operations[-1].timestamp - operations[0].timestamp
            avg_time_per_operation = total_time / total_operations if total_operations > 0 else 0
        else:
            total_time = 0
            avg_time_per_operation = 0
        
        return {
            "success_rate": successful_operations / total_operations,
            "avg_execution_time": avg_time_per_operation,
            "total_operations": total_operations,
            "operations_per_minute": total_operations / (total_time / 60) if total_time > 0 else 0,
            "efficiency_score": (successful_operations / total_operations) * (1 / max(avg_time_per_operation, 0.1))
        }
    
    def _generate_optimization_suggestions(
        self, 
        sequences: List[Dict[str, Any]], 
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on patterns"""
        suggestions = []
        
        # Suggest automation for frequent sequences
        for seq in sequences[:3]:  # Top 3 sequences
            if seq["frequency"] >= 3:
                suggestions.append({
                    "type": "automation",
                    "description": f"Create automation for {' → '.join(seq['pattern'])} sequence",
                    "potential_benefit": f"Used {seq['frequency']} times",
                    "implementation_effort": "medium"
                })
        
        # Suggest optimization for repetitive patterns
        for pattern in patterns[:3]:  # Top 3 patterns
            if pattern["optimization_potential"] == "high":
                suggestions.append({
                    "type": "optimization",
                    "description": f"Optimize repeated use of {pattern['tool']}",
                    "potential_benefit": f"Save time on {pattern['usage_count']} operations",
                    "implementation_effort": "low"
                })
        
        return suggestions
    
    def _count_pattern_occurrences(self, operations: List[OperationInfo], pattern: List[str]) -> int:
        """Count how many times a pattern occurs in operations"""
        count = 0
        for i in range(len(operations) - len(pattern) + 1):
            if [op.tool_name for op in operations[i:i + len(pattern)]] == pattern:
                count += 1
        return count
    
    def _find_similar_workflow_patterns(self, current_task: str) -> List[Dict[str, Any]]:
        """Find workflow patterns similar to current task"""
        # This would use more sophisticated matching in production
        # For now, return empty list as placeholder
        return []
    
    def _calculate_automation_confidence(self, patterns: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for automation suggestion"""
        if not patterns:
            return 0.0
        
        # Simple confidence calculation based on pattern frequency and success rate
        avg_frequency = sum(p.get("frequency", 1) for p in patterns) / len(patterns)
        avg_success = sum(p.get("success_rate", 0.5) for p in patterns) / len(patterns)
        
        return min(0.9, (avg_frequency * 0.1 + avg_success) / 2)
    
    def _generate_automation_steps(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Generate automation steps based on patterns"""
        # Placeholder implementation
        return ["Step 1: Analyze pattern", "Step 2: Create automation", "Step 3: Test automation"]
    
    def _estimate_time_savings(self, patterns: List[Dict[str, Any]]) -> str:
        """Estimate time savings from automation"""
        # Simple estimation based on pattern frequency
        total_frequency = sum(p.get("frequency", 1) for p in patterns)
        if total_frequency >= 10:
            return "High (>5 minutes per day)"
        elif total_frequency >= 5:
            return "Medium (2-5 minutes per day)"
        else:
            return "Low (<2 minutes per day)"


class UserExperienceEnhancer:
    """
    Proactive guidance and experience optimization based on user behavior,
    skill level, and interaction patterns.
    """
    
    def __init__(
        self, 
        conversational_interface: ConversationalInterface,
        workflow_intelligence: WorkflowIntelligence
    ):
        self.conversational_interface = conversational_interface
        self.workflow_intelligence = workflow_intelligence
        self.enhancement_history = []
        
    def enhance_user_experience(self, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide proactive enhancements to user experience
        
        Args:
            current_context: Current user context and state
            
        Returns:
            Experience enhancements and recommendations
        """
        try:
            enhancements = {
                "guidance": self._provide_proactive_guidance(current_context),
                "shortcuts": self._suggest_shortcuts(current_context),
                "learning": self._identify_learning_opportunities(current_context),
                "workflow": self._recommend_workflow_improvements(current_context),
                "personalization": self._suggest_personalization_options(current_context)
            }
            
            # Filter out empty enhancements
            enhancements = {k: v for k, v in enhancements.items() if v}
            
            # Record enhancement suggestions
            self._record_enhancements(enhancements)
            
            return enhancements
            
        except Exception as e:
            logger.error(f"Error enhancing user experience: {e}")
            return {"error": str(e)}
    
    def _provide_proactive_guidance(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Provide proactive guidance based on context"""
        user_profile = self.conversational_interface.user_profile
        conversation_state = self.conversational_interface.conversation_state
        
        guidance = []
        
        # Guidance for beginners
        if user_profile.skill_level == UserSkillLevel.BEGINNER:
            guidance.append({
                "type": "skill_building",
                "message": "💡 Try exploring different commands to build your skills",
                "priority": "medium"
            })
        
        # Guidance for troubleshooting mode
        if conversation_state.interaction_mode == InteractionMode.TROUBLESHOOTING:
            guidance.append({
                "type": "troubleshooting_help",
                "message": "🔧 I can help diagnose the issue. Can you describe what you expected to happen?",
                "priority": "high"
            })
        
        return {"suggestions": guidance} if guidance else None
    
    def _suggest_shortcuts(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Suggest shortcuts and efficiency improvements"""
        workflow_analysis = self.workflow_intelligence.analyze_workflow_patterns()
        shortcuts = []
        
        # Suggest shortcuts for repetitive patterns
        for pattern in workflow_analysis.get("repetitive_patterns", []):
            if pattern["usage_count"] >= 3:
                shortcuts.append({
                    "type": "automation_shortcut",
                    "tool": pattern["tool"],
                    "suggestion": f"Consider creating a shortcut for {pattern['tool']} - you've used it {pattern['usage_count']} times",
                    "time_saved": f"~{pattern['total_time']:.1f}s per use"
                })
        
        return {"shortcuts": shortcuts} if shortcuts else None
    
    def _identify_learning_opportunities(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Identify learning opportunities for skill development"""
        user_profile = self.conversational_interface.user_profile
        opportunities = []
        
        # Suggest advanced features for intermediate users
        if user_profile.skill_level == UserSkillLevel.INTERMEDIATE:
            opportunities.append({
                "type": "feature_exploration",
                "title": "Advanced Features",
                "description": "Ready to explore multi-step workflows and automation?",
                "difficulty": "intermediate"
            })
        
        # Suggest domain-specific learning
        if not user_profile.domain_expertise:
            opportunities.append({
                "type": "domain_learning",
                "title": "Specialize Your Skills",
                "description": "Focus on specific areas like file management, data processing, or automation",
                "difficulty": "beginner"
            })
        
        return {"learning_opportunities": opportunities} if opportunities else None
    
    def _recommend_workflow_improvements(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recommend workflow improvements"""
        automation_suggestion = self.workflow_intelligence.suggest_workflow_automation(
            context.get("current_task", "")
        )
        
        if automation_suggestion:
            return {
                "automation_available": True,
                "suggestion": automation_suggestion,
                "recommendation": "Consider automating this workflow to save time"
            }
        
        return None
    
    def _suggest_personalization_options(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Suggest personalization options"""
        user_profile = self.conversational_interface.user_profile
        suggestions = []
        
        # Suggest verbosity adjustment based on interaction patterns
        if len(user_profile.interaction_history) >= 10:
            recent_interactions = user_profile.interaction_history[-10:]
            avg_response_length = sum(i["response_length"] for i in recent_interactions) / len(recent_interactions)
            
            if avg_response_length > 300 and user_profile.preferred_verbosity != "minimal":
                suggestions.append({
                    "type": "verbosity_adjustment",
                    "suggestion": "Consider switching to more concise responses",
                    "action": "Set verbosity to 'minimal'"
                })
        
        return {"personalization": suggestions} if suggestions else None
    
    def _record_enhancements(self, enhancements: Dict[str, Any]):
        """Record enhancement suggestions for learning"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "enhancements": list(enhancements.keys()),
            "enhancement_count": len(enhancements)
        }
        
        self.enhancement_history.append(record)
        
        # Keep only recent history
        if len(self.enhancement_history) > 100:
            self.enhancement_history = self.enhancement_history[-100:]
