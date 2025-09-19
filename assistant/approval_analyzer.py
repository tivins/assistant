#!/usr/bin/env python3
"""
Approval Analyzer
Uses AI to analyze user responses for command approval.
"""

from typing import List, Dict, Any, Optional
import re


class ApprovalAnalyzer:
    """Analyzes user responses to determine if they approve command execution."""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
    
    def analyze_approval_response(self, response: str) -> bool:
        """
        Analyze if a response means 'yes' or 'no' using AI.
        Returns True for approval, False for rejection.
        """
        # First try simple keyword analysis
        simple_result = self._simple_analysis(response)
        if simple_result is not None:
            return simple_result
        
        # If ambiguous, use AI analysis
        return self._ai_analysis(response)
    
    def _simple_analysis(self, response: str) -> Optional[bool]:
        """Simple keyword-based analysis. Returns None if ambiguous."""
        response_lower = response.lower().strip()
        
        # Clear positive indicators
        positive_patterns = [
            r'\b(yes|oui|y|ok|okay|sure|bien|d\'accord|confirm|execute|go|run|do it)\b',
            r'\b(oui|bien sûr|d\'accord|confirmer|exécuter|lancer)\b',
            r'^[yY]$',  # Just 'y' or 'Y'
            r'^ok$',    # Just 'ok'
        ]
        
        # Clear negative indicators
        negative_patterns = [
            r'\b(no|non|n|cancel|stop|abort|annuler|refuser|ne pas)\b',
            r'\b(non|annuler|refuser|ne pas faire|arrêter)\b',
            r'^[nN]$',  # Just 'n' or 'N'
        ]
        
        # Check for positive patterns
        for pattern in positive_patterns:
            if re.search(pattern, response_lower):
                return True
        
        # Check for negative patterns
        for pattern in negative_patterns:
            if re.search(pattern, response_lower):
                return False
        
        # If no clear patterns found, return None for AI analysis
        return None
    
    def _ai_analysis(self, response: str) -> bool:
        """Use AI to analyze ambiguous responses."""
        try:
            # Create a simple prompt for the AI
            prompt = f"""
Analyze this user response to determine if they are approving or rejecting a command execution request.

User response: "{response}"

Does this response mean "YES" (approve) or "NO" (reject)?
Respond with only "YES" or "NO".
"""
            
            # Get AI response
            messages = [{"role": "user", "content": prompt}]
            ai_response = self.ai_client.get_ai_response(messages)
            
            # Parse AI response
            ai_response_clean = ai_response.strip().upper()
            if "YES" in ai_response_clean:
                return True
            elif "NO" in ai_response_clean:
                return False
            else:
                # If AI response is unclear, default to False for safety
                return False
                
        except Exception as e:
            print(f"Error in AI approval analysis: {e}")
            # Default to False for safety
            return False
    
    def extract_pending_commands(self, conversation_history: List[Dict[str, str]]) -> List[str]:
        """Extract commands that are waiting for approval from conversation history."""
        pending_commands = []
        
        # Look for recent AI responses with [EXECUTE:...] patterns
        for message in reversed(conversation_history[-5:]):  # Check last 5 messages
            if message['role'] == 'assistant':
                commands = self._extract_execute_commands(message['content'])
                if commands:
                    pending_commands.extend(commands)
                    break  # Only get commands from the most recent AI response
        
        return pending_commands
    
    def _extract_execute_commands(self, text: str) -> List[str]:
        """Extract [EXECUTE:command] patterns from text."""
        pattern = r'\[EXECUTE:([^\]]+)\]'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [match.strip() for match in matches]
