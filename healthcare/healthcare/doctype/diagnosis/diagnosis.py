# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Diagnosis(Document):
	pass


@frappe.whitelist()
def get_icd11_codes(doctype, txt, searchfield, start, page_len, filters):
	"""Get ICD-11 codes from Code Value for autocomplete"""
	return frappe.db.sql(
		"""
		SELECT name, code_value, display
		FROM `tabCode Value`
		WHERE code_system = 'ICD-11'
		AND (code_value LIKE %(txt)s OR display LIKE %(txt)s OR name LIKE %(txt)s)
		ORDER BY code_value
		LIMIT %(start)s, %(page_len)s
		""",
		{
			"txt": f"%{txt}%",
			"start": start,
			"page_len": page_len
		}
	)
