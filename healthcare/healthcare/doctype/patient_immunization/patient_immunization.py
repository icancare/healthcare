# Copyright (c) 2025, Earthians and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatientImmunization(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this section.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		administered_date: DF.Date
		dose: DF.Float | None
		dose_uom: DF.Data | None
		location: DF.Data | None
		lot: DF.Data | None
		manufacturer: DF.Data | None
		ndc: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		product: DF.Data | None
		route: DF.Literal["", "Oral", "Intramuscular", "Intravenous", "Subcutaneous", "Intranasal", "Other"]
		site: DF.Literal["", "Left Upper Arm", "Right Upper Arm", "Left Thigh", "Right Thigh", "Other"]
		vaccine_name: DF.Link
	# end: auto-generated types

	def validate(self):
		# Auto-fill manufacturer from Medication if vaccine is selected
		if self.vaccine_name and frappe.db.exists("Medication", self.vaccine_name):
			medication = frappe.get_doc("Medication", self.vaccine_name)
			
			# Auto-fill manufacturer if not already set
			if not self.manufacturer and medication.get("manufacturer"):
				self.manufacturer = medication.manufacturer

