"""
UI Components for Tree Bank Guardian
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from PIL import Image, ImageDraw
import time
import numpy as np

def render_sidebar(gemini_handler, prompts_manager):
    """Render the sidebar"""
    with st.sidebar:
        st.title("🌳 Tree Bank")
        st.markdown("---")
        
        # Demo mode toggle
        demo_mode = st.toggle(
            "Demo Mode", 
            value=st.session_state.get('demo_mode', True),
            help="Use mock data when enabled"
        )
        st.session_state.demo_mode = demo_mode
        
        if not demo_mode:
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                help="Get your API key from Google AI Studio",
                value=st.session_state.get('api_key', '')
            )
            
            if api_key and api_key != st.session_state.get('api_key'):
                from .gemini_handler import configure_gemini
                if configure_gemini(api_key):
                    st.success("Gemini API configured!")
                else:
                    st.error("Invalid API key")
        
        st.markdown("---")
        
        # Portfolio summary
        st.subheader("Portfolio Summary")
        from .data_manager import get_tree_statistics
        stats = get_tree_statistics()
        
        st.metric("Total Trees", stats["total_trees"])
        st.metric("Total Value", f"฿{stats['total_value']:,}/yr")
        
        if stats["total_trees"] > 0:
            st.metric("Avg Health", f"{stats['avg_health']:.1f}%")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            from .data_manager import load_tree_data
            load_tree_data()
            st.rerun()
        
        st.markdown("---")
        
        # Custom prompts info
        if prompts_manager:
            thai_species_count = len(prompts_manager.get_thai_species())
            st.caption(f"📚 {thai_species_count} Thai species in database")
        
        st.caption("Built for Google Gemini 3 Hackathon")
        st.caption(f"Version 1.0 | {datetime.now().strftime('%Y-%m-%d')}")

def render_header():
    """Render the main header"""
    st.title("🌳 Tree Bank Guardian")
    st.markdown("**AI-Powered Tree Monitoring System | Gemini 3 Hackathon**")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.caption("Monitor, Analyze, and Value Your Trees with AI")
    with col2:
        mode_status = "🔴 Demo Mode" if st.session_state.get('demo_mode', True) else "🟢 Live Mode"
        st.caption(mode_status)
    with col3:
        tree_count = len(st.session_state.get('trees', []))
        st.caption(f"📊 {tree_count} Trees in Portfolio")
    
    st.markdown("---")

def render_image_analysis_tab(gemini_handler, prompts_manager):
    """Render the image analysis tab"""
    st.header("📸 Tree Image Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Upload Tree Image")
        
        image_source = st.radio(
            "Choose image source:",
            ["Upload from computer", "Use sample image"],
            horizontal=True
        )
        
        image = None
        
        if image_source == "Upload from computer":
            uploaded_file = st.file_uploader(
                "Choose a tree image...", 
                type=['jpg', 'jpeg', 'png'],
                help="Upload a clear image of your tree"
            )
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Your tree", use_container_width=True)
                
        else:  # Use sample image
            st.info("Using sample mango tree image")
            sample_img = Image.new('RGB', (400, 300), color='darkgreen')
            draw = ImageDraw.Draw(sample_img)
            # Draw a simple tree
            draw.rectangle([180, 200, 220, 300], fill='saddlebrown')  # trunk
            draw.ellipse([100, 50, 300, 250], fill='forestgreen')     # canopy
            image = sample_img
            st.image(image, caption="Sample Mango Tree", use_container_width=True)
        
        location = st.text_input("Location (optional):", 
                                placeholder="e.g., Bangkok, Thailand")
        
        use_custom_prompts = st.checkbox("Use custom species knowledge", 
                                        value=True,
                                        help="Apply specific knowledge for Thai tree species")
        
        analyze_clicked = st.button(
            "🔍 Analyze with AI", 
            type="primary",
            use_container_width=True,
            disabled=image is None
        )
    
    with col2:
        st.subheader("Analysis Results")
        
        if analyze_clicked and image:
            with st.spinner("Analyzing with AI..."):
                time.sleep(1)  # Simulate processing
                
                analysis = gemini_handler.analyze_tree_image(
                    image, location, use_custom_prompts
                )
                
                from .utils import calculate_environmental_value
                env_value = calculate_environmental_value(analysis, prompts_manager)
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                # Species info
                st.subheader("🌿 Species Identification")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(
                        "Thai Name", 
                        analysis["species"]["thai_name"],
                        delta=f"{analysis['species']['confidence']*100:.0f}% confidence"
                    )
                with col_b:
                    st.metric(
                        "Scientific Name", 
                        analysis["species"]["scientific_name"]
                    )
                
                if analysis["species"].get("is_thai_species", False):
                    st.info("🇹🇭 This is a Thai tree species")
                
                # Health assessment
                st.subheader("💚 Health Assessment")
                health_score = analysis["health_assessment"]["score"]
                st.progress(health_score/100, 
                          text=f"Health Score: {health_score}/100")
                
                if analysis["health_assessment"]["issues"]:
                    st.warning("⚠️ Issues Detected:")
                    for issue in analysis["health_assessment"]["issues"]:
                        st.write(f"• {issue}")
                
                st.info("💡 Recommendations:")
                st.write(analysis["health_assessment"]["recommendations"])
                
                # Custom prompt info
                if "custom_prompt_info" in analysis:
                    with st.expander("📚 Custom Knowledge Applied"):
                        custom_info = analysis["custom_prompt_info"]
                        st.markdown("**Traditional Knowledge:**")
                        st.info(custom_info.get("traditional_knowledge", ""))
                        
                        st.markdown("**Special Care Tips:**")
                        for tip in custom_info.get("care_tips", []):
                            st.markdown(f"✅ {tip}")
                
                # Environmental value
                st.subheader("💰 Environmental Value")
                
                val_cols = st.columns(4)
                val_cols[0].metric("Carbon", f"{env_value['carbon_kg_per_year']:.1f} kg/yr", 
                                  f"฿{env_value['carbon_value_thb']:.0f}")
                val_cols[1].metric("Oxygen", f"{env_value['oxygen_kg_per_year']:.1f} kg/yr", 
                                  f"฿{env_value['oxygen_value_thb']:.0f}")
                val_cols[2].metric("Biodiversity", "", 
                                  f"฿{env_value['biodiversity_value_thb']:.0f}")
                val_cols[3].metric("Thai Bonus", f"{env_value['thai_species_bonus']:.1f}x")
                
                st.success(f"**Total Annual Value: ฿{env_value['total_value_thb']:,.0f}**")
                
                # Save to portfolio
                st.subheader("💾 Save to Portfolio")
                with st.form("save_tree_form"):
                    tree_name = st.text_input("Tree Nickname:", 
                                             value=f"My {analysis['species']['thai_name']}")
                    
                    if st.form_submit_button("Save Tree", use_container_width=True):
                        from .data_manager import add_tree_to_portfolio
                        tree_data = {
                            "name": tree_name,
                            "species": analysis["species"]["thai_name"],
                            "scientific_name": analysis["species"]["scientific_name"],
                            "health_score": health_score,
                            "environmental_value": env_value["total_value_thb"],
                            "location": location
                        }
                        
                        saved_tree = add_tree_to_portfolio(tree_data)
                        if saved_tree:
                            st.balloons()
                            st.success(f"✅ Tree saved! ID: {saved_tree['tree_id']}")

def render_chat_assistant_tab(gemini_handler, prompts_manager):
    """Render the chat assistant tab"""
    st.header("💬 Tree Care Assistant")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Tree Care Assistant. Ask me anything about tree care, diseases, or maintenance. 🌿"}
        ]
    
    # Quick questions
    st.subheader("Quick Questions")
    q_cols = st.columns(3)
    quick_questions = [
        "How to treat leaf spots?",
        "Best fertilizer for fruit trees?",
        "Watering schedule in dry season?"
    ]
    
    responses = [
        "For leaf spots: Remove affected leaves, apply neem oil spray weekly, improve air circulation.",
        "For fruit trees: Use balanced NPK fertilizer (15-15-15) every 3 months during growing season.",
        "In dry season: Water deeply 2-3 times per week, early morning. Use mulch to retain moisture."
    ]
    
    for idx, (question, response) in enumerate(zip(quick_questions, responses)):
        with q_cols[idx]:
            if st.button(question, use_container_width=True, key=f"quick_{idx}"):
                st.session_state.messages.append({"role": "user", "content": question})
                if st.session_state.get('demo_mode', True):
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    ai_response = gemini_handler.chat_about_tree_care(question, "General tree care advice")
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
    
    st.markdown("---")
    
    # Main chat interface
    st.subheader("Chat with Tree Care Expert")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Ask about tree care..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if st.session_state.get('demo_mode', True):
                    response = "I'm currently in demo mode. In the full version with Gemini API, I'd provide personalized advice based on your specific trees and location."
                else:
                    # Get tree context for better responses
                    tree_context = ""
                    trees = st.session_state.get('trees', [])
                    if trees:
                        recent_tree = trees[-1]
                        tree_context = f"Recent tree: {recent_tree['name']} ({recent_tree['species']}), Health: {recent_tree['health_score']}%"
                    
                    response = gemini_handler.chat_about_tree_care(user_input, tree_context)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

def render_dashboard_tab(prompts_manager):
    """Render the dashboard tab"""
    st.header("📊 Tree Portfolio Dashboard")
    
    from .data_manager import load_tree_data, get_tree_statistics
    load_tree_data()
    
    trees = st.session_state.get('trees', [])
    
    if not trees:
        st.info("🌱 Your portfolio is empty!")
        st.markdown("""
        Start by analyzing a tree in the **📸 Analyze Tree** tab and save it to your portfolio.
        
        Once you have trees, you'll see:
        - Portfolio statistics and values
        - Health trends over time
        - Environmental impact metrics
        - Care logs and maintenance schedule
        """)
        return
    
    # Portfolio summary
    st.subheader("🌿 Portfolio Summary")
    
    stats = get_tree_statistics()
    
    cols = st.columns(4)
    cols[0].metric("Total Trees", stats["total_trees"])
    cols[1].metric("Total Value", f"฿{stats['total_value']:,}/yr")
    cols[2].metric("Avg Health", f"{stats['avg_health']:.1f}%")
    cols[3].metric("Carbon Saved", f"{stats['total_carbon']:.0f} kg/yr")
    
    st.markdown("---")
    
    # Tree list with actions
    st.subheader("Your Trees")
    
    for tree in trees:
        with st.expander(f"🌳 {tree['name']} - {tree['tree_id']} | Health: {tree['health_score']}% | Value: ฿{tree['environmental_value']:,}/yr", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Tree info
                st.markdown(f"**Species:** {tree['species']} ({tree['scientific_name']})")
                st.markdown(f"**Added:** {tree['date_added']}")
                st.markdown(f"**Last Checkup:** {tree['last_checkup']}")
                
                # Health progress
                st.progress(tree['health_score']/100, 
                          text=f"Health Score: {tree['health_score']}%")
                
                # Care logs
                if tree.get('care_logs'):
                    st.markdown("**Recent Care Logs:**")
                    for log in tree['care_logs'][-3:]:
                        st.caption(f"{log['date']}: {log['activity']} - {log['notes'][:50]}...")
            
            with col2:
                # Quick actions
                if st.button("📝 Log Care", key=f"log_{tree['id']}", use_container_width=True):
                    st.session_state[f"show_log_form_{tree['id']}"] = True
                
                # Export this tree
                tree_json = json.dumps(tree, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Export",
                    data=tree_json,
                    file_name=f"{tree['tree_id']}_data.json",
                    mime="application/json",
                    key=f"export_{tree['id']}",
                    use_container_width=True
                )
            
            # Care log form
            if st.session_state.get(f"show_log_form_{tree['id']}"):
                with st.form(key=f"care_form_{tree['id']}"):
                    activity = st.selectbox(
                        "Activity Type",
                        ["Watering", "Fertilizing", "Pruning", "Pest Control", "Soil Treatment", "Other"],
                        key=f"activity_{tree['id']}"
                    )
                    notes = st.text_area("Notes", key=f"notes_{tree['id']}")
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        if st.form_submit_button("Save Log", use_container_width=True):
                            from .data_manager import add_care_log
                            if add_care_log(tree['id'], activity, notes):
                                st.success("Care log saved!")
                                st.session_state[f"show_log_form_{tree['id']}"] = False
                                st.rerun()
                    with col_cancel:
                        if st.form_submit_button("Cancel", use_container_width=True, type="secondary"):
                            st.session_state[f"show_log_form_{tree['id']}"] = False
                            st.rerun()
    
    st.markdown("---")
    
    # Environmental impact visualization
    st.subheader("📈 Environmental Impact Over Time")
    
    # Create sample growth data
    months = 12
    monthly_data = []
    
    for month in range(1, months + 1):
        month_value = stats["total_value"] * (month/12) * (1 + (month-1)*0.05)
        monthly_data.append({
            "Month": f"Month {month}",
            "Cumulative Value (฿)": month_value,
            "Carbon Equivalent (kg)": month_value / 30,
            "Trees Tracked": min(len(trees), month * 2)
        })
    
    df = pd.DataFrame(monthly_data)
    
    # Line chart
    st.line_chart(df.set_index("Month")[["Cumulative Value (฿)", "Carbon Equivalent (kg)"]])
    
    # Bar chart for tree distribution
    if len(trees) > 1:
        st.subheader("🌳 Tree Distribution by Species")
        
        species_counts = {}
        for tree in trees:
            species = tree.get("species", "Unknown")
            species_counts[species] = species_counts.get(species, 0) + 1
        
        if species_counts:
            species_df = pd.DataFrame({
                "Species": list(species_counts.keys()),
                "Count": list(species_counts.values())
            })
            st.bar_chart(species_df.set_index("Species"))
    
    # Export all data
    st.markdown("---")
    st.subheader("Data Export")
    
    col_export, col_report = st.columns(2)
    
    with col_export:
        all_data = {
            "portfolio": trees,
            "summary": stats,
            "generated_date": datetime.now().isoformat()
        }
        
        json_data = json.dumps(all_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="📥 Download Full Portfolio (JSON)",
            data=json_data,
            file_name=f"tree_portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )

def render_custom_prompts_tab(prompts_manager):
    """Render tab for managing custom prompts"""
    st.header("⚙️ Custom Species Prompts")
    st.markdown("กำหนดข้อมูลเฉพาะสำหรับ species ต่างๆ เพื่อเพิ่มความแม่นยำในการวิเคราะห์")
    
    # ส่วนที่ 1: ดูและแก้ไข prompts ที่มีอยู่
    st.subheader("📋 Existing Species Prompts")
    
    all_species = prompts_manager.get_all_species()
    
    if not all_species:
        st.info("No custom prompts yet. Add your first one below!")
    else:
        for species_name in all_species:
            with st.expander(f"🌿 {species_name}", expanded=False):
                prompt_data = prompts_manager.get_prompt_for_species(species_name)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Scientific Name:** {prompt_data.get('scientific_name', 'N/A')}")
                    st.markdown(f"**Carbon Factor:** {prompt_data.get('carbon_factor', 15.0)} kg CO2/ปี")
                    st.markdown(f"**Thai Species:** {'Yes' if prompt_data.get('is_thai_species', False) else 'No'}")
                    
                    # แสดง custom prompt
                    st.text_area(
                        "Custom Prompt",
                        value=prompt_data.get('custom_prompt', ''),
                        height=100,
                        key=f"view_{species_name}",
                        disabled=True
                    )
                    
                    # แสดง care tips
                    care_tips = prompt_data.get('care_tips', [])
                    if care_tips:
                        st.markdown("**Care Tips:**")
                        for tip in care_tips:
                            st.markdown(f"• {tip}")
                
                with col2:
                    # ปุ่มแก้ไข
                    if st.button("✏️ Edit", key=f"edit_{species_name}", use_container_width=True):
                        st.session_state[f"editing_{species_name}"] = True
    
    st.markdown("---")
    
    # ส่วนที่ 2: เพิ่ม prompts ใหม่
    st.subheader("➕ Add New Species Prompt")
    
    with st.form("add_new_prompt_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_thai = st.text_input("Thai Name*", placeholder="เช่น มะม่วง, ยางนา, สัก")
            new_scientific = st.text_input("Scientific Name", placeholder="เช่น Mangifera indica")
            new_carbon = st.number_input("Carbon Factor (kg CO2/ปี)*",
                                        value=15.0,
                                        min_value=1.0,
                                        max_value=100.0,
                                        step=0.5)
        
        with col2:
            new_prompt = st.text_area("Custom Prompt*",
                                     height=150,
                                     placeholder="Describe specific characteristics, cultural significance, uses, etc.")
        
        # Care tips
        st.subheader("Care Tips (at least 1)")
        care_tip1 = st.text_input("Tip 1*", placeholder="เช่น ให้ปุ๋ยสูตร 15-15-15 ทุก 3 เดือน")
        care_tip2 = st.text_input("Tip 2", placeholder="เช่น ให้น้ำสม่ำเสมอช่วงออกดอก")
        care_tip3 = st.text_input("Tip 3", placeholder="เช่น ตัดแต่งกิ่งหลังเก็บเกี่ยว")
        
        is_thai_species = st.checkbox("This is a Thai tree species", value=True)
        
        care_tips = []
        if care_tip1:
            care_tips.append(care_tip1)
        if care_tip2:
            care_tips.append(care_tip2)
        if care_tip3:
            care_tips.append(care_tip3)
        
        if st.form_submit_button("Add Species Prompt", use_container_width=True):
            if new_thai:
                success = prompts_manager.add_custom_prompt(
                    thai_name=new_thai,
                    scientific_name=new_scientific,
                    custom_prompt=new_prompt,
                    care_tips=care_tips,
                    carbon_factor=new_carbon,
                    is_thai_species=is_thai_species
                )
                
                if success:
                    st.success(f"✅ Added {new_thai} to custom prompts!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to add prompt")
            else:
                st.warning("Please enter Thai name")
    
    # ส่วนที่ 3: Import/Export prompts
    st.markdown("---")
    st.subheader("📁 Import/Export Prompts")
    
    col_export, col_import = st.columns(2)
    
    with col_export:
        # Export prompts
        prompts_json = json.dumps(prompts_manager.species_prompts, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Export Prompts (JSON)",
            data=prompts_json,
            file_name=f"species_prompts_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # ส่วนที่ 4: ข้อมูลสถิติ
    st.markdown("---")
    st.subheader("📊 Prompts Statistics")
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.metric("Total Species", len(all_species))
    
    with col_stat2:
        thai_species = [s for s in all_species if prompts_manager.species_prompts[s].get('is_thai_species', False)]
        st.metric("Thai Species", len(thai_species))
    
    with col_stat3:
        if all_species:
            avg_carbon = sum(prompts_manager.species_prompts[s].get('carbon_factor', 15.0) 
                            for s in all_species) / len(all_species)
            st.metric("Avg Carbon Factor", f"{avg_carbon:.1f} kg")
        else:
            st.metric("Avg Carbon Factor", "0.0 kg")