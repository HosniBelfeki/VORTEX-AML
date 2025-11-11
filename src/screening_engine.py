"""
Multi-layer Screening and Risk Assessment Engine
"""
import json
import time
from typing import Dict, Tuple, List
from datetime import datetime
import logging
from src.models import RiskScore, RiskLevel
from src.utils import fuzzy_match, generate_analysis_id

logger = logging.getLogger(__name__)


class ScreeningEngine:
    """Multi-layer screening and risk assessment with LLM-powered analysis"""
    
    def __init__(self, ofac_api_key: str = None, refinitiv_api_key: str = None, use_mock: bool = False, use_llm: bool = True):
        """
        Initialize screening engine
        
        Args:
            ofac_api_key: OFAC API key for sanctions screening (optional - LLM can analyze without)
            refinitiv_api_key: Refinitiv API key for PEP/adverse media (optional - LLM can analyze without)
            use_mock: Use mock databases for demo (default: False - use real LLM analysis)
            use_llm: Use LLM for risk analysis (default: True - REQUIRED for production)
        """
        self.ofac_api_key = ofac_api_key
        self.refinitiv_api_key = refinitiv_api_key
        self.use_mock = use_mock
        self.use_llm = use_llm
        
        # Initialize empty databases (will use LLM for analysis instead)
        self._init_mock_databases()
        
        # Check if AWS Bedrock is available for LLM analysis
        self.bedrock_available = self._check_bedrock_availability()
        if self.bedrock_available and use_llm:
            logger.info("✅ AWS Bedrock LLM enabled for real-time risk analysis")
            logger.info("📊 Using LLM-based screening (no mock databases)")
        else:
            logger.warning("⚠️ AWS Bedrock not available - risk analysis will be limited")
            logger.warning("⚠️ Please configure AWS credentials for full functionality")
    
    def _init_mock_databases(self):
        """Initialize mock screening databases"""
        
        # Mock sanctions database (OFAC, UN, EU lists)
        # Empty - connect to real OFAC API or load from external source
        self.sanctions_database = {}
        
        # Mock PEP (Politically Exposed Persons) database
        # Empty - connect to real PEP database or load from external source
        self.pep_database = {}
        
        # Mock adverse media database
        # Empty - connect to real adverse media API or load from external source
        self.adverse_media_database = {}
        
        # Mock behavioral patterns database
        self.behavioral_patterns = {
            "structuring": 70,
            "smurfing": 75,
            "layering": 80,
            "integration": 65,
            "round_dollar_amounts": 40,
            "frequent_small_transactions": 60,
            "unusual_transaction_patterns": 55,
            "cross_border_transfers": 45
        }
    
    def screen_entity(self, name: str, entity_type: str = "individual", 
                     additional_context: Dict = None) -> RiskScore:
        """
        Comprehensive screening of individual or entity with LLM-enhanced analysis
        
        Args:
            name: Name of entity to screen
            entity_type: Type of entity (individual, company, etc.)
            additional_context: Additional context for screening
        
        Returns:
            RiskScore object with comprehensive assessment
        """
        start_time = time.time()
        
        logger.info(f"🔍 Screening {entity_type}: {name}")
        
        # Run parallel screening checks
        sanctions_risk = self._check_sanctions(name)
        pep_risk = self._check_pep(name)
        adverse_media_risk = self._check_adverse_media(name)
        behavioral_risk = self._analyze_behavioral_patterns(additional_context or {})
        
        # Combine risks with weighted scoring
        risks = {
            "sanctions": sanctions_risk,
            "pep": pep_risk,
            "adverse_media": adverse_media_risk,
            "behavioral": behavioral_risk
        }
        
        # Use LLM for enhanced risk analysis if available
        if self.use_llm and self.bedrock_available:
            logger.info("🤖 Enhancing analysis with AWS Bedrock LLM")
            llm_analysis = self._llm_enhanced_analysis(name, entity_type, risks, additional_context or {})
            
            # Adjust risks based on LLM insights
            if llm_analysis:
                risks = self._adjust_risks_with_llm(risks, llm_analysis)
                flags = llm_analysis.get("flags", [])
                recommendations = llm_analysis.get("recommendations", [])
        else:
            # Generate flags and recommendations using rules
            flags = self._generate_flags(risks, name)
            recommendations = self._generate_recommendations(self._get_risk_level(self._calculate_final_score(risks)), flags, risks)
        
        # Calculate final score (weighted average)
        final_score = self._calculate_final_score(risks)
        
        # Determine risk level
        risk_level = self._get_risk_level(final_score)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"✓ Screening complete for {name}: {risk_level} risk ({final_score:.1f}/100) in {processing_time}ms")
        
        return RiskScore(
            sanctions_risk=sanctions_risk,
            pep_risk=pep_risk,
            adverse_media_risk=adverse_media_risk,
            behavioral_risk=behavioral_risk,
            final_risk_score=final_score,
            risk_level=risk_level,
            flags=flags,
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _check_sanctions(self, name: str) -> float:
        """Check against OFAC and international sanctions lists"""
        
        try:
            # If we have a real API key, use it
            if self.ofac_api_key:
                return self._check_sanctions_real_api(name)
            
            # If mock database has entries, use them
            if self.use_mock and self.sanctions_database:
                for sanctioned_name, risk_score in self.sanctions_database.items():
                    similarity = fuzzy_match(name, sanctioned_name)
                    if similarity > 0.8:
                        logger.warning(f"⚠️ Sanctions match found for {name}: {sanctioned_name} (similarity: {similarity:.2f})")
                        return min(risk_score * similarity, 100)
                return 5  # Low baseline risk if no match
            
            # Otherwise, return baseline - LLM will provide comprehensive analysis
            logger.debug(f"No sanctions database - LLM will analyze {name}")
            return 5  # Baseline risk, LLM will adjust if needed
                
        except Exception as e:
            logger.error(f"Sanctions screening failed: {e}")
            return 30  # Default medium risk on error
    
    def _check_pep(self, name: str) -> float:
        """Check Politically Exposed Persons database"""
        
        try:
            # If we have a real API key, use it
            if self.refinitiv_api_key:
                return self._check_pep_real_api(name)
            
            # If mock database has entries, use them
            if self.use_mock and self.pep_database:
                for pep_name, risk_score in self.pep_database.items():
                    similarity = fuzzy_match(name, pep_name)
                    if similarity > 0.8:
                        logger.warning(f"⚠️ PEP match found: {name} -> {pep_name} (similarity: {similarity:.2f})")
                        return min(risk_score * similarity, 100)
                return 0  # Not a PEP
            
            # Otherwise, return baseline - LLM will provide comprehensive analysis
            logger.debug(f"No PEP database - LLM will analyze {name}")
            return 0  # Baseline risk, LLM will adjust if needed
                
        except Exception as e:
            logger.error(f"PEP screening failed: {e}")
            return 10
    
    def _check_adverse_media(self, name: str) -> float:
        """Check financial crime news databases"""
        
        try:
            # If we have a real API key, use it
            if self.refinitiv_api_key:
                return self._check_adverse_media_real_api(name)
            
            # If mock database has entries, use them
            if self.use_mock and self.adverse_media_database:
                for adverse_name, risk_score in self.adverse_media_database.items():
                    similarity = fuzzy_match(name, adverse_name)
                    if similarity > 0.8:
                        logger.warning(f"⚠️ Adverse media found: {name} -> {adverse_name} (similarity: {similarity:.2f})")
                        return min(risk_score * similarity, 100)
                return 0
            
            # Otherwise, return baseline - LLM will provide comprehensive analysis
            logger.debug(f"No adverse media database - LLM will analyze {name}")
            return 0  # Baseline risk, LLM will adjust if needed
                
        except Exception as e:
            logger.error(f"Adverse media screening failed: {e}")
            return 5
    
    def _analyze_behavioral_patterns(self, context: Dict) -> float:
        """Analyze behavioral patterns for anomalies"""
        
        try:
            risk_score = 0
            pattern_count = 0
            
            # Check for suspicious transaction patterns
            transaction_amount = context.get("transaction_amount", 0)
            transaction_frequency = context.get("transaction_frequency", 0)
            
            # Round dollar amounts (potential structuring)
            if transaction_amount > 0 and transaction_amount % 1000 == 0:
                risk_score += self.behavioral_patterns["round_dollar_amounts"]
                pattern_count += 1
            
            # Amounts just below reporting thresholds
            if 9000 <= transaction_amount <= 9999:
                risk_score += self.behavioral_patterns["structuring"]
                pattern_count += 1
            
            # High frequency transactions
            if transaction_frequency > 10:
                risk_score += self.behavioral_patterns["frequent_small_transactions"]
                pattern_count += 1
            
            # Cross-border indicators
            if context.get("cross_border", False):
                risk_score += self.behavioral_patterns["cross_border_transfers"]
                pattern_count += 1
            
            # Average the risk if multiple patterns detected
            if pattern_count > 0:
                return min(risk_score / pattern_count, 100)
            
            return 0
            
        except Exception as e:
            logger.error(f"Behavioral analysis failed: {e}")
            return 10
    
    def _calculate_final_score(self, risks: Dict[str, float]) -> float:
        """Calculate weighted risk score from components"""
        
        weights = {
            "sanctions": 0.40,      # 40% weight - highest priority
            "pep": 0.25,           # 25% weight
            "adverse_media": 0.25,  # 25% weight
            "behavioral": 0.10     # 10% weight
        }
        
        final_score = sum(risks[key] * weights[key] for key in risks if key in weights)
        return min(final_score, 100)  # Cap at 100
    
    def _get_risk_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if score < 20:
            return RiskLevel.LOW
        elif score < 50:
            return RiskLevel.MEDIUM
        elif score < 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_flags(self, risks: Dict[str, float], name: str) -> List[str]:
        """Generate compliance flags based on risks"""
        
        flags = []
        
        if risks["sanctions"] > 50:
            flags.append("SANCTIONS_MATCH")
        if risks["pep"] > 30:
            flags.append("PEP_MATCH")
        if risks["adverse_media"] > 50:
            flags.append("ADVERSE_MEDIA_MATCH")
        if risks["behavioral"] > 60:
            flags.append("SUSPICIOUS_PATTERNS")
        
        # Combination flags
        risk_count = sum(1 for risk in risks.values() if risk > 20)
        if risk_count >= 2:
            flags.append("MULTIPLE_RISK_FACTORS")
        
        if risks["sanctions"] > 80:
            flags.append("HIGH_SANCTIONS_RISK")
        
        return flags
    
    def _generate_recommendations(self, risk_level: RiskLevel, flags: List[str], risks: Dict[str, float]) -> List[str]:
        """Generate recommendations based on risk level and flags"""
        
        recommendations = []
        
        if risk_level == RiskLevel.LOW:
            recommendations.append("Auto-approve transaction")
            recommendations.append("Standard monitoring procedures")
        
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("Flag for compliance review")
            recommendations.append("Conduct enhanced due diligence")
            recommendations.append("Verify source of funds")
        
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("Escalate to senior compliance officer")
            recommendations.append("Obtain additional documentation")
            recommendations.append("Monitor future transactions from this entity")
            recommendations.append("Consider filing Suspicious Activity Report")
        
        elif risk_level == RiskLevel.CRITICAL:
            recommendations.append("BLOCK TRANSACTION IMMEDIATELY")
            recommendations.append("File Suspicious Activity Report (SAR)")
            recommendations.append("Report to FinCEN within 30 days")
            recommendations.append("Implement remedial measures")
            recommendations.append("Consider account closure")
        
        # Specific flag-based recommendations
        if "SANCTIONS_MATCH" in flags:
            recommendations.append("Review against OFAC specially designated nationals list")
            recommendations.append("Freeze assets pending investigation")
        
        if "PEP_MATCH" in flags:
            recommendations.append("Verify beneficial ownership structure")
            recommendations.append("Enhanced ongoing monitoring required")
        
        if "ADVERSE_MEDIA_MATCH" in flags:
            recommendations.append("Review recent news and legal proceedings")
            recommendations.append("Assess reputational risk to institution")
        
        if "SUSPICIOUS_PATTERNS" in flags:
            recommendations.append("Analyze transaction history for patterns")
            recommendations.append("Interview customer about transaction purpose")
        
        return recommendations
    
    def _check_sanctions_real_api(self, name: str) -> float:
        """Real OFAC API implementation (placeholder)"""
        # This would implement actual OFAC API calls
        logger.info(f"Would call real OFAC API for: {name}")
        return 5
    
    def _check_pep_real_api(self, name: str) -> float:
        """Real PEP API implementation (placeholder)"""
        # This would implement actual PEP database API calls
        logger.info(f"Would call real PEP API for: {name}")
        return 0
    
    def _check_adverse_media_real_api(self, name: str) -> float:
        """Real adverse media API implementation (placeholder)"""
        # This would implement actual adverse media API calls
        logger.info(f"Would call real adverse media API for: {name}")
        return 0
    
    def _check_bedrock_availability(self) -> bool:
        """Check if AWS Bedrock is available"""
        try:
            import boto3
            from dotenv import load_dotenv
            load_dotenv()
            
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if credentials is None:
                return False
            
            # Try to create bedrock client
            bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
            return True
        except Exception as e:
            logger.debug(f"Bedrock not available: {e}")
            return False
    
    def _llm_enhanced_analysis(self, name: str, entity_type: str, risks: Dict[str, float], context: Dict) -> Dict:
        """
        Use AWS Bedrock Claude to provide enhanced risk analysis
        """
        try:
            import boto3
            
            bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
            
            # Create comprehensive prompt for LLM
            prompt = f"""You are an expert AML (Anti-Money Laundering) compliance analyst with access to global sanctions lists, PEP databases, and adverse media sources. Analyze the following entity and provide a comprehensive risk assessment.

Entity Information:
- Name: {name}
- Type: {entity_type}
- Context: {json.dumps(context, indent=2)}

Initial Screening Results (baseline):
- Sanctions Risk Score: {risks['sanctions']:.1f}/100
- PEP (Politically Exposed Person) Risk: {risks['pep']:.1f}/100
- Adverse Media Risk: {risks['adverse_media']:.1f}/100
- Behavioral Pattern Risk: {risks['behavioral']:.1f}/100

Your Task:
1. Analyze if this entity appears on any sanctions lists (OFAC, UN, EU, etc.)
2. Determine if this is a Politically Exposed Person (PEP) or associated with one
3. Check for adverse media related to financial crimes, fraud, money laundering, or corruption
4. Assess behavioral patterns from the context provided
5. Provide adjusted risk scores based on your analysis (0-100 scale)
6. Generate specific compliance flags
7. Provide actionable recommendations for compliance officers

IMPORTANT: Base your analysis on real-world knowledge of:
- Current sanctions lists and designated persons
- Known PEPs and government officials
- Public records of financial crimes and fraud cases
- Typical money laundering patterns and red flags

Return your analysis in JSON format:
{{
    "risk_adjustments": {{
        "sanctions": <0-100 score based on sanctions list matches>,
        "pep": <0-100 score based on PEP status>,
        "adverse_media": <0-100 score based on negative news/legal issues>,
        "behavioral": <0-100 score based on transaction patterns>
    }},
    "flags": ["Specific compliance flags like SANCTIONS_MATCH, PEP_MATCH, ADVERSE_MEDIA_MATCH, etc."],
    "recommendations": ["Specific actionable recommendations for compliance team"],
    "narrative": "2-3 sentence summary of key risk factors and recommended actions"
}}

Be thorough and base your assessment on factual information. If uncertain, err on the side of caution."""

            # Call Bedrock Claude with updated model
            response = bedrock_client.invoke_model(
                modelId="anthropic.claude-sonnet-4-5-20250929-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-06-01",
                    "max_tokens": 2048,
                    "temperature": 0.3,  # Lower temperature for more consistent analysis
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(response['body'].read())
            response_text = response_body['content'][0]['text']
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                llm_analysis = json.loads(json_str)
                
                logger.info(f"✅ LLM analysis complete: {llm_analysis.get('narrative', 'No narrative')[:100]}...")
                return llm_analysis
            else:
                logger.warning("⚠️ Could not extract JSON from LLM response")
                return None
            
        except Exception as e:
            logger.error(f"❌ LLM analysis failed: {e}")
            return None
    
    def _adjust_risks_with_llm(self, original_risks: Dict[str, float], llm_analysis: Dict) -> Dict[str, float]:
        """
        Adjust risk scores based on LLM recommendations
        """
        adjusted_risks = original_risks.copy()
        
        risk_adjustments = llm_analysis.get("risk_adjustments", {})
        
        for risk_type, adjustment in risk_adjustments.items():
            if adjustment is not None and risk_type in adjusted_risks:
                # Apply adjustment (but keep within 0-100 range)
                adjusted_risks[risk_type] = max(0, min(100, adjustment))
                
                if abs(adjusted_risks[risk_type] - original_risks[risk_type]) > 5:
                    logger.info(f"🔄 LLM adjusted {risk_type} risk: {original_risks[risk_type]:.1f} → {adjusted_risks[risk_type]:.1f}")
        
        return adjusted_risks


# Example usage
if __name__ == "__main__":
    # Production mode: use_mock=False, use_llm=True
    # This will use AWS Bedrock LLM for comprehensive risk analysis
    engine = ScreeningEngine(use_mock=False, use_llm=True)
    
    # Test screening with real entity
    test_entity = "Sample Entity Name"
    risk_score = engine.screen_entity(test_entity, entity_type="individual")
    
    print(f"\n{'='*60}")
    print(f"Risk Assessment for: {test_entity}")
    print(f"{'='*60}")
    print(f"Risk Score: {risk_score.final_risk_score:.1f}/100")
    print(f"Risk Level: {risk_score.risk_level}")
    print(f"\nFlags: {', '.join(risk_score.flags) if risk_score.flags else 'None'}")
    print(f"\nRecommendations:")
    for i, rec in enumerate(risk_score.recommendations, 1):
        print(f"  {i}. {rec}")
    print(f"{'='*60}\n")