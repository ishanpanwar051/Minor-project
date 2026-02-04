"""
AI-Driven Student Dropout Prediction System - Streamlit Dashboard
Early Warning System for Reducing Student Dropout Rates - NEP 2020 Aligned
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="🎓 Student Dropout Prediction System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .risk-safe {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    .risk-high {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .feature-importance {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class DropoutPredictionApp:
    """
    Streamlit Application for Student Dropout Prediction
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = None
        self.load_model_components()
    
    def load_model_components(self):
        """
        Load trained model, scaler, and feature names
        """
        try:
            # Load model
            self.model = joblib.load('model/model.pkl')
            
            # Load scaler
            self.scaler = joblib.load('model/scaler.pkl')
            
            # Load feature names
            self.features = joblib.load('model/features.pkl')
            
        except FileNotFoundError:
            st.error("❌ Model files not found. Please run `train_model.py` first.")
            st.stop()
    
    def calculate_risk_score(self, attendance, marks, behavior_score):
        """
        Calculate comprehensive risk score
        """
        attendance_risk = (100 - attendance) * 0.4
        academic_risk = (100 - marks) * 0.4
        behavior_risk = (10 - behavior_score) * 2
        
        total_risk = attendance_risk + academic_risk + behavior_risk
        return round(total_risk, 2)
    
    def predict_dropout_risk(self, attendance, marks, behavior_score):
        """
        Predict dropout risk using trained model
        """
        # Calculate risk score
        risk_score = self.calculate_risk_score(attendance, marks, behavior_score)
        
        # Prepare features
        features = np.array([[attendance, marks, behavior_score, risk_score]])
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0]
        
        return {
            'prediction': int(prediction),
            'risk_level': 'HIGH RISK' if prediction == 1 else 'SAFE',
            'probability': {
                'safe': float(probability[0]),
                'at_risk': float(probability[1])
            },
            'risk_score': risk_score,
            'confidence': max(probability) * 100
        }
    
    def create_gauge_chart(self, risk_score, prediction):
        """
        Create a simple gauge chart using HTML/CSS
        """
        # Determine color based on risk level
        if prediction == 1:
            color = '#dc3545'  # Red for high risk
        else:
            color = '#28a745'  # Green for safe
        
        # Create HTML gauge chart
        gauge_html = f"""
        <div style="width: 100%; text-align: center;">
            <div style="position: relative; width: 200px; height: 100px; margin: 0 auto;">
                <div style="position: absolute; width: 200px; height: 100px; border-radius: 100px 100px 0 0; background: #e9ecef; border: 2px solid #dee2e6;">
                </div>
                <div style="position: absolute; width: 200px; height: 100px; border-radius: 100px 100px 0 0; background: conic-gradient({color} 0deg {risk_score * 3.6}deg, #e9ecef {risk_score * 3.6}deg);">
                </div>
                <div style="position: absolute; top: 50px; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px;">
                    {risk_score}
                </div>
            </div>
            <p style="margin-top: 10px; font-weight: bold; color: {color};">
                {'HIGH RISK' if prediction == 1 else 'SAFE'}
            </p>
        </div>
        """
        
        return gauge_html
    
    def create_probability_chart(self, probabilities):
        """
        Create probability distribution chart using HTML/CSS
        """
        safe_percent = probabilities['safe'] * 100
        at_risk_percent = probabilities['at_risk'] * 100
        
        chart_html = f"""
        <div style="width: 100%; text-align: center;">
            <div style="position: relative; width: 200px; height: 200px; margin: 0 auto;">
                <div style="position: absolute; width: 200px; height: 200px; border-radius: 50%; background: conic-gradient(#28a745 0deg {safe_percent * 3.6}deg, #dc3545 {safe_percent * 3.6}deg);">
                </div>
                <div style="position: absolute; top: 50px; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 50%; width: 100px; height: 100px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <div style="font-size: 12px; color: #28a745; font-weight: bold;">Safe</div>
                    <div style="font-size: 18px; font-weight: bold;">{safe_percent:.1f}%</div>
                </div>
            </div>
            <div style="margin-top: 20px; display: flex; justify-content: center; gap: 20px;">
                <div style="display: flex; align-items: center; gap: 5px;">
                    <div style="width: 12px; height: 12px; background: #28a745; border-radius: 50%;"></div>
                    <span>Safe: {safe_percent:.1f}%</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <div style="width: 12px; height: 12px; background: #dc3545; border-radius: 50%;"></div>
                    <span>At-Risk: {at_risk_percent:.1f}%</span>
                </div>
            </div>
        </div>
        """
        
        return chart_html
    
    def render_header(self):
        """
        Render application header
        """
        st.markdown('<h1 class="main-header">🎓 AI-Driven Student Dropout Prediction System</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">Early Warning System for Reducing Student Dropout Rates - NEP 2020 Aligned</p>', unsafe_allow_html=True)
        st.markdown("---")
    
    def render_sidebar(self):
        """
        Render sidebar with input controls
        """
        st.sidebar.header("📊 Student Information")
        
        # Attendance slider
        attendance = st.sidebar.slider(
            "📈 Attendance Percentage",
            min_value=0,
            max_value=100,
            value=85,
            step=1,
            help="Student's attendance percentage"
        )
        
        # Marks slider
        marks = st.sidebar.slider(
            "📚 Academic Marks",
            min_value=0,
            max_value=100,
            value=75,
            step=1,
            help="Student's academic performance marks"
        )
        
        # Behavior score slider
        behavior_score = st.sidebar.slider(
            "🤝 Behavior Score",
            min_value=1,
            max_value=10,
            value=7,
            step=1,
            help="Behavior score (1=Poor, 10=Excellent)"
        )
        
        # Predict button
        predict_button = st.sidebar.button(
            "🔮 Predict Dropout Risk",
            type="primary",
            use_container_width=True
        )
        
        return attendance, marks, behavior_score, predict_button
    
    def render_input_summary(self, attendance, marks, behavior_score):
        """
        Render input summary cards
        """
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Attendance</h3>
                <h2 style="color: #667eea; margin: 0;">{}%</h2>
                <p style="margin: 0; color: #666;">Class Presence</p>
            </div>
            """.format(attendance), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>📚 Academic Marks</h3>
                <h2 style="color: #667eea; margin: 0;">{}</h2>
                <p style="margin: 0; color: #666;">Performance Score</p>
            </div>
            """.format(marks), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>🤝 Behavior Score</h3>
                <h2 style="color: #667eea; margin: 0;">{}/10</h2>
                <p style="margin: 0; color: #666;">Conduct Rating</p>
            </div>
            """.format(behavior_score), unsafe_allow_html=True)
    
    def render_prediction_results(self, results, attendance, marks, behavior_score):
        """
        Render prediction results
        """
        # Main prediction result
        if results['risk_level'] == 'HIGH RISK':
            st.markdown("""
            <div class="risk-high">
                <h2>🚨 HIGH RISK OF DROPOUT DETECTED!</h2>
                <p><strong>Immediate intervention recommended!</strong></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="risk-safe">
                <h2>✅ STUDENT IS SAFE</h2>
                <p><strong>Low risk of dropout - Continue monitoring!</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(self.create_gauge_chart(results['risk_score'], results['prediction']), unsafe_allow_html=True)
        
        with col2:
            st.markdown(self.create_probability_chart(results['probability']), unsafe_allow_html=True)
        
        # Detailed metrics
        st.markdown("### 📊 Detailed Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Risk Score", f"{results['risk_score']}", delta=None)
        
        with col2:
            st.metric("Confidence", f"{results['confidence']:.1f}%", delta=None)
        
        with col3:
            st.metric("Safe Probability", f"{results['probability']['safe']*100:.1f}%", delta=None)
        
        with col4:
            st.metric("At-Risk Probability", f"{results['probability']['at_risk']*100:.1f}%", delta=None)
        
        # Risk assessment
        st.markdown("### 🎯 Risk Assessment")
        
        if results['risk_score'] < 20:
            risk_level = "🟢 Very Low Risk"
            assessment = "Student is performing well across all parameters."
        elif results['risk_score'] < 40:
            risk_level = "🟡 Low Risk"
            assessment = "Student needs regular monitoring and encouragement."
        elif results['risk_score'] < 60:
            risk_level = "🟠 Medium Risk"
            assessment = "Consider counseling and targeted support."
        else:
            risk_level = "🔴 High Risk"
            assessment = "Immediate attention and intervention required."
        
        st.info(f"**Risk Level:** {risk_level}\n\n**Assessment:** {assessment}")
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        
        if results['risk_level'] == 'HIGH RISK':
            recommendations = [
                "📅 Schedule immediate counseling session",
                "🔍 Analyze specific areas of concern",
                "📋 Develop personalized improvement plan",
                "👥 Increase monitoring frequency",
                "👪 Involve parents/guardians if applicable",
                "📚 Provide additional academic support",
                "🎯 Set achievable short-term goals"
            ]
        else:
            recommendations = [
                "✅ Continue regular monitoring",
                "🎉 Acknowledge and encourage good performance",
                "📈 Maintain current performance levels",
                "🤝 Provide ongoing support and motivation",
                "🎯 Set challenging but achievable goals",
                "📊 Track progress regularly"
            ]
        
        for rec in recommendations:
            st.write(f"- {rec}")
    
    def render_feature_importance(self):
        """
        Render feature importance information
        """
        st.markdown("### 📈 Feature Importance")
        
        # Feature importance data (from training)
        feature_importance = pd.DataFrame({
            'feature': ['Risk Score', 'Attendance', 'Marks', 'Behavior Score'],
            'importance': [0.410718, 0.306468, 0.169417, 0.113397]
        })
        
        # Create bar chart using st.bar_chart
        st.bar_chart(feature_importance.set_index('feature')['importance'])
        
        st.markdown("""
        <div class="feature-importance">
            <h4>📊 How the Model Makes Predictions:</h4>
            <ul>
                <li><strong>Risk Score (41.1%)</strong>: Combined risk assessment based on all factors</li>
                <li><strong>Attendance (30.6%)</strong>: Regular class attendance is crucial for success</li>
                <li><strong>Marks (16.9%)</strong>: Academic performance indicates understanding</li>
                <li><strong>Behavior Score (11.3%)</strong>: Conduct and engagement affect learning</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def render_about_section(self):
        """
        Render about section
        """
        st.markdown("---")
        st.markdown("### 📚 About This System")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 System Overview:**
            - AI-powered early warning system
            - Machine Learning-based prediction
            - Real-time risk assessment
            - NEP 2020 aligned objectives
            
            **🔧 Technology Stack:**
            - Python & Scikit-learn
            - Random Forest Classifier
            - Streamlit Dashboard
            - Interactive Visualizations
            """)
        
        with col2:
            st.markdown("""
            **📈 Key Features:**
            - 97% prediction accuracy
            - Multi-factor risk analysis
            - Interactive dashboard
            - Real-time predictions
            - Actionable recommendations
            
            **🎓 Educational Impact:**
            - Early intervention support
            - Data-driven decisions
            - Student success focus
            - Retention improvement
            """)
    
    def run(self):
        """
        Main application runner
        """
        # Render header
        self.render_header()
        
        # Render sidebar
        attendance, marks, behavior_score, predict_button = self.render_sidebar()
        
        # Render input summary
        self.render_input_summary(attendance, marks, behavior_score)
        
        # Make prediction when button is clicked
        if predict_button:
            with st.spinner("🔮 Analyzing student data..."):
                results = self.predict_dropout_risk(attendance, marks, behavior_score)
            
            # Render results
            self.render_prediction_results(results, attendance, marks, behavior_score)
        
        # Render feature importance
        self.render_feature_importance()
        
        # Render about section
        self.render_about_section()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🎓 AI-Driven Student Dropout Prediction System | NEP 2020 Aligned</p>
            <p>Empowering Educational Institutions with Data-Driven Insights</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """
    Main function to run the Streamlit app
    """
    app = DropoutPredictionApp()
    app.run()

if __name__ == "__main__":
    main()
