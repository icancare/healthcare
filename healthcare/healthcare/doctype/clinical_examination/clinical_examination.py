# Copyright (c) 2024, ICanCare and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowtime


class ClinicalExamination(Document):
	def validate(self):
		if not self.examination_time:
			self.examination_time = nowtime()
	
	def on_submit(self):
		# Link to patient encounter if specified
		if self.patient_encounter:
			frappe.db.set_value("Patient Encounter", self.patient_encounter, 
				"clinical_examination", self.name)


@frappe.whitelist()
def get_clinical_examinations_for_patient(patient, limit=10):
	"""Get clinical examinations for a patient"""
	return frappe.get_all(
		"Clinical Examination",
		filters={"patient": patient, "docstatus": 1},
		fields=["name", "examination_date", "examination_type", "practitioner_name", 
				"provisional_diagnosis", "assessment_status"],
		order_by="examination_date DESC",
		limit=limit
	)


@frappe.whitelist()
def create_examination_from_encounter(encounter, template):
	"""Create a new clinical examination from patient encounter"""
	encounter_doc = frappe.get_doc("Patient Encounter", encounter)
	
	exam = frappe.new_doc("Clinical Examination")
	exam.examination_template = template
	exam.patient = encounter_doc.patient
	exam.practitioner = encounter_doc.practitioner
	exam.patient_encounter = encounter
	exam.examination_date = frappe.utils.today()
	
	return exam

