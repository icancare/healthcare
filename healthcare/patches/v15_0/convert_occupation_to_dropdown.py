import frappe


def execute():
	"""
	Convert existing Occupation text field to dropdown in Medical History tab
	"""
	
	try:
		# Update the existing occupation field to be a dropdown
		frappe.db.sql("""
			UPDATE `tabDocField` 
			SET 
				fieldtype = 'Select',
				options = '\nGovernment\nPrivate\nOwn-Business\nHouse hold\nRetired\nUnemployed able to work\nUnemployed – not able to work\nStudent\nRefuse\nOther'
			WHERE parent = 'Patient' 
			AND fieldname = 'occupation'
		""")
		
		frappe.db.commit()
		
		print("✓ Converted Occupation field to dropdown")
		print("  - Field type changed from Data to Select")
		print("  - Added occupation type options")
		
	except Exception as e:
		print(f"Error converting occupation field: {str(e)}")
		frappe.db.rollback()

