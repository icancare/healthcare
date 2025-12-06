# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VitalSigns(Document):
	def validate(self):
		self.set_title()
		self.fetch_patient_data()
		self.calculate_anthropometrics()

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
