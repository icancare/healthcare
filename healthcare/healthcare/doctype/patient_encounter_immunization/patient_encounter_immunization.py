# Copyright (c) 2025, Earthians and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PatientEncounterImmunization(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this section.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		administered_date: DF.Date
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		vaccine_name: DF.Link
	# end: auto-generated types

	pass

