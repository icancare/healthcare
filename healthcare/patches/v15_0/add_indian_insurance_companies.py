# Copyright (c) 2024, healthcare and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Add default Indian Insurance Companies
	"""
	frappe.logger().info("Adding Indian Insurance Companies...")
	
	# List of major Indian insurance companies
	indian_insurance_companies = [
		# Private Health Insurance Companies
		{
			"insurance_company_name": "Star Health and Allied Insurance",
			"company_code": "STAR",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 425 2255",
			"website": "https://www.starhealth.in",
		},
		{
			"insurance_company_name": "ICICI Lombard General Insurance",
			"company_code": "ICICI",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 2666",
			"website": "https://www.icicilombard.com",
		},
		{
			"insurance_company_name": "HDFC ERGO Health Insurance",
			"company_code": "HDFC",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 2700 700",
			"website": "https://www.hdfcergo.com",
		},
		{
			"insurance_company_name": "Max Bupa Health Insurance",
			"company_code": "MAXBUPA",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 4200 000",
			"website": "https://www.maxbupa.com",
		},
		{
			"insurance_company_name": "Bajaj Allianz General Insurance",
			"company_code": "BAJAJ",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 209 5858",
			"website": "https://www.bajajallianz.com",
		},
		{
			"insurance_company_name": "Reliance Health Insurance",
			"company_code": "RELIANCE",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 3009 3009",
			"website": "https://www.reliancegeneral.co.in",
		},
		{
			"insurance_company_name": "Care Health Insurance (Religare)",
			"company_code": "CARE",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 102 4488",
			"website": "https://www.careinsurance.com",
		},
		{
			"insurance_company_name": "Niva Bupa Health Insurance",
			"company_code": "NIVA",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 266 4545",
			"website": "https://www.nivabupa.com",
		},
		{
			"insurance_company_name": "Aditya Birla Health Insurance",
			"company_code": "ABHI",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 270 7000",
			"website": "https://www.adityabirlacapital.com",
		},
		{
			"insurance_company_name": "Manipal Cigna Health Insurance",
			"company_code": "CIGNA",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 102 4488",
			"website": "https://www.manipalcigna.com",
		},
		# Public Sector Insurance
		{
			"insurance_company_name": "Life Insurance Corporation (LIC)",
			"company_code": "LIC",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "022 6827 6827",
			"website": "https://www.licindia.in",
		},
		{
			"insurance_company_name": "New India Assurance",
			"company_code": "NIA",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 209 1415",
			"website": "https://www.newindia.co.in",
		},
		{
			"insurance_company_name": "National Insurance Company",
			"company_code": "NIC",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 425 0000",
			"website": "https://www.nationalinsurance.nic.co.in",
		},
		{
			"insurance_company_name": "Oriental Insurance Company",
			"company_code": "OICL",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 118 485",
			"website": "https://www.orientalinsurance.org.in",
		},
		{
			"insurance_company_name": "United India Insurance",
			"company_code": "UII",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 425 4444",
			"website": "https://www.uiic.co.in",
		},
		# Government Health Schemes
		{
			"insurance_company_name": "Ayushman Bharat (PM-JAY)",
			"company_code": "PMJAY",
			"company_type": "Government Scheme",
			"status": "Active",
			"contact_number": "14555",
			"website": "https://pmjay.gov.in",
			"notes": "Pradhan Mantri Jan Arogya Yojana - World's largest health insurance scheme",
		},
		{
			"insurance_company_name": "Central Government Health Scheme (CGHS)",
			"company_code": "CGHS",
			"company_type": "Government Scheme",
			"status": "Active",
			"contact_number": "1800 180 1104",
			"website": "https://cghs.gov.in",
			"notes": "For Central Government employees and pensioners",
		},
		{
			"insurance_company_name": "Employees' State Insurance (ESI)",
			"company_code": "ESI",
			"company_type": "Government Scheme",
			"status": "Active",
			"contact_number": "1800 118 005",
			"website": "https://www.esic.in",
			"notes": "For organized sector employees earning up to Rs. 21,000 per month",
		},
		{
			"insurance_company_name": "Rashtriya Swasthya Bima Yojana (RSBY)",
			"company_code": "RSBY",
			"company_type": "Government Scheme",
			"status": "Active",
			"website": "https://www.rsby.gov.in",
			"notes": "Health insurance scheme for BPL families",
		},
		# Major TPAs (Third Party Administrators)
		{
			"insurance_company_name": "Medi Assist India TPA",
			"company_code": "MEDIASSIST",
			"company_type": "TPA",
			"status": "Active",
			"contact_number": "1800 425 5333",
			"website": "https://www.mediassist.in",
		},
		{
			"insurance_company_name": "Vidal Health TPA",
			"company_code": "VIDAL",
			"company_type": "TPA",
			"status": "Active",
			"contact_number": "1800 425 2550",
			"website": "https://www.vidalhealth.com",
		},
		{
			"insurance_company_name": "Health India TPA",
			"company_code": "HEALTHINDIA",
			"company_type": "TPA",
			"status": "Active",
			"contact_number": "1800 11 4488",
			"website": "https://www.healthindiatpa.com",
		},
		{
			"insurance_company_name": "MD India Healthcare Services TPA",
			"company_code": "MDINDIA",
			"company_type": "TPA",
			"status": "Active",
			"contact_number": "1800 258 6161",
			"website": "https://www.mdindia.com",
		},
		{
			"insurance_company_name": "Paramount Health Services TPA",
			"company_code": "PARAMOUNT",
			"company_type": "TPA",
			"status": "Active",
			"contact_number": "1800 180 1104",
			"website": "https://www.paramounttpa.com",
		},
	]
	
	# Insert insurance companies
	for company_data in indian_insurance_companies:
		try:
			# Check if already exists
			if not frappe.db.exists("Insurance Company", company_data["insurance_company_name"]):
				doc = frappe.get_doc({
					"doctype": "Insurance Company",
					**company_data
				})
				doc.insert(ignore_permissions=True)
				frappe.logger().info(f"✅ Added: {company_data['insurance_company_name']}")
			else:
				frappe.logger().info(f"⏭️ Skipped (already exists): {company_data['insurance_company_name']}")
		except Exception as e:
			frappe.logger().error(f"❌ Error adding {company_data['insurance_company_name']}: {str(e)}")
			continue
	
	frappe.db.commit()
	frappe.logger().info("✅ Indian Insurance Companies added successfully!")

