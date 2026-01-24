// Copyright (c) 2016, ESS LLP and contributors
// For license information, please see license.txt

frappe.ui.form.on("Patient Encounter", {
	setup: function (frm) {
		frm.get_field("drug_prescription").grid.editable_fields = [
			{ fieldname: "drug_code", columns: 2 },
			{ fieldname: "drug_name", columns: 2 },
			{ fieldname: "dosage", columns: 2 },
			{ fieldname: "period", columns: 1 },
			{ fieldname: "dosage_form", columns: 2 }
		];
	},

	onload: function (frm) {
		if (frm.is_new()) {
			frm.set_value("encounter_date", frappe.datetime.get_today());
		}
	},

	refresh: function (frm) {
		frm.set_query("patient", function () {
			return {
				filters: { status: "Active" }
			};
		});

		frm.set_query("drug_code", "drug_prescription", function () {
			return {
				filters: { disabled: 0 }
			};
		});

		frm.set_query("lab_test_code", "lab_test_prescription", function () {
			return {
				filters: { disabled: 0, is_billable: 1 }
			};
		});

		frm.set_query("procedure", "procedure_prescription", function () {
			return {
				filters: { disabled: 0, is_billable: 1 }
			};
		});

		frm.set_query("therapy_type", "therapies", function () {
			return {
				filters: { disabled: 0 }
			};
		});

		frm.set_query("practitioner", function () {
			return {
				filters: { status: "Active" }
			};
		});

		// Set query for "who" field in Medical and Surgical History
		if (frm.doc.patient) {
			setup_who_field_queries(frm);
		}

		// Load Vital Signs mouth data if already linked
		if (frm.doc.vital_signs) {
			load_vital_signs_mouth_data(frm);
		}

		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__("Order"), function () {
				frappe.new_doc("Service Request");
			});

			frm.add_custom_button(__("Clinical Note"), function () {
				frappe.new_doc("Clinical Note", {
					patient: frm.doc.patient,
					encounter: frm.doc.name
				});
			});
		}

		// Load patient allergies and immunizations (functions not yet defined)
		// if (frm.doc.patient) {
		// 	load_patient_allergies(frm);
		// 	load_patient_immunizations(frm);
		// }

		// Check and render Clinical Examination if practitioner has template
		if (frm.doc.practitioner && frm.doc.show_clinical_examination) {
			// Use polling to wait for fields to be ready
			render_all_clinical_steps(frm);
		} else if (frm.doc.practitioner && !frm.doc.show_clinical_examination) {
			// Check if practitioner has template (for existing encounters)
			check_practitioner_examination_template(frm);
		}
		
		// Setup allergen query filter based on category (with safety check)
		if (frm.fields_dict.custom_allergy) {
			setup_allergen_category_filter(frm);
		}
	},


	// Trigger render when show_clinical_examination changes
	show_clinical_examination: function (frm) {
		if (frm.doc.show_clinical_examination && frm.doc.practitioner) {
			render_all_clinical_steps(frm);
		}
	},

	patient: function (frm) {
		if (frm.doc.patient) {
			frappe.call({
				method: "healthcare.healthcare.doctype.patient.patient.get_patient_detail",
				args: {
					patient: frm.doc.patient
				},
				callback: function (r) {
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

	practitioner: function (frm) {
		if (frm.doc.practitioner) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Healthcare Practitioner",
					filters: { name: frm.doc.practitioner },
					fieldname: ["practitioner_name", "department"]
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value("practitioner_name", r.message.practitioner_name);
						frm.set_value("medical_department", r.message.department);
					}
				}
			});

			// Check if practitioner has Clinical Examination Template assigned
			check_practitioner_examination_template(frm);
		} else {
			// Hide clinical examination if no practitioner
			frm.set_value("show_clinical_examination", 0);
		}
	},

	appointment: function (frm) {
		if (frm.doc.appointment) {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Patient Appointment",
					name: frm.doc.appointment
				},
				callback: function (r) {
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

	vital_signs: function (frm) {
		// Load mouth examination data from Vital Signs when linked
		if (frm.doc.vital_signs) {
			load_vital_signs_mouth_data(frm);
		}
	},

	get_applicable_treatment_plans: function (frm) {
		if (!frm.doc.patient) {
			frappe.msgprint(__("Please select a patient first"));
			return;
		}

		// Build encounter object for the API call
		let encounter = {
			patient: frm.doc.patient,
			symptoms: frm.doc.symptoms || [],
			diagnosis: frm.doc.diagnosis || []
		};

		frappe.call({
			method: "healthcare.healthcare.doctype.patient_encounter.patient_encounter.get_applicable_treatment_plans",
			args: { encounter: encounter },
			callback: function (r) {
				if (r.message && r.message.length > 0) {
					show_treatment_plan_dialog(frm, r.message);
				} else {
					frappe.msgprint({
						title: __("No Treatment Plans"),
						indicator: "orange",
						message: __("No applicable treatment plans found for the selected symptoms/diagnosis. Please create Treatment Plan Templates first.")
					});
				}
			}
		});
	}
});

// Show treatment plan selection dialog
function show_treatment_plan_dialog(frm, plans) {
	let plan_options = plans.map(p => ({
		label: `<strong>${p.template_name}</strong>${p.description ? ' - ' + p.description : ''}`,
		value: p.template_name
	}));

	let d = new frappe.ui.Dialog({
		title: __('Select Treatment Plans to Apply'),
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'plan_info',
				options: `<p class="text-muted">${__('Found {0} applicable treatment plan(s). Select the ones you want to apply:', [plans.length])}</p>`
			},
			{
				fieldtype: 'MultiCheck',
				fieldname: 'selected_plans',
				label: __('Treatment Plans'),
				options: plan_options,
				columns: 1
			}
		],
		primary_action_label: __('Apply Selected Plans'),
		primary_action: function () {
			let selected = d.get_value('selected_plans');
			if (selected && selected.length > 0) {
				frm.call('set_treatment_plans', { treatment_plans: selected })
					.then(() => {
						frm.reload_doc();
						frappe.show_alert({
							message: __('Treatment plans applied successfully'),
							indicator: 'green'
						});
					});
			}
			d.hide();
		}
	});
	d.show();
}

