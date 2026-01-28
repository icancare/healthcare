# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class VitalSigns(Document):
	def validate(self):
		self.set_title()
		self.fetch_patient_data()
		self.calculate_anthropometrics()
		self.calculate_peak_flow()
		self.validate_ecog_score()

	def set_title(self):
		self.title = f"{self.patient_name or self.patient} - {self.signs_date}"

	def fetch_patient_data(self):
		if self.patient:
			patient = frappe.get_doc("Patient", self.patient)
			if patient.dob:
				from datetime import date
				today = date.today()
				dob = patient.dob
				self.patient_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
			if patient.sex:
				self.patient_sex = patient.sex

	def calculate_anthropometrics(self):
		# Unit conversions
		h_cm = self.to_cm(self.height, self.height_unit)
		w_kg = self.to_kg(self.weight, self.weight_unit)
		waist_cm = self.to_cm(self.waist_circumference, self.waist_unit)
		hip_cm = self.to_cm(self.hip_circumference, self.hip_unit)
		h_m = h_cm / 100 if h_cm else 0
		age = self.patient_age or 30  # Default age if not available
		sex = self.get_sex() or 'M'  # Default to Male if not available

		# BMI - works without age/sex
		if h_m > 0 and w_kg > 0:
			self.bmi = round(w_kg / (h_m * h_m), 2)

		# WHR - works without age/sex
		if waist_cm > 0 and hip_cm > 0:
			self.whr = round(waist_cm / hip_cm, 2)

		# Body Fat % (BMI + Age formula)
		if self.bmi and age:
			sf = 1 if sex == 'M' else 0
			self.body_fat_percentage = round(max(0, (1.20 * self.bmi) + (0.23 * age) - (10.8 * sf) - 5.4), 2)

		# Lean Body Mass (Boer)
		if h_cm > 0 and w_kg > 0:
			if sex == 'M':
				self.lean_body_mass = round(max(0, (0.407 * w_kg) + (0.267 * h_cm) - 19.2), 2)
			else:
				self.lean_body_mass = round(max(0, (0.252 * w_kg) + (0.473 * h_cm) - 48.3), 2)

		# Muscle Mass (Lee)
		if h_m > 0 and w_kg > 0 and age:
			sf = 1 if sex == 'M' else 0
			self.muscle_mass = round(max(0, (0.244 * w_kg) + (7.8 * h_m) + (6.6 * sf) - (0.098 * age) - 4.5), 2)

		# Bone Mass (Hume)
		if w_kg > 0:
			factor = 0.10 if sex == 'M' else 0.086
			self.bone_mass = round(factor * w_kg, 2)

		# Bone Mineral Content (Hologic)
		if h_cm > 0 and w_kg > 0:
			sf = 2.07 if sex == 'M' else 0
			self.bone_mineral_content = round(max(0, (0.0029 * h_cm * h_cm / 100) + (0.0056 * w_kg) + sf - 3.11), 2)

		# Total Body Water (Watson)
		if h_cm > 0 and w_kg > 0 and age:
			if sex == 'M':
				tbw_l = 2.447 - (0.09516 * age) + (0.1074 * h_cm) + (0.3362 * w_kg)
			else:
				tbw_l = -2.097 + (0.1069 * h_cm) + (0.2466 * w_kg)
			self.total_body_water = round((tbw_l / w_kg) * 100, 2) if w_kg > 0 else 0

		# Protein %
		if self.lean_body_mass and w_kg > 0:
			self.protein_percentage = round((self.lean_body_mass * 0.20 / w_kg) * 100, 2)

		# BMR (Mifflin-St Jeor)
		if h_cm > 0 and w_kg > 0 and age:
			if sex == 'M':
				self.bmr = round((10 * w_kg) + (6.25 * h_cm) - (5 * age) + 5)
			else:
				self.bmr = round((10 * w_kg) + (6.25 * h_cm) - (5 * age) - 161)

		# Metabolic Age
		if self.bmr and self.lean_body_mass and self.lean_body_mass > 0:
			self.metabolic_age = round(max(0, 70 - ((self.bmr / (24 * self.lean_body_mass)) * 100)), 1)

		# Subcutaneous Fat (Jackson-Pollock)
		if age:
			sf_sum = 0
			bd = 0
			if sex == 'M' and self.skinfold_chest and self.skinfold_abdomen and self.skinfold_thigh:
				sf_sum = self.skinfold_chest + self.skinfold_abdomen + self.skinfold_thigh
				bd = 1.10938 - (0.0008267 * sf_sum) + (0.0000016 * sf_sum * sf_sum) - (0.0002574 * age)
			elif sex == 'F' and self.skinfold_triceps and self.skinfold_suprailiac and self.skinfold_thigh:
				sf_sum = self.skinfold_triceps + self.skinfold_suprailiac + self.skinfold_thigh
				bd = 1.0994921 - (0.0009929 * sf_sum) + (0.0000023 * sf_sum * sf_sum) - (0.0001392 * age)
			if bd > 0:
				self.subcutaneous_fat = round(max(0, ((495 / bd) - 450) * 0.85), 2)

	def to_cm(self, val, unit):
		if not val:
			return 0
		if unit == 'inch':
			return val * 2.54
		elif unit == 'feet':
			return val * 30.48
		return val

	def to_kg(self, val, unit):
		if not val:
			return 0
		if unit == 'lbs':
			return val * 0.453592
		return val

	def get_sex(self):
		if not self.patient_sex:
			return None
		s = self.patient_sex.lower()
		if 'female' in s:
			return 'F'
		elif 'male' in s:
			return 'M'
		return None

	def calculate_peak_flow(self):
		"""Calculate Expected Peak Flow and Variability based on age, height, and gender"""
		# Only calculate if we have current peak flow reading
		if not self.peak_flow_current:
			return
		
		# Get required parameters
		age = self.patient_age
		# Height is in Anthropometric section - convert to cm
		height_cm = self.to_cm(self.height, self.height_unit) if self.height else 0
		sex = self.get_sex()
		
		# Calculate Expected Peak Flow (PEFR) only if we have all required data
		expected_pefr = 0
		
		if age and height_cm > 0 and sex:
			if 5 <= age <= 7:
				# Ages 5-7 years and any ethnicity
				# PEFR = [(Height, cm - 100) × 5] + 100
				expected_pefr = ((height_cm - 100) * 5) + 100
			elif 8 <= age <= 17:
				# Ages 8-17 years, all other ethnicities
				# PEFR = [(Height, cm - 100) × 5] + 100
				expected_pefr = ((height_cm - 100) * 5) + 100
			elif 18 <= age <= 80:
				# Ages 18-80 years, all other ethnicities
				# Convert height from cm to meters for formula
				height_m = height_cm / 100
				
				if sex == 'M':
					# PEFR, male = {[(Height, m × 5.48) + 1.58] - [Age × 0.041]} × 60
					expected_pefr = (((height_m * 5.48) + 1.58) - (age * 0.041)) * 60
				elif sex == 'F':
					# PEFR, female = {[(Height, m × 3.72) + 2.24] - [Age × 0.03]} × 60
					expected_pefr = (((height_m * 3.72) + 2.24) - (age * 0.03)) * 60
			
			# Set expected peak flow (rounded to 0 decimal)
			if expected_pefr > 0:
				self.peak_flow_expected = round(expected_pefr, 0)
		
		# Calculate Peak Flow Variability if we have expected value
		if self.peak_flow_expected and self.peak_flow_expected > 0:
			# Peak flow variability, % = (actual peak flow rate / expected peak flow rate) × 100
			variability = (self.peak_flow_current / self.peak_flow_expected) * 100
			self.peak_flow_percentage = round(variability, 1)
			
			# Determine status based on variability
			# Green: 80-100% or above (good control)
			# Yellow: 50-80% (caution)
			# Red: Below 50% (medical emergency)
			if variability >= 80:
				self.peak_flow_status = 'Green'
			elif variability >= 50:
				self.peak_flow_status = 'Yellow'
			else:
				self.peak_flow_status = 'Red'
		# Fallback: Use Personal Best if Expected is not available
		elif self.peak_flow_personal_best and self.peak_flow_personal_best > 0:
			variability = (self.peak_flow_current / self.peak_flow_personal_best) * 100
			self.peak_flow_percentage = round(variability, 1)
			
			if variability >= 80:
				self.peak_flow_status = 'Green'
			elif variability >= 50:
				self.peak_flow_status = 'Yellow'
			else:
				self.peak_flow_status = 'Red'

	def validate_ecog_score(self):
		if self.ecog_score is None:
			return

		try:
			score = int(self.ecog_score)
		except (TypeError, ValueError):
			frappe.throw(_("ECOG Score must be an integer between 0 and 5."))

		if score < 0 or score > 5:
			frappe.throw(_("ECOG Score must be an integer between 0 and 5."))


