// Copyright (c) 2016, ESS LLP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Patient Encounter", {
	setup: function(frm) {
		frm.get_field("drug_prescription").grid.editable_fields = [
			{ fieldname: "drug_code", columns: 2 },
			{ fieldname: "drug_name", columns: 2 },
			{ fieldname: "dosage", columns: 2 },
			{ fieldname: "period", columns: 1 },
			{ fieldname: "dosage_form", columns: 2 }
		];
	},

	onload: function(frm) {
		if (frm.is_new()) {
			frm.set_value("encounter_date", frappe.datetime.get_today());
		}
	},

	refresh: function(frm) {
		frm.set_query("patient", function() {
			return {
				filters: { status: "Active" }
			};
		});

		frm.set_query("drug_code", "drug_prescription", function() {
			return {
				filters: { disabled: 0 }
			};
		});

		frm.set_query("lab_test_code", "lab_test_prescription", function() {
			return {
				filters: { disabled: 0, is_billable: 1 }
			};
		});

		frm.set_query("procedure", "procedure_prescription", function() {
			return {
				filters: { disabled: 0, is_billable: 1 }
			};
		});

		frm.set_query("therapy_type", "therapies", function() {
			return {
				filters: { disabled: 0 }
			};
		});

		frm.set_query("practitioner", function() {
			return {
				filters: { status: "Active" }
			};
		});

		// Set query for "who" field in Medical and Surgical History
		if (frm.doc.patient) {
			setup_who_field_queries(frm);
		}

		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__("Order"), function() {
				frappe.new_doc("Service Request");
			});

			frm.add_custom_button(__("Clinical Note"), function() {
				frappe.new_doc("Clinical Note", {
					patient: frm.doc.patient,
					encounter: frm.doc.name
				});
			});
		}

		// Load patient allergies and immunizations
		if (frm.doc.patient) {
			load_patient_allergies(frm);
			load_patient_immunizations(frm);
		}
	},

	patient: function(frm) {
		if (frm.doc.patient) {
			frappe.call({
				method: "healthcare.healthcare.doctype.patient.patient.get_patient_detail",
				args: {
					patient: frm.doc.patient
				},
				callback: function(r) {
					let data = r.message;
					frm.set_value("patient_age", data.patient_age);
					frm.set_value("patient_name", data.patient_name);
					frm.set_value("patient_sex", data.sex);
					frm.set_value("inpatient_record", data.inpatient_record);
					frm.set_value("inpatient_status", data.inpatient_status);
				}
			});

			// Auto-fill allergies and immunizations from Patient
			load_patient_medical_history(frm);
			
			// Setup who field queries
			setup_who_field_queries(frm);
		}
	},

	practitioner: function(frm) {
		if (frm.doc.practitioner) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Healthcare Practitioner",
					filters: { name: frm.doc.practitioner },
					fieldname: ["practitioner_name", "department"]
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value("practitioner_name", r.message.practitioner_name);
						frm.set_value("medical_department", r.message.department);
					}
				}
			});
		}
	},

	appointment: function(frm) {
		if (frm.doc.appointment) {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Patient Appointment",
					name: frm.doc.appointment
				},
				callback: function(r) {
					let values = {
						patient: r.message.patient,
						patient_name: r.message.patient_name,
						patient_sex: r.message.patient_sex,
						patient_age: r.message.patient_age,
						practitioner: r.message.practitioner,
						medical_department: r.message.department,
						appointment_type: r.message.appointment_type,
						invoiced: r.message.invoiced,
						company: r.message.company
					};
					frm.set_value(values);
				}
			});
		}
	},

	get_applicable_treatment_plans: function(frm) {
		if (frm.doc.patient) {
			frappe.call({
				method: "healthcare.healthcare.doctype.patient_encounter.patient_encounter.get_applicable_treatment_plans",
				args: { patient: frm.doc.patient },
				callback: function(r) {
					if (r.message) {
						frappe.msgprint({
							title: __("Treatment Plans"),
							indicator: "green",
							message: r.message
						});
					} else {
						frappe.msgprint(__("No applicable treatment plans for this patient"));
					}
				}
			});
		}
	}
});

