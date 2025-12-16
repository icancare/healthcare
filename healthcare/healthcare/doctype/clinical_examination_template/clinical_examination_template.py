# Copyright (c) 2024, ICanCare and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClinicalExaminationTemplate(Document):
	def validate(self):
		self.validate_practitioners()
	
	def validate_practitioners(self):
		"""Ensure only one default per practitioner"""
		default_count = {}
		for p in self.practitioners:
			if p.is_default:
				if p.practitioner in default_count:
					frappe.throw(f"Practitioner {p.practitioner_name} is marked as default multiple times")
				default_count[p.practitioner] = True


@frappe.whitelist()
def get_templates_for_practitioner(practitioner):
	"""Get all clinical examination templates assigned to a practitioner"""
	templates = frappe.db.sql("""
		SELECT 
			cet.name as template_name,
			cet.examination_type,
			cet.description,
			cetp.is_default
		FROM `tabClinical Examination Template` cet
		INNER JOIN `tabClinical Exam Template Practitioner` cetp 
			ON cetp.parent = cet.name
		WHERE cetp.practitioner = %s
			AND cet.disabled = 0
		ORDER BY cetp.is_default DESC, cet.template_name ASC
	""", (practitioner,), as_dict=True)
	
	return templates


@frappe.whitelist()
def get_default_template_for_practitioner(practitioner):
	"""Get the default clinical examination template for a practitioner"""
	template = frappe.db.sql("""
		SELECT 
			cet.name as template_name,
			cet.examination_type,
			cet.description
		FROM `tabClinical Examination Template` cet
		INNER JOIN `tabClinical Exam Template Practitioner` cetp 
			ON cetp.parent = cet.name
		WHERE cetp.practitioner = %s
			AND cetp.is_default = 1
			AND cet.disabled = 0
		LIMIT 1
	""", (practitioner,), as_dict=True)
	
	return template[0] if template else None

