"""
ML Routes for EduGuard System
Handles machine learning predictions and model management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db, Student, RiskProfile
from services.ml_predictor import predictor, train_dropout_model, predict_student_dropout, get_model_statistics

ml_bp = Blueprint('ml', __name__)

@ml_bp.route('/ml/predict', methods=['GET', 'POST'])
@login_required
def ml_prediction():
    """ML-based dropout prediction interface"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            
            if not student_id:
                flash('Please select a student', 'warning')
                return redirect(url_for('ml.ml_prediction'))
            
            # Get prediction
            prediction = predict_student_dropout(student_id)
            
            if 'error' in prediction:
                flash(f'Prediction error: {prediction["error"]}', 'danger')
                return redirect(url_for('ml.ml_prediction'))
            
            # Store prediction in risk profile
            student = Student.query.get(student_id)
            if student and student.risk_profile:
                student.risk_profile.ml_prediction = int(prediction['prediction'])
                student.risk_profile.ml_probability = prediction['dropout_probability']
                student.risk_profile.ml_confidence = prediction['model_confidence']
                student.risk_profile.last_updated = datetime.utcnow()
                db.session.commit()
                
                flash('ML prediction completed and saved!', 'success')
            
            return render_template('ml/prediction_result.html', prediction=prediction, student=student)
            
        except Exception as e:
            flash(f'Error in ML prediction: {str(e)}', 'danger')
            return redirect(url_for('ml.ml_prediction'))
    
    # Get students for dropdown
    students = Student.query.order_by(Student.last_name).all()
    return render_template('ml/predict.html', students=students)

@ml_bp.route('/ml/train')
@login_required
def train_model():
    """Train the ML model (Admin only)"""
    if current_user.role != 'admin':
        abort(403)
    
    if request.method == 'POST':
        try:
            # Train the model
            success = train_dropout_model()
            
            if success:
                flash('Machine learning model trained successfully!', 'success')
            else:
                flash('Model training failed. Please check the data.', 'danger')
            
            return redirect(url_for('ml.model_statistics'))
            
        except Exception as e:
            flash(f'Error training model: {str(e)}', 'danger')
    
    return render_template('ml/train.html')

@ml_bp.route('/ml/statistics')
@login_required
def model_statistics():
    """View ML model statistics and performance"""
    if current_user.role != 'admin':
        abort(403)
    
    try:
        # Get model statistics
        stats = get_model_statistics()
        
        # Get recent predictions
        from models import RiskProfile
        recent_predictions = RiskProfile.query.filter(
            RiskProfile.ml_prediction.isnot(None)
        ).order_by(RiskProfile.last_updated.desc()).limit(20).all()
        
        return render_template('ml/statistics.html', 
                               stats=stats,
                               recent_predictions=recent_predictions)
        
    except Exception as e:
        flash(f'Error loading model statistics: {str(e)}', 'danger')
        return render_template('ml/statistics.html')

@ml_bp.route('/ml/batch_predict', methods=['POST'])
@login_required
def batch_predict():
    """Batch predict for multiple students"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    if request.method == 'POST':
        try:
            student_ids = request.form.getlist('student_ids')
            
            if not student_ids:
                return jsonify({'error': 'No students selected'})
            
            # Load model if not already loaded
            if predictor.model is None:
                predictor.load_model()
            
            # Batch predict
            results = predictor.batch_predict_students(student_ids)
            
            return jsonify({
                'success': True,
                'results': results,
                'processed_count': len(results)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'error': 'Method not allowed'})

@ml_bp.route('/ml/api/predict/<int:student_id>')
@login_required
def api_predict_student(student_id):
    """API endpoint for student prediction"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        prediction = predict_student_dropout(student_id)
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@ml_bp.route('/ml/api/retrain')
@login_required
def api_retrain_model():
    """API endpoint to retrain model"""
    if current_user.role != 'admin':
        abort(403)
    
    try:
        success = train_dropout_model()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Model retrained successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Model training failed'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@ml_bp.route('/ml/api/features')
@login_required
def api_feature_importance():
    """API endpoint for feature importance"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        # Load model if not already loaded
        if predictor.model is None:
            predictor.load_model()
        
        feature_importance = predictor.get_feature_importance()
        
        return jsonify({
            'feature_importance': feature_importance,
            'model_info': {
                'model_type': 'Logistic Regression',
                'features_count': len(feature_importance) if feature_importance else 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

# Helper functions
def update_risk_profiles_with_ml():
    """Update all risk profiles with ML predictions"""
    try:
        from models import Student, RiskProfile, db
        
        students = Student.query.all()
        updated_count = 0
        
        for student in students:
            prediction = predict_student_dropout(student.id)
            
            if 'error' not in prediction and student.risk_profile:
                student.risk_profile.ml_prediction = int(prediction['prediction'])
                student.risk_profile.ml_probability = prediction['dropout_probability']
                student.risk_profile.ml_confidence = prediction['model_confidence']
                student.risk_profile.last_updated = datetime.utcnow()
                updated_count += 1
        
        db.session.commit()
        print(f"Updated {updated_count} risk profiles with ML predictions")
        
        return updated_count
        
    except Exception as e:
        print(f"Error updating risk profiles: {e}")
        return 0
