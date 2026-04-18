from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Student, RiskProfile, Attendance
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy import func, and_, or_

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')

@analysis_bp.route('/generate_report')
@login_required
def generate_report():
    """Generate comprehensive AI analysis report"""
    if current_user.role not in ['admin', 'faculty']:
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Get comprehensive data
        report_data = get_comprehensive_analysis()
        
        return render_template('ai_analysis_report.html', report=report_data)
    
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

@analysis_bp.route('/api/generate_insights')
@login_required
def generate_insights():
    """Generate AI insights for popup"""
    try:
        insights = get_ai_insights()
        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_comprehensive_analysis():
    """Get comprehensive AI analysis data"""
    
    # 1. Student Overview
    total_students = Student.query.count()
    active_students = Student.query.filter(Student.enrollment_date >= datetime.now() - timedelta(days=365)).count()
    
    # 2. Risk Analysis
    risk_distribution = db.session.query(
        RiskProfile.risk_level,
        func.count(RiskProfile.id)
    ).group_by(RiskProfile.risk_level).all()
    
    risk_data = {level: count for level, count in risk_distribution}
    
    # 3. Academic Performance
    performance_stats = db.session.query(
        func.avg(Student.gpa).label('avg_gpa'),
        func.min(Student.gpa).label('min_gpa'),
        func.max(Student.gpa).label('max_gpa'),
        func.count(Student.id).label('total_students')
    ).first()
    
    # 4. Attendance Analysis
    thirty_days_ago = datetime.now() - timedelta(days=30)
    attendance_stats = db.session.query(
        Attendance.status,
        func.count(Attendance.id).label('count')
    ).filter(Attendance.date >= thirty_days_ago).group_by(Attendance.status).all()
    
    attendance_data = {status: count for status, count in attendance_stats}
    
    # 5. Department-wise Analysis
    dept_analysis = db.session.query(
        Student.department,
        func.count(Student.id).label('count'),
        func.avg(Student.gpa).label('avg_gpa')
    ).group_by(Student.department).all()
    
    # 6. Year-wise Analysis
    year_analysis = db.session.query(
        Student.year,
        func.count(Student.id).label('count'),
        func.avg(Student.gpa).label('avg_gpa')
    ).group_by(Student.year).all()
    
    # 7. At-Risk Students Details
    at_risk_students = db.session.query(
        Student, RiskProfile
    ).join(RiskProfile, Student.id == RiskProfile.student_id)\
     .filter(RiskProfile.risk_level.in_(['High', 'Critical']))\
     .order_by(RiskProfile.ml_confidence.desc())\
     .limit(15).all()
    
    # 8. Top Performers
    top_performers = Student.query.filter(
        Student.gpa >= 8.5
    ).order_by(Student.gpa.desc()).limit(10).all()
    
    # 9. Recent Trends
    recent_trends = get_recent_trends()
    
    # 10. AI Predictions Summary
    ai_predictions = get_ai_predictions_summary()
    
    return {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'student_overview': {
            'total_students': total_students,
            'active_students': active_students,
            'new_students_this_month': Student.query.filter(
                Student.enrollment_date >= datetime.now() - timedelta(days=30)
            ).count()
        },
        'risk_analysis': {
            'distribution': risk_data,
            'total_at_risk': risk_data.get('High', 0) + risk_data.get('Critical', 0),
            'risk_percentage': ((risk_data.get('High', 0) + risk_data.get('Critical', 0)) / total_students * 100) if total_students > 0 else 0
        },
        'academic_performance': {
            'avg_gpa': round(performance_stats.avg_gpa or 0, 2),
            'min_gpa': round(performance_stats.min_gpa or 0, 2),
            'max_gpa': round(performance_stats.max_gpa or 0, 2),
            'high_performers': Student.query.filter(Student.gpa >= 8.0).count(),
            'low_performers': Student.query.filter(Student.gpa < 6.0).count()
        },
        'attendance_analysis': {
            'distribution': attendance_data,
            'total_classes': sum(attendance_data.values()),
            'attendance_rate': (attendance_data.get('Present', 0) / sum(attendance_data.values()) * 100) if sum(attendance_data.values()) > 0 else 0
        },
        'department_analysis': [
            {
                'department': dept,
                'count': count,
                'avg_gpa': round(avg_gpa, 2)
            }
            for dept, count, avg_gpa in dept_analysis
        ],
        'year_analysis': [
            {
                'year': year,
                'count': count,
                'avg_gpa': round(avg_gpa, 2)
            }
            for year, count, avg_gpa in year_analysis
        ],
        'at_risk_students': [
            {
                'name': f"{student.first_name} {student.last_name}",
                'student_id': student.student_id,
                'department': student.department,
                'year': student.year,
                'gpa': round(student.gpa, 2),
                'risk_level': risk.risk_level,
                'confidence': round((risk.ml_confidence or 0) * 100, 1),
                'risk_factors': risk.risk_reasons.split(',') if risk.risk_reasons else []
            }
            for student, risk in at_risk_students
        ],
        'top_performers': [
            {
                'name': f"{student.first_name} {student.last_name}",
                'student_id': student.student_id,
                'department': student.department,
                'year': student.year,
                'gpa': round(student.gpa, 2)
            }
            for student in top_performers
        ],
        'recent_trends': recent_trends,
        'ai_predictions': ai_predictions,
        'recommendations': generate_recommendations(risk_data, performance_stats)
    }

