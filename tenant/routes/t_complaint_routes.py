from flask import request, flash, redirect, url_for, Blueprint, session
from tenant.database.firebase import Database
from utils.ml_utils import extract_features, predict_priority

db = Database()
t_comp_bp = Blueprint('t_complaint',
                      __name__,
                    template_folder="../templates"
                    )

class ComplaintRoutes:
    
  @staticmethod
  @t_comp_bp.route('/submit', methods=['POST'])
  def submit_complaint():
      ten_id = session.get('tenant_id')
      desc = request.form.get("complaint")
      c_type = request.form.get("complaintType")

      features_df = extract_features(desc, c_type)
      predicted_priority = predict_priority(features_df)

      db.submit_complaint(ten_id, desc, c_type, predicted_priority)

      flash(f"Complaint submitted with {predicted_priority} priority.", "success")
      return redirect(url_for('t_dashboard.complaint_page'))
        

