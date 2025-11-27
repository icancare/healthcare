# Copyright (c) 2025, Earthians and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatientEncounterAllergy(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this section.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allergen: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reaction: DF.Link
		severity: DF.Literal["Mild", "Mild to moderate", "Moderate", "Moderate to severe", "Severe", "Life threatening", "Fatal"]
	# end: auto-generated types

	pass