def get_recent_trends():
    """Get recent performance trends"""
    
    # Last 30 days attendance trend
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    attendance_trend = db.session.query(
        func.date(Attendance.date).label('date'),
        func.count(func.case([(Attendance.status == 'Present', 1)])).label('present'),
        func.count(Attendance.id).label('total')
    ).filter(Attendance.date >= thirty_days_ago)\
     .group_by(func.date(Attendance.date))\
     .order_by(func.date(Attendance.date)).all()
    
    return [
        {
            'date': str(date),
            'attendance_rate': (present / total * 100) if total > 0 else 0
        }
        for date, present, total in attendance_trend
    ]

def get_ai_predictions_summary():
    """Get AI predictions summary"""
    
    # Get risk profile statistics
    risk_profiles = RiskProfile.query.all()
    
    predictions = {
        'total_predictions': len(risk_profiles),
        'high_confidence': len([rp for rp in risk_profiles if (rp.ml_confidence or 0) > 0.8]),
        'medium_confidence': len([rp for rp in risk_profiles if 0.5 <= (rp.ml_confidence or 0) <= 0.8]),
        'low_confidence': len([rp for rp in risk_profiles if (rp.ml_confidence or 0) < 0.5]),
        'average_confidence': round(sum(rp.ml_confidence or 0 for rp in risk_profiles) / len(risk_profiles) * 100, 1) if risk_profiles else 0
    }
    
    return predictions

def generate_recommendations(risk_data, performance_stats):
    """Generate AI-powered recommendations"""
    
    recommendations = []
    
    # Risk-based recommendations
    total_at_risk = risk_data.get('High', 0) + risk_data.get('Critical', 0)
    total_students = sum(risk_data.values())
    
    if total_at_risk > 0:
        risk_percentage = (total_at_risk / total_students * 100) if total_students > 0 else 0
        
        if risk_percentage > 20:
            recommendations.append({
                'priority': 'High',
                'category': 'Risk Management',
                'recommendation': f'Immediate intervention required for {total_at_risk} at-risk students ({risk_percentage:.1f}% of total)',
                'action': 'Schedule counseling sessions and parent meetings'
            })
        elif risk_percentage > 10:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Risk Management',
                'recommendation': f'Monitor {total_at_risk} at-risk students closely',
                'action': 'Weekly progress tracking and mentor assignments'
            })
    
    # Performance-based recommendations
    avg_gpa = performance_stats.avg_gpa or 0
    
    if avg_gpa < 6.5:
        recommendations.append({
            'priority': 'High',
            'category': 'Academic Performance',
            'recommendation': f'Average GPA ({avg_gpa:.2f}) is below acceptable level',
            'action': 'Implement academic support programs and tutoring'
        })
    elif avg_gpa < 7.5:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Academic Performance',
            'recommendation': f'Average GPA ({avg_gpa:.2f}) needs improvement',
            'action': 'Enhance teaching methods and provide additional resources'
        })
    
    # General recommendations
    recommendations.extend([
        {
            'priority': 'Medium',
            'category': 'Technology Integration',
            'recommendation': 'Implement AI-powered early warning system',
            'action': 'Deploy real-time monitoring and alert system'
        },
        {
            'priority': 'Low',
            'category': 'Continuous Improvement',
            'recommendation': 'Regular data analysis and model updates',
            'action': 'Monthly review and model retraining'
        }
    ])
    
    return recommendations

def get_ai_insights():
    """Get quick AI insights for popup"""
    
    total_students = Student.query.count()
    at_risk_count = RiskProfile.query.filter(RiskProfile.risk_level.in_(['High', 'Critical'])).count()
    avg_gpa = db.session.query(func.avg(Student.gpa)).scalar() or 0
    
    insights = []
    
    # Risk insight
    risk_percentage = (at_risk_count / total_students * 100) if total_students > 0 else 0
    if risk_percentage > 15:
        insights.append({
            'type': 'warning',
            'title': 'High Risk Alert',
            'message': f'{risk_percentage:.1f}% of students are at high risk of dropout',
            'icon': 'exclamation-triangle'
        })
    
    # Performance insight
    if avg_gpa < 6.5:
        insights.append({
            'type': 'danger',
            'title': 'Performance Concern',
            'message': f'Average GPA ({avg_gpa:.2f}) is below threshold',
            'icon': 'chart-line'
        })
    elif avg_gpa > 8.0:
        insights.append({
            'type': 'success',
            'title': 'Excellent Performance',
            'message': f'Average GPA ({avg_gpa:.2f}) is above expectations',
            'icon': 'trophy'
        })
    
    # General insight
    insights.append({
        'type': 'info',
        'title': 'AI Analysis Ready',
        'message': 'Comprehensive analysis report available',
        'icon': 'brain'
    })
    
    return insights
