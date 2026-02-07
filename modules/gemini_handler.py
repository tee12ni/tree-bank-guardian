"""
Gemini API Handler for Tree Bank Guardian
"""

import google.generativeai as genai
import json
import streamlit as st
from pathlib import Path

def configure_gemini(api_key):
    """Configure Gemini API with provided key"""
    try:
        if not api_key or api_key.strip() == "":
            st.error("API Key cannot be empty")
            return False
        
        if not api_key.startswith("AIza"):
            st.warning("API Key format may be incorrect. Should start with 'AIza'")
        
        genai.configure(api_key=api_key)
        
        # Test the API
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        test_response = model.generate_content("Say hello")
        
        st.session_state.gemini_configured = True
        st.session_state.api_key = api_key
        st.success("✅ Gemini API configured successfully!")
        return True
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg:
            st.error("❌ Invalid API Key. Please check and try again.")
        elif "quota" in error_msg.lower():
            st.error("⚠️ API quota exceeded. Try again later or check billing.")
        else:
            st.error(f"API Error: {error_msg[:100]}")
        return False

class GeminiHandler:
    def __init__(self, prompts_manager=None):
        self.prompts_manager = prompts_manager
        self.configured = False
    
    def analyze_tree_image(self, image, location_info="", use_custom_prompts=True):
        """Analyze tree image using Gemini Vision API"""
        try:
            if not st.session_state.get('gemini_configured', False):
                from .utils import get_mock_analysis_with_custom
                return get_mock_analysis_with_custom(self.prompts_manager)
            
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Prepare custom prompts context
            custom_context = ""
            if use_custom_prompts and self.prompts_manager:
                for species_name, prompt_data in self.prompts_manager.species_prompts.items():
                    custom_context += f"\n{species_name} ({prompt_data.get('scientific_name', '')}): {prompt_data.get('custom_prompt', '')[:100]}..."
            
            prompt = f"""
            คุณเป็นผู้เชี่ยวชาญด้านไม้ยืนต้นของประเทศไทย
            
            ## ข้อมูลเฉพาะสำหรับไม้ไทย (สำหรับใช้เป็น reference):
            {custom_context if custom_context else "ไม่มีข้อมูลเฉพาะสำหรับพันธุ์นี้"}
            
            ## คำสั่งการวิเคราะห์:
            1. ระบุชนิดพันธุ์ไม้จากภาพ (ให้ชื่อภาษาไทยและชื่อวิทยาศาสตร์)
            2. ประเมินสุขภาพ (0-100) พร้อมระบุปัญหาที่พบ
            3. ให้คำแนะนำการดูแลเฉพาะสำหรับพันธุ์นั้นๆ
            4. ประเมินคุณลักษณะทางกายภาพ
            
            ## รูปแบบการตอบกลับ (JSON เท่านั้น):
            {{
                "species": {{
                    "thai_name": "ชื่อภาษาไทย",
                    "scientific_name": "ชื่อวิทยาศาสตร์",
                    "confidence": 0.95,
                    "is_thai_species": true/false
                }},
                "health_assessment": {{
                    "score": 85,
                    "issues": ["รายการปัญหา"],
                    "recommendations": "คำแนะนำการดูแล",
                    "urgency": "low/medium/high"
                }},
                "physical_attributes": {{
                    "height_estimate_m": 0,
                    "age_estimate_years": 0,
                    "canopy_width_m": 0,
                    "trunk_diameter_cm": 0
                }},
                "thai_specific_info": {{
                    "common_in_regions": ["ภาคกลาง", "ภาคเหนือ"],
                    "traditional_uses": ["ไม้ก่อสร้าง", "ผลกินได้"],
                    "cultural_significance": "สูง/ปานกลาง/ต่ำ"
                }}
            }}
            
            ## ข้อมูลเพิ่มเติม:
            สถานที่: {location_info}
            
            **หมายเหตุ**: หากเป็นไม้ไทย โปรดอ้างอิงข้อมูลจาก custom prompts ด้านบน
            """
            
            response = model.generate_content([prompt, image])
            
            # Process response
            response_text = response.text
            json_str = self._extract_json(response_text)
            
            analysis = json.loads(json_str)
            
            # Add custom prompt info if applicable
            if analysis["species"].get("is_thai_species", False) and self.prompts_manager:
                thai_name = analysis["species"]["thai_name"]
                species_prompt = self.prompts_manager.get_prompt_for_species(thai_name)
                
                analysis["custom_prompt_info"] = {
                    "source": "custom_prompts",
                    "carbon_factor": species_prompt.get("carbon_factor", 15.0),
                    "care_tips": species_prompt.get("care_tips", []),
                    "traditional_knowledge": species_prompt.get("custom_prompt", "")
                }
            
            return analysis
            
        except Exception as e:
            st.warning(f"Gemini API error: {str(e)[:100]}")
            from .utils import get_mock_analysis_with_custom
            return get_mock_analysis_with_custom(self.prompts_manager)
    
    def chat_about_tree_care(self, user_message, tree_context=""):
        """Chat with Gemini about tree care"""
        try:
            if not st.session_state.get('gemini_configured', False):
                return "I'm currently in demo mode. In full version, I'd provide personalized tree care advice using Gemini AI."
            
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Add custom prompts context if available
            custom_context = ""
            if self.prompts_manager:
                thai_species = self.prompts_manager.get_thai_species()
                if thai_species:
                    custom_context = f"\nข้อมูลเฉพาะพันธุ์ไม้ไทย: {', '.join(thai_species[:3])}..."
            
            prompt = f"""
            You are a friendly and knowledgeable tree care expert specializing in tropical trees.
            
            Tree Context: {tree_context}
            {custom_context}
            
            User Question: {user_message}
            
            Provide a helpful, detailed answer with practical advice. Include specific recommendations when possible.
            Focus on sustainable and traditional methods when applicable.
            """
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"I apologize, but I'm having trouble connecting to the AI service. Error: {str(e)[:100]}"
    
    def _extract_json(self, text):
        """Extract JSON from Gemini response"""
        if "```json" in text:
            return text.split("```json")[1].split("```")[0].strip()
        elif "{" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            return text[start:end]
        else:
            # Try to find JSON-like structure
            import re
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, text, re.DOTALL)
            if match:
                return match.group()
            return '{"error": "Could not parse JSON"}'