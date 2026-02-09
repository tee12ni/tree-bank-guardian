# 🌳 Tree Bank Guardian

![Tree Bank Guardian](https://img.shields.io/badge/Google-Gemini%203%20Hackathon-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)

**AI-Powered Tree Monitoring System for Google Gemini 3 Hackathon**

## 🚀 Live Demo
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tree-bank-guardian.streamlit.app)

## 📹 product overview Video
[Watch on YouTube](#) <!https://youtu.be/WYnrVp9gGRM>

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Hackathon Details](#hackathon-details)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## 📖 Overview

Tree Bank Guardian is an AI-powered web application that helps users monitor, analyze, and value their trees using Google's Gemini 3 AI. Built for the Google Gemini 3 Hackathon, this tool transforms tree management through computer vision and natural language processing.

### The Problem
Traditional tree monitoring is manual, time-consuming, and inaccessible to non-experts. Tree Bank Guardian solves this by providing:
- Instant tree species identification
- Automated health assessment
- Environmental value calculation
- Personalized care recommendations

### The Solution
Using Gemini 3's multimodal capabilities, users can simply upload a tree photo and receive comprehensive analysis within seconds.

## ✨ Features

### 🌿 **Tree Image Analysis**
- Upload tree images for instant analysis
- Species identification with confidence scores
- Health assessment and issue detection
- Physical attribute estimation (height, age, canopy width)

### 💰 **Environmental Value Calculator**
- Carbon sequestration quantification
- Oxygen production measurement
- Monetary value estimation
- Biodiversity impact assessment

### 💬 **AI Tree Care Assistant**
- Natural language Q&A about tree care
- Personalized recommendations
- Disease diagnosis and treatment advice
- Maintenance scheduling guidance

### 📊 **Digital Tree Portfolio**
- Centralized tree management dashboard
- Health trend visualization
- Environmental impact tracking
- Care log history

## 🛠️ Tech Stack

### **Frontend & Backend**
- **Streamlit** - Full-stack web framework
- **Python 3.11** - Backend logic

### **AI & Machine Learning**
- **Google Gemini 3 API** - Core AI engine
  - `gemini-1.5-pro-vision` for image analysis
  - `gemini-1.5-flash` for conversational AI
- **Prompt Engineering** - Custom botanical expert prompts

### **Data Management**
- **JSON-based storage** - Local data persistence
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations

### **Deployment**
- **Streamlit Community Cloud** - Hosting platform
- **GitHub** - Version control and collaboration

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- Google Gemini API Key (free from [Google AI Studio](https://aistudio.google.com/))

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/tree-bank-guardian.git
cd tree-bank-guardian