// Auto-fill allergies and immunizations from Patient medical history
function load_patient_medical_history(frm) {
	if (!frm.doc.patient) return;

	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Patient",
			name: frm.doc.patient
		},
		callback: function(r) {
			if (r.message) {
				console.log("Patient data received:", r.message);
				
				// Auto-fill allergies if custom_allergy field exists
				if (frm.fields_dict.custom_allergy && r.message.patient_allergy && r.message.patient_allergy.length > 0) {
					console.log("Loading allergies:", r.message.patient_allergy.length);
					frm.clear_table("custom_allergy");
					r.message.patient_allergy.forEach(function(allergy) {
						let row = frm.add_child("custom_allergy");
						// Map Patient Allergy fields to Patient Encounter Allergy fields
						row.allergen = allergy.allergen;
						row.reaction = allergy.reaction;
						row.severity = allergy.severity;
						row.start_date = allergy.start_date;
						row.end_date = allergy.end_date;
						row.comments = allergy.comments;
					});
					frm.refresh_field("custom_allergy");
				}

				// Debug immunization
				console.log("custom_immunization field exists?", !!frm.fields_dict.custom_immunization);
				console.log("patient_immunization data:", r.message.patient_immunization);
				
				// Auto-fill immunizations if custom_immunization field exists
				if (frm.fields_dict.custom_immunization) {
					if (r.message.patient_immunization && r.message.patient_immunization.length > 0) {
						console.log("Loading immunizations:", r.message.patient_immunization.length);
						frm.clear_table("custom_immunization");
						r.message.patient_immunization.forEach(function(imm) {
							let row = frm.add_child("custom_immunization");
							// Map all Patient Immunization fields to Patient Encounter Immunization
							row.vaccine_name = imm.vaccine_name;
							row.manufacturer = imm.manufacturer;
							row.administered_date = imm.administered_date;
							row.dose = imm.dose;
							row.dose_uom = imm.dose_uom;
							row.route = imm.route;
							row.site = imm.site;
							row.location = imm.location;
							row.product = imm.product;
							row.lot = imm.lot;
							row.ndc = imm.ndc;
							console.log("Added immunization row:", imm.vaccine_name);
						});
						frm.refresh_field("custom_immunization");
					} else {
						console.log("No immunization data found in patient");
					}
				} else {
					console.log("custom_immunization field does not exist");
				}

				// Auto-fill Medical History if custom_medical_history field exists
				if (frm.fields_dict.custom_medical_history && r.message.patient_medical_history && r.message.patient_medical_history.length > 0) {
					console.log("Loading medical history:", r.message.patient_medical_history.length);
					frm.clear_table("custom_medical_history");
					r.message.patient_medical_history.forEach(function(history) {
						let row = frm.add_child("custom_medical_history");
						row.diagnosis_category = history.diagnosis_category;
						row.diagnosis = history.diagnosis;
						row.diagnosis_name = history.diagnosis_name;
						row.when = history.when;
						row.undergoing_treatment = history.undergoing_treatment;
						row.cardiovascular = history.cardiovascular;
						row.metabolic = history.metabolic;
						row.cancer_type = history.cancer_type;
						row.genetic_disorder = history.genetic_disorder;
						row.mental_health = history.mental_health;
						row.neurological = history.neurological;
						row.autoimmune = history.autoimmune;
						row.respiratory = history.respiratory;
						row.other_condition = history.other_condition;
						row.comment = history.comment;
					});
					frm.refresh_field("custom_medical_history");
				}

				// Auto-fill Surgical History if custom_surgical_history field exists
				if (frm.fields_dict.custom_surgical_history && r.message.patient_surgical_history && r.message.patient_surgical_history.length > 0) {
					console.log("Loading surgical history:", r.message.patient_surgical_history.length);
					frm.clear_table("custom_surgical_history");
					r.message.patient_surgical_history.forEach(function(history) {
						let row = frm.add_child("custom_surgical_history");
						row.procedure = history.procedure;
						row.procedure_name = history.procedure_name;
						row.when = history.when;
						row.undergoing_treatment = history.undergoing_treatment;
						row.comment = history.comment;
					});
					frm.refresh_field("custom_surgical_history");
				}

				// Auto-fill Smokeless Tobacco History
				if (frm.fields_dict.custom_smokeless_tobacco_history && r.message.patient_smokeless_tobacco_history && r.message.patient_smokeless_tobacco_history.length > 0) {
					console.log("Loading smokeless tobacco history:", r.message.patient_smokeless_tobacco_history.length);
					frm.clear_table("custom_smokeless_tobacco_history");
					r.message.patient_smokeless_tobacco_history.forEach(function(history) {
						let row = frm.add_child("custom_smokeless_tobacco_history");
						row.type = history.type;
						row.frequency = history.frequency;
						row.quantity = history.quantity;
						row.quantity_unit = history.quantity_unit;
						row.discontinued_since = history.discontinued_since;
						row.discontinued_since_unit = history.discontinued_since_unit;
						row.comment = history.comment;
					});
					frm.refresh_field("custom_smokeless_tobacco_history");
				}

				// Auto-fill Smoking Tobacco History
				if (frm.fields_dict.custom_smoking_tobacco_history && r.message.patient_smoking_tobacco_history && r.message.patient_smoking_tobacco_history.length > 0) {
					console.log("Loading smoking tobacco history:", r.message.patient_smoking_tobacco_history.length);
					frm.clear_table("custom_smoking_tobacco_history");
					r.message.patient_smoking_tobacco_history.forEach(function(history) {
						let row = frm.add_child("custom_smoking_tobacco_history");
						row.type = history.type;
						row.frequency = history.frequency;
						row.quantity = history.quantity;
						row.quantity_unit = history.quantity_unit;
						row.discontinued_since = history.discontinued_since;
						row.discontinued_since_unit = history.discontinued_since_unit;
						row.comment = history.comment;
					});
					frm.refresh_field("custom_smoking_tobacco_history");
				}

				// Auto-fill Substance Abuse History
				if (frm.fields_dict.custom_substance_abuse_history && r.message.patient_substance_abuse_history && r.message.patient_substance_abuse_history.length > 0) {
					console.log("Loading substance abuse history:", r.message.patient_substance_abuse_history.length);
					frm.clear_table("custom_substance_abuse_history");
					r.message.patient_substance_abuse_history.forEach(function(history) {
						let row = frm.add_child("custom_substance_abuse_history");
						row.type = history.type;
						row.frequency = history.frequency;
						row.quantity = history.quantity;
						row.quantity_unit = history.quantity_unit;
						row.discontinued_since = history.discontinued_since;
						row.discontinued_since_unit = history.discontinued_since_unit;
						row.comment = history.comment;
					});
					frm.refresh_field("custom_substance_abuse_history");
				}

				// Auto-fill Oral Habits History
				if (frm.fields_dict.custom_oral_habits_history && r.message.patient_oral_habits_history && r.message.patient_oral_habits_history.length > 0) {
					console.log("Loading oral habits history:", r.message.patient_oral_habits_history.length);
					frm.clear_table("custom_oral_habits_history");
					r.message.patient_oral_habits_history.forEach(function(history) {
						let row = frm.add_child("custom_oral_habits_history");
						row.type = history.type;
						row.oral_hygiene_practice = history.oral_hygiene_practice;
						row.dental_visits_frequency = history.dental_visits_frequency;
						row.mouth_wash_use = history.mouth_wash_use;
						row.restricted_mouth_opening = history.restricted_mouth_opening;
						row.comment = history.comment;
					});
					frm.refresh_field("custom_oral_habits_history");
				}

				// Auto-fill Diet History
				if (frm.fields_dict.custom_diet_history && r.message.patient_diet_history && r.message.patient_diet_history.length > 0) {
					console.log("Loading diet history:", r.message.patient_diet_history.length);
					frm.clear_table("custom_diet_history");
					r.message.patient_diet_history.forEach(function(history) {
						let row = frm.add_child("custom_diet_history");
						row.diet_type = history.diet_type;
						row.started_when = history.started_when;
						row.comment = history.comment;
					});
					frm.refresh_field("custom_diet_history");
				}

				// Auto-fill Occupational Exposure History
				if (frm.fields_dict.custom_occupational_exposure_history && r.message.patient_occupational_exposure_history && r.message.patient_occupational_exposure_history.length > 0) {
					console.log("Loading occupational exposure history:", r.message.patient_occupational_exposure_history.length);
					frm.clear_table("custom_occupational_exposure_history");
					r.message.patient_occupational_exposure_history.forEach(function(history) {
						let row = frm.add_child("custom_occupational_exposure_history");
						row.type = history.type;
						row.duration = history.duration;
						row.comment = history.comment;
					});
					frm.refresh_field("custom_occupational_exposure_history");
				}

				// Auto-fill Environmental Factors History
				if (frm.fields_dict.custom_environmental_factors_history && r.message.patient_environmental_factors_history && r.message.patient_environmental_factors_history.length > 0) {
					console.log("Loading environmental factors history:", r.message.patient_environmental_factors_history.length);
					frm.clear_table("custom_environmental_factors_history");
					r.message.patient_environmental_factors_history.forEach(function(history) {
						let row = frm.add_child("custom_environmental_factors_history");
						row.type = history.type;
						row.exposure_level = history.exposure_level;
						row.comment = history.comment;
					});
					frm.refresh_field("custom_environmental_factors_history");
				}

				// Auto-fill Family Medical History
				if (frm.fields_dict.encounter_family_medical_history && r.message.patient_family_medical_history && r.message.patient_family_medical_history.length > 0) {
					console.log("Loading family medical history:", r.message.patient_family_medical_history.length);
					frm.clear_table("encounter_family_medical_history");
					r.message.patient_family_medical_history.forEach(function(history) {
						let row = frm.add_child("encounter_family_medical_history");
						row.diagnosis_category = history.diagnosis_category;
						row.relation = history.relation;
						row.diagnosis = history.diagnosis;
						row.diagnosis_name = history.diagnosis_name;
						row.when = history.when;
						row.undergoing_treatment = history.undergoing_treatment;
						row.cardiovascular = history.cardiovascular;
						row.metabolic = history.metabolic;
						row.cancer_type = history.cancer_type;
						row.genetic_disorder = history.genetic_disorder;
						row.mental_health = history.mental_health;
						row.neurological = history.neurological;
						row.autoimmune = history.autoimmune;
						row.respiratory = history.respiratory;
						row.other_condition = history.other_condition;
						row.comment = history.comment;
					});
					frm.refresh_field("encounter_family_medical_history");
				}

				// Auto-fill Women Health fields (only for Female patients)
				if (r.message.sex === "Female") {
					// Direct fields
					if (frm.fields_dict.encounter_breast_fed) {
						frm.set_value("encounter_breast_fed", r.message.breast_fed || "");
					}
					if (frm.fields_dict.encounter_contraceptive_pills) {
						frm.set_value("encounter_contraceptive_pills", r.message.contraceptive_pills || "");
					}
					if (frm.fields_dict.encounter_hormone_replacement_rx) {
						frm.set_value("encounter_hormone_replacement_rx", r.message.hormone_replacement_rx || "");
					}
					if (frm.fields_dict.encounter_breast_symptoms) {
						frm.set_value("encounter_breast_symptoms", r.message.breast_symptoms || "");
					}
					if (frm.fields_dict.encounter_age_at_menarche) {
						frm.set_value("encounter_age_at_menarche", r.message.age_at_menarche || "");
					}
					if (frm.fields_dict.encounter_age_at_menopause) {
						frm.set_value("encounter_age_at_menopause", r.message.age_at_menopause || "");
					}
					if (frm.fields_dict.encounter_abortion_count) {
						frm.set_value("encounter_abortion_count", r.message.abortion_count || "");
					}
					if (frm.fields_dict.encounter_genitourinary_symptoms) {
						frm.set_value("encounter_genitourinary_symptoms", r.message.genitourinary_symptoms || "");
					}
					if (frm.fields_dict.encounter_women_health_note) {
						frm.set_value("encounter_women_health_note", r.message.women_health_note || "");
					}

					// Children Details table
					if (frm.fields_dict.encounter_children_details && r.message.patient_children_details && r.message.patient_children_details.length > 0) {
						console.log("Loading children details:", r.message.patient_children_details.length);
						frm.clear_table("encounter_children_details");
						r.message.patient_children_details.forEach(function(child) {
							let row = frm.add_child("encounter_children_details");
							row.child_number = child.child_number;
							row.age_at_delivery = child.age_at_delivery;
							row.delivery_type = child.delivery_type;
							row.comment = child.comment;
						});
						frm.refresh_field("encounter_children_details");
					}
				}
			}
		}
	});
}

