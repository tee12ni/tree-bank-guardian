#!/usr/bin/env python3
"""
Tree Bank Guardian - Main Application File
Google Gemini 3 Hackathon Submission
"""

import streamlit as st
import os
import sys
from pathlib import Path

# ============================================================================
# DEBUG INFO
# ============================================================================
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print("=" * 60)

# Add modules to path
current_dir = Path(__file__).parent
modules_dir = current_dir / "modules"
sys.path.insert(0, str(modules_dir))

print(f"Modules directory: {modules_dir}")
print(f"Modules exists: {modules_dir.exists()}")

# Import from modules
try:
    from modules import (
        PromptsManager, GeminiHandler,
        load_tree_data, save_tree_data,
        render_sidebar, render_header,
        render_image_analysis_tab, render_chat_assistant_tab,
        render_dashboard_tab, render_custom_prompts_tab
    )
    print("✅ All modules imported successfully")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Trying to import modules individually...")
    
    try:
        # Try importing individually
        import importlib.util
        import importlib
        
        # List of module files
        module_files = {
            'prompts_manager': modules_dir / 'prompts_manager.py',
            'gemini_handler': modules_dir / 'gemini_handler.py',
            'data_manager': modules_dir / 'data_manager.py',
            'ui_components': modules_dir / 'ui_components.py',
            'utils': modules_dir / 'utils.py'
        }
        
        # Load each module
        loaded_modules = {}
        for name, path in module_files.items():
            if path.exists():
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                loaded_modules[name] = module
                print(f"  ✅ Loaded {name}")
            else:
                print(f"  ❌ {path} not found")
        
        # Now import from loaded modules
        from prompts_manager import PromptsManager
        from gemini_handler import GeminiHandler
        from data_manager import load_tree_data, save_tree_data
        from ui_components import (
            render_sidebar, render_header,
            render_image_analysis_tab, render_chat_assistant_tab,
            render_dashboard_tab, render_custom_prompts_tab
        )
        
        print("✅ Individual imports successful")
        
    except Exception as e2:
        print(f"❌ Individual import failed: {e2}")
        st.error(f"Module import error: {e2}")
        st.stop()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables"""
    default_state = {
        'messages': [
            {"role": "assistant", "content": "Hello! I'm your Tree Care Assistant. 🌿"}
        ],
        'trees': [],
        'demo_mode': True,
        'api_key': None,
        'gemini_configured': False,
        'prompts_manager': None,
        'gemini_handler': None
    }
    
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize managers if not exists
    if st.session_state.prompts_manager is None:
        st.session_state.prompts_manager = PromptsManager()
    
    if st.session_state.gemini_handler is None:
        st.session_state.gemini_handler = GeminiHandler(
            prompts_manager=st.session_state.prompts_manager
        )

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application function"""
    
    # Initialize session state
    init_session_state()
    
    # Load data
    load_tree_data()
    
    # Get instances
    prompts_manager = st.session_state.prompts_manager
    gemini_handler = st.session_state.gemini_handler
    
    # Page configuration
    st.set_page_config(
        page_title="Tree Bank Guardian",
        page_icon="🌳",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render UI components
    render_sidebar(gemini_handler, prompts_manager)
    render_header()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📸 Analyze Tree", 
        "💬 Care Assistant", 
        "📊 Dashboard",
        "⚙️ Custom Prompts"
    ])
    
    # Render tabs
    with tab1:
        render_image_analysis_tab(gemini_handler, prompts_manager)
    
    with tab2:
        render_chat_assistant_tab(gemini_handler, prompts_manager)
    
    with tab3:
        render_dashboard_tab(prompts_manager)
    
    with tab4:
        render_custom_prompts_tab(prompts_manager)
    
    # Footer
    st.markdown("---")
    st.caption("""
    **Tree Bank Guardian** | Google Gemini 3 Hackathon Submission | 
    Built with Streamlit & Gemini AI | 
    [https://github.com/tee12ni/tree-bank-guardian.git](#)
    """)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    
    # Run the app
    main()
