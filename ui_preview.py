#!/usr/bin/env python3
"""
Simple UI preview test to check the enhanced Streamlit styling
"""

import streamlit as st

# Set page config
st.set_page_config(
    page_title="Multi-Agent Code Development",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the CSS from streamlit_app
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    .workflow-chain {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .agent-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        position: relative;
    }
    
    .agent-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 4px;
        background: linear-gradient(135deg, #10b981, #059669);
    }
    
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    load_css()
    
    # Header
    st.markdown("""
    <h1 class="main-header">🤖 Multi-Agent Code Development Workflow</h1>
    <div class="workflow-chain">
        <div style="display: flex; justify-content: center; align-items: center; gap: 1rem; flex-wrap: wrap;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600;">
                📄 Document Analyzer
            </div>
            <div style="font-size: 1.5rem; color: #64748b;">→</div>
            <div style="background: linear-gradient(135deg, #f093fb, #f5576c); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600;">
                🔨 Code Generator
            </div>
            <div style="font-size: 1.5rem; color: #64748b;">→</div>
            <div style="background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600;">
                🧪 Test Runner
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample agent cards
    st.markdown("## 🚀 Workflow Progress")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="agent-card">
            <h3 style="margin: 0; color: #1e293b; font-weight: 600;">
                📄 Step 1: Document Analyzer
            </h3>
            <div style="color: #10b981; font-weight: 500; margin: 0.5rem 0;">
                ✅ COMPLETED
            </div>
            <p style="color: #64748b; margin: 0;">
                Successfully extracted 4 scenarios from requirements
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="agent-card">
            <h3 style="margin: 0; color: #1e293b; font-weight: 600;">
                🔨 Step 2: Code Generator
            </h3>
            <div style="color: #f59e0b; font-weight: 500; margin: 0.5rem 0;">
                🔄 RUNNING
            </div>
            <p style="color: #64748b; margin: 0;">
                Generating Python code with error handling...
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="agent-card" style="opacity: 0.7;">
            <h3 style="margin: 0; color: #1e293b; font-weight: 600;">
                🧪 Step 3: Test Runner
            </h3>
            <div style="color: #64748b; font-weight: 500; margin: 0.5rem 0;">
                ⏳ PENDING
            </div>
            <p style="color: #64748b; margin: 0;">
                Waiting for code generation to complete
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sample metrics
    st.markdown("## 📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Workflow Status</div>
            <div class="metric-value" style="color: #f59e0b;">🔄 Running</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Agents Completed</div>
            <div class="metric-value" style="color: #10b981;">1/3</div>
            <div style="font-size: 0.8rem; color: #64748b;">33% Complete</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Output Location</div>
            <div class="metric-value" style="font-size: 1.2rem; color: #6366f1;">📁 workflow_20...</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Generated Files</div>
            <div class="metric-value" style="color: #8b5cf6;">📄 7</div>
            <div style="font-size: 0.8rem; color: #64748b;">Files Ready</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("✨ **UI Preview:** This shows the enhanced professional styling for the Multi-Agent Workflow interface!")
    
    st.info("🎨 **Design Features:** Modern gradients, professional typography, enhanced cards, and responsive layout")

if __name__ == "__main__":
    main()
