import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	Add Alcohol History section separate from Substance Abuse
	
	Creates:
	1. Alcohol Type master
	2. Patient Alcohol History child table
	3. Patient Encounter Alcohol History child table
	4. Custom fields in Patient and Patient Encounter
	5. Populates default alcohol types
	"""
	try:
		# Reload new doctypes
		frappe.reload_doctype("Alcohol Type", force=True)
		frappe.reload_doctype("Patient Alcohol History", force=True)
		frappe.reload_doctype("Patient Encounter Alcohol History", force=True)
		
		# Add Alcohol History table field to Patient (after Substance Abuse)
		patient_fields = {
			"Patient": [
				{
					"fieldname": "patient_alcohol_history",
					"label": "Alcohol History",
					"fieldtype": "Table",
					"options": "Patient Alcohol History",
					"insert_after": "patient_substance_abuse_history"
				}
			]
		}
		
		# Add Alcohol History table field to Patient Encounter (after Substance Abuse)
		encounter_fields = {
			"Patient Encounter": [
				{
					"fieldname": "custom_alcohol_history",
					"label": "Alcohol History",
					"fieldtype": "Table",
					"options": "Patient Encounter Alcohol History",
					"insert_after": "custom_substance_abuse_history"
				}
			]
		}
		
		create_custom_fields(patient_fields, update=True)
		create_custom_fields(encounter_fields, update=True)
		
		# Create default Alcohol Types
		alcohol_types = [
			{
				"alcohol_type_name": "Spirits / Hard Liquor (Whisky, Rum, Vodka, Gin, Brandy)",
				"description": "Distilled alcoholic beverages with high alcohol content"
			},
			{
				"alcohol_type_name": "Beer (Light, Strong, Craft, Local Brews)",
				"description": "Fermented alcoholic beverage made from grains"
			},
			{
				"alcohol_type_name": "Wine (Red, White, Fortified Wines)",
				"description": "Fermented alcoholic beverage made from grapes"
			},
			{
				"alcohol_type_name": "Traditional / Local Beverages (Desi Daru, Toddy, Arrack, Country Liquor)",
				"description": "Traditional and locally produced alcoholic beverages"
			},
			{
				"alcohol_type_name": "Mixed Drinks / Cocktails",
				"description": "Alcoholic beverages mixed with other ingredients"
			}
		]
		
		for alcohol_type in alcohol_types:
			if not frappe.db.exists("Alcohol Type", alcohol_type["alcohol_type_name"]):
				doc = frappe.get_doc({
					"doctype": "Alcohol Type",
					"alcohol_type_name": alcohol_type["alcohol_type_name"],
					"description": alcohol_type["description"]
				})
				doc.insert(ignore_permissions=True)
				print(f"✅ Created Alcohol Type: {alcohol_type['alcohol_type_name']}")
		
		frappe.db.commit()
		frappe.clear_cache()
		
		print("\n✅ Successfully added Alcohol History section")
		print("   - Created Alcohol Type master")
		print("   - Created Patient Alcohol History child table")
		print("   - Created Patient Encounter Alcohol History child table")
		print("   - Added table fields to Patient and Patient Encounter")
		print("   - Populated 5 default alcohol types")
		
	except Exception as e:
		print(f"❌ Error adding alcohol history section: {str(e)}")
		import traceback
		traceback.print_exc()
		frappe.db.rollback()

