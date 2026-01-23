import frappe


def execute():
	"""
	Create Allergen Category doctype and migrate existing allergen categories
	"""
	
	# Create default allergen categories
	categories = [
		{"name": "Drug", "description": "Medications and pharmaceutical products"},
		{"name": "Food", "description": "Food items and ingredients"},
		{"name": "Other", "description": "Environmental and other allergens"}
	]
	
	for category_data in categories:
		if not frappe.db.exists("Allergen Category", category_data["name"]):
			doc = frappe.get_doc({
				"doctype": "Allergen Category",
				"category_name": category_data["name"],
				"description": category_data["description"]
			})
			doc.insert()
			print(f"✅ Created Allergen Category: {category_data['name']}")
		else:
			print(f"✓ Allergen Category already exists: {category_data['name']}")
	
	frappe.db.commit()
	
	# Update existing allergens - convert Select to Link
	# Get all allergens with old category values
	allergens = frappe.db.sql("""
		SELECT name, allergen_category 
		FROM `tabAllergen` 
		WHERE allergen_category IS NOT NULL
	""", as_dict=1)
	
	updated_count = 0
	for allergen in allergens:
		# Category values should already be "Drug", "Food", or "Other"
		# which now exist as Allergen Category records
		if allergen.allergen_category in ["Drug", "Food", "Other"]:
			# No need to update, already correct
			updated_count += 1
		else:
			# If some other value, set to "Other"
			frappe.db.set_value("Allergen", allergen.name, "allergen_category", "Other")
			updated_count += 1
			print(f"✅ Updated allergen: {allergen.name}")
	
	frappe.db.commit()
	
	print(f"\n✅ Allergen Category migration completed!")
	print(f"   - Categories created: 3 (Drug, Food, Other)")
	print(f"   - Allergens verified: {updated_count}")

