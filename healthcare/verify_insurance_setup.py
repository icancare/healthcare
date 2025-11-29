#!/usr/bin/env python3
"""
Verification script for Insurance setup
Run: bench --site icancare.com execute healthcare.verify_insurance_setup.verify_all
"""

import frappe


def verify_all():
	"""Verify all insurance setup components"""
	print("\n" + "="*60)
	print("🔍 INSURANCE SETUP VERIFICATION")
	print("="*60 + "\n")
	
	# 1. Check Insurance Company DocType
	print("1️⃣ Checking Insurance Company DocType...")
	if frappe.db.exists("DocType", "Insurance Company"):
		print("   ✅ Insurance Company DocType exists")
		
		# Count insurance companies
		count = frappe.db.count("Insurance Company")
		print(f"   📊 Total Insurance Companies: {count}")
		
		if count > 0:
			# Show some examples
			companies = frappe.db.get_all("Insurance Company", 
				fields=["insurance_company_name", "company_type", "status"],
				limit=5
			)
			print("   📋 Sample Companies:")
			for company in companies:
				print(f"      - {company.insurance_company_name} ({company.company_type}) - {company.status}")
	else:
		print("   ❌ Insurance Company DocType NOT found")
	
	print()
	
	# 2. Check Patient Insurance DocType
	print("2️⃣ Checking Patient Insurance DocType...")
	if frappe.db.exists("DocType", "Patient Insurance"):
		print("   ✅ Patient Insurance DocType exists (Child Table)")
		
		# Get field count
		meta = frappe.get_meta("Patient Insurance")
		print(f"   📊 Total Fields: {len(meta.fields)}")
		print("   📋 Key Fields:")
		key_fields = ["insurance_company", "member_number", "is_policy_holder", 
					  "card_front_photo", "card_back_photo", "verified"]
		for field in key_fields:
			if meta.has_field(field):
				print(f"      ✅ {field}")
			else:
				print(f"      ❌ {field} - MISSING!")
	else:
		print("   ❌ Patient Insurance DocType NOT found")
	
	print()
	
	# 3. Check Patient DocType modifications
	print("3️⃣ Checking Patient DocType modifications...")
	if frappe.db.exists("DocType", "Patient"):
		patient_meta = frappe.get_meta("Patient")
		
		# Check for Health Insurance tab
		health_insurance_tab = False
		patient_insurance_field = False
		
		for field in patient_meta.fields:
			if field.fieldname == "health_insurance_tab":
				health_insurance_tab = True
				print("   ✅ Health Insurance Tab found")
			if field.fieldname == "patient_insurance":
				patient_insurance_field = True
				print("   ✅ Patient Insurance Table field found")
		
		if not health_insurance_tab:
			print("   ❌ Health Insurance Tab NOT found")
		if not patient_insurance_field:
			print("   ❌ Patient Insurance Table field NOT found")
	else:
		print("   ❌ Patient DocType NOT found")
	
	print()
	
	# 4. Test creating a sample insurance record
	print("4️⃣ Testing Insurance Company creation...")
	try:
		# Check if test company exists
		test_company_name = "Test Insurance Company - Verification"
		if frappe.db.exists("Insurance Company", test_company_name):
			frappe.delete_doc("Insurance Company", test_company_name, force=1)
		
		# Create test company
		test_doc = frappe.get_doc({
			"doctype": "Insurance Company",
			"insurance_company_name": test_company_name,
			"company_code": "TEST",
			"company_type": "Private Insurance",
			"status": "Active",
			"contact_number": "1800 000 0000",
		})
		test_doc.insert(ignore_permissions=True)
		print(f"   ✅ Test company created: {test_company_name}")
		
		# Clean up
		frappe.delete_doc("Insurance Company", test_company_name, force=1)
		print("   ✅ Test company deleted (cleanup)")
		
	except Exception as e:
		print(f"   ❌ Error creating test company: {str(e)}")
	
	print()
	
	# 5. Summary
	print("="*60)
	print("📊 VERIFICATION SUMMARY")
	print("="*60)
	
	all_checks = [
		frappe.db.exists("DocType", "Insurance Company"),
		frappe.db.exists("DocType", "Patient Insurance"),
		frappe.db.count("Insurance Company") > 0,
		health_insurance_tab,
		patient_insurance_field,
	]
	
	passed = sum(all_checks)
	total = len(all_checks)
	
	print(f"\n✅ Passed: {passed}/{total} checks")
	
	if passed == total:
		print("\n🎉 ALL CHECKS PASSED! Insurance setup is complete!")
		print("\n📝 Next Steps:")
		print("   1. Open Patient DocType in browser")
		print("   2. Create/Edit a patient")
		print("   3. Go to 'Health Insurance' tab")
		print("   4. Add insurance details and upload card photos")
		print("\n🌐 Access at: http://localhost:8000/app/patient")
	else:
		print("\n⚠️ Some checks failed. Please review the errors above.")
	
	print("\n" + "="*60 + "\n")


if __name__ == "__main__":
	verify_all()

