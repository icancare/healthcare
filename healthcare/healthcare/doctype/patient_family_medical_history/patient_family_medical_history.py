# Copyright (c) 2025, healthcare and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import re
from datetime import datetime


class PatientFamilyMedicalHistory(Document):
	def validate(self):
		if self.when:
			self.validate_since_when_format()
	
	def validate_since_when_format(self):
		"""
		Validate When field format
		Allowed formats: YYYY, MM/YYYY, M/YYYY
		Year must be <= current year
		"""
		value = self.when.strip()
		current_year = datetime.now().year
		
		# Pattern 1: YYYY (4 digits)
		pattern_year = r'^(\d{4})$'
		# Pattern 2: MM/YYYY or M/YYYY
		pattern_month_year = r'^(\d{1,2})/(\d{4})$'
		
		match_year = re.match(pattern_year, value)
		match_month_year = re.match(pattern_month_year, value)
		
		if match_year:
			year = int(match_year.group(1))
			if year > current_year:
				frappe.throw(_("Year in 'When' field cannot be greater than current year ({0})").format(current_year))
		elif match_month_year:
			month = int(match_month_year.group(1))
			year = int(match_month_year.group(2))
			
			if month < 1 or month > 12:
				frappe.throw(_("Month in 'When' field must be between 1 and 12"))
			
			if year > current_year:
				frappe.throw(_("Year in 'When' field cannot be greater than current year ({0})").format(current_year))
		else:
			frappe.throw(_("'When' field must be in format YYYY (e.g., 2023) or MM/YYYY (e.g., 01/2023, 1/2023)"))

