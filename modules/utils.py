"""
Utility Functions for Tree Bank Guardian
"""

import json
import streamlit as st
from datetime import datetime

def get_mock_analysis():
    """Return mock analysis data for demo mode"""
    return {
        "species": {
            "thai_name": "มะม่วง",
            "scientific_name": "Mangifera indica",
            "confidence": 0.92,
            "is_thai_species": True
        },
        "health_assessment": {
            "score": 85,
            "issues": ["Minor leaf spots", "Slight nutrient deficiency"],
            "recommendations": "Apply balanced fertilizer and ensure adequate sunlight. Water deeply once weekly.",
            "urgency": "medium"
        },
        "physical_attributes": {
            "height_estimate_m": 2.5,
            "age_estimate_years": 3,
            "canopy_width_m": 3.0,
            "trunk_diameter_cm": 15.0
        },
        "thai_specific_info": {
            "common_in_regions": ["ภาคกลาง", "ภาคเหนือ"],
            "traditional_uses": ["ผลกินได้", "ไม้ใช้สอย"],
            "cultural_significance": "สูง"
        }
    }

def get_mock_analysis_with_custom(prompts_manager=None):
    """Return mock analysis with custom prompt integration"""
    analysis = get_mock_analysis()
    
    if prompts_manager:
        species_name = analysis["species"]["thai_name"]
        species_prompt = prompts_manager.get_prompt_for_species(species_name)
        
        analysis["custom_prompt_info"] = {
            "source": "custom_prompts",
            "carbon_factor": species_prompt.get("carbon_factor", 12.5),
            "care_tips": species_prompt.get("care_tips", []),
            "traditional_knowledge": species_prompt.get("custom_prompt", "")
        }
    
    return analysis

def calculate_environmental_value(analysis, prompts_manager=None):
    """Calculate environmental value from analysis"""
    try:
        # Determine carbon factor
        carbon_factor = 15.0  # default
        
        if "custom_prompt_info" in analysis:
            carbon_factor = analysis["custom_prompt_info"]["carbon_factor"]
        elif prompts_manager:
            species_name = analysis["species"]["thai_name"]
            species_prompt = prompts_manager.get_prompt_for_species(species_name)
            carbon_factor = species_prompt.get("carbon_factor", 15.0)
        
        # Calculate values
        height = analysis["physical_attributes"]["height_estimate_m"]
        carbon_kg = carbon_factor * (height / 2.0)
        oxygen_kg = carbon_kg * 0.73
        
        # Value multipliers
        value_multiplier = 1.0
        if analysis["species"].get("is_thai_species", False):
            value_multiplier = 1.5
        if analysis["thai_specific_info"]["cultural_significance"] == "สูง":
            value_multiplier *= 1.2
        
        carbon_value = carbon_kg * 30 * value_multiplier
        oxygen_value = oxygen_kg * 20 * value_multiplier
        biodiversity_value = 200 if analysis["species"].get("is_thai_species", False) else 50
        
        total_value = carbon_value + oxygen_value + biodiversity_value
        
        return {
            "carbon_kg_per_year": carbon_kg,
            "oxygen_kg_per_year": oxygen_kg,
            "carbon_value_thb": carbon_value,
            "oxygen_value_thb": oxygen_value,
            "biodiversity_value_thb": biodiversity_value,
            "total_value_thb": total_value,
            "water_regulation_l_per_year": carbon_kg * 100,
            "thai_species_bonus": value_multiplier,
            "carbon_factor_used": carbon_factor
        }
    except:
        return {
            "carbon_kg_per_year": 25,
            "oxygen_kg_per_year": 18,
            "carbon_value_thb": 750,
            "oxygen_value_thb": 360,
            "biodiversity_value_thb": 100,
            "total_value_thb": 1210,
            "water_regulation_l_per_year": 2500,
            "thai_species_bonus": 1.0,
            "carbon_factor_used": 15.0
        }

def export_data():
    """Export all data as JSON"""
    try:
        all_data = {
            "trees": st.session_state.get("trees", []),
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "version": "1.0",
                "hackathon": "Google Gemini 3 Hackathon"
            }
        }
        
        json_str = json.dumps(all_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="Download Data",
            data=json_str,
            file_name=f"tree_bank_export_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
        return True
    except Exception as e:
        st.error(f"Export failed: {e}")
        return False