// Auto-fill allergies and immunizations from Patient medical history
function load_patient_medical_history(frm) {
	if (!frm.doc.patient) return;

	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Patient",
			name: frm.doc.patient
		},
		callback: function (r) {
			if (r.message) {
				console.log("Patient data received:", r.message);

				// Auto-fill allergies if custom_allergy field exists
				if (frm.fields_dict.custom_allergy && r.message.patient_allergy && r.message.patient_allergy.length > 0) {
					console.log("Loading allergies:", r.message.patient_allergy.length);
					frm.clear_table("custom_allergy");
					r.message.patient_allergy.forEach(function (allergy) {
						let row = frm.add_child("custom_allergy");
						// Map Patient Allergy fields to Patient Encounter Allergy fields
						row.allergen_category = allergy.allergen_category;
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
						r.message.patient_immunization.forEach(function (imm) {
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
				r.message.patient_medical_history.forEach(function (history) {
					let row = frm.add_child("custom_medical_history");
					row.diagnosis_category = history.diagnosis_category;
					row.diagnosis = history.diagnosis;
					row.diagnosis_name = history.diagnosis_name;
					row.when = history.when;
					row.undergoing_treatment = history.undergoing_treatment;
					row.is_hereditary = history.is_hereditary;
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
					r.message.patient_surgical_history.forEach(function (history) {
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
				r.message.patient_smokeless_tobacco_history.forEach(function (history) {
					let row = frm.add_child("custom_smokeless_tobacco_history");
					row.type = history.type;
					row.frequency = history.frequency;
					row.quantity = history.quantity;
					row.quantity_unit = history.quantity_unit;
					row.started_at_age = history.started_at_age;
					row.discontinued_at_age = history.discontinued_at_age;
					row.used_for_years = history.used_for_years;
					row.comment = history.comment;
				});
				frm.refresh_field("custom_smokeless_tobacco_history");
			}

			// Auto-fill Smoking Tobacco History
			if (frm.fields_dict.custom_smoking_tobacco_history && r.message.patient_smoking_tobacco_history && r.message.patient_smoking_tobacco_history.length > 0) {
				console.log("Loading smoking tobacco history:", r.message.patient_smoking_tobacco_history.length);
				frm.clear_table("custom_smoking_tobacco_history");
			r.message.patient_smoking_tobacco_history.forEach(function (history) {
				let row = frm.add_child("custom_smoking_tobacco_history");
				row.type = history.type;
				row.frequency = history.frequency;
				row.quantity = history.quantity;
				row.quantity_unit = history.quantity_unit;
				row.started_at_age = history.started_at_age;
				row.discontinued_at_age = history.discontinued_at_age;
				row.used_for_years = history.used_for_years;
				row.pack_years = history.pack_years;
				row.bidi_pack_years = history.bidi_pack_years;
				row.comment = history.comment;
				});
				frm.refresh_field("custom_smoking_tobacco_history");
			}

				// Auto-fill Substance Abuse History
			if (frm.fields_dict.custom_substance_abuse_history && r.message.patient_substance_abuse_history && r.message.patient_substance_abuse_history.length > 0) {
				console.log("Loading substance abuse history:", r.message.patient_substance_abuse_history.length);
				frm.clear_table("custom_substance_abuse_history");
				r.message.patient_substance_abuse_history.forEach(function (history) {
					let row = frm.add_child("custom_substance_abuse_history");
					row.type = history.type;
					row.frequency = history.frequency;
					row.quantity = history.quantity;
					row.quantity_unit = history.quantity_unit;
					row.started_at_age = history.started_at_age;
					row.discontinued_at_age = history.discontinued_at_age;
					row.used_for_years = history.used_for_years;
					row.comment = history.comment;
				});
				frm.refresh_field("custom_substance_abuse_history");
			}

			// Auto-fill Alcohol History
			if (frm.fields_dict.custom_alcohol_history && r.message.patient_alcohol_history && r.message.patient_alcohol_history.length > 0) {
				console.log("Loading alcohol history:", r.message.patient_alcohol_history.length);
				frm.clear_table("custom_alcohol_history");
				r.message.patient_alcohol_history.forEach(function (history) {
					let row = frm.add_child("custom_alcohol_history");
					row.type = history.type;
					row.frequency = history.frequency;
					row.quantity = history.quantity;
					row.quantity_unit = history.quantity_unit;
					row.years_of_use = history.years_of_use;
					row.alcohol_years = history.alcohol_years;
					row.comment = history.comment;
				});
				frm.refresh_field("custom_alcohol_history");
			}

		// Load Oral Hygiene direct fields (in Social History section)
			if (r.message.oral_habit_types) {
				frm.set_value("custom_oral_habit_types", r.message.oral_habit_types);
			}
			if (r.message.oral_hygiene_practice) {
				frm.set_value("custom_oral_hygiene_practice", r.message.oral_hygiene_practice);
			}
			if (r.message.dental_visits_frequency) {
				frm.set_value("custom_dental_visits_frequency", r.message.dental_visits_frequency);
			}
			if (r.message.mouth_wash_use) {
				frm.set_value("custom_mouth_wash_use", r.message.mouth_wash_use);
			}
			
			// Auto-fill Oral Habits History
			if (frm.fields_dict.custom_oral_habits_history && r.message.patient_oral_habits_history && r.message.patient_oral_habits_history.length > 0) {
				console.log("Loading oral habits history:", r.message.patient_oral_habits_history.length);
					frm.clear_table("custom_oral_habits_history");
					r.message.patient_oral_habits_history.forEach(function (history) {
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
					r.message.patient_diet_history.forEach(function (history) {
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
					r.message.patient_occupational_exposure_history.forEach(function (history) {
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
					r.message.patient_environmental_factors_history.forEach(function (history) {
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
				r.message.patient_family_medical_history.forEach(function (history) {
					let row = frm.add_child("encounter_family_medical_history");
					row.diagnosis_category = history.diagnosis_category;
					row.relation = history.relation;
					row.diagnosis = history.diagnosis;
					row.diagnosis_name = history.diagnosis_name;
					row.when = history.when;
					row.undergoing_treatment = history.undergoing_treatment;
					row.is_hereditary = history.is_hereditary;
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
						r.message.patient_children_details.forEach(function (child) {
							let row = frm.add_child("encounter_children_details");
							row.child_number = child.child_number;
							row.gender = child.gender;
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
	drug_code: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.drug_code) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Medication",
					filters: { name: row.drug_code },
					fieldname: ["medication_name", "default_prescription_dosage", "default_prescription_duration"]
				},
				callback: function (r) {
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

	drug_name: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.drug_name) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Medication",
					filters: { medication_name: row.drug_name },
					fieldname: ["name", "default_prescription_dosage", "default_prescription_duration"]
				},
				callback: function (r) {
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
	lab_test_code: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.lab_test_code) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Lab Test Template",
					filters: { name: row.lab_test_code },
					fieldname: ["lab_test_name", "lab_test_rate", "lab_test_description"]
				},
				callback: function (r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, "lab_test_name", r.message.lab_test_name);
					}
				}
			});
		}
	}
});

frappe.ui.form.on("Procedure Prescription", {
	procedure: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.procedure) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Clinical Procedure Template",
					filters: { name: row.procedure },
					fieldname: ["medical_department"]
				},
				callback: function (r) {
					if (r.message && r.message.medical_department) {
						frappe.model.set_value(cdt, cdn, "department", r.message.medical_department);
					}
				}
			});
		}
	}
});

// Clinical Exam Complaint child table - handle body_part change to update complaint_type options
frappe.ui.form.on("Clinical Exam Complaint", {
	body_part: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		let bodyPart = row.body_part;
		
		// Get complaints for this body part from BODY_PARTS_CONFIG
		let complaints = [];
		if (typeof BODY_PARTS_CONFIG !== 'undefined' && BODY_PARTS_CONFIG[bodyPart]) {
			complaints = BODY_PARTS_CONFIG[bodyPart].symptoms || [];
		}
		
		// Build options string for the select field
		let options = '\n' + complaints.join('\n');
		
		// Update the complaint_type field options for this row
		let grid_row = frm.fields_dict.exam_complaints.grid.grid_rows_by_docname[cdn];
		if (grid_row) {
			let complaint_field = grid_row.get_field('complaint_type');
			if (complaint_field) {
				complaint_field.df.options = options;
				complaint_field.refresh();
				
				// Clear the current complaint value if it's not in the new options
				if (row.complaint_type && !complaints.includes(row.complaint_type)) {
					frappe.model.set_value(cdt, cdn, 'complaint_type', '');
				}
			}
		}
	},
	
	exam_complaints_add: function(frm, cdt, cdn) {
		// When a new row is added, set up the complaint_type options based on body_part
		let row = locals[cdt][cdn];
		if (row.body_part) {
			// Trigger the body_part handler to set up complaint options
			frappe.ui.form.events["Clinical Exam Complaint"].body_part(frm, cdt, cdn);
		}
	},
	
	form_render: function(frm, cdt, cdn) {
		// When the edit form is rendered, ensure complaint_type options are correct
		let row = locals[cdt][cdn];
		if (row.body_part) {
			// Get complaints for this body part
			let complaints = [];
			if (typeof BODY_PARTS_CONFIG !== 'undefined' && BODY_PARTS_CONFIG[row.body_part]) {
				complaints = BODY_PARTS_CONFIG[row.body_part].symptoms || [];
			}
			
			// Build options string
			let options = '\n' + complaints.join('\n');
			
			// Update the field options in the edit form
			let grid_row = frm.fields_dict.exam_complaints.grid.grid_rows_by_docname[cdn];
			if (grid_row) {
				let complaint_field = grid_row.get_field('complaint_type');
				if (complaint_field) {
					complaint_field.df.options = options;
					complaint_field.refresh();
				}
			}
		}
	}
});

// Clinical Exam Finding child table (Step 2) - handle body_part change and custom edit form
frappe.ui.form.on("Clinical Exam Finding", {
	body_part: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		let bodyPart = row.body_part;
		
		// Clear location and abnormality when body part changes
		frappe.model.set_value(cdt, cdn, 'location', '');
		frappe.model.set_value(cdt, cdn, 'abnormality', '');
		
		// Re-render the custom form for new body part
		setTimeout(() => {
			render_step2_custom_edit_form(frm, cdt, cdn);
		}, 100);
	},
	
	form_render: function(frm, cdt, cdn) {
		// When the edit form is rendered, customize it based on body_part
		// Use setTimeout to ensure DOM is ready
		setTimeout(() => {
			render_step2_custom_edit_form(frm, cdt, cdn);
		}, 50);
	}
});

// Main function to render custom edit form based on body part
function render_step2_custom_edit_form(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let bodyPart = row.body_part;
	
	if (!bodyPart) return;
	
	let config = typeof STEP2_CONFIG !== 'undefined' ? STEP2_CONFIG[bodyPart] : null;
	if (!config) return;
	
	// Get the grid row
	let grid = frm.fields_dict.custom_physical_findings?.grid;
	if (!grid) return;
	
	let grid_row = grid.grid_rows_by_docname[cdn];
	if (!grid_row || !grid_row.grid_form) return;
	
	// Get the form wrapper
	let $form_area = $(grid_row.grid_form.wrapper);
	if (!$form_area.length) return;
	
	// Remove any existing custom form first
	$form_area.find('.step2-custom-edit-form').remove();
	
	// Hide ALL original fields except body_part and note
	$form_area.find('.frappe-control[data-fieldname="location"]').hide();
	$form_area.find('.frappe-control[data-fieldname="abnormality"]').hide();
	$form_area.find('.frappe-control[data-fieldname="column_break_1"]').hide();
	$form_area.find('.frappe-control[data-fieldname="section_break_2"]').hide();
	
	// Create custom form based on body part type
	let customFormHtml = '';
	
	if (config.special === 'mouth') {
		customFormHtml = create_mouth_edit_form_html(row);
	} else if (config.special === 'teeth') {
		customFormHtml = create_teeth_edit_form_html(row);
	} else {
		// Face, Neck - standard form
		customFormHtml = create_standard_edit_form_html(row, bodyPart, config);
	}
	
	// Insert custom form after body_part field
	let $bodyPartField = $form_area.find('.frappe-control[data-fieldname="body_part"]');
	if ($bodyPartField.length) {
		$bodyPartField.after(`<div class="step2-custom-edit-form" style="grid-column: 1 / -1;">${customFormHtml}</div>`);
	}
	
	// Setup event handlers
	if (config.special === 'mouth') {
		setup_mouth_edit_handlers($form_area, cdt, cdn);
	} else if (config.special === 'teeth') {
		setup_teeth_edit_handlers($form_area, cdt, cdn);
	} else {
		setup_standard_edit_handlers($form_area, cdt, cdn, config);
	}
}

// Create HTML for standard edit form (Face, Neck)
function create_standard_edit_form_html(row, bodyPart, config) {
	let currentLocation = row.location || '';
	let currentAbnormalities = (row.abnormality || '').split(', ').map(s => s.trim()).filter(s => s);
	
	let locationOptions = config.locations.map(loc => 
		`<option value="${loc}" ${loc === currentLocation ? 'selected' : ''}>${loc}</option>`
	).join('');
	
	let abnormalityCheckboxes = config.abnormalities.map(abn => {
		let isChecked = currentAbnormalities.includes(abn) ? 'checked' : '';
		return `
			<label class="step2-edit-abn-label" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; margin: 3px; background: ${isChecked ? 'rgba(36, 144, 239, 0.15)' : 'var(--control-bg)'}; border: 1px solid ${isChecked ? '#2490ef' : 'var(--border-color)'}; border-radius: 6px; cursor: pointer; font-size: 13px; transition: all 0.2s;">
				<input type="checkbox" class="step2-edit-abn-check" data-abn="${abn}" ${isChecked} style="width: 16px; height: 16px; accent-color: #2490ef;">
				<span style="color: ${isChecked ? '#2490ef' : 'var(--text-color)'}; font-weight: ${isChecked ? '600' : 'normal'};">${abn}</span>
			</label>
		`;
	}).join('');
	
	return `
		<div class="row" style="margin-top: 15px;">
			<div class="col-md-6">
				<div class="form-group">
					<label class="control-label" style="font-size: 12px; color: var(--text-muted);">Location <span class="text-danger">*</span></label>
					<select class="form-control step2-edit-location">
						<option value="">Select Location...</option>
						${locationOptions}
					</select>
				</div>
			</div>
		</div>
		<div style="margin-top: 15px;">
			<label class="control-label" style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px; display: block;">Abnormalities (Multiple Select)</label>
			<div style="display: flex; flex-wrap: wrap;">
				${abnormalityCheckboxes}
			</div>
		</div>
	`;
}

// Create HTML for Mouth edit form
function create_mouth_edit_form_html(row) {
	// Parse existing abnormality data
	let abnData = row.abnormality || '';
	let mouthData = {
		fingers: '', opening: '', measured: '', tongue: [], protrusion: '', hygiene: '', prosthesis: ''
	};
	
	if (abnData) {
		abnData.split(' | ').forEach(part => {
			let [key, val] = part.split(': ');
			if (key && val) {
				key = key.toLowerCase().trim();
				if (key === 'fingers') mouthData.fingers = val;
				else if (key === 'opening') mouthData.opening = val.replace('mm', '');
				else if (key === 'measured') mouthData.measured = val;
				else if (key === 'tongue') mouthData.tongue = val.split(', ');
				else if (key === 'protrusion') mouthData.protrusion = val.replace('mm', '');
				else if (key === 'hygiene') mouthData.hygiene = val;
				else if (key === 'prosthesis') mouthData.prosthesis = val;
			}
		});
	}
	
	// Check if Normal or Abnormal
	let isNormal = mouthData.tongue.includes('Normal');
	let isAbnormal = mouthData.tongue.some(t => t !== 'Normal');
	
	// Abnormal conditions checkboxes (excluding Normal)
	let abnormalConditions = ['Painful', 'Deviation Left', 'Deviation Right', 'Restricted'];
	let conditionCheckboxes = abnormalConditions.map(opt => {
		let isChecked = mouthData.tongue.includes(opt) ? 'checked' : '';
		return `
			<label style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; margin: 3px; background: ${isChecked ? 'rgba(36, 144, 239, 0.15)' : 'var(--control-bg)'}; border: 1px solid ${isChecked ? '#2490ef' : 'var(--border-color)'}; border-radius: 6px; cursor: pointer; font-size: 13px;">
				<input type="checkbox" class="step2-edit-tongue-condition" data-val="${opt}" ${isChecked} style="width: 16px; height: 16px; accent-color: #2490ef;">
				<span style="color: ${isChecked ? '#2490ef' : 'var(--text-color)'};">${opt}</span>
			</label>
		`;
	}).join('');
	
	return `
		<div style="margin-top: 15px;">
			<label class="control-label" style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px; display: block;">Mouth Opening</label>
			<div class="row">
				<div class="col-md-3">
					<div class="form-group">
						<label class="control-label" style="font-size: 11px; color: var(--text-muted);">Fingers</label>
						<select class="form-control step2-edit-mouth-fingers">
							<option value="">Select...</option>
							<option value="One" ${mouthData.fingers === 'One' ? 'selected' : ''}>One</option>
							<option value="Two" ${mouthData.fingers === 'Two' ? 'selected' : ''}>Two</option>
							<option value="Three" ${mouthData.fingers === 'Three' ? 'selected' : ''}>Three</option>
							<option value="Four" ${mouthData.fingers === 'Four' ? 'selected' : ''}>Four</option>
						</select>
					</div>
				</div>
				<div class="col-md-3">
					<div class="form-group">
						<label class="control-label" style="font-size: 11px; color: var(--text-muted);">Opening (mm)</label>
						<input type="number" class="form-control step2-edit-mouth-opening" value="${mouthData.opening}">
					</div>
				</div>
				<div class="col-md-3">
					<div class="form-group">
						<label class="control-label" style="font-size: 11px; color: var(--text-muted);">Measured With</label>
						<select class="form-control step2-edit-mouth-measured">
							<option value="">Select...</option>
							<option value="TrisCare" ${mouthData.measured === 'TrisCare' ? 'selected' : ''}>TrisCare</option>
							<option value="Caliper" ${mouthData.measured === 'Caliper' ? 'selected' : ''}>Caliper</option>
							<option value="Other" ${mouthData.measured === 'Other' ? 'selected' : ''}>Other</option>
						</select>
					</div>
				</div>
			</div>
		</div>
		<div style="margin-top: 15px;">
			<label class="control-label" style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px; display: block;">Tongue Movement</label>
			<div style="display: flex; gap: 20px; margin-bottom: 15px;">
				<label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 8px 16px; background: var(--control-bg); border: 2px solid ${isNormal ? '#2490ef' : 'var(--border-color)'}; border-radius: 6px; font-weight: ${isNormal ? '600' : '500'};">
					<input type="radio" name="tongue_status_edit" class="step2-edit-tongue-radio" value="normal" ${isNormal ? 'checked' : ''} style="width: 18px; height: 18px; cursor: pointer;"> Normal
				</label>
				<label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 8px 16px; background: var(--control-bg); border: 2px solid ${isAbnormal ? '#2490ef' : 'var(--border-color)'}; border-radius: 6px; font-weight: ${isAbnormal ? '600' : '500'};">
					<input type="radio" name="tongue_status_edit" class="step2-edit-tongue-radio" value="abnormal" ${isAbnormal ? 'checked' : ''} style="width: 18px; height: 18px; cursor: pointer;"> Abnormal
				</label>
			</div>
			<div class="step2-edit-tongue-conditions-wrapper" style="display: ${isAbnormal ? 'block' : 'none'}; padding: 15px; background: var(--subtle-bg); border-radius: 6px; border: 1px solid var(--border-color);">
				<label style="font-weight: 500; display: block; margin-bottom: 10px; color: var(--heading-color);">Select Conditions:</label>
				<div style="display: flex; flex-wrap: wrap;">${conditionCheckboxes}</div>
			</div>
		</div>
		<div class="row" style="margin-top: 15px;">
			<div class="col-md-3">
				<div class="form-group">
					<label class="control-label" style="font-size: 12px; color: var(--text-muted);">Tongue Protrusion (mm)</label>
					<input type="number" class="form-control step2-edit-mouth-protrusion" value="${mouthData.protrusion}">
				</div>
			</div>
			<div class="col-md-3">
				<div class="form-group">
					<label class="control-label" style="font-size: 12px; color: var(--text-muted);">Oral Hygiene</label>
					<select class="form-control step2-edit-mouth-hygiene">
						<option value="">Select...</option>
						<option value="Good" ${mouthData.hygiene === 'Good' ? 'selected' : ''}>Good</option>
						<option value="Moderate" ${mouthData.hygiene === 'Moderate' ? 'selected' : ''}>Moderate</option>
						<option value="Poor" ${mouthData.hygiene === 'Poor' ? 'selected' : ''}>Poor</option>
					</select>
				</div>
			</div>
			<div class="col-md-3">
				<div class="form-group">
					<label class="control-label" style="font-size: 12px; color: var(--text-muted);">Prosthesis</label>
					<select class="form-control step2-edit-mouth-prosthesis">
						<option value="">Select...</option>
						<option value="Yes" ${mouthData.prosthesis === 'Yes' ? 'selected' : ''}>Yes</option>
						<option value="No" ${mouthData.prosthesis === 'No' ? 'selected' : ''}>No</option>
					</select>
				</div>
			</div>
		</div>
	`;
}

// Create HTML for Teeth edit form
function create_teeth_edit_form_html(row) {
	let teethNumbers = '';
	if (row.location && row.location.includes('Teeth #')) {
		teethNumbers = row.location.replace('Teeth #', '');
	}
	let currentIssues = (row.abnormality || '').split(', ').map(s => s.trim()).filter(s => s);
	
	let teethIssues = STEP2_CONFIG['Teeth']?.teethIssues || [];
	let issueCheckboxes = teethIssues.map(issue => {
		let isChecked = currentIssues.includes(issue) ? 'checked' : '';
		return `
			<label style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; margin: 3px; background: ${isChecked ? 'rgba(36, 144, 239, 0.15)' : 'var(--control-bg)'}; border: 1px solid ${isChecked ? '#2490ef' : 'var(--border-color)'}; border-radius: 6px; cursor: pointer; font-size: 13px;">
				<input type="checkbox" class="step2-edit-teeth-issue" data-issue="${issue}" ${isChecked} style="width: 16px; height: 16px; accent-color: #2490ef;">
				<span style="color: ${isChecked ? '#2490ef' : 'var(--text-color)'};">${issue}</span>
			</label>
		`;
	}).join('');
	
	return `
		<div class="row" style="margin-top: 15px;">
			<div class="col-md-6">
				<div class="form-group">
					<label class="control-label" style="font-size: 12px; color: var(--text-muted);">Teeth Numbers <span class="text-danger">*</span></label>
					<input type="text" class="form-control step2-edit-teeth-numbers" value="${teethNumbers}" placeholder="e.g., 11, 12, 21, 22">
					<small style="color: var(--text-muted);">Enter teeth numbers separated by commas</small>
				</div>
			</div>
		</div>
		<div style="margin-top: 15px;">
			<label class="control-label" style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px; display: block;">Teeth Issues (Multiple Select)</label>
			<div style="display: flex; flex-wrap: wrap;">${issueCheckboxes}</div>
		</div>
	`;
}

// Setup handlers for standard edit form (Face, Neck)
function setup_standard_edit_handlers($form_area, cdt, cdn, config) {
	// Location change
	$($form_area).find('.step2-edit-location').on('change', function() {
		frappe.model.set_value(cdt, cdn, 'location', $(this).val());
	});
	
	// Abnormality checkboxes change
	$($form_area).find('.step2-edit-abn-check').on('change', function() {
		let selected = [];
		$($form_area).find('.step2-edit-abn-check:checked').each(function() {
			selected.push($(this).data('abn'));
		});
		frappe.model.set_value(cdt, cdn, 'abnormality', selected.join(', '));
		
		// Update checkbox styling
		$($form_area).find('.step2-edit-abn-label').each(function() {
			let $checkbox = $(this).find('.step2-edit-abn-check');
			let isChecked = $checkbox.is(':checked');
			$(this).css({
				'background': isChecked ? 'rgba(36, 144, 239, 0.15)' : 'var(--control-bg)',
				'border-color': isChecked ? '#2490ef' : 'var(--border-color)'
			});
			$(this).find('span').css({
				'color': isChecked ? '#2490ef' : 'var(--text-color)',
				'font-weight': isChecked ? '600' : 'normal'
			});
		});
	});
}

// Setup handlers for Mouth edit form
function setup_mouth_edit_handlers($form_area, cdt, cdn) {
	function updateMouthData() {
		let parts = [];
		let fingers = $($form_area).find('.step2-edit-mouth-fingers').val();
		let opening = $($form_area).find('.step2-edit-mouth-opening').val();
		let measured = $($form_area).find('.step2-edit-mouth-measured').val();
		let tongue = [];
		
		// Check tongue status
		let tongueStatus = $($form_area).find('.step2-edit-tongue-radio:checked').val();
		if (tongueStatus === 'normal') {
			tongue.push('Normal');
		} else if (tongueStatus === 'abnormal') {
			// Get selected abnormal conditions
			$($form_area).find('.step2-edit-tongue-condition:checked').each(function() {
				tongue.push($(this).data('val'));
			});
		}
		
		let protrusion = $($form_area).find('.step2-edit-mouth-protrusion').val();
		let hygiene = $($form_area).find('.step2-edit-mouth-hygiene').val();
		let prosthesis = $($form_area).find('.step2-edit-mouth-prosthesis').val();
		
		if (fingers) parts.push('Fingers: ' + fingers);
		if (opening) parts.push('Opening: ' + opening + 'mm');
		if (measured) parts.push('Measured: ' + measured);
		if (tongue.length) parts.push('Tongue: ' + tongue.join(', '));
		if (protrusion) parts.push('Protrusion: ' + protrusion + 'mm');
		if (hygiene) parts.push('Hygiene: ' + hygiene);
		if (prosthesis) parts.push('Prosthesis: ' + prosthesis);
		
		frappe.model.set_value(cdt, cdn, 'location', 'Mouth Opening');
		frappe.model.set_value(cdt, cdn, 'abnormality', parts.join(' | '));
	}
	
	// Tongue radio button change - show/hide conditions
	$($form_area).find('.step2-edit-tongue-radio').on('change', function() {
		let $wrapper = $($form_area).find('.step2-edit-tongue-conditions-wrapper');
		
		// Update radio button styling
		$($form_area).find('.step2-edit-tongue-radio').each(function() {
			let $thisLabel = $(this).closest('label');
			let isChecked = $(this).is(':checked');
			$thisLabel.css({
				'border-color': isChecked ? '#2490ef' : 'var(--border-color)',
				'font-weight': isChecked ? '600' : '500'
			});
		});
		
		if ($(this).val() === 'abnormal') {
			$wrapper.show();
		} else {
			$wrapper.hide();
			// Uncheck all conditions if normal is selected
			$wrapper.find('.step2-edit-tongue-condition').prop('checked', false);
		}
		updateMouthData();
	});
	
	// Tongue condition checkboxes styling and update
	$($form_area).find('.step2-edit-tongue-condition').on('change', function() {
		let $label = $(this).closest('label');
		let isChecked = $(this).is(':checked');
		$label.css({
			'background': isChecked ? 'rgba(36, 144, 239, 0.15)' : 'var(--control-bg)',
			'border-color': isChecked ? '#2490ef' : 'var(--border-color)'
		});
		$label.find('span').css({
			'color': isChecked ? '#2490ef' : 'var(--text-color)'
		});
		updateMouthData();
	});
	
	// All other fields
	$($form_area).find('.step2-edit-mouth-fingers, .step2-edit-mouth-opening, .step2-edit-mouth-measured, .step2-edit-mouth-protrusion, .step2-edit-mouth-hygiene, .step2-edit-mouth-prosthesis').on('change keyup', updateMouthData);
}

// Setup handlers for Teeth edit form
function setup_teeth_edit_handlers($form_area, cdt, cdn) {
	function updateTeethData() {
		let numbers = $($form_area).find('.step2-edit-teeth-numbers').val();
		let issues = [];
		$($form_area).find('.step2-edit-teeth-issue:checked').each(function() {
			issues.push($(this).data('issue'));
		});
		
		frappe.model.set_value(cdt, cdn, 'location', numbers ? 'Teeth #' + numbers : '');
		frappe.model.set_value(cdt, cdn, 'abnormality', issues.join(', '));
	}
	
	$($form_area).find('.step2-edit-teeth-numbers, .step2-edit-teeth-issue').on('change keyup', updateTeethData);
}

// Setup who field queries to show patient and related patients
function setup_who_field_queries(frm) {
	if (!frm.doc.patient) return;

	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Patient",
			name: frm.doc.patient
		},
		callback: function (r) {
			if (r.message) {
				let patient_list = [r.message.name]; // Include self

				// Add related patients from patient_relation
				if (r.message.patient_relation) {
					r.message.patient_relation.forEach(function (rel) {
						if (rel.patient) {
							patient_list.push(rel.patient);
						}
					});
				}

				// Set query for Medical History "who" field
				if (frm.fields_dict.custom_medical_history) {
					frm.fields_dict.custom_medical_history.grid.get_field('who').get_query = function () {
						return {
							filters: [['Patient', 'name', 'in', patient_list]]
						};
					};
				}

				// Set query for Surgical History "who" field
				if (frm.fields_dict.custom_surgical_history) {
					frm.fields_dict.custom_surgical_history.grid.get_field('who').get_query = function () {
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

// Clinical Examination Integration
function setup_clinical_examination_button(frm) {
	// Get templates assigned to this practitioner
	frappe.call({
		method: "healthcare.healthcare.doctype.clinical_examination_template.clinical_examination_template.get_templates_for_practitioner",
		args: { practitioner: frm.doc.practitioner },
		callback: function (r) {
			if (r.message && r.message.length > 0) {
				let templates = r.message;

				// Add Clinical Examination button with dropdown
				if (templates.length === 1) {
					// Single template - direct button
					frm.add_custom_button(__("Clinical Examination"), function () {
						create_clinical_examination(frm, templates[0].template_name);
					}, __("Create"));
				} else {
					// Multiple templates - dropdown
					templates.forEach(function (template) {
						let label = template.examination_type;
						if (template.is_default) {
							label += " ★";
						}
						frm.add_custom_button(__(label), function () {
							create_clinical_examination(frm, template.template_name);
						}, __("Clinical Examination"));
					});
				}

				// Show default form section in encounter if practitioner has default template
				let default_template = templates.find(t => t.is_default);
				if (default_template) {
					render_default_clinical_exam_section(frm, default_template);
				}
			}
		}
	});
}

function create_clinical_examination(frm, template_name) {
	frappe.call({
		method: "healthcare.healthcare.doctype.clinical_examination.clinical_examination.create_examination_from_encounter",
		args: {
			encounter: frm.doc.name,
			template: template_name
		},
		callback: function (r) {
			if (r.message) {
				frappe.set_route("Form", "Clinical Examination", r.message.name);
			}
		}
	});
}

function render_default_clinical_exam_section(frm, template) {
	// Add a section in the form showing quick access to clinical examination
	let wrapper = frm.fields_dict.physical_examination ?
		frm.fields_dict.physical_examination.$wrapper.parent() : null;

	if (!wrapper) return;

	// Check if section already exists
	if (wrapper.find('.clinical-exam-quick-access').length > 0) {
		return;
	}

	let html = `
		<div class="clinical-exam-quick-access" style="
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
			border-radius: 10px;
			padding: 20px;
			margin: 15px 0;
			color: #fff;
		">
			<div class="row">
				<div class="col-md-8">
					<h5 style="margin: 0 0 5px 0; color: #fff;">
						<i class="fa fa-stethoscope"></i> ${template.examination_type}
					</h5>
					<p style="margin: 0; opacity: 0.9; font-size: 13px;">
						${template.description || 'Clinical Examination Form assigned to you'}
					</p>
				</div>
				<div class="col-md-4 text-right">
					<button class="btn btn-light btn-sm open-clinical-exam" 
						data-template="${template.template_name}"
						style="font-weight: 600;">
						<i class="fa fa-external-link"></i> Open Form
					</button>
				</div>
			</div>
		</div>
	`;

	wrapper.prepend(html);

	wrapper.find('.open-clinical-exam').on('click', function () {
		let template_name = $(this).data('template');
		create_clinical_examination(frm, template_name);
	});
}

// Check if practitioner has examination template assigned (from Healthcare Practitioner settings)
function check_practitioner_examination_template(frm) {
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Healthcare Practitioner",
			filters: { name: frm.doc.practitioner },
			fieldname: ["default_examination_template"]
		},
		callback: function (r) {
			if (r.message && r.message.default_examination_template) {
				// Practitioner has clinical examination template assigned
				frm.set_value("show_clinical_examination", 1);

				// Set examination template directly from practitioner's default
				if (!frm.doc.exam_examination_template) {
					frm.set_value("exam_examination_template", r.message.default_examination_template);
				}

				// Get template details for alert
				frappe.call({
					method: "frappe.client.get_value",
					args: {
						doctype: "Clinical Examination Template",
						filters: { name: r.message.default_examination_template },
						fieldname: ["template_name", "examination_type"]
					},
					callback: function (template_r) {
						if (template_r.message) {

							// Render diagram and images
							setTimeout(() => {
								render_clinical_exam_diagram(frm);
								render_clinical_images_section(frm);
								render_step4_pictures(frm);
							}, 500);

							frappe.show_alert({
								message: __('Clinical Examination: {0}', [template_r.message.template_name]),
								indicator: 'blue'
							});
						}
					}
				});
			} else {
				// No clinical examination template - hide section
				frm.set_value("show_clinical_examination", 0);
			}
		}
	});
}

// Render all clinical steps with polling to wait for fields
function render_all_clinical_steps(frm, attempt = 0) {
	const maxAttempts = 10;
	const delay = 300;

	// Check if key fields have their wrappers ready
	let step1_ready = frm.fields_dict.exam_step1_table_html && frm.fields_dict.exam_step1_table_html.$wrapper && frm.fields_dict.exam_step1_table_html.$wrapper.length > 0;
	let step2_ready = (frm.fields_dict.exam_step2_table_html && frm.fields_dict.exam_step2_table_html.$wrapper && frm.fields_dict.exam_step2_table_html.$wrapper.length > 0) || step1_ready;

	let step4_ready = frm.fields_dict.exam_pictures_taken_by && frm.fields_dict.exam_pictures_taken_by.$wrapper && frm.fields_dict.exam_pictures_taken_by.$wrapper.length > 0;

	if (step1_ready || step2_ready || step4_ready || attempt >= maxAttempts) {
		// At least some fields are ready, render them
		console.log(`Clinical steps rendering (attempt ${attempt + 1}): Step1=${step1_ready}, Step2=${step2_ready}, Step4=${step4_ready}`);

		if (step1_ready) render_step1_table_form(frm);
		if (step2_ready) render_step2_table_form(frm);
		render_clinical_exam_diagram(frm);
		render_clinical_images_section(frm);
		// Always try to render Step 4, even if field not detected
		render_step4_pictures(frm);

		// If not all ready and we haven't maxed out, retry for remaining fields
		if ((!step1_ready || !step2_ready || !step4_ready) && attempt < maxAttempts) {
			setTimeout(() => render_all_clinical_steps(frm, attempt + 1), delay);
		}
	} else {
		// Fields not ready yet, try again
		if (attempt < maxAttempts) {
			setTimeout(() => render_all_clinical_steps(frm, attempt + 1), delay);
		}
	}
}

// Clinical Examination Diagram Rendering - STEP 3
function render_clinical_exam_diagram(frm) {
	// Render both old diagram and new STEP 3 interactive diagrams
	render_step3_interactive_diagrams(frm);
	// Also render existing lesions table
	setTimeout(() => render_step3_lesions_table(frm), 500);
}


// STEP 3 - Professional Interactive Diagrams
function render_step3_interactive_diagrams(frm) {
	if (!frm.fields_dict.exam_diagram_interactive) return;

	let wrapper = frm.fields_dict.exam_diagram_interactive.$wrapper;
	wrapper.empty();

	// Professional Medical Diagrams with 3D-like styling
	let svg_html = `
		<style>
			.diagram-container {
				padding: 25px;
				background: linear-gradient(145deg, #1a1a2e 0%, #0f0f23 50%, #1a1a2e 100%);
				border-radius: 16px;
				margin: 15px 0;
				box-shadow: 0 10px 40px rgba(0,0,0,0.3);
			}
			.diagram-header {
				text-align: center;
				margin-bottom: 20px;
				padding-bottom: 15px;
				border-bottom: 1px solid rgba(255,255,255,0.1);
			}
			.diagram-header h4 {
				color: #fff;
				margin: 0 0 5px 0;
				font-weight: 600;
				text-shadow: 0 2px 4px rgba(0,0,0,0.3);
			}
			.diagram-header small {
				color: rgba(255,255,255,0.6);
			}
			.diagrams-grid {
				display: grid;
				grid-template-columns: repeat(2, 1fr);
				gap: 25px;
			}
			@media (max-width: 1000px) {
				.diagrams-grid {
					grid-template-columns: 1fr;
				}
			}
			.diagram-card {
				background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
				border-radius: 12px;
				padding: 20px;
				box-shadow: 0 4px 20px rgba(0,0,0,0.15);
				transition: all 0.3s ease;
			}
			.diagram-card:hover {
				transform: translateY(-5px);
				box-shadow: 0 8px 30px rgba(0,0,0,0.2);
			}
			.diagram-card h6 {
				text-align: center;
				color: #2c3e50;
				margin-bottom: 15px;
				font-weight: 600;
				font-size: 14px;
			}
			.clickable-region {
			cursor: pointer;
			transition: all 0.2s ease;
			pointer-events: all;
		}
		.clickable-region:hover {
			opacity: 0.7;
			filter: brightness(1.1);
		}
		text.clickable-region {
			cursor: pointer;
			pointer-events: all;
			user-select: none;
		}
		text.clickable-region:hover {
			opacity: 0.8;
			font-weight: bold;
		}
			.region-label {
				font-size: 8px;
				fill: #333;
				pointer-events: none;
			}
			.lesion-marker {
				fill: #ff4444;
				stroke: #fff;
				stroke-width: 2;
				filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
				cursor: pointer;
			}
			.legend-box {
				background: rgba(255,255,255,0.05);
				border-radius: 8px;
				padding: 15px;
				margin-top: 20px;
			}
			.legend-item {
				display: inline-flex;
				align-items: center;
				margin-right: 15px;
				color: rgba(255,255,255,0.8);
				font-size: 12px;
			}
			.legend-color {
				width: 12px;
				height: 12px;
				border-radius: 50%;
				margin-right: 6px;
			}
		</style>
		
		<div class="diagram-container">
			<div class="diagram-header">
				<h4><i class="fa fa-crosshairs"></i> STEP 3 - Representation MARKING on Diagram</h4>
				<small>Click on any region to mark a lesion. Marked lesions will appear in the table below.</small>
			</div>
			
			<div class="diagrams-grid">
				<!-- FACE & LIPS DIAGRAM - Detailed Oral Regions -->
				<div class="diagram-card">
					<h6><i class="fa fa-user"></i> Face & Lips - Oral Regions</h6>
					<svg viewBox="0 0 400 450" style="width: 100%; display: block; margin: 0 auto;">
						<defs>
							<radialGradient id="skinGradient" cx="50%" cy="40%" r="60%">
								<stop offset="0%" style="stop-color:#ffe4c4"/>
								<stop offset="100%" style="stop-color:#deb887"/>
							</radialGradient>
							<linearGradient id="lipGradFace" x1="0%" y1="0%" x2="0%" y2="100%">
								<stop offset="0%" style="stop-color:#e07070"/>
								<stop offset="100%" style="stop-color:#cc5555"/>
							</linearGradient>
						</defs>
						
						<!-- Face Outline -->
						<ellipse cx="200" cy="120" rx="90" ry="100" fill="url(#skinGradient)" stroke="#c9a77a" stroke-width="2"/>
						
						<!-- Hair -->
						<ellipse cx="200" cy="45" rx="95" ry="50" fill="#4a3728"/>
						
						<!-- Eyes (decorative) -->
						<ellipse cx="160" cy="95" rx="20" ry="12" fill="#fff" stroke="#333" stroke-width="1.5"/>
						<ellipse cx="240" cy="95" rx="20" ry="12" fill="#fff" stroke="#333" stroke-width="1.5"/>
						<circle cx="160" cy="95" r="7" fill="#4a3728"/>
						<circle cx="240" cy="95" r="7" fill="#4a3728"/>
						
						<!-- Nose (decorative) -->
						<path d="M200,85 L195,125 Q200,133 205,125 L200,85" fill="#deb887" stroke="#c9a77a"/>
						
					<!-- Buccal Mucosa (Cheeks) - maps to oral location -->
					<ellipse cx="120" cy="140" rx="30" ry="35" fill="rgba(255,182,193,0.3)" stroke="#cc8888" stroke-width="2" class="clickable-region" data-region="buccal-mucosa" data-side="Left" data-diagram="Face"/>
					<ellipse cx="280" cy="140" rx="30" ry="35" fill="rgba(255,182,193,0.3)" stroke="#cc8888" stroke-width="2" class="clickable-region" data-region="buccal-mucosa" data-side="Right" data-diagram="Face"/>
					<text x="120" y="145" text-anchor="middle" font-size="9" fill="#993333" class="clickable-region" data-region="buccal-mucosa" data-side="Left" data-diagram="Face" style="cursor: pointer; pointer-events: all;">Buccal L</text>
					<text x="280" y="145" text-anchor="middle" font-size="9" fill="#993333" class="clickable-region" data-region="buccal-mucosa" data-side="Right" data-diagram="Face" style="cursor: pointer; pointer-events: all;">Buccal R</text>
						
						<!-- DETAILED LIPS SECTION -->
						<text x="200" y="175" text-anchor="middle" font-size="11" font-weight="bold" fill="#663333">LIPS & MOUTH</text>
						
						<!-- Upper Lip Left -->
						<path d="M145,195 Q172,180 200,190" fill="url(#lipGradFace)" stroke="#993333" stroke-width="2" class="clickable-region" data-region="upper-lip" data-side="Left" data-diagram="Face"/>
						<text x="168" y="188" text-anchor="middle" font-size="7" fill="#fff">UL-L</text>
						<!-- Upper Lip Right -->
						<path d="M200,190 Q228,180 255,195" fill="url(#lipGradFace)" stroke="#993333" stroke-width="2" class="clickable-region" data-region="upper-lip" data-side="Right" data-diagram="Face"/>
						<text x="232" y="188" text-anchor="middle" font-size="7" fill="#fff">UL-R</text>
						
						<!-- Lower Lip Left -->
						<path d="M145,210 Q172,230 200,215" fill="url(#lipGradFace)" stroke="#993333" stroke-width="2" class="clickable-region" data-region="lower-lip" data-side="Left" data-diagram="Face"/>
						<text x="168" y="218" text-anchor="middle" font-size="7" fill="#fff">LL-L</text>
						<!-- Lower Lip Right -->
						<path d="M200,215 Q228,230 255,210" fill="url(#lipGradFace)" stroke="#993333" stroke-width="2" class="clickable-region" data-region="lower-lip" data-side="Right" data-diagram="Face"/>
						<text x="232" y="218" text-anchor="middle" font-size="7" fill="#fff">LL-R</text>
						
						<!-- Angle of Mouth -->
						<circle cx="140" cy="203" r="10" fill="rgba(255,150,100,0.6)" stroke="#ff6633" stroke-width="2" class="clickable-region" data-region="angle-of-mouth" data-side="Left" data-diagram="Face"/>
						<circle cx="260" cy="203" r="10" fill="rgba(255,150,100,0.6)" stroke="#ff6633" stroke-width="2" class="clickable-region" data-region="angle-of-mouth" data-side="Right" data-diagram="Face"/>
						<text x="140" y="206" text-anchor="middle" font-size="6" fill="#993300">AoM</text>
						<text x="260" y="206" text-anchor="middle" font-size="6" fill="#993300">AoM</text>
						
						<!-- INTRA-ORAL SCHEMATIC BELOW FACE -->
						<text x="200" y="255" text-anchor="middle" font-size="11" font-weight="bold" fill="#663333">INTRA-ORAL (Schematic)</text>
						
						<!-- Mouth Opening Outline -->
						<ellipse cx="200" cy="340" rx="140" ry="80" fill="#8b0000" stroke="#660000" stroke-width="2"/>
						
						<!-- Hard Palate -->
						<ellipse cx="200" cy="290" rx="60" ry="20" fill="rgba(255,200,200,0.6)" stroke="#cc8888" stroke-width="1" class="clickable-region" data-region="hard-palate" data-side="Midline" data-diagram="Face"/>
						<text x="200" y="293" text-anchor="middle" font-size="8" fill="#993333">Hard Palate</text>
						
						<!-- Soft Palate -->
						<ellipse cx="200" cy="275" rx="40" ry="12" fill="rgba(255,150,150,0.6)" stroke="#cc6666" stroke-width="1" class="clickable-region" data-region="soft-palate" data-side="Midline" data-diagram="Face"/>
						<text x="200" y="278" text-anchor="middle" font-size="7" fill="#993333">Soft Palate</text>
						
						<!-- Tongue Dorsum -->
						<ellipse cx="200" cy="340" rx="55" ry="40" fill="#ff6b6b" stroke="#cc4444" stroke-width="2" class="clickable-region" data-region="tongue-dorsum" data-side="Midline" data-diagram="Face"/>
						<text x="200" y="345" text-anchor="middle" font-size="9" fill="#fff">Dorsum Tongue</text>
						
						<!-- Lateral Tongue -->
						<ellipse cx="150" cy="340" rx="15" ry="30" fill="rgba(255,100,100,0.4)" stroke="#cc4444" class="clickable-region" data-region="tongue-lateral" data-side="Left" data-diagram="Face"/>
						<ellipse cx="250" cy="340" rx="15" ry="30" fill="rgba(255,100,100,0.4)" stroke="#cc4444" class="clickable-region" data-region="tongue-lateral" data-side="Right" data-diagram="Face"/>
						<text x="150" y="343" text-anchor="middle" font-size="6" fill="#993333">Lat L</text>
						<text x="250" y="343" text-anchor="middle" font-size="6" fill="#993333">Lat R</text>
						
						<!-- Ventral Tongue -->
						<path d="M165,380 Q200,395 235,380" fill="rgba(255,150,150,0.5)" stroke="#cc6666" stroke-width="2" class="clickable-region" data-region="tongue-ventral" data-side="Midline" data-diagram="Face"/>
						<text x="200" y="388" text-anchor="middle" font-size="7" fill="#993333">Ventral</text>
						
						<!-- Floor of Mouth -->
						<ellipse cx="200" cy="400" rx="50" ry="15" fill="rgba(200,100,100,0.4)" stroke="#993333" class="clickable-region" data-region="floor-of-mouth" data-side="Midline" data-diagram="Face"/>
						<text x="200" y="403" text-anchor="middle" font-size="7" fill="#fff">Floor of Mouth</text>
						
						<!-- RMT -->
						<circle cx="90" cy="320" r="12" fill="rgba(200,150,150,0.5)" stroke="#cc8888" stroke-width="2" class="clickable-region" data-region="retromolar-trigone" data-side="Left" data-diagram="Face"/>
						<circle cx="310" cy="320" r="12" fill="rgba(200,150,150,0.5)" stroke="#cc8888" stroke-width="2" class="clickable-region" data-region="retromolar-trigone" data-side="Right" data-diagram="Face"/>
						<text x="90" y="323" text-anchor="middle" font-size="6" fill="#993333">RMT</text>
						<text x="310" y="323" text-anchor="middle" font-size="6" fill="#993333">RMT</text>
						
						<!-- Tonsils -->
						<ellipse cx="100" cy="290" rx="12" ry="18" fill="rgba(255,100,150,0.5)" stroke="#cc3366" class="clickable-region" data-region="tonsil" data-side="Left" data-diagram="Face"/>
						<ellipse cx="300" cy="290" rx="12" ry="18" fill="rgba(255,100,150,0.5)" stroke="#cc3366" class="clickable-region" data-region="tonsil" data-side="Right" data-diagram="Face"/>
						<text x="100" y="293" text-anchor="middle" font-size="6" fill="#993366">Tonsil</text>
						<text x="300" y="293" text-anchor="middle" font-size="6" fill="#993366">Tonsil</text>
						
						<!-- Oropharynx -->
						<ellipse cx="200" cy="265" rx="25" ry="12" fill="rgba(100,50,50,0.6)" stroke="#663333" class="clickable-region" data-region="oropharynx" data-side="Midline" data-diagram="Face"/>
						<text x="200" y="268" text-anchor="middle" font-size="6" fill="#ffcccc">Oropharynx</text>
						
						<!-- Alveolus Upper -->
						<path d="M80,305 Q200,280 320,305" fill="none" stroke="#ffb6c1" stroke-width="8" class="clickable-region" data-region="upper-alveolus" data-side="Midline" data-diagram="Face"/>
						<text x="200" y="298" text-anchor="middle" font-size="6" fill="#993333">Upper Alveolus</text>
						
						<!-- Alveolus Lower -->
						<path d="M80,375 Q200,400 320,375" fill="none" stroke="#ffb6c1" stroke-width="8" class="clickable-region" data-region="lower-alveolus" data-side="Midline" data-diagram="Face"/>
						<text x="200" y="382" text-anchor="middle" font-size="6" fill="#993333">Lower Alveolus</text>
						
						<!-- GB Sulcus markers -->
						<path d="M75,310 Q85,318 95,310" fill="none" stroke="#cc6699" stroke-width="4" class="clickable-region" data-region="upper-gb-sulcus" data-side="Left" data-diagram="Face"/>
						<path d="M305,310 Q315,318 325,310" fill="none" stroke="#cc6699" stroke-width="4" class="clickable-region" data-region="upper-gb-sulcus" data-side="Right" data-diagram="Face"/>
						<path d="M75,370 Q85,362 95,370" fill="none" stroke="#cc6699" stroke-width="4" class="clickable-region" data-region="lower-gb-sulcus" data-side="Left" data-diagram="Face"/>
						<path d="M305,370 Q315,362 325,370" fill="none" stroke="#cc6699" stroke-width="4" class="clickable-region" data-region="lower-gb-sulcus" data-side="Right" data-diagram="Face"/>
						
						<!-- Anterior Arch -->
						<path d="M115,280 L110,300 L118,300 Z" fill="rgba(200,100,100,0.5)" stroke="#993333" class="clickable-region" data-region="anterior-arch" data-side="Left" data-diagram="Face"/>
						<path d="M285,280 L290,300 L282,300 Z" fill="rgba(200,100,100,0.5)" stroke="#993333" class="clickable-region" data-region="anterior-arch" data-side="Right" data-diagram="Face"/>
						<text x="115" y="295" text-anchor="middle" font-size="5" fill="#993333">AA</text>
						<text x="285" y="295" text-anchor="middle" font-size="5" fill="#993333">AA</text>
						
						<!-- Base of Tongue -->
						<ellipse cx="200" cy="310" rx="30" ry="12" fill="rgba(180,60,60,0.5)" stroke="#993333" class="clickable-region" data-region="tongue-base" data-side="Midline" data-diagram="Face"/>
						<text x="200" y="313" text-anchor="middle" font-size="6" fill="#fff">Base</text>
						
						<!-- FOM Left/Right -->
						<ellipse cx="150" cy="400" rx="20" ry="10" fill="rgba(180,80,80,0.4)" stroke="#993333" class="clickable-region" data-region="fom" data-side="Left" data-diagram="Face"/>
						<ellipse cx="250" cy="400" rx="20" ry="10" fill="rgba(180,80,80,0.4)" stroke="#993333" class="clickable-region" data-region="fom" data-side="Right" data-diagram="Face"/>
						<text x="150" y="403" text-anchor="middle" font-size="5" fill="#fff">FOM-L</text>
						<text x="250" y="403" text-anchor="middle" font-size="5" fill="#fff">FOM-R</text>
						
						<g id="face-markers"></g>
					</svg>
				</div>
				
				<!-- ORAL CAVITY DIAGRAM -->
				<div class="diagram-card">
					<h6><i class="fa fa-teeth-open"></i> Oral Cavity - Open Mouth View</h6>
					<svg viewBox="0 0 280 260" style="width: 100%; max-width: 320px; display: block; margin: 0 auto;">
						<defs>
							<radialGradient id="mouthGradient" cx="50%" cy="50%" r="50%">
								<stop offset="0%" style="stop-color:#8b0000"/>
								<stop offset="100%" style="stop-color:#4a0000"/>
							</radialGradient>
							<radialGradient id="tongueGradient" cx="50%" cy="40%" r="60%">
								<stop offset="0%" style="stop-color:#ff6b6b"/>
								<stop offset="100%" style="stop-color:#cc4444"/>
							</radialGradient>
							<linearGradient id="lipGradient" x1="0%" y1="0%" x2="0%" y2="100%">
								<stop offset="0%" style="stop-color:#e07070"/>
								<stop offset="100%" style="stop-color:#cc5555"/>
							</linearGradient>
						</defs>
						
						<!-- Outer Lips Frame -->
						<ellipse cx="140" cy="130" rx="120" ry="110" fill="url(#lipGradient)" stroke="#993333" stroke-width="3"/>
						
						<!-- Inner Mouth Cavity -->
						<ellipse cx="140" cy="130" rx="95" ry="85" fill="url(#mouthGradient)" stroke="#660000" stroke-width="2"/>
						
						<!-- Upper Lip Left -->
						<path d="M50,70 Q95,45 140,65 L135,80 Q95,60 60,80 Z" fill="url(#lipGradient)" stroke="#993333" stroke-width="1" class="clickable-region" data-region="upper-lip" data-side="Left" data-diagram="Oral Cavity"/>
						<!-- Upper Lip Right -->
						<path d="M140,65 Q185,45 230,70 L220,85 Q185,60 145,80 Z" fill="url(#lipGradient)" stroke="#993333" stroke-width="1" class="clickable-region" data-region="upper-lip" data-side="Right" data-diagram="Oral Cavity"/>
						
						<!-- Lower Lip Left -->
						<path d="M50,190 Q95,215 140,195 L135,180 Q95,195 60,175 Z" fill="url(#lipGradient)" stroke="#993333" stroke-width="1" class="clickable-region" data-region="lower-lip" data-side="Left" data-diagram="Oral Cavity"/>
						<!-- Lower Lip Right -->
						<path d="M140,195 Q185,215 230,190 L220,175 Q185,195 145,180 Z" fill="url(#lipGradient)" stroke="#993333" stroke-width="1" class="clickable-region" data-region="lower-lip" data-side="Right" data-diagram="Oral Cavity"/>
						
						<!-- Angle of Mouth (Commissures) -->
						<circle cx="48" cy="130" r="8" fill="rgba(255,150,100,0.5)" stroke="#ff6633" stroke-width="2" class="clickable-region" data-region="angle-of-mouth" data-side="Left" data-diagram="Oral Cavity"/>
						<circle cx="232" cy="130" r="8" fill="rgba(255,150,100,0.5)" stroke="#ff6633" stroke-width="2" class="clickable-region" data-region="angle-of-mouth" data-side="Right" data-diagram="Oral Cavity"/>
						<text x="48" y="133" text-anchor="middle" font-size="6" fill="#993300">AoM</text>
						<text x="232" y="133" text-anchor="middle" font-size="6" fill="#993300">AoM</text>
						
						<!-- Upper Teeth Row -->
						<g class="clickable-region" data-region="teeth-upper" data-side="Midline" data-diagram="Teeth">
							<rect x="60" y="75" width="12" height="18" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="75" y="73" width="12" height="20" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="90" y="71" width="14" height="22" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="107" y="70" width="16" height="23" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="126" y="70" width="8" height="20" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="136" y="70" width="8" height="20" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="147" y="70" width="16" height="23" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="166" y="71" width="14" height="22" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="183" y="73" width="12" height="20" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="198" y="75" width="12" height="18" fill="#f5f5f0" stroke="#ccc" rx="2"/>
						</g>
						
						<!-- Lower Teeth Row -->
						<g class="clickable-region" data-region="teeth-lower" data-side="Midline" data-diagram="Teeth">
							<rect x="65" y="167" width="11" height="16" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="79" y="165" width="11" height="18" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="93" y="163" width="13" height="20" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="109" y="162" width="14" height="21" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="126" y="162" width="8" height="18" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="136" y="162" width="8" height="18" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="147" y="162" width="14" height="21" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="164" y="163" width="13" height="20" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="180" y="165" width="11" height="18" fill="#f5f5f0" stroke="#ccc" rx="2"/>
							<rect x="194" y="167" width="11" height="16" fill="#f5f5f0" stroke="#ccc" rx="2"/>
						</g>
						
						<!-- Gingiva/Alveolus Upper Left -->
						<path d="M55,95 Q95,88 140,92 L138,98 Q95,94 60,100 Z" fill="#ffb6c1" stroke="#cc8888" class="clickable-region" data-region="upper-alveolus" data-side="Left" data-diagram="Oral Cavity"/>
						<!-- Gingiva/Alveolus Upper Right -->
						<path d="M140,92 Q185,88 225,95 L220,100 Q185,94 142,98 Z" fill="#ffb6c1" stroke="#cc8888" class="clickable-region" data-region="upper-alveolus" data-side="Right" data-diagram="Oral Cavity"/>
						
						<!-- Upper GB Sulcus Left -->
						<path d="M55,100 Q70,105 85,100" fill="none" stroke="#cc6699" stroke-width="3" class="clickable-region" data-region="upper-gb-sulcus" data-side="Left" data-diagram="Oral Cavity"/>
						<!-- Upper GB Sulcus Right -->
						<path d="M195,100 Q210,105 225,100" fill="none" stroke="#cc6699" stroke-width="3" class="clickable-region" data-region="upper-gb-sulcus" data-side="Right" data-diagram="Oral Cavity"/>
						
						<!-- Lower GB Sulcus Left -->
						<path d="M55,160 Q70,155 85,160" fill="none" stroke="#cc6699" stroke-width="3" class="clickable-region" data-region="lower-gb-sulcus" data-side="Left" data-diagram="Oral Cavity"/>
						<!-- Lower GB Sulcus Right -->
						<path d="M195,160 Q210,155 225,160" fill="none" stroke="#cc6699" stroke-width="3" class="clickable-region" data-region="lower-gb-sulcus" data-side="Right" data-diagram="Oral Cavity"/>
						
						<!-- Gingiva/Alveolus Lower Left -->
						<path d="M55,165 Q95,172 140,168 L138,162 Q95,166 60,160 Z" fill="#ffb6c1" stroke="#cc8888" class="clickable-region" data-region="lower-alveolus" data-side="Left" data-diagram="Oral Cavity"/>
						<!-- Gingiva/Alveolus Lower Right -->
						<path d="M140,168 Q185,172 225,165 L220,160 Q185,166 142,162 Z" fill="#ffb6c1" stroke="#cc8888" class="clickable-region" data-region="lower-alveolus" data-side="Right" data-diagram="Oral Cavity"/>
						
						<!-- Buccal Mucosa Left -->
						<ellipse cx="55" cy="130" rx="20" ry="35" fill="rgba(255,182,193,0.4)" stroke="#cc8888" stroke-width="1" class="clickable-region" data-region="buccal-mucosa" data-side="Left" data-diagram="Oral Cavity"/>
						<text x="55" y="135" text-anchor="middle" class="region-label" fill="#993333">L</text>
						
						<!-- Buccal Mucosa Right -->
						<ellipse cx="225" cy="130" rx="20" ry="35" fill="rgba(255,182,193,0.4)" stroke="#cc8888" stroke-width="1" class="clickable-region" data-region="buccal-mucosa" data-side="Right" data-diagram="Oral Cavity"/>
						<text x="225" y="135" text-anchor="middle" class="region-label" fill="#993333">R</text>
						
						<!-- Hard Palate Left -->
						<path d="M90,105 Q115,95 140,102 L140,115 Q115,108 90,115 Z" fill="rgba(255,200,200,0.5)" stroke="#cc8888" stroke-width="1" class="clickable-region" data-region="hard-palate" data-side="Left" data-diagram="Oral Cavity"/>
						<!-- Hard Palate Midline -->
						<ellipse cx="140" cy="105" rx="15" ry="12" fill="rgba(255,180,180,0.6)" stroke="#cc8888" stroke-width="1" class="clickable-region" data-region="hard-palate" data-side="Midline" data-diagram="Oral Cavity"/>
						<!-- Hard Palate Right -->
						<path d="M140,102 Q165,95 190,105 L190,115 Q165,108 140,115 Z" fill="rgba(255,200,200,0.5)" stroke="#cc8888" stroke-width="1" class="clickable-region" data-region="hard-palate" data-side="Right" data-diagram="Oral Cavity"/>
						<text x="140" y="108" text-anchor="middle" class="region-label" fill="#993333">HP</text>
						
						<!-- Soft Palate Left -->
						<path d="M100,90 Q120,82 140,88 L140,95 Q120,90 105,95 Z" fill="rgba(255,150,150,0.5)" stroke="#cc6666" class="clickable-region" data-region="soft-palate" data-side="Left" data-diagram="Oral Cavity"/>
						<!-- Soft Palate Midline (Uvula) -->
						<ellipse cx="140" cy="85" rx="10" ry="8" fill="rgba(255,120,120,0.6)" stroke="#cc4444" class="clickable-region" data-region="soft-palate" data-side="Midline" data-diagram="Oral Cavity"/>
						<!-- Soft Palate Right -->
						<path d="M140,88 Q160,82 180,90 L175,95 Q160,90 140,95 Z" fill="rgba(255,150,150,0.5)" stroke="#cc6666" class="clickable-region" data-region="soft-palate" data-side="Right" data-diagram="Oral Cavity"/>
						<text x="140" y="88" text-anchor="middle" font-size="6" fill="#993333">SP</text>
						
						<!-- Anterior Arch (Pillars) -->
						<path d="M95,85 L90,100 L95,100 L100,88 Z" fill="rgba(200,100,100,0.4)" stroke="#993333" class="clickable-region" data-region="anterior-arch" data-side="Left" data-diagram="Oral Cavity"/>
						<path d="M180,88 L185,100 L190,100 L185,85 Z" fill="rgba(200,100,100,0.4)" stroke="#993333" class="clickable-region" data-region="anterior-arch" data-side="Right" data-diagram="Oral Cavity"/>
						
						<!-- Tonsils -->
						<ellipse cx="85" cy="95" rx="8" ry="12" fill="rgba(255,100,150,0.4)" stroke="#cc3366" stroke-width="1" class="clickable-region" data-region="tonsil" data-side="Left" data-diagram="Oral Cavity"/>
						<ellipse cx="195" cy="95" rx="8" ry="12" fill="rgba(255,100,150,0.4)" stroke="#cc3366" stroke-width="1" class="clickable-region" data-region="tonsil" data-side="Right" data-diagram="Oral Cavity"/>
						<text x="85" y="98" text-anchor="middle" font-size="5" fill="#993366">T</text>
						<text x="195" y="98" text-anchor="middle" font-size="5" fill="#993366">T</text>
						
						<!-- Oropharynx -->
						<ellipse cx="140" cy="75" rx="20" ry="10" fill="rgba(100,50,50,0.5)" stroke="#663333" stroke-width="1" class="clickable-region" data-region="oropharynx" data-side="Midline" data-diagram="Oral Cavity"/>
						<text x="140" y="78" text-anchor="middle" font-size="5" fill="#ffcccc">Oropharynx</text>
						
						<!-- Tongue Dorsum (main body) -->
						<ellipse cx="140" cy="140" rx="45" ry="35" fill="url(#tongueGradient)" stroke="#cc4444" stroke-width="2" class="clickable-region" data-region="tongue-dorsum" data-side="Midline" data-diagram="Tongue"/>
						<line x1="140" y1="105" x2="140" y2="175" stroke="#cc4444" stroke-width="1" stroke-dasharray="3,3"/>
						<text x="140" y="140" text-anchor="middle" class="region-label" fill="#fff">Dorsum</text>
						
						<!-- Tongue Lateral Left -->
						<ellipse cx="100" cy="140" rx="12" ry="25" fill="rgba(255,100,100,0.3)" stroke="#cc4444" stroke-dasharray="2,2" class="clickable-region" data-region="tongue-lateral" data-side="Left" data-diagram="Tongue"/>
						<!-- Tongue Lateral Right -->
						<ellipse cx="180" cy="140" rx="12" ry="25" fill="rgba(255,100,100,0.3)" stroke="#cc4444" stroke-dasharray="2,2" class="clickable-region" data-region="tongue-lateral" data-side="Right" data-diagram="Tongue"/>
						<text x="100" y="143" text-anchor="middle" font-size="6" fill="#fff">Lat L</text>
						<text x="180" y="143" text-anchor="middle" font-size="6" fill="#fff">Lat R</text>
						
						<!-- Ventral Tongue Left -->
						<path d="M110,165 Q125,175 140,170 L140,178 Q125,183 110,175 Z" fill="rgba(255,150,150,0.4)" stroke="#cc6666" class="clickable-region" data-region="tongue-ventral" data-side="Left" data-diagram="Tongue"/>
						<!-- Ventral Tongue Midline -->
						<ellipse cx="140" cy="172" rx="8" ry="6" fill="rgba(255,120,120,0.5)" stroke="#cc4444" class="clickable-region" data-region="tongue-ventral" data-side="Midline" data-diagram="Tongue"/>
						<!-- Ventral Tongue Right -->
						<path d="M140,170 Q155,175 170,165 L170,175 Q155,183 140,178 Z" fill="rgba(255,150,150,0.4)" stroke="#cc6666" class="clickable-region" data-region="tongue-ventral" data-side="Right" data-diagram="Tongue"/>
						
						<!-- Base of Tongue Left -->
						<path d="M105,110 Q122,100 140,108 L140,118 Q122,112 108,118 Z" fill="rgba(200,80,80,0.4)" stroke="#993333" class="clickable-region" data-region="tongue-base" data-side="Left" data-diagram="Tongue"/>
						<!-- Base of Tongue Midline -->
						<ellipse cx="140" cy="112" rx="10" ry="8" fill="rgba(180,60,60,0.5)" stroke="#993333" class="clickable-region" data-region="tongue-base" data-side="Midline" data-diagram="Tongue"/>
						<!-- Base of Tongue Right -->
						<path d="M140,108 Q158,100 175,110 L172,118 Q158,112 140,118 Z" fill="rgba(200,80,80,0.4)" stroke="#993333" class="clickable-region" data-region="tongue-base" data-side="Right" data-diagram="Tongue"/>
						<text x="140" y="115" text-anchor="middle" font-size="5" fill="#fff">Base</text>
						
						<!-- Floor of Mouth Left (FOM L) -->
						<path d="M95,185 Q117,195 140,188 L140,195 Q117,202 95,195 Z" fill="rgba(200,100,100,0.3)" stroke="#993333" class="clickable-region" data-region="fom" data-side="Left" data-diagram="Oral Cavity"/>
						<!-- Floor of Mouth Anterior (Midline) -->
						<ellipse cx="140" cy="190" rx="15" ry="8" fill="rgba(180,80,80,0.4)" stroke="#993333" class="clickable-region" data-region="floor-of-mouth" data-side="Midline" data-diagram="Oral Cavity"/>
						<!-- Floor of Mouth Right (FOM R) -->
						<path d="M140,188 Q163,195 185,185 L185,195 Q163,202 140,195 Z" fill="rgba(200,100,100,0.3)" stroke="#993333" class="clickable-region" data-region="fom" data-side="Right" data-diagram="Oral Cavity"/>
						<text x="140" y="193" text-anchor="middle" font-size="6" fill="#fff">FOM</text>
						
						<!-- Retromolar Trigone -->
						<circle cx="75" cy="115" r="8" fill="rgba(200,150,150,0.4)" stroke="#cc8888" class="clickable-region" data-region="retromolar-trigone" data-side="Left" data-diagram="Oral Cavity"/>
						<circle cx="205" cy="115" r="8" fill="rgba(200,150,150,0.4)" stroke="#cc8888" class="clickable-region" data-region="retromolar-trigone" data-side="Right" data-diagram="Oral Cavity"/>
						
						<!-- Markers container -->
						<g id="oral-markers"></g>
					</svg>
				</div>
				
				<!-- TEETH CHART -->
				<div class="diagram-card">
					<h6><i class="fa fa-tooth"></i> Teeth Chart - Dental Numbering</h6>
					<svg viewBox="0 0 300 200" style="width: 100%; max-width: 340px; display: block; margin: 0 auto;">
						<defs>
							<linearGradient id="toothGradient" x1="0%" y1="0%" x2="0%" y2="100%">
								<stop offset="0%" style="stop-color:#ffffff"/>
								<stop offset="100%" style="stop-color:#e8e8e0"/>
							</linearGradient>
						</defs>
						
						<!-- Upper Arch -->
						<text x="150" y="15" text-anchor="middle" font-size="10" fill="#666" font-weight="bold">UPPER</text>
						<path d="M30,50 Q150,20 270,50" fill="none" stroke="#ffb6c1" stroke-width="15" opacity="0.5"/>
						
						<!-- Upper Teeth -->
						<g transform="translate(30,30)">
							${[18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28].map((num, i) => `
								<g class="clickable-region" data-region="tooth-${num}" data-side="${num < 20 ? 'Right' : 'Left'}" data-diagram="Teeth" transform="translate(${i * 15}, 0)">
									<rect x="0" y="0" width="13" height="25" fill="url(#toothGradient)" stroke="#ccc" rx="3"/>
									<text x="6.5" y="35" text-anchor="middle" font-size="7" fill="#666">${num}</text>
								</g>
							`).join('')}
						</g>
						
						<!-- Midline -->
						<line x1="150" y1="25" x2="150" y2="180" stroke="#ccc" stroke-width="1" stroke-dasharray="5,5"/>
						<text x="145" y="100" font-size="8" fill="#999">R</text>
						<text x="155" y="100" font-size="8" fill="#999">L</text>
						
						<!-- Lower Arch -->
						<text x="150" y="190" text-anchor="middle" font-size="10" fill="#666" font-weight="bold">LOWER</text>
						<path d="M30,150 Q150,180 270,150" fill="none" stroke="#ffb6c1" stroke-width="15" opacity="0.5"/>
						
						<!-- Lower Teeth -->
						<g transform="translate(30,130)">
							${[48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38].map((num, i) => `
								<g class="clickable-region" data-region="tooth-${num}" data-side="${num > 40 ? 'Right' : 'Left'}" data-diagram="Teeth" transform="translate(${i * 15}, 0)">
									<rect x="0" y="0" width="13" height="25" fill="url(#toothGradient)" stroke="#ccc" rx="3"/>
									<text x="6.5" y="35" text-anchor="middle" font-size="7" fill="#666">${num}</text>
								</g>
							`).join('')}
						</g>
						
						<!-- Markers container -->
						<g id="teeth-markers"></g>
					</svg>
				</div>
				
				<!-- NECK LYMPH NODES - Maps to "Other" location -->
				<div class="diagram-card">
					<h6><i class="fa fa-project-diagram"></i> Neck Lymph Nodes (Extra-oral)</h6>
					<svg viewBox="0 0 400 450" style="width: 100%; display: block; margin: 0 auto;">
						<defs>
							<radialGradient id="neckSkin" cx="50%" cy="30%" r="70%">
								<stop offset="0%" style="stop-color:#ffe4c4"/>
								<stop offset="100%" style="stop-color:#deb887"/>
							</radialGradient>
						</defs>
						
						<!-- Info text -->
						<text x="200" y="20" text-anchor="middle" font-size="10" fill="#666">Note: All neck regions map to "Other" location</text>
						
						<!-- Neck outline -->
						<path d="M100,50 Q200,30 300,50 L320,400 Q200,430 80,400 Z" fill="url(#neckSkin)" stroke="#c9a77a" stroke-width="2"/>
						
						<!-- Jaw line -->
						<path d="M80,55 Q200,80 320,55" fill="none" stroke="#c9a77a" stroke-width="3"/>
						
						<!-- Clavicle -->
						<path d="M50,400 Q200,370 350,400" fill="none" stroke="#c9a77a" stroke-width="4"/>
						
						<!-- Level I - Submental (Ia) -->
						<ellipse cx="200" cy="85" rx="40" ry="18" fill="rgba(255,100,100,0.4)" stroke="#ff6666" stroke-width="2" class="clickable-region" data-region="level-i-submental" data-side="Midline" data-diagram="Neck"/>
						<text x="200" y="90" text-anchor="middle" font-size="11" fill="#cc3333" font-weight="bold">Level Ia</text>
						<text x="200" y="102" text-anchor="middle" font-size="8" fill="#993333">Submental</text>
						
						<!-- Level I - Submandibular (Ib) -->
						<ellipse cx="130" cy="105" rx="30" ry="25" fill="rgba(255,150,100,0.4)" stroke="#ff9966" stroke-width="2" class="clickable-region" data-region="level-i-submandibular" data-side="Left" data-diagram="Neck"/>
						<ellipse cx="270" cy="105" rx="30" ry="25" fill="rgba(255,150,100,0.4)" stroke="#ff9966" stroke-width="2" class="clickable-region" data-region="level-i-submandibular" data-side="Right" data-diagram="Neck"/>
						<text x="130" y="108" text-anchor="middle" font-size="10" fill="#cc6633" font-weight="bold">Ib L</text>
						<text x="270" y="108" text-anchor="middle" font-size="10" fill="#cc6633" font-weight="bold">Ib R</text>
						
						<!-- Level II - Upper Jugular -->
						<ellipse cx="120" cy="165" rx="35" ry="40" fill="rgba(255,255,100,0.4)" stroke="#cccc00" stroke-width="2" class="clickable-region" data-region="level-ii-upper-jugular" data-side="Left" data-diagram="Neck"/>
						<ellipse cx="280" cy="165" rx="35" ry="40" fill="rgba(255,255,100,0.4)" stroke="#cccc00" stroke-width="2" class="clickable-region" data-region="level-ii-upper-jugular" data-side="Right" data-diagram="Neck"/>
						<text x="120" y="165" text-anchor="middle" font-size="11" fill="#999900" font-weight="bold">Level II</text>
						<text x="120" y="178" text-anchor="middle" font-size="8" fill="#666600">Upper Jugular</text>
						<text x="280" y="165" text-anchor="middle" font-size="11" fill="#999900" font-weight="bold">Level II</text>
						<text x="280" y="178" text-anchor="middle" font-size="8" fill="#666600">Upper Jugular</text>
						
						<!-- Level III - Middle Jugular -->
						<ellipse cx="125" cy="245" rx="30" ry="40" fill="rgba(100,255,100,0.4)" stroke="#66cc66" stroke-width="2" class="clickable-region" data-region="level-iii-middle-jugular" data-side="Left" data-diagram="Neck"/>
						<ellipse cx="275" cy="245" rx="30" ry="40" fill="rgba(100,255,100,0.4)" stroke="#66cc66" stroke-width="2" class="clickable-region" data-region="level-iii-middle-jugular" data-side="Right" data-diagram="Neck"/>
						<text x="125" y="245" text-anchor="middle" font-size="11" fill="#339933" font-weight="bold">Level III</text>
						<text x="125" y="258" text-anchor="middle" font-size="8" fill="#226622">Mid Jugular</text>
						<text x="275" y="245" text-anchor="middle" font-size="11" fill="#339933" font-weight="bold">Level III</text>
						<text x="275" y="258" text-anchor="middle" font-size="8" fill="#226622">Mid Jugular</text>
						
						<!-- Level IV - Lower Jugular -->
						<ellipse cx="130" cy="325" rx="30" ry="40" fill="rgba(100,200,255,0.4)" stroke="#66aacc" stroke-width="2" class="clickable-region" data-region="level-iv-lower-jugular" data-side="Left" data-diagram="Neck"/>
						<ellipse cx="270" cy="325" rx="30" ry="40" fill="rgba(100,200,255,0.4)" stroke="#66aacc" stroke-width="2" class="clickable-region" data-region="level-iv-lower-jugular" data-side="Right" data-diagram="Neck"/>
						<text x="130" y="325" text-anchor="middle" font-size="11" fill="#3388aa" font-weight="bold">Level IV</text>
						<text x="130" y="338" text-anchor="middle" font-size="8" fill="#226688">Lower Jugular</text>
						<text x="270" y="325" text-anchor="middle" font-size="11" fill="#3388aa" font-weight="bold">Level IV</text>
						<text x="270" y="338" text-anchor="middle" font-size="8" fill="#226688">Lower Jugular</text>
						
						<!-- Level V - Posterior Triangle -->
						<path d="M75,140 L55,300 L95,300 Z" fill="rgba(200,100,255,0.4)" stroke="#aa66cc" stroke-width="2" class="clickable-region" data-region="level-v-posterior" data-side="Left" data-diagram="Neck"/>
						<path d="M325,140 L345,300 L305,300 Z" fill="rgba(200,100,255,0.4)" stroke="#aa66cc" stroke-width="2" class="clickable-region" data-region="level-v-posterior" data-side="Right" data-diagram="Neck"/>
						<text x="75" y="230" text-anchor="middle" font-size="10" fill="#8833aa" font-weight="bold">V</text>
						<text x="325" y="230" text-anchor="middle" font-size="10" fill="#8833aa" font-weight="bold">V</text>
						
						<!-- Level VI - Anterior/Central -->
						<ellipse cx="200" cy="290" rx="35" ry="50" fill="rgba(255,200,200,0.4)" stroke="#cc9999" stroke-width="2" class="clickable-region" data-region="level-vi-central" data-side="Midline" data-diagram="Neck"/>
						<text x="200" y="285" text-anchor="middle" font-size="11" fill="#996666" font-weight="bold">Level VI</text>
						<text x="200" y="298" text-anchor="middle" font-size="8" fill="#664444">Anterior</text>
						
						<!-- Thyroid -->
						<path d="M175,340 Q200,320 225,340 L235,380 Q200,400 165,380 Z" fill="rgba(100,150,255,0.4)" stroke="#6699cc" stroke-width="2" class="clickable-region" data-region="thyroid" data-side="Midline" data-diagram="Neck"/>
						<text x="200" y="365" text-anchor="middle" font-size="10" fill="#336699" font-weight="bold">Thyroid</text>
						
						<!-- Legend -->
						<rect x="20" y="415" width="360" height="30" fill="rgba(255,255,255,0.8)" rx="5"/>
						<text x="200" y="435" text-anchor="middle" font-size="9" fill="#666">Click any region to mark lesion → Location will be set to "Other"</text>
						
						<g id="neck-markers"></g>
					</svg>
				</div>
			</div>
			
			<!-- Legend -->
			<div class="legend-box">
				<div style="color: #fff; font-weight: 600; margin-bottom: 10px;"><i class="fa fa-info-circle"></i> Instructions</div>
				<div style="color: rgba(255,255,255,0.7); font-size: 12px;">
					• Click on any colored region to mark a lesion<br>
					• A dialog will appear to enter lesion details<br>
					• Marked lesions will be listed in the table below<br>
					• You can add multiple lesions to the same region
				</div>
			</div>
		</div>
	`;

	wrapper.html(svg_html);

	// Add click handlers for all diagram regions
	wrapper.find('.clickable-region').on('click', function (e) {
		let region = $(this).data('region');
		let side = $(this).data('side') || 'Midline';
		let diagram = $(this).data('diagram') || 'Face';

		add_lesion_marking(frm, region, side, diagram, e);
	});
}

// Add lesion from diagram click - Updated with all client sheet fields
function add_lesion_marking(frm, region, side, diagram, event) {
	// Format region name for display (Title Case for dialog title)
	let region_display = region.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
	
	// Map diagram region to location option - use original hyphenated region for mapping
	let location_default = map_region_to_location(region, side);

	let d = new frappe.ui.Dialog({
		title: __('Add Lesion - {0}', [region_display]),
		size: 'extra-large',
		fields: get_lesion_popup_fields(location_default, side, diagram),
		primary_action_label: __('Add Lesion'),
		primary_action: function () {
			let values = d.get_values();
			
			// Collect palpation values from HTML checkboxes (3 groups)
			let palpation_values = [];
			d.$wrapper.find('input[name="palp_consistency"]:checked').each(function() {
				palpation_values.push($(this).val());
			});
			d.$wrapper.find('input[name="palp_surface"]:checked').each(function() {
				palpation_values.push($(this).val());
			});
			d.$wrapper.find('input[name="palp_findings"]:checked').each(function() {
				palpation_values.push($(this).val());
			});
			
			// Override palpation with collected values
			values.palpation = palpation_values;
			
			// Remove texture field (no longer exists)
			delete values.texture;
			
			add_lesion_to_table(frm, values, diagram, region);
			d.hide();
		}
	});
	d.show();
}

// Map diagram region to location dropdown option
function map_region_to_location(region, side) {
	// Convert region to lowercase for matching
	let regionLower = region.toLowerCase().trim();
	
	// COMPLETE mapping from ALL SVG data-region values to location dropdown options
	// Grouped by diagram type for clarity
	
	// === FACE DIAGRAM REGIONS ===
	if (regionLower === 'lower-lip') {
		return side === 'Left' ? 'Lower lip (L)' : (side === 'Right' ? 'Lower lip (R)' : 'Lower lip (L)');
	}
	if (regionLower === 'upper-lip') {
		return side === 'Left' ? 'Upper lip (L)' : (side === 'Right' ? 'Upper lip (R)' : 'Upper lip (L)');
	}
	if (regionLower === 'cheek') {
		return side === 'Left' ? 'Buccal mucosa (L)' : 'Buccal mucosa (R)';
	}
	// Face regions that map to Other (not oral cavity)
	if (['forehead', 'eye', 'nose', 'ear', 'chin', 'parotid'].includes(regionLower)) {
		return 'Other';
	}
	
	// === ORAL CAVITY DIAGRAM REGIONS ===
	if (regionLower === 'buccal-mucosa') {
		return side === 'Left' ? 'Buccal mucosa (L)' : 'Buccal mucosa (R)';
	}
	if (regionLower === 'hard-palate') {
		return side === 'Midline' ? 'Hard palate (Midline)' : (side === 'Left' ? 'Hard palate (L)' : 'Hard palate (R)');
	}
	if (regionLower === 'soft-palate') {
		return side === 'Midline' ? 'Soft palate (Midline)' : (side === 'Left' ? 'Soft palate (L)' : 'Soft palate (R)');
	}
	if (regionLower === 'upper-alveolus') {
		return side === 'Left' ? 'Upper Alveolus & Gingivo-Buccal Sulcus (L)' : (side === 'Right' ? 'Upper Alveolus & Gingivo-Buccal Sulcus (R)' : 'Upper Alveolus & Gingivo-Buccal Sulcus (L)');
	}
	if (regionLower === 'lower-alveolus') {
		return side === 'Left' ? 'Lower Alveolus & Gingivo-Buccal Sulcus (L)' : (side === 'Right' ? 'Lower Alveolus & Gingivo-Buccal Sulcus (R)' : 'Lower Alveolus & Gingivo-Buccal Sulcus (L)');
	}
	if (regionLower === 'floor-of-mouth') {
		return side === 'Midline' ? 'Anterior Floor of Mouth' : (side === 'Left' ? 'FOM (L)' : 'FOM (R)');
	}
	if (regionLower === 'retromolar-trigone') {
		return side === 'Left' ? 'RMT (L)' : 'RMT (R)';
	}
	
	// === TONGUE DIAGRAM REGIONS ===
	if (regionLower === 'tongue-dorsum') {
		return 'Dorsum Tongue';
	}
	if (regionLower === 'tongue-lateral') {
		return side === 'Left' ? 'Lateral Tongue (L)' : 'Lateral Tongue (R)';
	}
	if (regionLower === 'tongue-ventral' || regionLower === 'tongue') {
		return side === 'Midline' ? 'Ventral Tongue (Midline)' : (side === 'Left' ? 'Ventral Tongue (L)' : 'Ventral Tongue (R)');
	}
	if (regionLower === 'tongue-tip') {
		return 'Ventral Tongue (Midline)';
	}
	if (regionLower === 'tongue-base') {
		return side === 'Midline' ? 'Base of Tongue (Midline)' : (side === 'Left' ? 'Base of Tongue (L)' : 'Base of Tongue (R)');
	}
	
	// === TEETH DIAGRAM REGIONS ===
	if (regionLower === 'teeth-upper') {
		return 'Upper Alveolus & Gingivo-Buccal Sulcus (L)';
	}
	if (regionLower === 'teeth-lower') {
		return 'Lower Alveolus & Gingivo-Buccal Sulcus (L)';
	}
	// Individual teeth (tooth-11, tooth-21, etc.)
	if (regionLower.startsWith('tooth-')) {
		let toothNum = parseInt(regionLower.replace('tooth-', ''));
		// Upper teeth (11-18, 21-28)
		if (toothNum >= 11 && toothNum <= 18) {
			return 'Upper Alveolus & Gingivo-Buccal Sulcus (R)';
		}
		if (toothNum >= 21 && toothNum <= 28) {
			return 'Upper Alveolus & Gingivo-Buccal Sulcus (L)';
		}
		// Lower teeth (31-38, 41-48)
		if (toothNum >= 31 && toothNum <= 38) {
			return 'Lower Alveolus & Gingivo-Buccal Sulcus (L)';
		}
		if (toothNum >= 41 && toothNum <= 48) {
			return 'Lower Alveolus & Gingivo-Buccal Sulcus (R)';
		}
		return 'Other';
	}
	
	// === NECK DIAGRAM REGIONS (Level I-V) ===
	// Level I - Submental & Submandibular
	if (regionLower === 'level-i-submental' || regionLower === 'neck-submental') {
		return 'Other'; // Neck region - not oral cavity
	}
	if (regionLower === 'level-i-submandibular' || regionLower === 'neck-submandibular') {
		return 'Other'; // Neck region - not oral cavity
	}
	// Level II - Upper Jugular
	if (regionLower === 'level-ii-upper-jugular') {
		return 'Other';
	}
	// Level III - Middle Jugular
	if (regionLower === 'level-iii-middle-jugular') {
		return 'Other';
	}
	// Level IV - Lower Jugular
	if (regionLower === 'level-iv-lower-jugular') {
		return 'Other';
	}
	// Level V - Posterior Triangle
	if (regionLower === 'level-v-posterior') {
		return 'Other';
	}
	// Level VI - Anterior Compartment
	if (regionLower === 'level-vi-anterior') {
		return 'Other';
	}
	// Other neck regions
	if (regionLower === 'neck-cervical' || regionLower === 'cervical') {
		return 'Other';
	}
	if (regionLower.includes('neck') || regionLower.includes('jugular') || regionLower.includes('level-')) {
		return 'Other';
	}
	
	// === OTHER REGIONS ===
	if (regionLower === 'tonsil') {
		return side === 'Left' ? 'Tonsil (L)' : 'Tonsil (R)';
	}
	if (regionLower === 'oropharynx') {
		return side === 'Midline' ? 'Oropharynx (Midline)' : (side === 'Left' ? 'Oropharynx (L)' : 'Oropharynx (R)');
	}
	if (regionLower === 'angle-of-mouth' || regionLower === 'labial-commissure') {
		return side === 'Left' ? 'Angle of Mouth (L)' : 'Angle of Mouth (R)';
	}
	if (regionLower === 'anterior-arch') {
		return side === 'Left' ? 'Anterior Arch (L)' : 'Anterior Arch (R)';
	}
	
	// GB Sulcus regions
	if (regionLower === 'upper-gb-sulcus') {
		return side === 'Left' ? 'Upper anterior GB sulcus (L)' : 'Upper anterior GB sulcus (R)';
	}
	if (regionLower === 'lower-gb-sulcus') {
		return side === 'Left' ? 'Lower anterior GB sulcus (L)' : 'Lower anterior GB sulcus (R)';
	}
	if (regionLower === 'gb-sulcus' || regionLower === 'sulcus') {
		return side === 'Left' ? 'Upper anterior GB sulcus (L)' : 'Upper anterior GB sulcus (R)';
	}
	
	// FOM (Floor of Mouth) Left/Right
	if (regionLower === 'fom') {
		return side === 'Left' ? 'FOM (L)' : 'FOM (R)';
	}
	
	// Default fallback
	return 'Other';
}

// Get all lesion popup fields as per client sheet
function get_lesion_popup_fields(location_default, side_default, diagram) {
	return [
		// Location Section
		{
			fieldtype: 'Section Break',
			label: 'Lesion Location'
		},
		{
			fieldname: 'location',
			fieldtype: 'Select',
			label: 'Location',
			reqd: 1,
			default: location_default,
			options: '\nLower lip (L)\nLower lip (R)\nUpper lip (L)\nUpper lip (R)\nAnterior Arch (L)\nAnterior Arch (R)\nUpper anterior GB sulcus (L)\nUpper anterior GB sulcus (R)\nLower anterior GB sulcus (L)\nLower anterior GB sulcus (R)\nAngle of Mouth (L)\nAngle of Mouth (R)\nUpper Alveolus & Gingivo-Buccal Sulcus (L)\nUpper Alveolus & Gingivo-Buccal Sulcus (R)\nLower Alveolus & Gingivo-Buccal Sulcus (L)\nLower Alveolus & Gingivo-Buccal Sulcus (R)\nVentral Tongue (L)\nVentral Tongue (R)\nVentral Tongue (Midline)\nRMT (L)\nRMT (R)\nDorsum Tongue\nAnterior Floor of Mouth\nLateral Tongue (L)\nLateral Tongue (R)\nFOM (L)\nFOM (R)\nBuccal mucosa (L)\nBuccal mucosa (R)\nHard palate (L)\nHard palate (R)\nHard palate (Midline)\nSoft palate (L)\nSoft palate (R)\nSoft palate (Midline)\nOropharynx (L)\nOropharynx (R)\nOropharynx (Midline)\nBase of Tongue (L)\nBase of Tongue (R)\nBase of Tongue (Midline)\nTonsil (L)\nTonsil (R)\nOther'
		},
		// Size Section
		{
			fieldtype: 'Section Break',
			label: 'Size'
		},
		{
			fieldname: 'size_length',
			fieldtype: 'Float',
			label: 'Length (mm)'
		},
		{
			fieldtype: 'Column Break'
		},
		{
			fieldname: 'size_width',
			fieldtype: 'Float',
			label: 'Width (mm)'
		},
		// Color Section
		{
			fieldtype: 'Section Break',
			label: 'Color'
		},
		{
			fieldname: 'color',
			fieldtype: 'MultiCheck',
			label: '',
			options: [
				{label: 'Uniform', value: 'Uniform'},
				{label: 'Variegated', value: 'Variegated'},
				{label: 'White', value: 'White'},
				{label: 'Red', value: 'Red'},
				{label: 'Black', value: 'Black'},
				{label: 'Brown', value: 'Brown'},
				{label: 'Mixed', value: 'Mixed'}
			],
			columns: 7
		},
		// Shape Section
		{
			fieldtype: 'Section Break',
			label: 'Shape'
		},
		{
			fieldname: 'shape',
			fieldtype: 'MultiCheck',
			label: '',
			options: [
				{label: 'Round', value: 'Round'},
				{label: 'Oval', value: 'Oval'},
				{label: 'Irregular', value: 'Irregular'},
				{label: 'Rectangular', value: 'Rectangular'}
			],
			columns: 4
		},
		// Margin Section (as per client sheet)
		{
			fieldtype: 'Section Break',
			label: 'Margin'
		},
		{
			fieldname: 'margin',
			fieldtype: 'MultiCheck',
			label: '',
			options: [
				{label: 'Well-defined (circumscribed)', value: 'Well-defined (circumscribed)'},
				{label: 'Poorly-defined (vague)', value: 'Poorly-defined (vague)'},
				{label: 'Regular', value: 'Regular'},
				{label: 'Irregular borders', value: 'Irregular borders'}
			],
			columns: 4
		},
		// Description/Lesion Type Section (All 26 options from client sheet)
		{
			fieldtype: 'Section Break',
			label: 'Description (Lesion Type)'
		},
		{
			fieldname: 'description',
			fieldtype: 'MultiCheck',
			label: '',
			options: [
				{label: 'Foul Smell (Halitosis)', value: 'Foul Smell (Halitosis)'},
				{label: 'Cracked', value: 'Cracked'},
				{label: 'Macule - flat', value: 'Macule - flat'},
				{label: 'Vesicle - elevated', value: 'Vesicle - elevated'},
				{label: 'Pustule - purulent', value: 'Pustule - purulent'},
				{label: 'Papule (<5mm, raised)', value: 'Papule (<5mm, raised)'},
				{label: 'Nodule (<2cm, raised)', value: 'Nodule (<2cm, raised)'},
				{label: 'Plaque - broad, raised', value: 'Plaque - broad, raised'},
				{label: 'Sessile - broad based', value: 'Sessile - broad based'},
				{label: 'Pedunculated - stalk-like', value: 'Pedunculated - stalk-like'},
				{label: 'Leukoplakia - smooth', value: 'Leukoplakia - smooth'},
				{label: 'Leukoplakia - verrucous', value: 'Leukoplakia - verrucous'},
				{label: 'Leukoplakia - irregular', value: 'Leukoplakia - irregular'},
				{label: 'Leukoplakia - lacy like', value: 'Leukoplakia - lacy like'},
				{label: 'Erythroplakia - Smooth', value: 'Erythroplakia - Smooth'},
				{label: 'Erythroplakia - Erosive', value: 'Erythroplakia - Erosive'},
				{label: 'Superficial Ulcer', value: 'Superficial Ulcer'},
				{label: 'Deep ulcer - smooth margins', value: 'Deep ulcer - smooth margins'},
				{label: 'Deep ulcer - irregular margins', value: 'Deep ulcer - irregular margins'},
				{label: 'Proliferative ulcer', value: 'Proliferative ulcer'},
				{label: 'Fungal lesion (scrapable)', value: 'Fungal lesion (scrapable)'},
				{label: 'Bleeding', value: 'Bleeding'},
				{label: 'Marbelled Mucosa', value: 'Marbelled Mucosa'},
				{label: 'Hypertrophic Mucosa', value: 'Hypertrophic Mucosa'},
				{label: 'Fibrous bands', value: 'Fibrous bands'},
				{label: 'Hypertrophic Papillae', value: 'Hypertrophic Papillae'}
			],
			columns: 3
		},
		// Palpation Section (All options from client sheet)
		{
			fieldtype: 'Section Break',
			label: 'Palpation (Palpate gently using gloved finger)'
		},
		{
			fieldname: 'palpation',
			fieldtype: 'HTML',
			options: `
				<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 15px;">
					<div>
						<h6 style="font-weight: 600; margin-bottom: 10px; color: var(--heading-color); font-size: 13px;">Consistency</h6>
						<div style="display: flex; flex-direction: column; gap: 8px;">
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_consistency" value="Tender" style="width: 16px; height: 16px;"> Tender</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_consistency" value="Soft" style="width: 16px; height: 16px;"> Soft</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_consistency" value="Firm" style="width: 16px; height: 16px;"> Firm</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_consistency" value="Hard" style="width: 16px; height: 16px;"> Hard</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_consistency" value="Fluctuant" style="width: 16px; height: 16px;"> Fluctuant</label>
						</div>
					</div>
					<div>
						<h6 style="font-weight: 600; margin-bottom: 10px; color: var(--heading-color); font-size: 13px;">Surface</h6>
						<div style="display: flex; flex-direction: column; gap: 8px;">
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_surface" value="Smooth" style="width: 16px; height: 16px;"> Smooth</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_surface" value="Rough-papillary (finger-like projections)" style="width: 16px; height: 16px;"> Rough-papillary (finger-like projections)</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_surface" value="Corrugated (rippled)" style="width: 16px; height: 16px;"> Corrugated (rippled)</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_surface" value="Fissured (deep crevices)" style="width: 16px; height: 16px;"> Fissured (deep crevices)</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_surface" value="Crusted (covered with scab)" style="width: 16px; height: 16px;"> Crusted (covered with scab)</label>
						</div>
					</div>
					<div>
						<h6 style="font-weight: 600; margin-bottom: 10px; color: var(--heading-color); font-size: 13px;">Findings</h6>
						<div style="display: flex; flex-direction: column; gap: 8px;">
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_findings" value="Bleeds on Touch" style="width: 16px; height: 16px;"> Bleeds on Touch</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_findings" value="Blanching of mucosa" style="width: 16px; height: 16px;"> Blanching of mucosa</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_findings" value="Scrapable white" style="width: 16px; height: 16px;"> Scrapable white</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_findings" value="Scrapable red" style="width: 16px; height: 16px;"> Scrapable red</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_findings" value="Non-Scrapable" style="width: 16px; height: 16px;"> Non-Scrapable</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_findings" value="No Induration" style="width: 16px; height: 16px;"> No Induration</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_findings" value="Mild Induration" style="width: 16px; height: 16px;"> Mild Induration</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;"><input type="checkbox" name="palp_findings" value="Extensive Induration" style="width: 16px; height: 16px;"> Extensive Induration</label>
						</div>
					</div>
				</div>
			`
		},
		// Additional Details Section
		{
			fieldtype: 'Section Break',
			label: 'Additional Details'
		},
		{
			fieldname: 'fixed_location',
			fieldtype: 'Select',
			label: 'Fixed Location',
			options: '\nTip of Tongue\nBase of Tongue\nPhiltrum\nAngle of Mouth\nAnterior Pillar\nRetro Molar Trigone'
		},
		{
			fieldtype: 'Column Break'
		},
		{
			fieldname: 'tooth_relation',
			fieldtype: 'Data',
			label: 'Relation to Tooth#',
			description: 'e.g., 23, 24, 25'
		},
		{
			fieldname: 'distance_mm',
			fieldtype: 'Float',
			label: 'Distance (mm)'
		},
		// Notes Section
		{
			fieldtype: 'Section Break',
			label: 'Notes'
		},
		{
			fieldname: 'note',
			fieldtype: 'Small Text',
			label: 'Clinical Notes'
		}
	];
}

// Add lesion to ERPNext table
function add_lesion_to_table(frm, values, diagram, region) {
	let lesion_count = (frm.doc.custom_lesion_details || []).length + 1;
	
	let row = frm.add_child('custom_lesion_details');
	row.lesion_number = lesion_count;
	row.location = values.location;
	row.size_length = values.size_length;
	row.size_width = values.size_width;
	row.color = Array.isArray(values.color) ? values.color.join(', ') : values.color;
	row.shape = Array.isArray(values.shape) ? values.shape.join(', ') : values.shape;
	row.margin = Array.isArray(values.margin) ? values.margin.join(', ') : values.margin;
	row.description = Array.isArray(values.description) ? values.description.join(', ') : values.description;
	row.palpation = Array.isArray(values.palpation) ? values.palpation.join(', ') : values.palpation;
	row.fixed_location = values.fixed_location;
	row.tooth_relation = values.tooth_relation;
	row.distance_mm = values.distance_mm;
	row.note = values.note;
	row.diagram_type = diagram;
	row.diagram_region = region;
	
	frm.refresh_field('custom_lesion_details');
	
	frappe.show_alert({
		message: __('Lesion #{0} added: {1}', [lesion_count, values.location]),
		indicator: 'green'
	});
}

// Render lesions table - Now uses ERPNext standard table
function render_step3_lesions_table(frm) {
	// Show the ERPNext standard table
	if (frm.fields_dict.custom_lesion_details) {
		frm.set_df_property('custom_lesion_details', 'hidden', 0);
		frm.refresh_field('custom_lesion_details');
	}
	
	// Remove any old custom table containers
	let wrapper = frm.fields_dict.exam_diagram_interactive?.$wrapper;
	if (wrapper) {
		wrapper.find('#step3_lesions_table_container').remove();
		wrapper.find('#step3_lesion_examination_container').remove();
	}
}

// Lesion Examination Section - moved from Step 2 to Step 3
function render_step3_lesion_examination(frm, wrapper) {
	// Find or create lesion examination container
	let lesionExamContainer = wrapper.find('#step3_lesion_examination_container');
	if (lesionExamContainer.length === 0) {
		wrapper.append('<div id="step3_lesion_examination_container" style="margin-top: 25px; padding-top: 20px; border-top: 2px solid var(--border-color);"></div>');
		lesionExamContainer = wrapper.find('#step3_lesion_examination_container');
	}

	let currentStatus = frm.doc.exam_lesion_present || '';

	let html = `
		<style>
			.lesion-exam-section { font-size: 13px; }
			.lesion-exam-title { font-size: 14px; font-weight: 600; color: var(--heading-color); margin-bottom: 15px; }
			.lesion-radio-group { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; }
			.lesion-radio-label { display: inline-flex; align-items: center; gap: 6px; padding: 8px 15px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 4px; cursor: pointer; font-size: 12px; }
			.lesion-radio-label:hover { background: var(--subtle-bg); border-color: var(--primary); }
			.lesion-radio-label input { margin: 0; }
		</style>
		
		<div class="lesion-exam-section">
			<div class="lesion-exam-title">
				<i class="fa fa-stethoscope"></i> Lesion Examination
			</div>
			
			<div class="lesion-radio-group">
				<label class="lesion-radio-label">
					<input type="radio" name="step3_lesion_present" value="No" ${currentStatus !== 'Yes' ? 'checked' : ''}> No Lesion
				</label>
				<label class="lesion-radio-label">
					<input type="radio" name="step3_lesion_present" value="Yes" ${currentStatus === 'Yes' ? 'checked' : ''}> Lesion Present
				</label>
			</div>
			
			<div id="step3_lesion_form_section" style="display: ${currentStatus === 'Yes' ? 'block' : 'none'};">
				<button type="button" class="btn btn-primary btn-sm" id="step3_add_lesion_btn">
					<i class="fa fa-plus"></i> Add Lesion Details
				</button>
			</div>
		</div>
	`;

	lesionExamContainer.html(html);

	// Lesion Present handler
	lesionExamContainer.find('input[name="step3_lesion_present"]').on('change', function() {
		let val = $(this).val();
		frm.set_value('exam_lesion_present', val);
		if (val === 'Yes') {
			lesionExamContainer.find('#step3_lesion_form_section').show();
		} else {
			lesionExamContainer.find('#step3_lesion_form_section').hide();
		}
	});

	// Add Lesion button handler
	lesionExamContainer.find('#step3_add_lesion_btn').on('click', function() {
		show_lesion_examination_popup(frm);
	});

	// Render lesion examination table if data exists
	render_step3_lesion_exam_table(frm, lesionExamContainer);
}

// Lesion Examination Popup
function show_lesion_examination_popup(frm) {
	let d = new frappe.ui.Dialog({
		title: 'Add Lesion Examination Details',
		size: 'extra-large',
		fields: [
			{ fieldtype: 'Section Break', label: 'Lesion Location' },
			{ fieldtype: 'HTML', fieldname: 'location_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0;">
					${LESION_CONFIG.locations.map(loc => `
						<label class="lesion-location-label" style="display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 4px; cursor: pointer; font-size: 12px;">
							<input type="radio" name="lesion_location" value="${loc}" style="cursor: pointer;"> <span style="cursor: pointer;">${loc}</span>
						</label>
					`).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Size' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Int', fieldname: 'size_length', label: 'Length (mm)' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Int', fieldname: 'size_width', label: 'Width (mm)' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Section Break', label: 'Color' },
			{ fieldtype: 'HTML', fieldname: 'color_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">
					${LESION_CONFIG.colors.map(c => `
						<label style="display: inline-flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px;">
							<input type="checkbox" name="lesion_color" value="${c}"> ${c}
						</label>
					`).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Shape' },
			{ fieldtype: 'HTML', fieldname: 'shape_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">
					${LESION_CONFIG.shapes.map(s => `
						<label style="display: inline-flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px;">
							<input type="checkbox" name="lesion_shape" value="${s}"> ${s}
						</label>
					`).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Margin' },
			{ fieldtype: 'HTML', fieldname: 'margin_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">
					${LESION_CONFIG.margins.map(m => `
						<label style="display: inline-flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px;">
							<input type="checkbox" name="lesion_margin" value="${m}"> ${m}
						</label>
					`).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Description (Lesion Type)' },
			{ fieldtype: 'HTML', fieldname: 'desc_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">
					${LESION_CONFIG.descriptions.map(d => `
						<label style="display: inline-flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px;">
							<input type="checkbox" name="lesion_desc" value="${d}"> ${d}
						</label>
					`).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Palpation' },
			{ fieldtype: 'HTML', fieldname: 'palpation_help', options: `
				<div style="padding: 8px 12px; background: #e8f4fd; border-left: 3px solid #2490ef; margin-bottom: 15px; border-radius: 4px;">
					<small style="color: #1f7ab7;"><i class="fa fa-info-circle"></i> Palpate gently using gloved finger</small>
				</div>
			` },
			{ fieldtype: 'HTML', fieldname: 'palp_html', options: `
				<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 10px 0;">
					<!-- Consistency Column -->
					<div>
						<h6 style="font-weight: 600; margin-bottom: 10px; color: var(--heading-color); font-size: 13px;">Consistency</h6>
						<div style="display: flex; flex-direction: column; gap: 8px;">
							${LESION_CONFIG.palpation.consistency.map(item => `
								<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;">
									<input type="checkbox" name="lesion_palp_consistency" value="${item}" style="width: 16px; height: 16px;"> ${item}
								</label>
							`).join('')}
						</div>
					</div>
					<!-- Surface Column -->
					<div>
						<h6 style="font-weight: 600; margin-bottom: 10px; color: var(--heading-color); font-size: 13px;">Surface</h6>
						<div style="display: flex; flex-direction: column; gap: 8px;">
							${LESION_CONFIG.palpation.surface.map(item => `
								<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;">
									<input type="checkbox" name="lesion_palp_surface" value="${item}" style="width: 16px; height: 16px;"> ${item}
								</label>
							`).join('')}
						</div>
					</div>
					<!-- Findings Column -->
					<div>
						<h6 style="font-weight: 600; margin-bottom: 10px; color: var(--heading-color); font-size: 13px;">Findings</h6>
						<div style="display: flex; flex-direction: column; gap: 8px;">
							${LESION_CONFIG.palpation.findings.map(item => `
								<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;">
									<input type="checkbox" name="lesion_palp_findings" value="${item}" style="width: 16px; height: 16px;"> ${item}
								</label>
							`).join('')}
						</div>
					</div>
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Additional Details' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Select', fieldname: 'fixed_location', label: 'Fixed Location', options: '\n' + LESION_CONFIG.fixedLocations.join('\n') },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Int', fieldname: 'distance_mm', label: 'Distance in mm (from Fixed Location)' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Data', fieldname: 'relation_tooth', label: 'Relation to tooth#' },
			{ fieldtype: 'Section Break', label: 'Notes' },
			{ fieldtype: 'Small Text', fieldname: 'notes', label: 'Notes' }
		],
		primary_action_label: 'Add Lesion',
		primary_action: function() {
			let values = d.get_values();
			
			// Get location
			let location = d.$wrapper.find('input[name="lesion_location"]:checked').val();
			if (!location) {
				frappe.msgprint('Please select a lesion location');
				return;
			}
			
			// Get selected values
			let colors = [];
			d.$wrapper.find('input[name="lesion_color"]:checked').each(function() { colors.push($(this).val()); });
			
			let shapes = [];
			d.$wrapper.find('input[name="lesion_shape"]:checked').each(function() { shapes.push($(this).val()); });
			
			let margins = [];
			d.$wrapper.find('input[name="lesion_margin"]:checked').each(function() { margins.push($(this).val()); });
			
			let descriptions = [];
			d.$wrapper.find('input[name="lesion_desc"]:checked').each(function() { descriptions.push($(this).val()); });
			
			// Get palpation values from all 3 groups
			let palpations = [];
			d.$wrapper.find('input[name="lesion_palp_consistency"]:checked').each(function() { palpations.push($(this).val()); });
			d.$wrapper.find('input[name="lesion_palp_surface"]:checked').each(function() { palpations.push($(this).val()); });
			d.$wrapper.find('input[name="lesion_palp_findings"]:checked').each(function() { palpations.push($(this).val()); });
			
			// Add to child table (exam_lesion_details or similar)
			if (!frm.doc.exam_lesion_examination) {
				frm.doc.exam_lesion_examination = [];
			}
			
			let row = frm.add_child('exam_lesion_examination');
			row.location = location;
			row.size_length = values.size_length || '';
			row.size_width = values.size_width || '';
			row.color = colors.join(', ');
			row.shape = shapes.join(', ');
			row.margin = margins.join(', ');
			row.description = descriptions.join(', ');
			row.palpation = palpations.join(', ');
			row.fixed_location = values.fixed_location || '';
			row.distance_mm = values.distance_mm || '';
			row.relation_tooth = values.relation_tooth || '';
			row.note = values.notes || '';
			
			frm.refresh_field('exam_lesion_examination');
			
			// Re-render lesion exam table
			let wrapper = frm.fields_dict.exam_diagram_interactive?.$wrapper;
			if (wrapper) {
				let lesionExamContainer = wrapper.find('#step3_lesion_examination_container');
				render_step3_lesion_exam_table(frm, lesionExamContainer);
			}
			
			d.hide();
			frappe.show_alert({
				message: 'Lesion examination added',
				indicator: 'green'
			});
		}
	});

	// Make entire label clickable for location
	d.$wrapper.on('click', '.lesion-location-label', function(e) {
		if (e.target.tagName !== 'INPUT') {
			$(this).find('input[type="radio"]').prop('checked', true);
		}
	});

	d.show();
}

// Lesion Examination Edit Popup
function show_lesion_examination_edit_popup(frm, idx, container) {
	let lesion = frm.doc.exam_lesion_examination[idx];
	
	// Parse existing palpation values into groups
	let existingPalpations = (lesion.palpation || '').split(', ').map(p => p.trim()).filter(p => p);
	
	let d = new frappe.ui.Dialog({
		title: 'Edit Lesion Examination Details',
		size: 'extra-large',
		fields: [
			{ fieldtype: 'Section Break', label: 'Lesion Location' },
			{ fieldtype: 'HTML', fieldname: 'location_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0;">
					${LESION_CONFIG.locations.map(loc => `
						<label class="lesion-location-label" style="display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 4px; cursor: pointer; font-size: 12px;">
							<input type="radio" name="lesion_location" value="${loc}" ${lesion.location === loc ? 'checked' : ''} style="cursor: pointer;"> <span style="cursor: pointer;">${loc}</span>
						</label>
					`).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Size' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Int', fieldname: 'size_length', label: 'Length (mm)', default: lesion.size_length || '' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Int', fieldname: 'size_width', label: 'Width (mm)', default: lesion.size_width || '' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Section Break', label: 'Color' },
			{ fieldtype: 'HTML', fieldname: 'color_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">
					${LESION_CONFIG.colors.map(c => {
						let isChecked = (lesion.color || '').split(', ').includes(c);
						return `
						<label style="display: inline-flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px;">
							<input type="checkbox" name="lesion_color" value="${c}" ${isChecked ? 'checked' : ''}> ${c}
						</label>
						`;
					}).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Shape' },
			{ fieldtype: 'HTML', fieldname: 'shape_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">
					${LESION_CONFIG.shapes.map(s => {
						let isChecked = (lesion.shape || '').split(', ').includes(s);
						return `
						<label style="display: inline-flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px;">
							<input type="checkbox" name="lesion_shape" value="${s}" ${isChecked ? 'checked' : ''}> ${s}
						</label>
						`;
					}).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Margin' },
			{ fieldtype: 'HTML', fieldname: 'margin_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">
					${LESION_CONFIG.margins.map(m => {
						let isChecked = (lesion.margin || '').split(', ').includes(m);
						return `
						<label style="display: inline-flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px;">
							<input type="checkbox" name="lesion_margin" value="${m}" ${isChecked ? 'checked' : ''}> ${m}
						</label>
						`;
					}).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Description (Lesion Type)' },
			{ fieldtype: 'HTML', fieldname: 'desc_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">
					${LESION_CONFIG.descriptions.map(desc => {
						let isChecked = (lesion.description || '').split(', ').includes(desc);
						return `
						<label style="display: inline-flex; align-items: center; gap: 5px; cursor: pointer; font-size: 12px;">
							<input type="checkbox" name="lesion_desc" value="${desc}" ${isChecked ? 'checked' : ''}> ${desc}
						</label>
						`;
					}).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Palpation' },
			{ fieldtype: 'HTML', fieldname: 'palpation_help', options: `
				<div style="padding: 8px 12px; background: #e8f4fd; border-left: 3px solid #2490ef; margin-bottom: 15px; border-radius: 4px;">
					<small style="color: #1f7ab7;"><i class="fa fa-info-circle"></i> Palpate gently using gloved finger</small>
				</div>
			` },
			{ fieldtype: 'HTML', fieldname: 'palp_html', options: `
				<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 10px 0;">
					<!-- Consistency Column -->
					<div>
						<h6 style="font-weight: 600; margin-bottom: 10px; color: var(--heading-color); font-size: 13px;">Consistency</h6>
						<div style="display: flex; flex-direction: column; gap: 8px;">
							${LESION_CONFIG.palpation.consistency.map(item => {
								let isChecked = existingPalpations.includes(item);
								return `
								<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;">
									<input type="checkbox" name="lesion_palp_consistency" value="${item}" ${isChecked ? 'checked' : ''} style="width: 16px; height: 16px;"> ${item}
								</label>
								`;
							}).join('')}
						</div>
					</div>
					<!-- Surface Column -->
					<div>
						<h6 style="font-weight: 600; margin-bottom: 10px; color: var(--heading-color); font-size: 13px;">Surface</h6>
						<div style="display: flex; flex-direction: column; gap: 8px;">
							${LESION_CONFIG.palpation.surface.map(item => {
								let isChecked = existingPalpations.includes(item);
								return `
								<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;">
									<input type="checkbox" name="lesion_palp_surface" value="${item}" ${isChecked ? 'checked' : ''} style="width: 16px; height: 16px;"> ${item}
								</label>
								`;
							}).join('')}
						</div>
					</div>
					<!-- Findings Column -->
					<div>
						<h6 style="font-weight: 600; margin-bottom: 10px; color: var(--heading-color); font-size: 13px;">Findings</h6>
						<div style="display: flex; flex-direction: column; gap: 8px;">
							${LESION_CONFIG.palpation.findings.map(item => {
								let isChecked = existingPalpations.includes(item);
								return `
								<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 12px;">
									<input type="checkbox" name="lesion_palp_findings" value="${item}" ${isChecked ? 'checked' : ''} style="width: 16px; height: 16px;"> ${item}
								</label>
								`;
							}).join('')}
						</div>
					</div>
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Additional Details' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Select', fieldname: 'fixed_location', label: 'Fixed Location', options: '\n' + LESION_CONFIG.fixedLocations.join('\n'), default: lesion.fixed_location || '' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Int', fieldname: 'distance_mm', label: 'Distance in mm (from Fixed Location)', default: lesion.distance_mm || '' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Data', fieldname: 'relation_tooth', label: 'Relation to tooth#', default: lesion.relation_tooth || '' },
			{ fieldtype: 'Section Break', label: 'Notes' },
			{ fieldtype: 'Small Text', fieldname: 'notes', label: 'Notes', default: lesion.note || '' }
		],
		primary_action_label: 'Update Lesion',
		primary_action: function() {
			let values = d.get_values();
			
			// Get location
			let location = d.$wrapper.find('input[name="lesion_location"]:checked').val();
			if (!location) {
				frappe.msgprint('Please select a lesion location');
				return;
			}
			
			// Get selected values
			let colors = [];
			d.$wrapper.find('input[name="lesion_color"]:checked').each(function() { colors.push($(this).val()); });
			
			let shapes = [];
			d.$wrapper.find('input[name="lesion_shape"]:checked').each(function() { shapes.push($(this).val()); });
			
			let margins = [];
			d.$wrapper.find('input[name="lesion_margin"]:checked').each(function() { margins.push($(this).val()); });
			
			let descriptions = [];
			d.$wrapper.find('input[name="lesion_desc"]:checked').each(function() { descriptions.push($(this).val()); });
			
			// Get palpation values from all 3 groups
			let palpations = [];
			d.$wrapper.find('input[name="lesion_palp_consistency"]:checked').each(function() { palpations.push($(this).val()); });
			d.$wrapper.find('input[name="lesion_palp_surface"]:checked').each(function() { palpations.push($(this).val()); });
			d.$wrapper.find('input[name="lesion_palp_findings"]:checked').each(function() { palpations.push($(this).val()); });
			
			// Update existing row
			frm.doc.exam_lesion_examination[idx].location = location;
			frm.doc.exam_lesion_examination[idx].size_length = values.size_length || '';
			frm.doc.exam_lesion_examination[idx].size_width = values.size_width || '';
			frm.doc.exam_lesion_examination[idx].color = colors.join(', ');
			frm.doc.exam_lesion_examination[idx].shape = shapes.join(', ');
			frm.doc.exam_lesion_examination[idx].margin = margins.join(', ');
			frm.doc.exam_lesion_examination[idx].description = descriptions.join(', ');
			frm.doc.exam_lesion_examination[idx].palpation = palpations.join(', ');
			frm.doc.exam_lesion_examination[idx].fixed_location = values.fixed_location || '';
			frm.doc.exam_lesion_examination[idx].distance_mm = values.distance_mm || '';
			frm.doc.exam_lesion_examination[idx].relation_tooth = values.relation_tooth || '';
			frm.doc.exam_lesion_examination[idx].note = values.notes || '';
			
			frm.refresh_field('exam_lesion_examination');
			
			// Re-render lesion exam table
			render_step3_lesion_exam_table(frm, container);
			
			d.hide();
			frappe.show_alert({
				message: 'Lesion examination updated',
				indicator: 'green'
			});
		}
	});

	// Make entire label clickable for location
	d.$wrapper.on('click', '.lesion-location-label', function(e) {
		if (e.target.tagName !== 'INPUT') {
			$(this).find('input[type="radio"]').prop('checked', true);
		}
	});

	d.show();
}

// Render Lesion Examination Table
function render_step3_lesion_exam_table(frm, container) {
	let tableContainer = container.find('#step3_lesion_exam_table');
	if (tableContainer.length === 0) {
		container.append('<div id="step3_lesion_exam_table" style="margin-top: 15px;"></div>');
		tableContainer = container.find('#step3_lesion_exam_table');
	}

	let lesions = frm.doc.exam_lesion_examination || [];

	if (lesions.length === 0) {
		tableContainer.html('<p style="color: var(--text-muted); margin-top: 10px;">No lesion examination details added yet.</p>');
		return;
	}

	let html = `
		<table class="table table-bordered" style="font-size: 12px; margin-top: 15px; background: var(--card-bg);">
			<thead>
				<tr style="background: var(--subtle-bg);">
					<th>#</th>
					<th>Location</th>
					<th>Size (mm)</th>
					<th>Color</th>
					<th>Shape</th>
					<th>Margin</th>
					<th>Description</th>
					<th>Palpation</th>
					<th>Fixed Location</th>
					<th>Distance (mm)</th>
					<th>Relation to tooth#</th>
					<th>Notes</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				${lesions.map((l, idx) => `
					<tr>
						<td>${idx + 1}</td>
						<td>${l.location || '-'}</td>
						<td>${l.size_length || '-'} × ${l.size_width || '-'}</td>
						<td>${l.color || '-'}</td>
						<td>${l.shape || '-'}</td>
						<td>${l.margin || '-'}</td>
						<td>${l.description || '-'}</td>
						<td>${l.palpation || '-'}</td>
						<td>${l.fixed_location || '-'}</td>
						<td>${l.distance_mm || '-'}</td>
						<td>${l.relation_tooth || '-'}</td>
						<td>${l.note || '-'}</td>
						<td>
							<button type="button" class="btn btn-xs btn-primary step3-edit-lesion-exam" data-idx="${idx}" style="margin-right: 5px;">
								<i class="fa fa-edit"></i>
							</button>
							<button type="button" class="btn btn-xs btn-danger step3-delete-lesion-exam" data-idx="${idx}">
								<i class="fa fa-trash"></i>
							</button>
						</td>
					</tr>
				`).join('')}
			</tbody>
		</table>
	`;

	tableContainer.html(html);

	// Edit handler
	tableContainer.find('.step3-edit-lesion-exam').on('click', function() {
		let idx = parseInt($(this).data('idx'));
		show_lesion_examination_edit_popup(frm, idx, container);
	});

	// Delete handler
	tableContainer.find('.step3-delete-lesion-exam').on('click', function() {
		let idx = parseInt($(this).data('idx'));
		if (confirm('Delete this lesion examination?')) {
			frm.doc.exam_lesion_examination.splice(idx, 1);
			frm.refresh_field('exam_lesion_examination');
			render_step3_lesion_exam_table(frm, container);
			frappe.show_alert({ message: 'Lesion examination deleted', indicator: 'orange' });
		}
	});
}


// Legacy diagram function - now calls new STEP 3 function
function render_old_clinical_exam_diagram(frm) {
	if (!frm.fields_dict.exam_diagram_html) return;

	let wrapper = frm.fields_dict.exam_diagram_html.$wrapper;
	wrapper.empty();

	// Interactive Oral Cavity SVG Diagram
	let svg_html = `
		<div class="oral-exam-diagram-container" style="padding: 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 12px; margin: 10px 0;">
			<div style="text-align: center; margin-bottom: 15px;">
				<h5 style="color: #fff; margin: 0;">
					<i class="fa fa-teeth"></i> Oral Cavity Diagram - Click to Mark Lesions
				</h5>
				<small style="color: #888;">Click on any region to add a lesion marker</small>
			</div>
			
			<div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;">
				<!-- Face Front View -->
				<div class="diagram-card" style="background: #fff; border-radius: 10px; padding: 15px; min-width: 280px;">
					<h6 style="text-align: center; color: #333; margin-bottom: 10px;">Face & Neck</h6>
					<svg viewBox="0 0 200 250" style="width: 100%; max-width: 250px; display: block; margin: 0 auto;">
						<!-- Face outline -->
						<ellipse cx="100" cy="80" rx="60" ry="70" fill="#ffe4c4" stroke="#333" stroke-width="1.5" class="face-region" data-region="face"/>
						<!-- Eyes -->
						<ellipse cx="75" cy="60" rx="12" ry="6" fill="#fff" stroke="#333" class="clickable-region" data-region="eye-left"/>
						<ellipse cx="125" cy="60" rx="12" ry="6" fill="#fff" stroke="#333" class="clickable-region" data-region="eye-right"/>
						<circle cx="75" cy="60" r="4" fill="#4a4a4a"/>
						<circle cx="125" cy="60" r="4" fill="#4a4a4a"/>
						<!-- Nose -->
						<path d="M100,55 L95,85 Q100,90 105,85 L100,55" fill="#deb887" stroke="#333" class="clickable-region" data-region="nose"/>
						<!-- Mouth -->
						<ellipse cx="100" cy="110" rx="20" ry="8" fill="#cc6666" stroke="#333" stroke-width="1" class="clickable-region" data-region="lips"/>
						<!-- Cheeks -->
						<circle cx="55" cy="85" r="15" fill="rgba(255,182,193,0.3)" stroke="none" class="clickable-region" data-region="cheek-left"/>
						<circle cx="145" cy="85" r="15" fill="rgba(255,182,193,0.3)" stroke="none" class="clickable-region" data-region="cheek-right"/>
						<!-- Ears -->
						<ellipse cx="38" cy="75" rx="8" ry="15" fill="#ffe4c4" stroke="#333" class="clickable-region" data-region="ear-left"/>
						<ellipse cx="162" cy="75" rx="8" ry="15" fill="#ffe4c4" stroke="#333" class="clickable-region" data-region="ear-right"/>
						<!-- Neck -->
						<rect x="70" y="145" width="60" height="50" fill="#ffe4c4" stroke="#333" class="clickable-region" data-region="neck-central"/>
						<rect x="40" y="155" width="35" height="40" fill="#ffe4c4" stroke="#333" class="clickable-region" data-region="neck-left"/>
						<rect x="125" y="155" width="35" height="40" fill="#ffe4c4" stroke="#333" class="clickable-region" data-region="neck-right"/>
						<!-- Labels -->
						<text x="100" y="140" text-anchor="middle" font-size="8" fill="#666">Neck</text>
					</svg>
				</div>
				
				<!-- Open Mouth View -->
				<div class="diagram-card" style="background: #fff; border-radius: 10px; padding: 15px; min-width: 300px;">
					<h6 style="text-align: center; color: #333; margin-bottom: 10px;">Oral Cavity (Open Mouth)</h6>
					<svg viewBox="0 0 220 200" style="width: 100%; max-width: 280px; display: block; margin: 0 auto;">
						<!-- Outer lips -->
						<ellipse cx="110" cy="100" rx="95" ry="85" fill="#cc8888" stroke="#8b4513" stroke-width="2"/>
						<!-- Inner mouth cavity -->
						<ellipse cx="110" cy="100" rx="75" ry="65" fill="#8b0000" stroke="#660000" stroke-width="1"/>
						
						<!-- Upper lip -->
						<path d="M40,70 Q110,40 180,70" fill="none" stroke="#cc6666" stroke-width="8" class="clickable-region" data-region="upper-lip"/>
						<!-- Lower lip -->
						<path d="M40,130 Q110,160 180,130" fill="none" stroke="#cc6666" stroke-width="8" class="clickable-region" data-region="lower-lip"/>
						
						<!-- Tongue -->
						<ellipse cx="110" cy="115" rx="45" ry="35" fill="#ff6b6b" stroke="#cc4444" stroke-width="1" class="clickable-region" data-region="tongue-dorsum"/>
						<line x1="110" y1="80" x2="110" y2="145" stroke="#cc4444" stroke-width="1"/>
						
						<!-- Teeth Upper -->
						<path d="M50,65 L55,80 L65,80 L70,65 L80,65 L85,80 L95,80 L100,65 L110,65 L115,65 L120,80 L130,80 L135,65 L145,65 L150,80 L160,80 L165,65 L170,65" 
							  fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" class="clickable-region" data-region="teeth-upper"/>
						
						<!-- Teeth Lower -->
						<path d="M55,135 L60,120 L70,120 L75,135 L85,135 L90,120 L100,120 L105,135 L115,135 L120,120 L130,120 L135,135 L145,135 L150,120 L160,120 L165,135" 
							  fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" class="clickable-region" data-region="teeth-lower"/>
						
						<!-- Buccal regions -->
						<ellipse cx="45" cy="100" rx="15" ry="25" fill="rgba(255,150,150,0.5)" stroke="#cc6666" class="clickable-region" data-region="buccal-left"/>
						<ellipse cx="175" cy="100" rx="15" ry="25" fill="rgba(255,150,150,0.5)" stroke="#cc6666" class="clickable-region" data-region="buccal-right"/>
						
						<!-- Hard Palate -->
						<ellipse cx="110" cy="55" rx="40" ry="15" fill="#ffb6c1" stroke="#cc8888" class="clickable-region" data-region="hard-palate"/>
						
						<!-- Uvula/Soft Palate area -->
						<ellipse cx="110" cy="45" rx="15" ry="8" fill="#ff9999" stroke="#cc6666" class="clickable-region" data-region="soft-palate"/>
						
						<!-- Floor of mouth -->
						<ellipse cx="110" cy="155" rx="35" ry="12" fill="#cc6666" stroke="#993333" class="clickable-region" data-region="floor-mouth"/>
						
						<!-- Labels -->
						<text x="110" y="58" text-anchor="middle" font-size="7" fill="#fff">Palate</text>
						<text x="110" y="118" text-anchor="middle" font-size="8" fill="#fff">Tongue</text>
						<text x="45" cy="100" text-anchor="middle" font-size="6" fill="#333">L</text>
						<text x="175" cy="100" text-anchor="middle" font-size="6" fill="#333">R</text>
					</svg>
				</div>
				
				<!-- Tongue Detail -->
				<div class="diagram-card" style="background: #fff; border-radius: 10px; padding: 15px; min-width: 250px;">
					<h6 style="text-align: center; color: #333; margin-bottom: 10px;">Tongue (Detailed View)</h6>
					<svg viewBox="0 0 180 150" style="width: 100%; max-width: 220px; display: block; margin: 0 auto;">
						<!-- Tongue body -->
						<path d="M90,10 Q150,30 150,70 Q150,110 90,140 Q30,110 30,70 Q30,30 90,10" 
							  fill="#ff6b6b" stroke="#cc4444" stroke-width="2"/>
						<!-- Midline -->
						<line x1="90" y1="15" x2="90" y2="135" stroke="#cc4444" stroke-width="1" stroke-dasharray="3,3"/>
						
						<!-- Regions -->
						<ellipse cx="90" cy="35" rx="35" ry="18" fill="rgba(255,100,100,0.3)" stroke="#cc4444" class="clickable-region" data-region="tongue-base"/>
						<ellipse cx="60" cy="75" rx="20" ry="25" fill="rgba(255,150,150,0.3)" stroke="#cc4444" class="clickable-region" data-region="tongue-lateral-left"/>
						<ellipse cx="120" cy="75" rx="20" ry="25" fill="rgba(255,150,150,0.3)" stroke="#cc4444" class="clickable-region" data-region="tongue-lateral-right"/>
						<ellipse cx="90" cy="110" rx="25" ry="15" fill="rgba(255,180,180,0.3)" stroke="#cc4444" class="clickable-region" data-region="tongue-tip"/>
						
						<!-- Ventral indicator -->
						<text x="90" y="75" text-anchor="middle" font-size="8" fill="#fff">Dorsum</text>
						<text x="60" y="75" text-anchor="middle" font-size="6" fill="#333">L</text>
						<text x="120" y="75" text-anchor="middle" font-size="6" fill="#333">R</text>
						<text x="90" y="125" text-anchor="middle" font-size="7" fill="#fff">Tip</text>
					</svg>
				</div>
			</div>
			
			<!-- Lesion Markers Display -->
			<div id="lesion-markers-display" style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px; display: none;">
				<h6 style="color: #fff; margin-bottom: 10px;"><i class="fa fa-map-marker-alt"></i> Marked Lesions</h6>
				<div id="lesion-list" style="color: #ccc;"></div>
			</div>
		</div>
	`;

	wrapper.html(svg_html);

	// Add click handlers for diagram regions
	wrapper.find('.clickable-region').on('click', function () {
		let region = $(this).data('region');
		add_lesion_from_diagram(frm, region);
	});

	// Style clickable regions
	wrapper.find('.clickable-region').css({
		'cursor': 'pointer',
		'transition': 'all 0.2s ease'
	}).hover(
		function () { $(this).css({ 'opacity': '0.7', 'stroke-width': '3' }); },
		function () { $(this).css({ 'opacity': '1', 'stroke-width': '' }); }
	);
}

function add_lesion_from_diagram(frm, region) {
	// Format region name
	let region_name = region.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

	let d = new frappe.ui.Dialog({
		title: __('Add Lesion - {0}', [region_name]),
		fields: [
			{
				fieldname: 'lesion_type',
				fieldtype: 'Select',
				label: 'Lesion Type',
				options: '\\nWhite Patch (Leukoplakia)\\nRed Patch (Erythroplakia)\\nUlcer - Superficial\\nUlcer - Deep\\nNodule/Lump\\nSwelling\\nFibrous Bands\\nVesicle\\nPapule\\nPlaque\\nOther',
				reqd: 1
			},
			{
				fieldname: 'description',
				fieldtype: 'Small Text',
				label: 'Description'
			}
		],
		primary_action_label: __('Add Lesion'),
		primary_action: function () {
			let values = d.get_values();

			// Add to lesions table
			let row = frm.add_child('exam_lesions');
			row.lesion_number = (frm.doc.exam_lesions || []).length;
			row.diagram_region = region_name;
			row.lesion_type = values.lesion_type;
			row.description = values.description;

			frm.refresh_field('exam_lesions');
			d.hide();

			frappe.show_alert({
				message: __('Lesion added for {0}', [region_name]),
				indicator: 'green'
			});
		}
	});
	d.show();
}

// Clinical Images Section with Direct Upload
function render_clinical_images_section(frm) {
	if (!frm.fields_dict.exam_images_section) return;

	// Add custom image upload UI before the table
	let wrapper = frm.fields_dict.exam_images_section.$wrapper;

	// Remove existing custom UI
	wrapper.find('.clinical-images-upload-ui').remove();

	let image_categories = [
		'Face and Neck',
		'Open Mouth with Scale',
		'Central Arch with Lips',
		'Right Cheek with Alveolus',
		'Left Cheek with Alveolus',
		'Tongue Protruded',
		'Tongue with Floor of Mouth',
		'Hard and Soft Palate',
		'Abnormal Area Focused',
		'Special Tests'
	];

	let upload_html = `
		<div class="clinical-images-upload-ui" style="padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin: 10px 0;">
			<h6 style="color: #fff; margin-bottom: 15px;">
				<i class="fa fa-camera"></i> Clinical Images - Quick Upload
			</h6>
			<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px;">
				${image_categories.map((cat, idx) => `
					<div class="image-upload-card" data-category="${cat}" style="
						background: rgba(255,255,255,0.95);
						border-radius: 8px;
						padding: 10px;
						text-align: center;
						cursor: pointer;
						transition: all 0.2s ease;
						border: 2px dashed #ccc;
					">
						<div class="upload-icon" style="font-size: 24px; color: #667eea; margin-bottom: 5px;">
							<i class="fa fa-plus-circle"></i>
						</div>
						<div style="font-size: 11px; color: #333; font-weight: 500;">
							${idx + 1}. ${cat}
						</div>
						<div class="image-preview" style="margin-top: 8px; display: none;">
							<img src="" style="max-width: 100%; border-radius: 4px;"/>
						</div>
					</div>
				`).join('')}
			</div>
		</div>
	`;

	wrapper.prepend(upload_html);

	// Add click handlers for image upload
	wrapper.find('.image-upload-card').on('click', function () {
		let category = $(this).data('category');
		let card = $(this);

		new frappe.ui.FileUploader({
			doctype: frm.doctype,
			docname: frm.docname,
			folder: 'Home/Attachments',
			on_success: function (file_doc) {
				// Add to images table
				let row = frm.add_child('exam_images');
				row.image_category = category;
				row.image = file_doc.file_url;
				row.uploaded_by = frappe.session.user;
				row.upload_time = frappe.datetime.now_datetime();

				frm.refresh_field('exam_images');

				// Update card UI
				card.find('.upload-icon').html('<i class="fa fa-check-circle" style="color: #28a745;"></i>');
				card.find('.image-preview').show().find('img').attr('src', file_doc.file_url);
				card.css('border-color', '#28a745');

				frappe.show_alert({
					message: __('Image uploaded: {0}', [category]),
					indicator: 'green'
				});
			}
		});
	});

	// Hover effects
	wrapper.find('.image-upload-card').hover(
		function () { $(this).css({ 'transform': 'scale(1.02)', 'box-shadow': '0 4px 15px rgba(0,0,0,0.1)' }); },
		function () { $(this).css({ 'transform': 'scale(1)', 'box-shadow': 'none' }); }
	);

	// Show existing images
	if (frm.doc.exam_images && frm.doc.exam_images.length > 0) {
		frm.doc.exam_images.forEach(img => {
			let card = wrapper.find(`.image-upload-card[data-category="${img.image_category}"]`);
			if (card.length && img.image) {
				card.find('.upload-icon').html('<i class="fa fa-check-circle" style="color: #28a745;"></i>');
				card.find('.image-preview').show().find('img').attr('src', img.image);
				card.css('border-color', '#28a745');
			}
		});
	}
}

// STEP 4 - Pictures Upload with Direct Display
function render_step4_pictures(frm) {
	// Find the Pictures HTML field to render Clinical Photographs UI
	let picturesHtmlField = frm.fields_dict.exam_pictures_html;
	if (!picturesHtmlField || !picturesHtmlField.$wrapper) {
		console.log('Step 4: exam_pictures_html field not found');
		return;
	}

	// Remove any existing step4-pictures-container
	$('.step4-pictures-container').remove();

	// Find the section body to append full-width container
	let sectionBody = picturesHtmlField.$wrapper.closest('.section-body');
	if (!sectionBody.length) {
		sectionBody = picturesHtmlField.$wrapper.closest('.frappe-control').parent();
	}

	console.log('Step 4: Rendering picture grid in section body');


	// Picture categories matching the sheet
	const picture_categories = [
		{ num: 1, name: 'Face and Neck', field: 'exam_pic_1_face_neck', icon: 'fa-user' },
		{ num: 2, name: 'Open Mouth with Scale/Triscare', field: 'exam_pic_2_open_mouth', icon: 'fa-teeth-open' },
		{ num: 3, name: 'Central Arch with Both Lips', field: 'exam_pic_3_central_arch', icon: 'fa-lips' },
		{ num: 4, name: 'Right Cheek with Alveolus', field: 'exam_pic_4_right_cheek', icon: 'fa-face-smile' },
		{ num: 5, name: 'Left Cheek with Alveolus', field: 'exam_pic_5_left_cheek', icon: 'fa-face-smile' },
		{ num: 6, name: 'Tongue Protruded', field: 'exam_pic_6_tongue', icon: 'fa-tongue' },
		{ num: 7, name: 'Tongue with Floor of Mouth', field: 'exam_pic_7_tongue_floor', icon: 'fa-tongue' },
		{ num: 8, name: 'Hard and Soft Palate', field: 'exam_pic_8_palate', icon: 'fa-circle' },
		{ num: 9, name: 'Abnormal Area Focused', field: 'exam_pic_9_abnormal', icon: 'fa-search-plus' },
		{ num: 10, name: 'Special Tests', field: 'exam_pic_10_special', icon: 'fa-microscope' }
	];

	let html = `
		<style>
			.step4-container {
				padding: 15px;
				background: var(--card-bg);
				border-radius: 8px;
				margin: 10px 0;
				border: 1px solid var(--border-color);
				width: 100%;
				max-width: 100%;
				box-sizing: border-box;
			}
			/* Make container full width */
			[data-fieldname="exam_pictures_html"],
			.step4-pictures-container {
				width: 100% !important;
				max-width: 100% !important;
			}
			[data-fieldname="exam_pictures_html"] .frappe-control,
			.step4-pictures-container .step4-container {
				width: 100% !important;
			}
			.step4-header {
				color: var(--heading-color);
				margin-bottom: 15px;
				padding-bottom: 10px;
				border-bottom: 1px solid var(--border-color);
			}
			.step4-header h5 {
				margin: 0;
				font-size: 14px;
			}
			.step4-header small {
				color: var(--text-muted);
			}
			.pictures-grid {
				display: grid;
				grid-template-columns: repeat(5, 1fr);
				gap: 10px;
			}
			@media (max-width: 1200px) {
				.pictures-grid { grid-template-columns: repeat(4, 1fr); }
			}
			@media (max-width: 900px) {
				.pictures-grid { grid-template-columns: repeat(3, 1fr); }
			}
			@media (max-width: 600px) {
				.pictures-grid { grid-template-columns: repeat(2, 1fr); }
			}
		.picture-card {
			background: var(--card-bg);
			border-radius: 6px;
			overflow: hidden;
			border: 1px solid var(--border-color);
			transition: all 0.2s ease;
			cursor: pointer;
		}
		.picture-card:hover {
			border-color: var(--primary);
			box-shadow: 0 2px 10px rgba(0,0,0,0.15);
			transform: translateY(-2px);
		}
		.picture-card-header {
			background: var(--subtle-bg);
			color: var(--text-color);
			padding: 8px;
			font-size: 10px;
			font-weight: 600;
			text-align: center;
			border-bottom: 1px solid var(--border-color);
		}
		.picture-card-body {
			padding: 0;
			aspect-ratio: 4 / 3;
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: center;
			background: var(--control-bg);
			position: relative;
		}
		.picture-placeholder {
			width: 100%;
			height: 100%;
			border: 2px dashed var(--border-color);
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: center;
			cursor: pointer;
			transition: all 0.2s ease;
			background: var(--control-bg);
		}
		.picture-placeholder:hover {
			border-color: var(--primary);
			background: var(--subtle-bg);
		}
		.picture-placeholder i {
			font-size: 24px;
			color: var(--text-muted);
			margin-bottom: 5px;
		}
		.picture-placeholder span {
			font-size: 11px;
			color: var(--text-muted);
			font-weight: 500;
		}
		.picture-preview {
			width: 100%;
			height: 100%;
			position: relative;
			display: flex;
			align-items: center;
			justify-content: center;
			background: var(--control-bg);
		}
		.picture-preview img {
			width: 100%;
			height: 100%;
			object-fit: contain;
			cursor: pointer;
		}
		.picture-actions {
			position: absolute;
			top: 5px;
			right: 5px;
			display: flex;
			gap: 5px;
			opacity: 0;
			transition: opacity 0.2s ease;
			z-index: 10;
		}
		.picture-card:hover .picture-actions {
			opacity: 1;
		}
		.picture-action-btn {
			width: 32px;
			height: 32px;
			border-radius: 50%;
			border: none;
			cursor: pointer;
			display: flex;
			align-items: center;
			justify-content: center;
			font-size: 14px;
			transition: all 0.2s ease;
			box-shadow: 0 2px 5px rgba(0,0,0,0.3);
		}
		.btn-view {
			background: rgba(0,123,255,0.95);
			color: #fff;
		}
		.btn-view:hover {
			background: rgba(0,123,255,1);
		}
		.btn-view i {
			color: #fff;
		}
		.btn-replace {
			background: rgba(255,193,7,0.95);
			color: #333;
		}
		.btn-replace:hover {
			background: rgba(255,193,7,1);
		}
		.btn-replace i {
			color: #333;
			font-size: 14px;
		}
		.btn-delete {
			background: rgba(220,53,69,0.95);
			color: #fff;
		}
		.btn-delete:hover {
			background: rgba(220,53,69,1);
		}
		.btn-delete i {
			color: #fff;
		}
		.picture-action-btn:hover {
			transform: scale(1.15);
		}
		.upload-status {
			position: absolute;
			bottom: 8px;
			left: 50%;
			transform: translateX(-50%);
			font-size: 10px;
			color: #28a745;
			display: none;
			font-weight: 500;
			background: rgba(255,255,255,0.9);
			padding: 3px 8px;
			border-radius: 10px;
		}
		.upload-status.show {
			display: block;
		}
		</style>
		
		<div class="step4-container">
			<div class="step4-header">
				<h5 style="margin: 0;"><i class="fa fa-camera"></i> Clinical Photographs</h5>
				<small style="opacity: 0.8;">Click on any card to upload image. Images will display directly.</small>
			</div>
			
			<div class="pictures-grid">
				${picture_categories.map(cat => {
		let existing_image = frm.doc[cat.field];
		return `
						<div class="picture-card" data-field="${cat.field}" data-name="${cat.name}">
							<div class="picture-card-header">
								<i class="fa ${cat.icon}"></i> ${cat.num}. ${cat.name}
							</div>
							<div class="picture-card-body">
								${existing_image ? `
									<div class="picture-preview">
									<img src="${existing_image}" alt="${cat.name}" class="preview-img"/>
									<div class="picture-actions">
										<button class="picture-action-btn btn-view" title="View Full"><i class="fa fa-expand"></i></button>
										<button class="picture-action-btn btn-replace" title="Replace"><i class="fa fa-repeat"></i></button>
										<button class="picture-action-btn btn-delete" title="Delete"><i class="fa fa-trash"></i></button>
									</div>
								</div>
									<div class="upload-status show"><i class="fa fa-check"></i> Uploaded</div>
								` : `
									<div class="picture-placeholder">
										<i class="fa fa-cloud-upload-alt"></i>
										<span>Click to Upload</span>
									</div>
									<div class="upload-status"><i class="fa fa-check"></i> Uploaded</div>
								`}
							</div>
						</div>
					`;
	}).join('')}
			</div>
		</div>
	`;

	// Create container and append to section body (full width)
	let container = $('<div class="step4-pictures-container" style="width:100%; margin-top:15px;">').html(html);
	sectionBody.append(container);
	console.log('Step 4: HTML appended to section body');


	// Add click handlers for upload
	container.find('.picture-placeholder').on('click', function (e) {
		e.stopPropagation();
		let card = $(this).closest('.picture-card');
		let field = card.data('field');
		let name = card.data('name');
		upload_picture(frm, card, field, name);
	});

	// Click on card with image - expand image
	container.find('.picture-card').on('click', function (e) {
		// Don't trigger if clicking on action buttons
		if ($(e.target).closest('.picture-action-btn').length > 0) {
			return;
		}
		
		let img = $(this).find('.preview-img');
		if (img.length > 0) {
			let img_src = img.attr('src');
			let name = $(this).data('name');

			let d = new frappe.ui.Dialog({
				title: name,
				size: 'extra-large'
			});
			d.$body.html(`<img src="${img_src}" style="width: 100%; max-height: 80vh; object-fit: contain; background: var(--control-bg);"/>`);
			d.show();
		}
	});

	// View full image
	container.find('.btn-view').on('click', function (e) {
		e.stopPropagation();
		let img_src = $(this).closest('.picture-preview').find('img').attr('src');
		let name = $(this).closest('.picture-card').data('name');

		let d = new frappe.ui.Dialog({
			title: name,
			size: 'extra-large'
		});
		d.$body.html(`<img src="${img_src}" style="width: 100%; max-height: 80vh; object-fit: contain; background: var(--control-bg);"/>`);
		d.show();
	});

	// Replace image
	container.find('.btn-replace').on('click', function (e) {
		e.stopPropagation();
		let card = $(this).closest('.picture-card');
		let field = card.data('field');
		let name = card.data('name');
		upload_picture(frm, card, field, name);
	});

	// Delete image
	container.find('.btn-delete').on('click', function (e) {
		e.stopPropagation();
		let card = $(this).closest('.picture-card');
		let field = card.data('field');
		let name = card.data('name');

		frappe.confirm(
			__('Are you sure you want to delete the image for "{0}"?', [name]),
			() => {
				frm.set_value(field, '');

				// Update UI
				card.find('.picture-card-body').html(`
					<div class="picture-placeholder">
						<i class="fa fa-cloud-upload-alt"></i>
						<span>Click to Upload</span>
					</div>
					<div class="upload-status"><i class="fa fa-check"></i> Uploaded</div>
				`);

				// Re-bind click handler
				card.find('.picture-placeholder').on('click', function () {
					upload_picture(frm, card, field, name);
				});

				frappe.show_alert({
					message: __('Image deleted: {0}', [name]),
					indicator: 'orange'
				});
			}
		);
	});
}

// Upload picture helper function
function upload_picture(frm, card, field, name) {
	new frappe.ui.FileUploader({
		doctype: frm.doctype,
		docname: frm.docname,
		folder: 'Home/Attachments',
		restrictions: {
			allowed_file_types: ['image/*']
		},
		on_success: function (file_doc) {
			// Set field value
			frm.set_value(field, file_doc.file_url);

			// Update card UI
			card.find('.picture-card-body').html(`
				<div class="picture-preview">
				<img src="${file_doc.file_url}" alt="${name}" class="preview-img"/>
				<div class="picture-actions">
					<button class="picture-action-btn btn-view" title="View Full"><i class="fa fa-expand"></i></button>
					<button class="picture-action-btn btn-replace" title="Replace"><i class="fa fa-repeat"></i></button>
					<button class="picture-action-btn btn-delete" title="Delete"><i class="fa fa-trash"></i></button>
				</div>
			</div>
				<div class="upload-status show"><i class="fa fa-check"></i> Uploaded</div>
			`);

			// Re-bind action handlers
			card.find('.btn-view').on('click', function (e) {
				e.stopPropagation();
				let d = new frappe.ui.Dialog({
					title: name,
					size: 'extra-large'
				});
				d.$body.html(`<img src="${file_doc.file_url}" style="width: 100%; max-height: 80vh; object-fit: contain;"/>`);
				d.show();
			});

			card.find('.btn-replace').on('click', function (e) {
				e.stopPropagation();
				upload_picture(frm, card, field, name);
			});

			card.find('.btn-delete').on('click', function (e) {
				e.stopPropagation();
				frappe.confirm(
					__('Are you sure you want to delete the image for "{0}"?', [name]),
					() => {
						frm.set_value(field, '');
						render_step4_pictures(frm); // Re-render
						frappe.show_alert({
							message: __('Image deleted: {0}', [name]),
							indicator: 'orange'
						});
					}
				);
			});

			frappe.show_alert({
				message: __('Image uploaded: {0}', [name]),
				indicator: 'green'
			});
		}
	});
}


// ================== STEP 1 - PATIENT COMPLAINTS (REDESIGNED v2) ==================
// Body Part selection opens popup with complaints, uses ERPNext standard table

const BODY_PARTS_CONFIG = {
	'Face': {
		symptoms: ['Lump/Swelling on face', 'Pigmentation', 'Ulcer', 'Other']
	},
	'Neck': {
		symptoms: ['Lump/Swelling in Neck (outside)', 'Swelling/lump in Throat (inside)', 'Stickiness in throat', 'Change in Voice', 'Sore throat/Hoarseness', 'Swallowing Difficulty/pain', 'Other']
	},
	'Oral Cavity (Mouth and Tongue)': {
		symptoms: ['Restricted Mouth opening', 'Restricted Tongue Movement', 'Pain', 'Painful Ulcer', 'Painless Ulcer', 'Recurrent Ulcer', 'Red patch in mouth', 'White patch in mouth', 'Nodule/Lump', 'Swelling', 'Sensitivity in mouth/teeth', 'Burning Sensation', 'Bleeding', 'Decreased Salivation', 'Increased Salivation', 'Foul Smell (Halitosis)', 'Swallowing Difficulty/pain during', 'Others']
	},
	'Teeth (Dental)': {
		symptoms: ['Painful teeth', 'Loosening of teeth', 'Lost teeth', 'Teeth or gum problem', 'Denture problem', 'Other']
	},
	'Others': {
		symptoms: ['Earache', 'Others']
	}
};

const OPTION_VALUES = ['Increasing', 'Decreasing', 'Persistent', 'Intermittent', 'Recurrent'];

function render_step1_table_form(frm) {
	console.log('Step 1: render_step1_table_form called');
	let wrapper = frm.fields_dict.exam_step1_table_html?.$wrapper;
	if (!wrapper) {
		console.log('Step 1: wrapper not found, returning');
		return;
	}
	console.log('Step 1: wrapper found, rendering HTML');

	wrapper.empty();

	let currentStatus = frm.doc.exam_complaints_status || '';
	let isNormal = currentStatus === 'No Complaints - Normal';
	let isAbnormal = currentStatus === 'Complaints - Abnormal';

	let html = `
		<style>
			.step1-radio-group { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; }
			.step1-radio-label { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 6px; cursor: pointer; font-size: 13px; transition: all 0.2s; }
			.step1-radio-label:hover { background: var(--subtle-accent); border-color: var(--primary); }
			.step1-radio-label input[type="radio"] { margin: 0; }
			.step1-section-title { font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 10px; }
		</style>
		
		<div class="step1-form">
			<!-- Complaints Status -->
			<div class="row" style="margin-bottom: 15px;">
				<div class="col-md-4">
					<div class="form-group">
						<label class="control-label" style="font-size: 12px; color: var(--text-muted);">Complaints Status</label>
						<select class="form-control input-sm" id="step1_status">
							<option value="">Select...</option>
							<option value="No Complaints - Normal" ${isNormal ? 'selected' : ''}>No Complaints - Normal</option>
							<option value="Complaints - Abnormal" ${isAbnormal ? 'selected' : ''}>Complaints - Abnormal</option>
						</select>
					</div>
				</div>
			</div>
			
			<!-- Normal Message - Only show when Normal is selected -->
			<div id="step1_normal_msg" style="display: ${isNormal ? 'block' : 'none'}; padding: 20px; text-align: center; background: var(--subtle-bg); border-radius: 6px; margin-bottom: 15px;">
				<span style="color: var(--green-500);">✓ No complaints reported. Patient is normal.</span>
			</div>
			
			<!-- Body Part Selection - Only shows for Abnormal status -->
			<div id="step1_body_part_section" style="display: ${isAbnormal ? 'block' : 'none'};">
				<div style="margin-bottom: 15px;">
					<div class="step1-section-title">Select Body Part</div>
					<div class="step1-radio-group">
						${Object.keys(BODY_PARTS_CONFIG).map(bp => `
							<label class="step1-radio-label">
								<input type="radio" name="step1_bodypart" value="${bp}"> ${bp}
							</label>
						`).join('')}
					</div>
				</div>
			</div>
			
		</div>
	`;

	wrapper.html(html);

	// Setup handlers
	setup_step1_handlers(frm, wrapper);

	// Show/hide the ERPNext standard table based on status
	toggle_complaints_table_visibility(frm);
}

function toggle_complaints_table_visibility(frm) {
	// Show the standard ERPNext table field for complaints
	let status = frm.doc.exam_complaints_status || '';
	let isAbnormal = status === 'Complaints - Abnormal';
	
	console.log('toggle_complaints_table_visibility called, status:', status, 'isAbnormal:', isAbnormal);
	console.log('exam_complaints field exists:', !!frm.fields_dict.exam_complaints);
	
	if (frm.fields_dict.exam_complaints) {
		console.log('exam_complaints wrapper exists:', !!frm.fields_dict.exam_complaints.$wrapper);
		
		if (isAbnormal) {
			// Show table
			frm.set_df_property('exam_complaints', 'hidden', 0);
			frm.toggle_display('exam_complaints', true);
			if (frm.fields_dict.exam_complaints.$wrapper) {
				frm.fields_dict.exam_complaints.$wrapper.show();
				frm.fields_dict.exam_complaints.$wrapper.css('display', 'block');
			}
		} else {
			// Hide table
			frm.set_df_property('exam_complaints', 'hidden', 1);
			frm.toggle_display('exam_complaints', false);
			if (frm.fields_dict.exam_complaints.$wrapper) {
				frm.fields_dict.exam_complaints.$wrapper.hide();
			}
		}
		frm.refresh_field('exam_complaints');
	} else {
		console.log('exam_complaints field NOT found in frm.fields_dict');
	}
}

function show_complaints_popup(frm, bodyPart) {
	let symptoms = BODY_PARTS_CONFIG[bodyPart]?.symptoms || [];
	
	if (symptoms.length === 0) {
		frappe.msgprint(__('No complaints configured for this body part'));
		return;
	}

	// Get existing complaints for this body part with full data for editing
	let existingComplaints = new Map(); // Map of complaint_type -> row data
	if (frm.doc.exam_complaints && frm.doc.exam_complaints.length > 0) {
		frm.doc.exam_complaints.forEach(row => {
			if (row.body_part === bodyPart && row.complaint_type) {
				existingComplaints.set(row.complaint_type, row);
			}
		});
	}

	// Build the popup content with checkboxes for multiple selection
	let popup_html = `
		<style>
			.complaint-popup-table { width: 100%; border-collapse: collapse; }
			.complaint-popup-table th { 
				background: var(--subtle-bg); 
				padding: 10px 8px; 
				text-align: left; 
				font-size: 12px; 
				font-weight: 600; 
				color: var(--text-muted); 
				border-bottom: 1px solid var(--border-color);
			}
			.complaint-popup-table td { 
				padding: 8px; 
				border-bottom: 1px solid var(--border-color); 
				font-size: 12px; 
				vertical-align: middle;
			}
			.complaint-popup-table tbody tr:hover { background: var(--subtle-bg); }
			.complaint-popup-table tbody tr.already-added { 
				background: var(--bg-green); 
				opacity: 0.7;
			}
			.complaint-popup-table input[type="checkbox"] { 
				width: 16px; 
				height: 16px; 
				cursor: pointer; 
			}
			.complaint-popup-table input[type="checkbox"]:disabled { 
				cursor: not-allowed; 
			}
			.complaint-popup-table input[type="number"] { 
				width: 70px; 
				padding: 4px 6px; 
				border: 1px solid var(--border-color); 
				border-radius: 4px; 
				font-size: 12px;
			}
			.complaint-popup-table select { 
				width: 120px; 
				padding: 4px 6px; 
				border: 1px solid var(--border-color); 
				border-radius: 4px; 
				font-size: 12px;
			}
			.complaint-popup-table input[type="text"] { 
				width: 100%; 
				padding: 4px 6px; 
				border: 1px solid var(--border-color); 
				border-radius: 4px; 
				font-size: 12px;
			}
		</style>
		<table class="complaint-popup-table">
			<thead>
				<tr>
					<th style="width: 30px;"></th>
					<th>Complaint</th>
					<th style="width: 80px;">Days</th>
					<th style="width: 130px;">Option</th>
					<th style="width: 60px;">Trauma</th>
					<th style="width: 80px;">Treated Before</th>
					<th style="width: 150px;">Notes</th>
				</tr>
			</thead>
			<tbody>
				${symptoms.map((symptom, idx) => {
					const isAlreadyAdded = existingComplaints.has(symptom);
					const existingData = isAlreadyAdded ? existingComplaints.get(symptom) : null;
					
					// Pre-fill values if already added
					const daysValue = existingData ? existingData.duration_days || 0 : 0;
					const optionValue = existingData ? existingData.option || '' : '';
					const traumaChecked = existingData && existingData.trauma_related ? 'checked' : '';
					const treatedChecked = existingData && existingData.medical_treatment_taken ? 'checked' : '';
					const notesValue = existingData ? existingData.note || '' : '';
					
					return `
					<tr class="${isAlreadyAdded ? 'already-added' : ''}">
						<td><input type="checkbox" class="complaint-check" data-symptom="${symptom}" data-idx="${idx}" ${isAlreadyAdded ? 'checked' : ''}></td>
						<td>${symptom}${isAlreadyAdded ? ' <span style="color: var(--green-500); font-size: 11px;">(Already Added)</span>' : ''}</td>
						<td><input type="number" class="complaint-days" data-idx="${idx}" min="0" placeholder="0" value="${daysValue}" ${isAlreadyAdded ? '' : 'disabled'}></td>
						<td>
							<select class="complaint-option" data-idx="${idx}" ${isAlreadyAdded ? '' : 'disabled'}>
								<option value="">Select...</option>
								${OPTION_VALUES.map(opt => `<option value="${opt}" ${opt === optionValue ? 'selected' : ''}>${opt}</option>`).join('')}
							</select>
						</td>
						<td style="text-align: center;"><input type="checkbox" class="complaint-trauma" data-idx="${idx}" ${traumaChecked} ${isAlreadyAdded ? '' : 'disabled'}></td>
						<td style="text-align: center;"><input type="checkbox" class="complaint-treated" data-idx="${idx}" ${treatedChecked} ${isAlreadyAdded ? '' : 'disabled'}></td>
						<td><input type="text" class="complaint-notes" data-idx="${idx}" placeholder="Notes..." value="${notesValue}" ${isAlreadyAdded ? '' : 'disabled'}></td>
					</tr>
				`;
				}).join('')}
			</tbody>
		</table>
	`;

	let d = new frappe.ui.Dialog({
		title: __('Select Complaints for {0}', [bodyPart]),
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'complaints_html',
				options: popup_html
			}
		],
		size: 'large',
		primary_action_label: __('Add Selected'),
		primary_action: function() {
			let toAdd = [];
			let toUpdate = [];
			
			d.$wrapper.find('.complaint-check:checked').each(function() {
				let idx = $(this).data('idx');
				let symptom = $(this).data('symptom');
				let days = d.$wrapper.find(`.complaint-days[data-idx="${idx}"]`).val() || 0;
				let option = d.$wrapper.find(`.complaint-option[data-idx="${idx}"]`).val() || '';
				let trauma = d.$wrapper.find(`.complaint-trauma[data-idx="${idx}"]`).is(':checked') ? 1 : 0;
				let treated = d.$wrapper.find(`.complaint-treated[data-idx="${idx}"]`).is(':checked') ? 1 : 0;
				let notes = d.$wrapper.find(`.complaint-notes[data-idx="${idx}"]`).val() || '';
				
				let complaintData = {
					body_part: bodyPart,
					complaint_type: symptom,
					duration_days: parseInt(days) || 0,
					option: option,
					trauma_related: trauma,
					medical_treatment_taken: treated,
					note: notes
				};
				
				// Check if this complaint already exists
				if (existingComplaints.has(symptom)) {
					toUpdate.push(complaintData);
				} else {
					toAdd.push(complaintData);
				}
			});

			if (toAdd.length === 0 && toUpdate.length === 0) {
				frappe.msgprint(__('Please select at least one complaint'));
				return;
			}

			// Update existing complaints
			toUpdate.forEach(complaint => {
				let existingRow = frm.doc.exam_complaints.find(row => 
					row.body_part === complaint.body_part && 
					row.complaint_type === complaint.complaint_type
				);
				if (existingRow) {
					existingRow.duration_days = complaint.duration_days;
					existingRow.option = complaint.option;
					existingRow.trauma_related = complaint.trauma_related;
					existingRow.medical_treatment_taken = complaint.medical_treatment_taken;
					existingRow.note = complaint.note;
				}
			});

			// Add new complaints
			toAdd.forEach(complaint => {
				let row = frm.add_child('exam_complaints');
				row.body_part = complaint.body_part;
				row.complaint_type = complaint.complaint_type;
				row.duration_days = complaint.duration_days;
				row.option = complaint.option;
				row.trauma_related = complaint.trauma_related;
				row.medical_treatment_taken = complaint.medical_treatment_taken;
				row.note = complaint.note;
			});

			// Make sure table is visible and refresh
			frm.set_df_property('exam_complaints', 'hidden', 0);
			if (frm.fields_dict.exam_complaints && frm.fields_dict.exam_complaints.$wrapper) {
				frm.fields_dict.exam_complaints.$wrapper.show();
			}
			frm.refresh_field('exam_complaints');
			
			d.hide();
			
			// Scroll to the table after dialog closes
			setTimeout(() => {
				if (frm.fields_dict.exam_complaints && frm.fields_dict.exam_complaints.$wrapper) {
					frm.fields_dict.exam_complaints.$wrapper[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
				}
			}, 300);

			let totalCount = toAdd.length + toUpdate.length;
			let message = '';
			if (toAdd.length > 0 && toUpdate.length > 0) {
				message = __('Added {0} and updated {1} complaint(s)', [toAdd.length, toUpdate.length]);
			} else if (toAdd.length > 0) {
				message = __('Added {0} complaint(s)', [toAdd.length]);
			} else if (toUpdate.length > 0) {
				message = __('Updated {0} complaint(s)', [toUpdate.length]);
			}
			
			frappe.show_alert({
				message: message,
				indicator: 'green'
			});

			// Reset body part selection - MOVED TO AFTER DIALOG HIDE
		}
	});

	// Reset body part selection when dialog is closed (any way - X button, ESC, or primary action)
	d.$wrapper.on('hidden.bs.modal', function() {
		let wrapper = frm.fields_dict.exam_step1_table_html?.$wrapper;
		if (wrapper) {
			wrapper.find('input[name="step1_bodypart"]').prop('checked', false);
		}
	});

	d.show();

	// Enable/disable fields based on checkbox
	d.$wrapper.find('.complaint-check').on('change', function() {
		let idx = $(this).data('idx');
		let isChecked = $(this).is(':checked');
		d.$wrapper.find(`.complaint-days[data-idx="${idx}"]`).prop('disabled', !isChecked);
		d.$wrapper.find(`.complaint-option[data-idx="${idx}"]`).prop('disabled', !isChecked);
		d.$wrapper.find(`.complaint-trauma[data-idx="${idx}"]`).prop('disabled', !isChecked);
		d.$wrapper.find(`.complaint-treated[data-idx="${idx}"]`).prop('disabled', !isChecked);
		d.$wrapper.find(`.complaint-notes[data-idx="${idx}"]`).prop('disabled', !isChecked);
	});
}

function setup_step1_handlers(frm, wrapper) {

	// Status change
	wrapper.find('#step1_status').on('change', function () {
		let val = $(this).val();
		frm.set_value('exam_complaints_status', val);

		if (val === 'No Complaints - Normal') {
			wrapper.find('#step1_normal_msg').show();
			wrapper.find('#step1_body_part_section').hide();
			// Hide complaints table
			if (frm.fields_dict.exam_complaints && frm.fields_dict.exam_complaints.$wrapper) {
				frm.fields_dict.exam_complaints.$wrapper.hide();
			}
		} else if (val === 'Complaints - Abnormal') {
			wrapper.find('#step1_normal_msg').hide();
			wrapper.find('#step1_body_part_section').show();
			// Show complaints table
			frm.set_df_property('exam_complaints', 'hidden', 0);
			if (frm.fields_dict.exam_complaints && frm.fields_dict.exam_complaints.$wrapper) {
				frm.fields_dict.exam_complaints.$wrapper.show();
			}
			frm.refresh_field('exam_complaints');
		} else {
			wrapper.find('#step1_normal_msg').hide();
			wrapper.find('#step1_body_part_section').hide();
			// Hide complaints table
			if (frm.fields_dict.exam_complaints && frm.fields_dict.exam_complaints.$wrapper) {
				frm.fields_dict.exam_complaints.$wrapper.hide();
			}
		}
	});

	// Body part change - open popup
	wrapper.find('input[name="step1_bodypart"]').on('change', function () {
		let bodyPart = $(this).val();
		let status = frm.doc.exam_complaints_status || '';
		
		// Only show popup if status is Abnormal
		if (status === 'Complaints - Abnormal') {
			show_complaints_popup(frm, bodyPart);
		} else if (status === 'No Complaints - Normal') {
			// For Normal status, just show a message
			frappe.show_alert({
				message: __('Patient status is Normal. Change to Abnormal to add complaints.'),
				indicator: 'blue'
			});
			// Uncheck the radio
			$(this).prop('checked', false);
		}
	});
}


// ================== STEP 2 - PHYSICAL EXAMINATION (REDESIGNED v3) ==================
// Different fields for different body parts, Edit functionality, Lesion form

const STEP2_CONFIG = {
	'Face': {
		locations: [
			'Forehead - Left', 'Forehead - Right', 'Eye - Left', 'Eye - Right',
			'Nose - Left', 'Nose - Right', 'Chin', 'Cheek - Left', 'Cheek - Right',
			'Parotid - Left', 'Parotid - Right', 'Ear - Left', 'Ear - Right'
		],
		abnormalities: ['Pain', 'Asymmetry', 'Swelling/Nodule', 'Lymph Nodes', 'Ulcer', 'Decreased Movement'],
		tableColumns: ['Location', 'Abnormalities', 'Notes']
	},
	'Neck': {
		locations: [
			'Neck - Left', 'Neck - Right', 'Neck - Central',
			'SUBMANDIBULAR - Left', 'SUBMANDIBULAR - Right',
			'THYROID - Left Lobe', 'THYROID - Right Lobe', 'THYROID - Central',
			'Parathyroid', 'Back of Neck - Left', 'Back of Neck - Right', 'Any Other'
		],
		abnormalities: ['Pain', 'Asymmetry', 'Swelling/Nodule', 'Lymph Nodes', 'Ulcer', 'Decreased Movement'],
		tableColumns: ['Location', 'Abnormalities', 'Notes']
	},
	'Mouth': {
		special: 'mouth',
		tableColumns: ['Fingers', 'Opening (mm)', 'Tongue', 'Oral Hygiene', 'Prosthesis', 'Notes']
	},
	'Teeth': {
		special: 'teeth',
		teethIssues: ['Loose', 'Painful', 'Lost', 'Caries', 'Stained', 'Calculus', 'Missing', 'Broken', 'Abrasion', 'Irregular Alignment', 'Sharp', 'Attrition', 'Root Stump', 'Tender'],
		tableColumns: ['Teeth #', 'Issues', 'Notes']
	}
};

const LESION_CONFIG = {
	locations: [
		'Lower lip (L)', 'Lower lip (R)', 'Upper lip (L)', 'Upper lip (R)',
		'Anterior Arch (L)', 'Anterior Arch (R)', 'Buccal mucosa (L)', 'Buccal mucosa (R)',
		'Ventral Tongue (L)', 'Ventral Tongue (R)', 'Ventral Tongue (Midline)',
		'Hard palate (L)', 'Hard palate (R)', 'Hard palate (Midline)',
		'Soft palate', 'Tonsil (L)', 'Tonsil (R)', 'Other'
	],
	colors: ['Uniform', 'Variegated', 'White', 'Red', 'Black', 'Brown', 'Mixed'],
	shapes: ['Round', 'Oval', 'Irregular', 'Rectangular'],
	margins: ['Well-defined', 'Poorly-defined', 'Regular', 'Irregular borders'],
	descriptions: ['Bleeding', 'Hypertrophic Mucosa', 'Papule (<5mm, raised)'],
	palpation: {
		consistency: ['Tender', 'Soft', 'Firm', 'Hard', 'Fluctuant'],
		surface: [
			'Smooth',
			'Rough-papillary (finger-like projections)',
			'Corrugated (rippled)',
			'Fissured (deep crevices)',
			'Crusted (covered with scab)'
		],
		findings: [
			'Bleeds on Touch',
			'Blanching of mucosa',
			'Scrapable white',
			'Scrapable red',
			'Non-Scrapable',
			'No Induration',
			'Mild Induration',
			'Extensive Induration'
		]
	},
	fixedLocations: [
		'Tip of Tongue',
		'Base of Tongue',
		'Philtrum',
		'Angle of Mouth',
		'Anterior Pillar',
		'Retro Molar Trigone'
	]
};

// Store findings in memory for this form session
let step2Findings = [];
let step2LesionFindings = [];
let editingFindingIndex = -1;
let editingLesionIndex = -1;

function render_step2_table_form(frm) {
	console.log('Step 2: render_step2_table_form called');

	// Use HTML field wrapper
	let wrapper = frm.fields_dict.exam_step2_table_html?.$wrapper;
	if (!wrapper) {
		console.log('Step 2: wrapper not found');
		return;
	}

	// Remove any existing container
	wrapper.empty();
	console.log('Step 2: Using HTML wrapper');

	// Get current status
	let currentStatus = frm.doc.exam_step2_status || '';
	let isNormal = currentStatus === 'Normal';
	let isAbnormal = currentStatus === 'Abnormal';

	let html = `
        <style>
            .step2-form { font-size: 13px; }
            .step2-section-title { font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 10px; }
            .step2-radio-group { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; }
            .step2-radio-label { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 6px; cursor: pointer; font-size: 13px; transition: all 0.2s; }
            .step2-radio-label:hover { background: var(--subtle-accent); border-color: var(--primary); }
            .step2-radio-label input { margin: 0; }
            .step2-normal-msg { padding: 20px; background: var(--subtle-bg); border-radius: 6px; text-align: center; margin-bottom: 15px; }
        </style>
        
        <div class="step2-form">
            <!-- Examination Status - Same style as Step 1 (label on top, dropdown below) -->
            <div class="row" style="margin-bottom: 15px;">
                <div class="col-md-4">
                    <div class="form-group">
                        <label class="control-label" style="font-size: 12px; color: var(--text-muted);">Examination Status</label>
                        <select class="form-control input-sm" id="step2_status">
                            <option value="">Select...</option>
                            <option value="Normal" ${isNormal ? 'selected' : ''}>Normal</option>
                            <option value="Abnormal" ${isAbnormal ? 'selected' : ''}>Abnormal</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <!-- Normal Message -->
            <div id="step2_normal_msg" class="step2-normal-msg" style="display: ${isNormal ? 'block' : 'none'};">
                <span style="color: var(--green-500);">✓ No abnormalities reported in physical examination.</span>
            </div>
            
            <!-- Body Part Selection - shown only when Abnormal -->
            <div id="step2_body_part_section" style="display: ${isAbnormal ? 'block' : 'none'};">
                <div class="step2-section-title">Select Body Part</div>
                <div class="step2-radio-group" id="step2_body_parts">
                    ${Object.keys(STEP2_CONFIG).map(bp => `
                        <label class="step2-radio-label">
                            <input type="radio" name="step2_bodypart" value="${bp}"> ${bp}
                        </label>
                    `).join('')}
                </div>
            </div>
        </div>
	`;

	// Set HTML to wrapper
	wrapper.html(html);
	console.log('Step 2: HTML set to wrapper');

	setup_step2_handlers_v4(frm, wrapper);
	
	// Show table if has data
	toggle_step2_findings_table(frm);
}

// Toggle Step 2 findings table visibility - Same as Step 1
function toggle_step2_findings_table(frm) {
	let status = frm.doc.exam_step2_status || '';
	let isAbnormal = status === 'Abnormal';
	
	console.log('toggle_step2_findings_table: status=', status, 'isAbnormal=', isAbnormal);
	
	if (frm.fields_dict.custom_physical_findings) {
		if (isAbnormal) {
			// Show table
			frm.set_df_property('custom_physical_findings', 'hidden', 0);
			frm.toggle_display('custom_physical_findings', true);
			if (frm.fields_dict.custom_physical_findings.$wrapper) {
				frm.fields_dict.custom_physical_findings.$wrapper.show();
				frm.fields_dict.custom_physical_findings.$wrapper.css('display', 'block');
			}
		} else {
			// Hide table
			frm.set_df_property('custom_physical_findings', 'hidden', 1);
			frm.toggle_display('custom_physical_findings', false);
			if (frm.fields_dict.custom_physical_findings.$wrapper) {
				frm.fields_dict.custom_physical_findings.$wrapper.hide();
			}
		}
		frm.refresh_field('custom_physical_findings');
	}
}

function setup_step2_handlers_v4(frm, wrapper) {
	// Status change handler
	wrapper.find('#step2_status').on('change', function () {
		let status = $(this).val();
		console.log('Step 2: Status changed to:', status);
		frm.set_value('exam_step2_status', status);
		
		if (status === 'Normal') {
			wrapper.find('#step2_normal_msg').show();
			wrapper.find('#step2_body_part_section').hide();
			frm.set_df_property('custom_physical_findings', 'hidden', 1);
			if (frm.fields_dict.custom_physical_findings && frm.fields_dict.custom_physical_findings.$wrapper) {
				frm.fields_dict.custom_physical_findings.$wrapper.hide();
			}
		} else if (status === 'Abnormal') {
			wrapper.find('#step2_normal_msg').hide();
			wrapper.find('#step2_body_part_section').show();
			// Show Physical Findings table directly when Abnormal is selected
			console.log('Step 2: Showing Physical Findings table');
			console.log('Step 2: custom_physical_findings field exists:', !!frm.fields_dict.custom_physical_findings);
			console.log('Step 2: custom_physical_findings wrapper exists:', !!(frm.fields_dict.custom_physical_findings && frm.fields_dict.custom_physical_findings.$wrapper));
			
			frm.set_df_property('custom_physical_findings', 'hidden', 0);
			frm.toggle_display('custom_physical_findings', true);
			if (frm.fields_dict.custom_physical_findings && frm.fields_dict.custom_physical_findings.$wrapper) {
				frm.fields_dict.custom_physical_findings.$wrapper.show();
				frm.fields_dict.custom_physical_findings.$wrapper.css('display', 'block');
				// Also show all parent elements
				frm.fields_dict.custom_physical_findings.$wrapper.parents().show();
				frm.fields_dict.custom_physical_findings.$wrapper.parents('.section-body').show();
				frm.fields_dict.custom_physical_findings.$wrapper.parents('.form-section').show();
				frm.fields_dict.custom_physical_findings.$wrapper.closest('.frappe-control').show();
				console.log('Step 2: Wrapper shown');
				console.log('Step 2: Wrapper HTML:', frm.fields_dict.custom_physical_findings.$wrapper.html()?.substring(0, 200));
				console.log('Step 2: Wrapper parent:', frm.fields_dict.custom_physical_findings.$wrapper.parent().attr('class'));
			} else {
				console.log('Step 2: WARNING - wrapper not found!');
			}
			frm.refresh_field('custom_physical_findings');
		} else {
			wrapper.find('#step2_normal_msg').hide();
			wrapper.find('#step2_body_part_section').hide();
		}
	});

	// Body Part Selection - Open Popup
	wrapper.find('input[name="step2_bodypart"]').on('change', function () {
		let bodyPart = $(this).val();
		if (bodyPart) {
			show_step2_popup(frm, bodyPart);
			// Uncheck after popup opens
			$(this).prop('checked', false);
		}
	});
}

// Show Step 2 Physical Examination Popup
function show_step2_popup(frm, bodyPart) {
	let config = STEP2_CONFIG[bodyPart];
	
	if (config.special === 'mouth') {
		show_mouth_popup(frm);
	} else if (config.special === 'teeth') {
		show_teeth_popup(frm);
	} else {
		show_standard_body_part_popup(frm, bodyPart, config);
	}
}

// Standard Body Part Popup (Face, Neck)
function show_standard_body_part_popup(frm, bodyPart, config) {
	// Get existing findings for this body part with full data for editing
	let existingFindings = new Map(); // Map of location -> row data
	if (frm.doc.custom_physical_findings && frm.doc.custom_physical_findings.length > 0) {
		frm.doc.custom_physical_findings.forEach(row => {
			if (row.body_part === bodyPart && row.location) {
				existingFindings.set(row.location, row);
			}
		});
	}

	let locationsHtml = config.locations.map((loc, idx) => {
		const isLocationAdded = existingFindings.has(loc);
		const existingData = isLocationAdded ? existingFindings.get(loc) : null;
		
		// Get existing abnormalities as Set
		const existingAbnormalities = new Set();
		if (existingData && existingData.abnormality) {
			existingData.abnormality.split(',').forEach(abn => {
				existingAbnormalities.add(abn.trim());
			});
		}
		
		// Get existing notes
		const notesValue = existingData ? existingData.note || '' : '';
		
		return `
		<tr class="step2-popup-row ${isLocationAdded ? 'already-added' : ''}" data-location="${loc}">
			<td style="padding: 10px; border-bottom: 1px solid var(--border-color); vertical-align: top;">
				<label style="display: flex; align-items: center; gap: 8px; cursor: pointer; margin: 0;">
					<input type="checkbox" class="step2-loc-check" data-loc="${loc}" ${isLocationAdded ? 'checked' : ''}>
					<span>${loc}${isLocationAdded ? ' <span style="color: var(--green-500); font-size: 11px;">(Already Added)</span>' : ''}</span>
				</label>
			</td>
			<td style="padding: 10px; border-bottom: 1px solid var(--border-color);">
				<div class="step2-abn-group" data-loc="${loc}" style="display: flex; flex-wrap: wrap; gap: 6px;">
					${config.abnormalities.map(abn => {
						const isAbnChecked = existingAbnormalities.has(abn);
						return `
						<label class="step2-abn-label ${isLocationAdded ? 'enabled' : ''} ${isAbnChecked ? 'selected' : ''}" data-loc="${loc}">
							<input type="checkbox" class="step2-abn-check" data-loc="${loc}" data-abn="${abn}" ${isLocationAdded ? '' : 'disabled'} ${isAbnChecked ? 'checked' : ''}>
							<span>${abn}</span>
						</label>
					`;
					}).join('')}
				</div>
			</td>
			<td style="padding: 10px; border-bottom: 1px solid var(--border-color); vertical-align: top;">
				<input type="text" class="step2-notes-input" data-loc="${loc}" placeholder="Notes..." value="${notesValue}" ${isLocationAdded ? '' : 'disabled'}>
			</td>
		</tr>
	`;
	}).join('');

	let d = new frappe.ui.Dialog({
		title: `Physical Examination - ${bodyPart}`,
		size: 'extra-large',
		fields: [{
			fieldtype: 'HTML',
			fieldname: 'popup_content',
			options: `
				<style>
					.step2-popup-table { width: 100%; border-collapse: collapse; }
					.step2-popup-table th { 
						background: var(--subtle-bg); 
						padding: 12px; 
						text-align: left; 
						font-size: 13px; 
						font-weight: 600; 
						border-bottom: 2px solid var(--border-color); 
						color: var(--heading-color); 
					}
					.step2-popup-row:hover { background: var(--subtle-bg); }
					.step2-popup-row.already-added { 
						background: var(--bg-green); 
						opacity: 0.7;
					}
					.step2-popup-row .step2-loc-check {
						width: 16px;
						height: 16px;
						cursor: pointer;
						accent-color: #2490ef;
					}
					.step2-popup-row .step2-loc-check:checked + span {
						font-weight: 600;
						color: #2490ef !important;
					}
					.step2-popup-row span {
						color: var(--text-color) !important;
					}
					.step2-abn-label {
						display: inline-flex;
						align-items: center;
						gap: 5px;
						font-size: 12px;
						cursor: pointer;
						padding: 5px 10px;
						background: var(--control-bg);
						border: 1px solid var(--border-color);
						border-radius: 4px;
						opacity: 0.4;
						transition: all 0.2s;
					}
					.step2-abn-label span {
						color: var(--text-color) !important;
					}
					.step2-abn-label.enabled {
						opacity: 1;
						cursor: pointer;
					}
					.step2-abn-label.enabled:hover {
						background: rgba(36, 144, 239, 0.1);
						border-color: #2490ef;
					}
					.step2-abn-label.selected {
						background: rgba(36, 144, 239, 0.15) !important;
						border-color: #2490ef !important;
					}
					.step2-abn-label.selected span {
						color: #2490ef !important;
						font-weight: 600;
					}
					.step2-abn-check {
						width: 14px;
						height: 14px;
						accent-color: #2490ef;
					}
					.step2-notes-input {
						width: 100%;
						padding: 6px 10px;
						border: 1px solid var(--border-color);
						border-radius: 4px;
						font-size: 12px;
						background: var(--control-bg);
					}
					.step2-notes-input:disabled {
						opacity: 0.5;
					}
				</style>
				<div style="max-height: 450px; overflow-y: auto;">
					<table class="step2-popup-table">
						<thead>
							<tr>
								<th style="width: 20%;">Location</th>
								<th style="width: 55%;">Abnormalities (Multiple Select)</th>
								<th style="width: 25%;">Notes</th>
							</tr>
						</thead>
						<tbody>
							${locationsHtml}
						</tbody>
					</table>
				</div>
			`
		}],
		primary_action_label: __('Add Selected'),
		primary_action: function() {
			let toAdd = [];
			let toUpdate = [];
			
			d.$wrapper.find('.step2-loc-check:checked').each(function() {
				let loc = $(this).data('loc');
				let abnormalities = [];
				d.$wrapper.find(`.step2-abn-check[data-loc="${loc}"]:checked`).each(function() {
					abnormalities.push($(this).data('abn'));
				});
				let notes = d.$wrapper.find(`.step2-notes-input[data-loc="${loc}"]`).val() || '';
				
				if (abnormalities.length > 0) {
					let findingData = {
						body_part: bodyPart,
						location: loc,
						abnormality: abnormalities.join(', '),
						note: notes
					};
					
					// Check if this location already exists
					if (existingFindings.has(loc)) {
						toUpdate.push(findingData);
					} else {
						toAdd.push(findingData);
					}
				}
			});
			
			if (toAdd.length === 0 && toUpdate.length === 0) {
				frappe.msgprint(__('Please select at least one location with abnormalities'));
				return;
			}
			
			// Update existing findings
			toUpdate.forEach(finding => {
				let existingRow = frm.doc.custom_physical_findings.find(row => 
					row.body_part === finding.body_part && 
					row.location === finding.location
				);
				if (existingRow) {
					existingRow.abnormality = finding.abnormality;
					existingRow.note = finding.note;
				}
			});
			
			// Add new findings
			toAdd.forEach(f => {
				let row = frm.add_child('custom_physical_findings');
				row.body_part = f.body_part;
				row.location = f.location;
				row.abnormality = f.abnormality;
				row.note = f.note;
			});

			// Make sure table is visible and refresh - SAME AS STEP 1
			frm.set_df_property('custom_physical_findings', 'hidden', 0);
			frm.toggle_display('custom_physical_findings', true);
			if (frm.fields_dict.custom_physical_findings && frm.fields_dict.custom_physical_findings.$wrapper) {
				frm.fields_dict.custom_physical_findings.$wrapper.show();
				frm.fields_dict.custom_physical_findings.$wrapper.css('display', 'block');
			}
			frm.refresh_field('custom_physical_findings');
			
			d.hide();
			
			// Scroll to the table after dialog closes
			setTimeout(() => {
				if (frm.fields_dict.custom_physical_findings && frm.fields_dict.custom_physical_findings.$wrapper) {
					frm.fields_dict.custom_physical_findings.$wrapper[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
				}
			}, 300);

			let totalCount = toAdd.length + toUpdate.length;
			let message = '';
			if (toAdd.length > 0 && toUpdate.length > 0) {
				message = __('Added {0} and updated {1} finding(s) for {2}', [toAdd.length, toUpdate.length, bodyPart]);
			} else if (toAdd.length > 0) {
				message = __('Added {0} finding(s) for {1}', [toAdd.length, bodyPart]);
			} else if (toUpdate.length > 0) {
				message = __('Updated {0} finding(s) for {1}', [toUpdate.length, bodyPart]);
			}
			
			frappe.show_alert({
				message: message,
				indicator: 'green'
			});

			// Reset body part selection
			let wrapper = frm.fields_dict.exam_step2_table_html?.$wrapper;
			if (wrapper) {
				wrapper.find('input[name="step2_bodypart"]').prop('checked', false);
			}
		}
	});

	d.show();

	// Enable/disable abnormalities and notes based on location checkbox
	d.$wrapper.find('.step2-loc-check').on('change', function() {
		let loc = $(this).data('loc');
		let isChecked = $(this).is(':checked');
		
		d.$wrapper.find(`.step2-abn-check[data-loc="${loc}"]`).prop('disabled', !isChecked);
		d.$wrapper.find(`.step2-notes-input[data-loc="${loc}"]`).prop('disabled', !isChecked);
		
		// Update styling for enabled/disabled
		d.$wrapper.find(`.step2-abn-group[data-loc="${loc}"] .step2-abn-label`).each(function() {
			if (isChecked) {
				$(this).addClass('enabled').css('opacity', '1');
			} else {
				$(this).removeClass('enabled selected').css('opacity', '0.5');
				$(this).find('.step2-abn-check').prop('checked', false);
			}
		});
	});
	
	// Add selected class when abnormality checkbox is checked
	d.$wrapper.find('.step2-abn-check').on('change', function() {
		let $label = $(this).closest('.step2-abn-label');
		if ($(this).is(':checked')) {
			$label.addClass('selected');
		} else {
			$label.removeClass('selected');
		}
	});
}

// Mouth Special Popup - Fresh form every time (no auto-fill)
function show_mouth_popup(frm) {
	// Check if Mouth entry already exists
	let existingMouthRow = null;
	if (frm.doc.custom_physical_findings && frm.doc.custom_physical_findings.length > 0) {
		existingMouthRow = frm.doc.custom_physical_findings.find(row => 
			row.body_part === 'Mouth' && row.location === 'Mouth Opening'
		);
	}
	
	// Pre-fill values if editing existing row OR from linked Vital Signs
	let prefilledValues = {};
	if (existingMouthRow) {
		// Parse the abnormality string to extract values
		let abn = existingMouthRow.abnormality || '';
		
		// Extract Fingers
		let fingersMatch = abn.match(/Fingers:\s*(\w+)/);
		if (fingersMatch) prefilledValues.fingers = fingersMatch[1];
		
		// Extract Opening mm
		let openingMatch = abn.match(/Opening:\s*(\d+)mm/);
		if (openingMatch) prefilledValues.opening_mm = parseInt(openingMatch[1]);
		
		// Extract Measured With
		let measuredMatch = abn.match(/Measured:\s*(\w+)/);
		if (measuredMatch) prefilledValues.measured_with = measuredMatch[1];
		
		// Extract Tongue status
		let tongueMatch = abn.match(/Tongue:\s*([^|]+)/);
		if (tongueMatch) {
			let tongueStr = tongueMatch[1].trim();
			if (tongueStr === 'Normal') {
				prefilledValues.tongue_status = 'normal';
			} else {
				prefilledValues.tongue_status = 'abnormal';
				prefilledValues.tongue_conditions = tongueStr.split(',').map(s => s.trim());
			}
		}
		
		// Extract Protrusion
		let protrusionMatch = abn.match(/Protrusion:\s*(\d+)mm/);
		if (protrusionMatch) prefilledValues.tongue_protrusion = parseInt(protrusionMatch[1]);
		
		// Extract Hygiene
		let hygieneMatch = abn.match(/Hygiene:\s*(\w+)/);
		if (hygieneMatch) prefilledValues.oral_hygiene = hygieneMatch[1];
		
		// Extract Prosthesis
		let prosthesisMatch = abn.match(/Prosthesis:\s*(\w+)/);
		if (prosthesisMatch) prefilledValues.prosthesis = prosthesisMatch[1];
		
		// Extract Notes
		prefilledValues.notes = existingMouthRow.note || '';
	} else if (frm._vital_signs_mouth_data) {
		// If no existing mouth row but Vital Signs data is available, use it
		if (frm._vital_signs_mouth_data.fingers) {
			prefilledValues.fingers = frm._vital_signs_mouth_data.fingers;
		}
		if (frm._vital_signs_mouth_data.opening_mm) {
			prefilledValues.opening_mm = parseInt(frm._vital_signs_mouth_data.opening_mm);
		}
		if (frm._vital_signs_mouth_data.measured_with) {
			prefilledValues.measured_with = frm._vital_signs_mouth_data.measured_with;
		}
	}
	
	let d = new frappe.ui.Dialog({
		title: existingMouthRow ? 'Edit Mouth Examination' : 'Physical Examination - Mouth',
		size: 'large',
		fields: [
			{ fieldtype: 'Section Break', label: 'Mouth Opening' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Select', fieldname: 'fingers', label: 'Mouth Opening (Fingers)', options: '\nOne\nTwo\nThree\nFour' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Int', fieldname: 'opening_mm', label: 'Mouth Opening (mm)' },
			{ fieldtype: 'Column Break' },
			{ fieldtype: 'Select', fieldname: 'measured_with', label: 'Measured With', options: '\nTrisCare\nCaliper\nOther' },
			{ fieldtype: 'Section Break', label: 'Tongue Movement' },
			{ fieldtype: 'HTML', fieldname: 'tongue_html', options: `
				<div style="padding: 10px 0;">
					<div style="display: flex; gap: 20px; margin-bottom: 15px;">
						<label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 8px 16px; background: var(--control-bg); border: 2px solid var(--border-color); border-radius: 6px; font-weight: 500;">
							<input type="radio" name="tongue_status" id="tongue_normal" value="normal" style="width: 18px; height: 18px; cursor: pointer;"> Normal
						</label>
						<label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 8px 16px; background: var(--control-bg); border: 2px solid var(--border-color); border-radius: 6px; font-weight: 500;">
							<input type="radio" name="tongue_status" id="tongue_abnormal" value="abnormal" style="width: 18px; height: 18px; cursor: pointer;"> Abnormal
						</label>
					</div>
					<div id="tongue_conditions_wrapper" style="display: none; padding: 15px; background: var(--subtle-bg); border-radius: 6px; border: 1px solid var(--border-color);">
						<label style="font-weight: 500; display: block; margin-bottom: 10px; color: var(--heading-color);">Select Conditions:</label>
						<div style="display: flex; flex-wrap: wrap; gap: 10px;">
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 6px 12px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 4px;">
								<input type="checkbox" id="tongue_painful" style="width: 16px; height: 16px;"> Painful
							</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 6px 12px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 4px;">
								<input type="checkbox" id="tongue_dev_left" style="width: 16px; height: 16px;"> Deviation Left
							</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 6px 12px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 4px;">
								<input type="checkbox" id="tongue_dev_right" style="width: 16px; height: 16px;"> Deviation Right
							</label>
							<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 6px 12px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 4px;">
								<input type="checkbox" id="tongue_restricted" style="width: 16px; height: 16px;"> Restricted
							</label>
						</div>
					</div>
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Tongue Protrusion' },
			{ fieldtype: 'Int', fieldname: 'tongue_protrusion', label: 'Tongue Protrusion (mm)' },
			{ fieldtype: 'Section Break', label: 'Oral Hygiene' },
			{ fieldtype: 'Select', fieldname: 'oral_hygiene', label: 'Oral Hygiene', options: '\nGood\nModerate\nPoor' },
			{ fieldtype: 'Section Break', label: 'Prosthesis' },
			{ fieldtype: 'Select', fieldname: 'prosthesis', label: 'Prosthesis', options: '\nYes\nNo' },
			{ fieldtype: 'Section Break', label: 'Notes' },
			{ fieldtype: 'Small Text', fieldname: 'notes', label: 'Notes' }
		],
		primary_action_label: __('Add Selected'),
		primary_action: function() {
			let values = d.get_values();
			
			// Get tongue values
			let tongue = [];
			let tongueStatus = d.$wrapper.find('input[name="tongue_status"]:checked').val();
			
			if (tongueStatus === 'normal') {
				tongue.push('Normal');
			} else if (tongueStatus === 'abnormal') {
				// Get selected conditions only if Abnormal is selected
				if (d.$wrapper.find('#tongue_painful').is(':checked')) tongue.push('Painful');
				if (d.$wrapper.find('#tongue_dev_left').is(':checked')) tongue.push('Deviation Left');
				if (d.$wrapper.find('#tongue_dev_right').is(':checked')) tongue.push('Deviation Right');
				if (d.$wrapper.find('#tongue_restricted').is(':checked')) tongue.push('Restricted');
			}
			
			// Build abnormality string
			let abnParts = [];
			if (values.fingers) abnParts.push('Fingers: ' + values.fingers);
			if (values.opening_mm) abnParts.push('Opening: ' + values.opening_mm + 'mm');
			if (values.measured_with) abnParts.push('Measured: ' + values.measured_with);
			if (tongue.length > 0) abnParts.push('Tongue: ' + tongue.join(', '));
			if (values.tongue_protrusion) abnParts.push('Protrusion: ' + values.tongue_protrusion + 'mm');
			if (values.oral_hygiene) abnParts.push('Hygiene: ' + values.oral_hygiene);
			if (values.prosthesis) abnParts.push('Prosthesis: ' + values.prosthesis);
			
			if (abnParts.length === 0) {
				frappe.msgprint(__('Please fill at least one field'));
				return;
			}
			
			// Update existing row or add new
			let row;
			if (existingMouthRow) {
				// Update existing row
				row = existingMouthRow;
			} else {
				// Add new row
				row = frm.add_child('custom_physical_findings');
				row.body_part = 'Mouth';
				row.location = 'Mouth Opening';
			}
			row.abnormality = abnParts.join(' | ');
			row.note = values.notes || '';
			
			// Show and refresh table
			frm.set_df_property('custom_physical_findings', 'hidden', 0);
			if (frm.fields_dict.custom_physical_findings && frm.fields_dict.custom_physical_findings.$wrapper) {
				frm.fields_dict.custom_physical_findings.$wrapper.show();
			}
			frm.refresh_field('custom_physical_findings');
			
			d.hide();
			
			// Scroll to table
			setTimeout(() => {
				if (frm.fields_dict.custom_physical_findings && frm.fields_dict.custom_physical_findings.$wrapper) {
					frm.fields_dict.custom_physical_findings.$wrapper[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
				}
			}, 300);
			
			frappe.show_alert({
				message: __('Mouth examination added'),
				indicator: 'green'
			});
			
			// Reset body part selection
			let wrapper = frm.fields_dict.exam_step2_table_html?.$wrapper;
			if (wrapper) {
				wrapper.find('input[name="step2_bodypart"]').prop('checked', false);
			}
		}
	});

	d.show();
	
	// Set prefilled values if editing existing row
	if (existingMouthRow) {
		d.set_values({
			fingers: prefilledValues.fingers || '',
			opening_mm: prefilledValues.opening_mm || '',
			measured_with: prefilledValues.measured_with || '',
			tongue_protrusion: prefilledValues.tongue_protrusion || '',
			oral_hygiene: prefilledValues.oral_hygiene || '',
			prosthesis: prefilledValues.prosthesis || '',
			notes: prefilledValues.notes || ''
		});
		
		// Set tongue radio button
		if (prefilledValues.tongue_status === 'normal') {
			d.$wrapper.find('#tongue_normal').prop('checked', true);
		} else if (prefilledValues.tongue_status === 'abnormal') {
			d.$wrapper.find('#tongue_abnormal').prop('checked', true);
			d.$wrapper.find('#tongue_conditions_wrapper').show();
			
			// Check condition checkboxes
			if (prefilledValues.tongue_conditions) {
				prefilledValues.tongue_conditions.forEach(cond => {
					if (cond === 'Painful') d.$wrapper.find('#tongue_painful').prop('checked', true);
					if (cond === 'Deviation Left') d.$wrapper.find('#tongue_dev_left').prop('checked', true);
					if (cond === 'Deviation Right') d.$wrapper.find('#tongue_dev_right').prop('checked', true);
					if (cond === 'Restricted') d.$wrapper.find('#tongue_restricted').prop('checked', true);
				});
			}
		}
	}
	
	// If we have pre-filled values from Vital Signs, set them now
	if (!existingMouthRow && (prefilledValues.fingers || prefilledValues.opening_mm || prefilledValues.measured_with)) {
		d.set_values({
			fingers: prefilledValues.fingers || '',
			opening_mm: prefilledValues.opening_mm || '',
			measured_with: prefilledValues.measured_with || ''
		});
	}
	
	// Add event listeners for tongue movement radio buttons
	d.$wrapper.find('input[name="tongue_status"]').on('change', function() {
		let selectedValue = $(this).val();
		if (selectedValue === 'normal') {
			// Hide conditions wrapper
			d.$wrapper.find('#tongue_conditions_wrapper').slideUp(200);
			// Uncheck all condition checkboxes
			d.$wrapper.find('#tongue_painful, #tongue_dev_left, #tongue_dev_right, #tongue_restricted').prop('checked', false);
		} else if (selectedValue === 'abnormal') {
			// Show conditions wrapper
			d.$wrapper.find('#tongue_conditions_wrapper').slideDown(200);
		}
	});
}

// Teeth Special Popup (renamed from Dental) with duplicate validation
function show_teeth_popup(frm) {
	let teethIssues = STEP2_CONFIG['Teeth'].teethIssues;
	
	// Get existing teeth numbers from table
	let existingTeeth = [];
	if (frm.doc.custom_physical_findings && frm.doc.custom_physical_findings.length > 0) {
		frm.doc.custom_physical_findings.forEach(f => {
			if (f.location && f.location.startsWith('Teeth')) {
				// Extract teeth numbers from location like "Teeth - Teeth #11,12,13"
				let match = f.location.match(/Teeth #([\d,\s]+)/);
				if (match) {
					let nums = match[1].split(',').map(n => n.trim());
					existingTeeth = existingTeeth.concat(nums);
				}
			}
		});
	}
	
	let d = new frappe.ui.Dialog({
		title: 'Physical Examination - Teeth',
		size: 'large',
		fields: [
			{ fieldtype: 'Section Break', label: 'Teeth Information' },
			{ fieldtype: 'HTML', fieldname: 'teeth_input_html', options: `
				<div style="margin-bottom: 15px;">
					<label style="font-weight: 500; margin-bottom: 5px; display: block;">Teeth Numbers <span style="color: red;">*</span></label>
					<input type="text" id="teeth_numbers_input" style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 14px;" placeholder="e.g., 11, 12, 21, 22">
					<small style="color: var(--text-muted);">Enter valid teeth numbers (11-18, 21-28, 31-38, 41-48) separated by commas</small>
					<div id="teeth_validation_error" style="display: none; margin-top: 8px; padding: 10px; background: #f8d7da; border: 1px solid #dc3545; border-radius: 4px; color: #721c24;">
						<i class="fa fa-times-circle"></i> <span id="validation_error_text"></span>
					</div>
					<div id="teeth_duplicate_warning" style="display: none; margin-top: 8px; padding: 10px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; color: #856404;">
						<i class="fa fa-exclamation-triangle"></i> <span id="duplicate_teeth_text"></span>
					</div>
					<div id="teeth_help" style="margin-top: 10px; padding: 10px; background: var(--subtle-bg); border-radius: 4px; font-size: 12px;">
						<strong>Valid Teeth Numbers:</strong><br>
						<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 5px;">
							<div><strong>Quadrant 1 (Upper Right):</strong> 11-18</div>
							<div><strong>Quadrant 2 (Upper Left):</strong> 21-28</div>
							<div><strong>Quadrant 3 (Lower Left):</strong> 31-38</div>
							<div><strong>Quadrant 4 (Lower Right):</strong> 41-48</div>
						</div>
					</div>
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Teeth Issues (Multiple Select)' },
			{ fieldtype: 'HTML', fieldname: 'issues_html', options: `
				<div style="display: flex; flex-wrap: wrap; gap: 12px; padding: 10px 0;">
					${teethIssues.map(issue => `
						<label style="display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 6px 12px; background: var(--control-bg); border: 1px solid var(--border-color); border-radius: 4px;">
							<input type="checkbox" class="teeth-issue-check" value="${issue}" style="width: 16px; height: 16px;"> ${issue}
						</label>
					`).join('')}
				</div>
			` },
			{ fieldtype: 'Section Break', label: 'Notes' },
			{ fieldtype: 'Small Text', fieldname: 'notes', label: 'Notes' }
		],
		primary_action_label: __('Add Selected'),
		primary_action: function() {
			let values = d.get_values();
			let teethNumbers = d.$wrapper.find('#teeth_numbers_input').val() || '';
			
			// Get selected issues
			let issues = [];
			d.$wrapper.find('.teeth-issue-check:checked').each(function() {
				issues.push($(this).val());
			});
			
			// Teeth numbers are now mandatory
			if (!teethNumbers || !teethNumbers.trim()) {
				frappe.msgprint(__('Please enter teeth numbers'));
				return;
			}
			
			// Validate teeth numbers
			let newTeeth = teethNumbers.split(',').map(n => n.trim()).filter(n => n);
			let invalidTeeth = [];
			let validTeethNumbers = [];
			
			// Valid teeth ranges: 11-18, 21-28, 31-38, 41-48
			newTeeth.forEach(tooth => {
				let num = parseInt(tooth);
				if (isNaN(num)) {
					invalidTeeth.push(tooth);
				} else {
					let quadrant = Math.floor(num / 10);
					let position = num % 10;
					
					// Check if quadrant is 1-4 and position is 1-8
					if (quadrant >= 1 && quadrant <= 4 && position >= 1 && position <= 8) {
						validTeethNumbers.push(tooth);
					} else {
						invalidTeeth.push(tooth);
					}
				}
			});
			
			// Show error if invalid teeth found
			if (invalidTeeth.length > 0) {
				frappe.msgprint({
					title: __('Invalid Teeth Numbers'),
					message: __('Invalid teeth numbers: {0}<br><br>Valid teeth numbers are:<br>• Quadrant 1 (Upper Right): 11-18<br>• Quadrant 2 (Upper Left): 21-28<br>• Quadrant 3 (Lower Left): 31-38<br>• Quadrant 4 (Lower Right): 41-48', [invalidTeeth.join(', ')]),
					indicator: 'red'
				});
				return;
			}
			
			// Check for duplicate entries in the same input
			let duplicatesInInput = [];
			let uniqueTeeth = new Set();
			validTeethNumbers.forEach(tooth => {
				if (uniqueTeeth.has(tooth)) {
					if (!duplicatesInInput.includes(tooth)) {
						duplicatesInInput.push(tooth);
					}
				} else {
					uniqueTeeth.add(tooth);
				}
			});
			
			if (duplicatesInInput.length > 0) {
				frappe.msgprint({
					title: __('Duplicate Teeth Numbers'),
					message: __('You have entered the same teeth number(s) multiple times: {0}<br><br>Please enter each tooth number only once.', [duplicatesInInput.join(', ')]),
					indicator: 'red'
				});
				return;
			}
			
			// Remove duplicates and use unique teeth only
			validTeethNumbers = Array.from(uniqueTeeth);
			
			// Check for duplicates with existing table entries
			let duplicatesWithTable = validTeethNumbers.filter(t => existingTeeth.includes(t));
			if (duplicatesWithTable.length > 0) {
				frappe.msgprint(__('Teeth {0} already exist in the table. Please edit existing entry or use different teeth numbers.', [duplicatesWithTable.join(', ')]));
				return;
			}
			
			// Add to child table
			let row = frm.add_child('custom_physical_findings');
			row.body_part = 'Teeth';
			row.location = 'Teeth #' + validTeethNumbers.join(', ');
			row.abnormality = issues.join(', ');
			row.note = values.notes || '';
			
			// Show and refresh table
			frm.set_df_property('custom_physical_findings', 'hidden', 0);
			if (frm.fields_dict.custom_physical_findings && frm.fields_dict.custom_physical_findings.$wrapper) {
				frm.fields_dict.custom_physical_findings.$wrapper.show();
			}
			frm.refresh_field('custom_physical_findings');
			
			d.hide();
			
			// Scroll to table
			setTimeout(() => {
				if (frm.fields_dict.custom_physical_findings && frm.fields_dict.custom_physical_findings.$wrapper) {
					frm.fields_dict.custom_physical_findings.$wrapper[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
				}
			}, 300);
			
			frappe.show_alert({
				message: __('Teeth examination added'),
				indicator: 'green'
			});
			
			// Reset body part selection
			let wrapper = frm.fields_dict.exam_step2_table_html?.$wrapper;
			if (wrapper) {
				wrapper.find('input[name="step2_bodypart"]').prop('checked', false);
			}
		}
	});

	d.show();
	
	// Add real-time validation on input
	d.$wrapper.find('#teeth_numbers_input').on('input', function() {
		let inputVal = $(this).val();
		let $validationError = d.$wrapper.find('#teeth_validation_error');
		let $duplicateWarning = d.$wrapper.find('#teeth_duplicate_warning');
		
		// Hide both messages initially
		$validationError.hide();
		$duplicateWarning.hide();
		$(this).css('border-color', 'var(--border-color)');
		
		if (inputVal) {
			let newTeeth = inputVal.split(',').map(n => n.trim()).filter(n => n);
			let invalidTeeth = [];
			let validTeeth = [];
			
			// Validate each tooth number
			newTeeth.forEach(tooth => {
				let num = parseInt(tooth);
				if (isNaN(num)) {
					invalidTeeth.push(tooth);
				} else {
					let quadrant = Math.floor(num / 10);
					let position = num % 10;
					
					if (quadrant >= 1 && quadrant <= 4 && position >= 1 && position <= 8) {
						validTeeth.push(tooth);
					} else {
						invalidTeeth.push(tooth);
					}
				}
			});
			
			// Check for duplicate entries in the same input
			let duplicatesInInput = [];
			let uniqueTeeth = new Set();
			validTeeth.forEach(tooth => {
				if (uniqueTeeth.has(tooth)) {
					if (!duplicatesInInput.includes(tooth)) {
						duplicatesInInput.push(tooth);
					}
				} else {
					uniqueTeeth.add(tooth);
				}
			});
			
			// Show validation error if invalid teeth found
			if (invalidTeeth.length > 0) {
				$(this).css('border-color', '#dc3545');
				$validationError.find('#validation_error_text').text('Invalid teeth numbers: ' + invalidTeeth.join(', '));
				$validationError.show();
			}
			
			// Show validation error if duplicate entries in same input
			if (duplicatesInInput.length > 0) {
				$(this).css('border-color', '#dc3545');
				$validationError.find('#validation_error_text').text('Duplicate teeth numbers in input: ' + duplicatesInInput.join(', ') + ' (entered multiple times)');
				$validationError.show();
			}
			
			// Check for duplicates with existing table entries (only if no duplicates in input)
			if (duplicatesInInput.length === 0) {
				let duplicatesWithTable = Array.from(uniqueTeeth).filter(t => existingTeeth.includes(t));
				if (duplicatesWithTable.length > 0) {
					$(this).css('border-color', '#ffc107');
					$duplicateWarning.find('#duplicate_teeth_text').text('Teeth ' + duplicatesWithTable.join(', ') + ' already exist in table. Please edit existing entry.');
					$duplicateWarning.show();
				}
			}
		}
	});
}

// Setup allergen category filter
function setup_allergen_category_filter(frm) {
	try {
		if (frm.fields_dict && frm.fields_dict.custom_allergy) {
			frm.set_query('allergen', 'custom_allergy', function(doc, cdt, cdn) {
				let row = locals[cdt][cdn];
				if (row && row.allergen_category) {
					return {
						filters: {
							'allergen_category': row.allergen_category
						}
					};
				}
				return {};
			});
		}
	} catch (e) {
		console.log("Allergen category filter setup skipped:", e.message);
	}
}

// Allergen Category and Allergen Autocomplete Handlers
frappe.ui.form.on("Patient Encounter Allergy", {
	allergen_category: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Only process if allergen exists and was set BEFORE category
		// This prevents clearing allergen when category is auto-filled
		if (row.allergen && row.allergen_category) {
			frappe.db.get_value('Allergen', row.allergen, 'allergen_category', function(r) {
				// Only clear if allergen's category doesn't match selected category
				if (r && r.allergen_category && r.allergen_category !== row.allergen_category) {
					// Allergen doesn't belong to selected category, clear it
					frappe.model.set_value(cdt, cdn, 'allergen', '');
				}
				// If categories match, do nothing - keep the allergen
			});
		}
	},
	
	allergen: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Auto-fill category when allergen is selected (only if category is empty)
		if (row.allergen && !row.allergen_category) {
			frappe.db.get_value('Allergen', row.allergen, 'allergen_category', function(r) {
				if (r && r.allergen_category) {
					frappe.model.set_value(cdt, cdn, 'allergen_category', r.allergen_category);
				}
			});
		}
	}
});

// Patient Encounter Alcohol History - Computation Logic
frappe.ui.form.on('Patient Encounter Alcohol History', {
	quantity: function(frm, cdt, cdn) {
		compute_alcohol_years_encounter(frm, cdt, cdn);
	},
	years_of_use: function(frm, cdt, cdn) {
		compute_alcohol_years_encounter(frm, cdt, cdn);
	},
	frequency: function(frm, cdt, cdn) {
		compute_alcohol_years_encounter(frm, cdt, cdn);
	}
});

function compute_alcohol_years_encounter(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	
	if (row.quantity && row.years_of_use) {
		// Convert quantity to daily based on frequency
		let daily_quantity = get_daily_quantity_encounter(row.quantity, row.frequency);
		
		// Alcohol Years = Daily Quantity × Years of Use
		const alcohol_years = daily_quantity * row.years_of_use;
		frappe.model.set_value(cdt, cdn, 'alcohol_years', alcohol_years.toFixed(2));
	} else {
		frappe.model.set_value(cdt, cdn, 'alcohol_years', 0);
	}
}

// Smoking Tobacco History - Age Computation and Pack Years (Encounter)
frappe.ui.form.on('Patient Encounter Smoking Tobacco History', {
	started_at_age: function(frm, cdt, cdn) {
		compute_used_years_smoking_encounter(frm, cdt, cdn);
	},
	discontinued_at_age: function(frm, cdt, cdn) {
		compute_used_years_smoking_encounter(frm, cdt, cdn);
	},
	quantity: function(frm, cdt, cdn) {
		compute_pack_years_encounter(frm, cdt, cdn);
	},
	frequency: function(frm, cdt, cdn) {
		compute_pack_years_encounter(frm, cdt, cdn);
	},
	type: function(frm, cdt, cdn) {
		compute_pack_years_encounter(frm, cdt, cdn);
	}
});

// Smokeless Tobacco History - Age Computation (Encounter)
frappe.ui.form.on('Patient Encounter Smokeless Tobacco History', {
	started_at_age: function(frm, cdt, cdn) {
		compute_used_years_encounter(frm, cdt, cdn);
	},
	discontinued_at_age: function(frm, cdt, cdn) {
		compute_used_years_encounter(frm, cdt, cdn);
	}
});

// Substance Abuse History - Age Computation (Encounter)
frappe.ui.form.on('Patient Encounter Substance Abuse History', {
	started_at_age: function(frm, cdt, cdn) {
		compute_used_years_encounter(frm, cdt, cdn);
	},
	discontinued_at_age: function(frm, cdt, cdn) {
		compute_used_years_encounter(frm, cdt, cdn);
	}
});

// Helper function to convert quantity to daily based on frequency (Encounter)
function get_daily_quantity_encounter(quantity, frequency) {
	if (!quantity) return 0;
	
	switch(frequency) {
		case 'Daily':
			return quantity;
		case 'Weekly':
			return quantity / 7;
		case 'Monthly':
			return quantity / 30;
		case 'Yearly':
			return quantity / 365;
		default:
			return quantity; // Default to daily if not specified
	}
}

function compute_used_years_encounter(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	
	if (row.started_at_age) {
		let years_used = 0;
		
		if (row.discontinued_at_age) {
			// Discontinued - calculate difference + 1
			years_used = row.discontinued_at_age - row.started_at_age + 1;
		} else {
			// Ongoing - get patient DOB from encounter
			if (frm.doc.patient) {
				frappe.db.get_value('Patient', frm.doc.patient, 'dob', function(r) {
					if (r && r.dob) {
						const current_age = Math.floor(frappe.datetime.get_diff(frappe.datetime.nowdate(), r.dob) / 365.25);
						years_used = current_age - row.started_at_age + 1;
						
						if (years_used > 0) {
							frappe.model.set_value(cdt, cdn, 'used_for_years', years_used);
						} else {
							frappe.model.set_value(cdt, cdn, 'used_for_years', 0);
						}
					}
				});
				return; // Exit early, callback will handle the rest
			}
		}
		
		if (years_used > 0) {
			frappe.model.set_value(cdt, cdn, 'used_for_years', years_used);
		} else {
			frappe.model.set_value(cdt, cdn, 'used_for_years', 0);
		}
	} else {
		frappe.model.set_value(cdt, cdn, 'used_for_years', 0);
	}
}

// Smoking-specific computation (includes pack years) - Encounter
function compute_used_years_smoking_encounter(frm, cdt, cdn) {
	compute_used_years_encounter(frm, cdt, cdn);
	compute_pack_years_encounter(frm, cdt, cdn);
}

// Pack Years computation for Smoking Tobacco (Encounter)
function compute_pack_years_encounter(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	
	// Reset both fields first
	frappe.model.set_value(cdt, cdn, 'pack_years', 0);
	frappe.model.set_value(cdt, cdn, 'bidi_pack_years', 0);
	
	if (!row.quantity || !row.used_for_years || row.used_for_years <= 0) {
		return;
	}
	
	// Convert quantity to daily
	let daily_quantity = get_daily_quantity_encounter(row.quantity, row.frequency);
	
	// Check type and compute accordingly
	if (row.type && row.type.toLowerCase().includes('cigarette')) {
		// Pack Years = (Cigarettes per day / 20) × Years Smoked
		const pack_years = (daily_quantity / 20) * row.used_for_years;
		frappe.model.set_value(cdt, cdn, 'pack_years', pack_years.toFixed(2));
	} else if (row.type && row.type.toLowerCase().includes('bidi')) {
		// Bidi Pack Years = (Bidis per day / 4) / 20 × Years Smoked
		const bidi_pack_years = ((daily_quantity / 4) / 20) * row.used_for_years;
		frappe.model.set_value(cdt, cdn, 'bidi_pack_years', bidi_pack_years.toFixed(2));
	}
}

// Step 2 Physical Findings - Data fields, popup handles the selection


// Load mouth examination data from Vital Signs into Patient Encounter Step 2
// This function is called when vital_signs field changes
// It does NOT automatically add rows to the table
// It only stores the data for popup pre-fill
function load_vital_signs_mouth_data(frm) {
	if (!frm.doc.vital_signs) {
		return;
	}

	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Vital Signs",
			name: frm.doc.vital_signs
		},
		callback: function (r) {
			if (r.message) {
				const vital_signs = r.message;
				
				// Store vital signs mouth data in frm for popup to use
				if (vital_signs.mouth_opening_fingers || vital_signs.mouth_opening_mm || vital_signs.measured_with) {
					frm._vital_signs_mouth_data = {
						fingers: vital_signs.mouth_opening_fingers,
						opening_mm: vital_signs.mouth_opening_mm,
						measured_with: vital_signs.measured_with
					};
				}
			}
		}
	});
}
