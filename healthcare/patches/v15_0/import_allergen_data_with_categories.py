import frappe


def execute():
	"""
	Import allergen data with categories and descriptions
	"""
	
	allergens_data = [
		{"name": "Local Anesthetics", "category": "Drug", "description": "Local anesthetic allergy"},
		{"name": "Codeine", "category": "Drug", "description": "Codeine/opioid allergy"},
		{"name": "Aspirin", "category": "Drug", "description": "Aspirin allergy"},
		{"name": "Cockroach Allergen", "category": "Other", "description": "Cockroach allergy"},
		{"name": "ARBs", "category": "Drug", "description": "Angiotensin receptor blocker allergy"},
		{"name": "ACE-Inhibitors", "category": "Drug", "description": "ACE inhibitor medication allergy"},
		{"name": "Food Colourings", "category": "Food", "description": "Food dye allergy"},
		{"name": "Cosmetics/Hair Dye", "category": "Other", "description": "Cosmetic products allergy"},
		{"name": "Nickel", "category": "Drug", "description": "Nickel metal allergy"},
		{"name": "Fragrances", "category": "Other", "description": "Fragrance/perfume allergy"},
		{"name": "MSG/Additives", "category": "Food", "description": "Food additives allergy"},
		{"name": "Sesame Seeds", "category": "Food", "description": "Sesame allergy"},
		{"name": "Wheat", "category": "Food", "description": "Wheat allergy"},
		{"name": "Soy", "category": "Food", "description": "Soy allergy"},
		{"name": "Fish", "category": "Food", "description": "Fish allergy"},
		{"name": "Mold/Fungi", "category": "Other", "description": "Mold and fungi allergy"},
		{"name": "Animal Dander", "category": "Other", "description": "Pet dander allergy"},
		{"name": "Dust Mites", "category": "Other", "description": "Dust mite allergy"},
		{"name": "Pollen", "category": "Other", "description": "Pollen allergy (hay fever)"},
		{"name": "Bee/Wasp Sting", "category": "Other", "description": "Insect sting allergy"},
		{"name": "Gluten", "category": "Food", "description": "Gluten intolerance/allergy"},
		{"name": "Milk", "category": "Food", "description": "Milk/dairy allergy"},
		{"name": "Eggs", "category": "Food", "description": "Egg allergy"},
		{"name": "Tree Nuts", "category": "Food", "description": "Tree nuts allergy (almonds, cashews, walnuts, etc.)"},
		{"name": "Peanuts", "category": "Food", "description": "Peanut allergy"},
		{"name": "Seafood", "category": "Food", "description": "Seafood allergy"},
		{"name": "Shellfish", "category": "Food", "description": "Shellfish allergy"},
		{"name": "Contrast Dye (Iodinated)", "category": "Drug", "description": "Iodine-based contrast media allergy"},
		{"name": "Latex", "category": "Other", "description": "Natural rubber latex allergy"},
		{"name": "NSAIDs", "category": "Drug", "description": "Non-steroidal anti-inflammatory drugs allergy"},
		{"name": "Sulfa Drugs", "category": "Drug", "description": "Sulfonamide antibiotics allergy"},
		{"name": "Penicillin", "category": "Drug", "description": "Antibiotic allergy"}
	]
	
	imported_count = 0
	updated_count = 0
	
	for allergen_data in allergens_data:
		allergen_name = allergen_data["name"]
		
		# Check if allergen already exists
		if frappe.db.exists("Allergen", allergen_name):
			# Update existing allergen with category and description
			doc = frappe.get_doc("Allergen", allergen_name)
			doc.allergen_category = allergen_data["category"]
			doc.description = allergen_data["description"]
			doc.save()
			updated_count += 1
			print(f"✅ Updated: {allergen_name}")
		else:
			# Create new allergen
			doc = frappe.get_doc({
				"doctype": "Allergen",
				"allergen_name": allergen_name,
				"allergen_category": allergen_data["category"],
				"description": allergen_data["description"]
			})
			doc.insert()
			imported_count += 1
			print(f"✅ Created: {allergen_name}")
	
	frappe.db.commit()
	
	print(f"\n✅ Allergen import completed!")
	print(f"   - New allergens created: {imported_count}")
	print(f"   - Existing allergens updated: {updated_count}")
	print(f"   - Total allergens processed: {imported_count + updated_count}")


