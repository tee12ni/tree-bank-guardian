"""
Custom Prompts Manager for Tree Bank Guardian
"""

import json
import os
from pathlib import Path
import streamlit as st

class PromptsManager:
    def __init__(self, prompts_file="data/species_prompts.json"):
        # สร้างโฟลเดอร์ data ถ้ายังไม่มี
        os.makedirs("data", exist_ok=True)
        
        self.prompts_file = prompts_file
        self.species_prompts = self.load_prompts()
    
    def load_prompts(self):
        """โหลด prompts จากไฟล์ JSON"""
        default_prompts = {
            "มะม่วง": {
                "thai_name": "มะม่วง",
                "scientific_name": "Mangifera indica",
                "custom_prompt": "มะม่วงเป็นไม้ผลยืนต้นที่สำคัญของไทย มีหลายพันธุ์เช่นน้ำดอกไม้ อกร่อง เขียวเสวย ควรดูแลด้วยการให้ปุ๋ยสูตร 15-15-15 ทุก 3 เดือน และควบคุมการให้น้ำเพื่อกระตุ้นการออกดอก",
                "care_tips": [
                    "ตัดแต่งกิ่งหลังเก็บเกี่ยวผลผลิต",
                    "ระวังโรคแอนแทรคโนสในฤดูฝน",
                    "ให้น้ำสม่ำเสมอโดยเฉพาะช่วงออกดอก"
                ],
                "carbon_factor": 12.5,
                "value_multiplier": 1.2,
                "is_thai_species": True
            },
            "ยางนา": {
                "thai_name": "ยางนา",
                "scientific_name": "Dipterocarpus alatus",
                "custom_prompt": "ยางนาเป็นไม้ยืนต้นขนาดใหญ่ที่สำคัญต่อระบบนิเวศ ให้ร่มเงาดีและดูดซับคาร์บอนได้สูง เป็นไม้หอมที่ใช้ในงานก่อสร้าง",
                "care_tips": [
                    "ปลูกในพื้นที่ที่มีน้ำใต้ดินสูง",
                    "ไม่ชอบน้ำท่วมขัง",
                    "ต้องการแสงแดดเต็มที่"
                ],
                "carbon_factor": 25.0,
                "value_multiplier": 2.5,
                "is_thai_species": True
            }
        }
        
        try:
            if os.path.exists(self.prompts_file):
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # รวมกับ default prompts
                    merged = {**default_prompts, **data}
                    return merged
            else:
                # สร้างไฟล์ใหม่ด้วย default prompts
                self.save_prompts(default_prompts)
                return default_prompts
        except Exception as e:
            st.error(f"Error loading prompts: {e}")
            return default_prompts
    
    def save_prompts(self, prompts):
        """บันทึก prompts ลงไฟล์"""
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving prompts: {e}")
            return False
    
    def get_prompt_for_species(self, species_name):
        """ดึง prompt สำหรับ species ที่ระบุ"""
        # ค้นหาด้วยชื่อไทย
        for key, prompt_data in self.species_prompts.items():
            if species_name.lower() in key.lower() or key.lower() in species_name.lower():
                return prompt_data
        
        # ค้นหาด้วย scientific name
        for prompt_data in self.species_prompts.values():
            if species_name.lower() in prompt_data.get("scientific_name", "").lower():
                return prompt_data
        
        # ถ้าไม่เจอ สร้าง prompt ใหม่
        return {
            "thai_name": species_name,
            "scientific_name": "",
            "custom_prompt": f"{species_name} เป็นไม้ยืนต้นที่พบในประเทศไทย",
            "care_tips": ["ดูแลรักษาตามสภาพพื้นที่"],
            "carbon_factor": 15.0,
            "value_multiplier": 1.0,
            "is_thai_species": False
        }
    
    def add_custom_prompt(self, thai_name, scientific_name="", custom_prompt="", 
                         care_tips=None, carbon_factor=15.0, is_thai_species=True):
        """เพิ่ม prompt ใหม่"""
        if care_tips is None:
            care_tips = ["ดูแลรักษาตามสภาพพื้นที่"]
        
        self.species_prompts[thai_name] = {
            "thai_name": thai_name,
            "scientific_name": scientific_name,
            "custom_prompt": custom_prompt,
            "care_tips": care_tips,
            "carbon_factor": carbon_factor,
            "value_multiplier": carbon_factor / 15.0,
            "is_thai_species": is_thai_species
        }
        
        self.save_prompts(self.species_prompts)
        return True
    
    def get_all_species(self):
        """ดึงรายการ species ทั้งหมด"""
        return list(self.species_prompts.keys())
    
    def get_thai_species(self):
        """ดึงเฉพาะ species ไทย"""
        return [name for name, data in self.species_prompts.items() 
                if data.get('is_thai_species', False)]