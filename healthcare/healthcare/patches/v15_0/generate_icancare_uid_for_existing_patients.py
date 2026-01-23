"""
Patch to generate ICanCare UID for all existing patients
Format: ICC-YYCCCC<6-Digit Random>
"""

import random
import frappe
from frappe.utils import now_datetime


def execute():
	"""
	Generate ICanCare UID for all existing patients who don't have one
	"""
	frappe.db.auto_commit_on_many_writes = True
	
	# Get all patients without UID
	patients = frappe.db.sql(
		"""
		SELECT name, creation
		FROM `tabPatient`
		WHERE uid IS NULL OR uid = ''
		ORDER BY creation ASC
		""",
		as_dict=True
	)
	
	if not patients:
		print("✅ All patients already have ICanCare UID")
		return
	
	print(f"🔄 Generating ICanCare UID for {len(patients)} patients...")
	
	# Track counters per year
	year_counters = {}
	generated_uids = set()
	
	success_count = 0
	error_count = 0
	
	for patient in patients:
		try:
			# Get year from patient creation date
			year = patient.creation.strftime("%y") if patient.creation else now_datetime().strftime("%y")
			
			# Initialize counter for this year
			if year not in year_counters:
				# Find last counter for this year
				last_uid = frappe.db.sql(
					"""
					SELECT uid FROM `tabPatient`
					WHERE uid LIKE %s
					ORDER BY creation DESC
					LIMIT 1
					""",
					f"ICC-{year}%",
					as_dict=True
				)
				
				if last_uid and last_uid[0].uid:
					try:
						year_counters[year] = int(last_uid[0].uid[5:9]) + 1
					except (ValueError, IndexError):
						year_counters[year] = 1
				else:
					year_counters[year] = 1
			
			# Generate unique UID
			uid = None
			max_attempts = 100
			
			for attempt in range(max_attempts):
				counter = year_counters[year]
				random_suffix = random.randint(100000, 999999)
				test_uid = f"ICC-{year}{counter:04d}{random_suffix}"
				
				# Check uniqueness (in DB and in current batch)
				if not frappe.db.exists("Patient", {"uid": test_uid}) and test_uid not in generated_uids:
					uid = test_uid
					generated_uids.add(uid)
					year_counters[year] += 1
					break
			
			if not uid:
				# Fallback: use timestamp-based suffix
				timestamp_suffix = int(now_datetime().timestamp() * 1000000) % 1000000
				uid = f"ICC-{year}{year_counters[year]:04d}{timestamp_suffix:06d}"
				generated_uids.add(uid)
				year_counters[year] += 1
			
			# Update patient with UID
			frappe.db.set_value("Patient", patient.name, "uid", uid, update_modified=False)
			success_count += 1
			
			if success_count % 50 == 0:
				print(f"   ✅ Processed {success_count}/{len(patients)} patients...")
				frappe.db.commit()
		
		except Exception as e:
			error_count += 1
			print(f"   ❌ Error for patient {patient.name}: {str(e)}")
			continue
	
	frappe.db.commit()
	
	print(f"\n✅ UID Generation Complete!")
	print(f"   📊 Success: {success_count} patients")
	if error_count > 0:
		print(f"   ⚠️ Errors: {error_count} patients")
	print(f"   📅 Years processed: {list(year_counters.keys())}")
	print(f"   🔢 Counters: {year_counters}")



