@frappe.whitelist()
def get_vital_parameter_history(patient, parameter):
	"""
	Get history of a specific vital parameter for a patient
	Used for displaying charts in Vital Signs form
	
	Args:
		patient: Patient ID
		parameter: Field name of the parameter (e.g., 'bmi', 'whr', 'body_fat_percentage')
	
	Returns:
		dict with labels (dates) and values for charting
	"""
	if not patient or not parameter:
		return {"labels": [], "values": []}
	
	# Map parameter names to their database field names
	parameter_field_map = {
		"bmi": "bmi",
		"whr": "whr",
		"body_fat_percentage": "body_fat_percentage",
		"lean_body_mass": "lean_body_mass",
		"muscle_mass": "muscle_mass",
		"bone_mass": "bone_mass",
		"bone_mineral_content": "bone_mineral_content",
		"total_body_water": "total_body_water",
		"protein_percentage": "protein_percentage",
		"bmr": "bmr",
		"metabolic_age": "metabolic_age",
		"subcutaneous_fat": "subcutaneous_fat",
		# Vital Signs
		"temperature": "temperature",
		"pulse": "pulse",
		"spo2": "spo2",
		"respiratory_rate": "respiratory_rate",
		"bp_systolic": "bp_systolic",
		"bp_diastolic": "bp_diastolic",
		"blood_sugar": "blood_sugar",
		# Anthropometric
		"height": "height",
		"weight": "weight",
		"waist_circumference": "waist_circumference",
		"hip_circumference": "hip_circumference",
		# Tobacco & respiratory
		"spirometer_fev1_fvc": "spirometer_fev1_fvc",
		"spirometer_fvc": "spirometer_fvc",
		"spirometer_fev1": "spirometer_fev1",
		"spirometer_pef": "spirometer_pef",
		"mouth_opening_mm": "mouth_opening_mm",
		"peak_flow_current": "peak_flow_current",
		"peak_flow_personal_best": "peak_flow_personal_best",
		"breath_holding_time": "breath_holding_time",
		"co_reading": "co_reading",
		"cohb_percentage": "cohb_percentage",
		"urinal_nicotine": "urinal_nicotine",
		"ecg_done": "ecg_done",
		"echo_done": "echo_done",
		"dexascan_done": "dexascan_done",
		"left_ear_abnormality": "left_ear_abnormality",
		"right_ear_abnormality": "right_ear_abnormality",
		"left_eye_pupil_dilation": "left_eye_pupil_dilation",
		"left_eye_opacity": "left_eye_opacity",
		"right_eye_pupil_dilation": "right_eye_pupil_dilation",
		"right_eye_opacity": "right_eye_opacity"
	}
	
	field_name = parameter_field_map.get(parameter, parameter)
	
	# Fetch all vital signs for this patient with the specific field
	vitals = frappe.db.get_all(
		"Vital Signs",
		filters={"patient": patient, "docstatus": ["!=", 2]},
		fields=["signs_date", "signs_time", field_name],
		order_by="signs_date asc, signs_time asc"
	)
	
	labels = []
	values = []
	
	for vital in vitals:
		value = vital.get(field_name)
		normalized = normalize_chart_value(value)
		if normalized is not None:
			# Format date for display
			date_str = frappe.utils.formatdate(vital.signs_date, "dd-MM-yyyy")
			time_str = str(vital.signs_time)[:5] if vital.signs_time else ""
			label = f"{date_str} {time_str}".strip()
			
			labels.append(label)
			values.append(normalized)
	
	return {
		"labels": labels,
		"values": values
	}


def normalize_chart_value(value):
	"""Convert various field values to floats for charting."""
	if value is None:
		return None

	if isinstance(value, (int, float)):
		return float(value)

	if isinstance(value, str):
		val = value.strip()
		if not val:
			return None
		lower_val = val.lower()
		boolean_map = {
			"yes": 1,
			"true": 1,
			"done": 1,
			"present": 1,
			"abnormal": 1,
			"positive": 1,
			"no": 0,
			"false": 0,
			"pending": 0,
			"pending upload": 0,
			"stored": 1,
			"recorded": 1,
			"normal": 1,
			"none": 0,
		}
		if lower_val in boolean_map:
			return float(boolean_map[lower_val])
		try:
			return float(val)
		except ValueError:
			return None

	return None
