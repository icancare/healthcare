# Copyright (c) 2025, Earthians and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatientAllergy(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this section.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allergen: DF.Link
		comments: DF.SmallText | None
		end_date: DF.Date | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reaction: DF.Link
		severity: DF.Literal["Mild", "Mild to moderate", "Moderate", "Moderate to severe", "Severe", "Life threatening", "Fatal"]
		start_date: DF.Date | None
	# end: auto-generated types

	def validate(self):
		# Allow manual entry if allergen not in master
		if self.allergen and not frappe.db.exists("Allergen", self.allergen):
			# Create new allergen entry automatically
			allergen_doc = frappe.get_doc({
				"doctype": "Allergen",
				"allergen_name": self.allergen
			})
			allergen_doc.insert(ignore_permissions=True)
		
		# Allow manual entry if reaction not in master
		if self.reaction and not frappe.db.exists("Allergen Reaction", self.reaction):
			# Create new allergen reaction entry automatically
			reaction_doc = frappe.get_doc({
				"doctype": "Allergen Reaction",
				"reaction_name": self.reaction
			})
			reaction_doc.insert(ignore_permissions=True)

