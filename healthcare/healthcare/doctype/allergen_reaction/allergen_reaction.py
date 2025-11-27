# Copyright (c) 2025, Earthians and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AllergenReaction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this section.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText | None
		reaction_name: DF.Data
	# end: auto-generated types

	pass