frappe.ui.form.on("Drug Prescription", {
	drug_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.drug_code) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Medication",
					filters: { name: row.drug_code },
					fieldname: ["medication_name", "default_prescription_dosage", "default_prescription_duration"]
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "drug_name", r.message.medication_name);
						if (r.message.default_prescription_dosage)
							frappe.model.set_value(cdt, cdn, "dosage", r.message.default_prescription_dosage);
						if (r.message.default_prescription_duration)
							frappe.model.set_value(cdt, cdn, "period", r.message.default_prescription_duration);
					}
				}
			});
		}
	},

	drug_name: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.drug_name) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Medication",
					filters: { medication_name: row.drug_name },
					fieldname: ["name", "default_prescription_dosage", "default_prescription_duration"]
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "drug_code", r.message.name);
						if (r.message.default_prescription_dosage)
							frappe.model.set_value(cdt, cdn, "dosage", r.message.default_prescription_dosage);
						if (r.message.default_prescription_duration)
							frappe.model.set_value(cdt, cdn, "period", r.message.default_prescription_duration);
					}
				}
			});
		}
	}
});

frappe.ui.form.on("Lab Prescription", {
	lab_test_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.lab_test_code) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Lab Test Template",
					filters: { name: row.lab_test_code },
					fieldname: ["lab_test_name", "lab_test_rate", "lab_test_description"]
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "lab_test_name", r.message.lab_test_name);
					}
				}
			});
		}
	}
});

