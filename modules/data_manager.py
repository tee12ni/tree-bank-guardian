"""
Data Management for Tree Bank Guardian
"""

import json
import os
from datetime import datetime
import streamlit as st
from pathlib import Path

def init_data_directory():
    """Initialize data directory if not exists"""
    os.makedirs("data", exist_ok=True)

def load_tree_data():
    """Load tree data from JSON file"""
    init_data_directory()
    
    data_file = "data/tree_data.json"
    
    try:
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "trees" in data:
                    st.session_state.trees = data["trees"]
                return data
        else:
            # Create initial data structure
            initial_data = {
                "trees": [],
                "users": [],
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            st.session_state.trees = []
            return initial_data
    except Exception as e:
        st.error(f"Error loading tree data: {e}")
        return {"trees": [], "users": []}

def save_tree_data():
    """Save tree data to JSON file"""
    init_data_directory()
    
    try:
        data = {
            "trees": st.session_state.get("trees", []),
            "users": [],
            "last_updated": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open("data/tree_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving tree data: {e}")
        return False

def add_tree_to_portfolio(tree_data):
    """Add a new tree to portfolio"""
    try:
        trees = st.session_state.get("trees", [])
        tree_id = len(trees) + 1
        
        tree_record = {
            "id": tree_id,
            "tree_id": f"TREE-{tree_id:04d}",
            "name": tree_data.get("name", "Unknown Tree"),
            "species": tree_data.get("species", "Unknown"),
            "scientific_name": tree_data.get("scientific_name", ""),
            "health_score": tree_data.get("health_score", 0),
            "environmental_value": tree_data.get("environmental_value", 0),
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_checkup": datetime.now().strftime("%Y-%m-%d"),
            "location": tree_data.get("location", ""),
            "notes": tree_data.get("notes", ""),
            "image_data": tree_data.get("image_data", ""),
            "care_logs": []
        }
        
        trees.append(tree_record)
        st.session_state.trees = trees
        save_tree_data()
        
        return tree_record
    except Exception as e:
        st.error(f"Error adding tree: {e}")
        return None

def add_care_log(tree_id, activity, notes):
    """Add care log to a tree"""
    try:
        trees = st.session_state.get("trees", [])
        
        for tree in trees:
            if tree["id"] == tree_id:
                log_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "activity": activity,
                    "notes": notes
                }
                tree["care_logs"].append(log_entry)
                tree["last_checkup"] = datetime.now().strftime("%Y-%m-%d")
                
                st.session_state.trees = trees
                save_tree_data()
                return True
        
        return False
    except Exception as e:
        st.error(f"Error adding care log: {e}")
        return False

def get_tree_statistics():
    """Calculate tree portfolio statistics"""
    trees = st.session_state.get("trees", [])
    
    if not trees:
        return {
            "total_trees": 0,
            "total_value": 0,
            "avg_health": 0,
            "total_carbon": 0
        }
    
    total_trees = len(trees)
    total_value = sum(tree.get("environmental_value", 0) for tree in trees)
    avg_health = sum(tree.get("health_score", 0) for tree in trees) / total_trees
    total_carbon = total_value / 30  # Estimate
    
    return {
        "total_trees": total_trees,
        "total_value": total_value,
        "avg_health": avg_health,
        "total_carbon": total_carbon
    }