frappe.ui.form.on("Procedure Prescription", {
	procedure: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.procedure) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Clinical Procedure Template",
					filters: { name: row.procedure },
					fieldname: ["medical_department"]
				},
				callback: function(r) {
					if (r.message && r.message.medical_department) {
						frappe.model.set_value(cdt, cdn, "department", r.message.medical_department);
					}
				}
			});
		}
	}
});

// Setup who field queries to show patient and related patients
function setup_who_field_queries(frm) {
	if (!frm.doc.patient) return;

	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Patient",
			name: frm.doc.patient
		},
		callback: function(r) {
			if (r.message) {
				let patient_list = [r.message.name]; // Include self
				
				// Add related patients from patient_relation
				if (r.message.patient_relation) {
					r.message.patient_relation.forEach(function(rel) {
						if (rel.patient) {
							patient_list.push(rel.patient);
						}
					});
				}

				// Set query for Medical History "who" field
				if (frm.fields_dict.custom_medical_history) {
					frm.fields_dict.custom_medical_history.grid.get_field('who').get_query = function() {
						return {
							filters: [['Patient', 'name', 'in', patient_list]]
						};
					};
				}

				// Set query for Surgical History "who" field
				if (frm.fields_dict.custom_surgical_history) {
					frm.fields_dict.custom_surgical_history.grid.get_field('who').get_query = function() {
						return {
							filters: [['Patient', 'name', 'in', patient_list]]
						};
					};
				}

				// Note: relation_type (Who) field has been removed from all tables as per client request
			}
		}
	});
}
