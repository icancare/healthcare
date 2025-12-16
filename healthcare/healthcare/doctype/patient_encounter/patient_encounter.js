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
		
		// Check and render Clinical Examination if practitioner has template
		if (frm.doc.practitioner && frm.doc.show_clinical_examination) {
			setTimeout(() => {
				render_clinical_exam_diagram(frm);
				render_clinical_images_section(frm);
				render_step4_pictures(frm);
			}, 300);
		} else if (frm.doc.practitioner && !frm.doc.show_clinical_examination) {
			// Check if practitioner has template (for existing encounters)
			check_practitioner_examination_template(frm);
		}
	},
	
	// Trigger render when show_clinical_examination changes
	show_clinical_examination: function(frm) {
		if (frm.doc.show_clinical_examination && frm.doc.practitioner) {
			setTimeout(() => {
				render_clinical_exam_diagram(frm);
				render_clinical_images_section(frm);
				render_step4_pictures(frm);
			}, 300);
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
			
			// Check if practitioner has Clinical Examination Template assigned
			check_practitioner_examination_template(frm);
		} else {
			// Hide clinical examination if no practitioner
			frm.set_value("show_clinical_examination", 0);
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
			callback: function(r) {
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
		primary_action: function() {
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

// Clinical Examination Integration
function setup_clinical_examination_button(frm) {
	// Get templates assigned to this practitioner
	frappe.call({
		method: "healthcare.healthcare.doctype.clinical_examination_template.clinical_examination_template.get_templates_for_practitioner",
		args: { practitioner: frm.doc.practitioner },
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				let templates = r.message;
				
				// Add Clinical Examination button with dropdown
				if (templates.length === 1) {
					// Single template - direct button
					frm.add_custom_button(__("Clinical Examination"), function() {
						create_clinical_examination(frm, templates[0].template_name);
					}, __("Create"));
				} else {
					// Multiple templates - dropdown
					templates.forEach(function(template) {
						let label = template.examination_type;
						if (template.is_default) {
							label += " ★";
						}
						frm.add_custom_button(__(label), function() {
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
		callback: function(r) {
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
	
	wrapper.find('.open-clinical-exam').on('click', function() {
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
		callback: function(r) {
			if (r.message && r.message.default_examination_template) {
				// Practitioner has clinical examination template assigned
				frm.set_value("show_clinical_examination", 1);
				
				// Get template details
				frappe.call({
					method: "frappe.client.get_value",
					args: {
						doctype: "Clinical Examination Template",
						filters: { name: r.message.default_examination_template },
						fieldname: ["template_name", "examination_type"]
					},
					callback: function(template_r) {
						if (template_r.message) {
							// Set examination type
							if (!frm.doc.exam_examination_type) {
								frm.set_value("exam_examination_type", template_r.message.examination_type);
							}
							
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

// Clinical Examination Diagram Rendering - STEP 3
function render_clinical_exam_diagram(frm) {
	// Render both old diagram and new STEP 3 interactive diagrams
	render_step3_interactive_diagrams(frm);
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
				grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
				gap: 20px;
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
			}
			.clickable-region:hover {
				opacity: 0.7;
				filter: brightness(1.1);
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
				<!-- FACE DIAGRAM -->
				<div class="diagram-card">
					<h6><i class="fa fa-user"></i> Face & Neck - Front View</h6>
					<svg viewBox="0 0 250 320" style="width: 100%; max-width: 280px; display: block; margin: 0 auto;">
						<!-- Face Background with 3D effect -->
						<defs>
							<radialGradient id="skinGradient" cx="50%" cy="40%" r="60%">
								<stop offset="0%" style="stop-color:#ffe4c4"/>
								<stop offset="100%" style="stop-color:#deb887"/>
							</radialGradient>
							<filter id="shadow3d">
								<feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.3"/>
							</filter>
						</defs>
						
						<!-- Hair -->
						<ellipse cx="125" cy="50" rx="70" ry="40" fill="#4a3728"/>
						
						<!-- Face Outline -->
						<ellipse cx="125" cy="100" rx="65" ry="75" fill="url(#skinGradient)" stroke="#c9a77a" stroke-width="2" filter="url(#shadow3d)"/>
						
						<!-- Forehead Left -->
						<path d="M70,50 Q90,35 110,45 L110,70 Q90,65 70,70 Z" fill="rgba(255,200,150,0.3)" stroke="#deb887" class="clickable-region" data-region="forehead" data-side="Left" data-diagram="Face"/>
						<!-- Forehead Right -->
						<path d="M140,45 Q160,35 180,50 L180,70 Q160,65 140,70 Z" fill="rgba(255,200,150,0.3)" stroke="#deb887" class="clickable-region" data-region="forehead" data-side="Right" data-diagram="Face"/>
						
						<!-- Eyes -->
						<ellipse cx="95" cy="85" rx="18" ry="10" fill="#fff" stroke="#333" stroke-width="1.5" class="clickable-region" data-region="eye" data-side="Left" data-diagram="Face"/>
						<ellipse cx="155" cy="85" rx="18" ry="10" fill="#fff" stroke="#333" stroke-width="1.5" class="clickable-region" data-region="eye" data-side="Right" data-diagram="Face"/>
						<circle cx="95" cy="85" r="6" fill="#4a3728"/>
						<circle cx="155" cy="85" r="6" fill="#4a3728"/>
						<circle cx="93" cy="83" r="2" fill="#fff"/>
						<circle cx="153" cy="83" r="2" fill="#fff"/>
						
						<!-- Eyebrows -->
						<path d="M72,70 Q95,62 115,70" fill="none" stroke="#4a3728" stroke-width="3"/>
						<path d="M135,70 Q155,62 178,70" fill="none" stroke="#4a3728" stroke-width="3"/>
						
						<!-- Nose -->
						<path d="M125,75 L120,110 Q125,118 130,110 L125,75" fill="#deb887" stroke="#c9a77a" stroke-width="1" class="clickable-region" data-region="nose" data-side="Midline" data-diagram="Face"/>
						<ellipse cx="117" cy="112" rx="6" ry="4" fill="#deb887" stroke="#c9a77a"/>
						<ellipse cx="133" cy="112" rx="6" ry="4" fill="#deb887" stroke="#c9a77a"/>
						
						<!-- Cheeks -->
						<ellipse cx="70" cy="115" rx="22" ry="25" fill="rgba(255,182,193,0.2)" stroke="#deb887" stroke-dasharray="3,3" class="clickable-region" data-region="cheek" data-side="Left" data-diagram="Face"/>
						<ellipse cx="180" cy="115" rx="22" ry="25" fill="rgba(255,182,193,0.2)" stroke="#deb887" stroke-dasharray="3,3" class="clickable-region" data-region="cheek" data-side="Right" data-diagram="Face"/>
						
						<!-- Parotid Region -->
						<ellipse cx="55" cy="100" rx="12" ry="18" fill="rgba(255,220,180,0.3)" stroke="#c9a77a" stroke-dasharray="2,2" class="clickable-region" data-region="parotid" data-side="Left" data-diagram="Face"/>
						<ellipse cx="195" cy="100" rx="12" ry="18" fill="rgba(255,220,180,0.3)" stroke="#c9a77a" stroke-dasharray="2,2" class="clickable-region" data-region="parotid" data-side="Right" data-diagram="Face"/>
						
						<!-- Ears -->
						<ellipse cx="48" cy="95" rx="10" ry="20" fill="url(#skinGradient)" stroke="#c9a77a" stroke-width="1.5" class="clickable-region" data-region="ear" data-side="Left" data-diagram="Face"/>
						<ellipse cx="202" cy="95" rx="10" ry="20" fill="url(#skinGradient)" stroke="#c9a77a" stroke-width="1.5" class="clickable-region" data-region="ear" data-side="Right" data-diagram="Face"/>
						
						<!-- Lips/Mouth -->
						<path d="M100,140 Q125,130 150,140" fill="none" stroke="#cc6666" stroke-width="5" stroke-linecap="round" class="clickable-region" data-region="upper-lip" data-side="Midline" data-diagram="Face"/>
						<path d="M100,145 Q125,158 150,145" fill="none" stroke="#cc6666" stroke-width="5" stroke-linecap="round" class="clickable-region" data-region="lower-lip" data-side="Midline" data-diagram="Face"/>
						
						<!-- Chin -->
						<ellipse cx="125" cy="165" rx="25" ry="15" fill="rgba(255,200,150,0.3)" stroke="#deb887" stroke-dasharray="3,3" class="clickable-region" data-region="chin" data-side="Midline" data-diagram="Face"/>
						
						<!-- NECK -->
						<rect x="85" y="180" width="80" height="80" fill="url(#skinGradient)" stroke="#c9a77a" stroke-width="2" rx="5"/>
						
						<!-- Neck Regions -->
						<rect x="85" y="185" width="35" height="35" fill="rgba(100,200,255,0.1)" stroke="#4a90d9" stroke-dasharray="3,3" class="clickable-region" data-region="neck-submandibular" data-side="Left" data-diagram="Neck"/>
						<rect x="130" y="185" width="35" height="35" fill="rgba(100,200,255,0.1)" stroke="#4a90d9" stroke-dasharray="3,3" class="clickable-region" data-region="neck-submandibular" data-side="Right" data-diagram="Neck"/>
						<rect x="85" y="225" width="35" height="30" fill="rgba(100,255,100,0.1)" stroke="#4ad94a" stroke-dasharray="3,3" class="clickable-region" data-region="neck-cervical" data-side="Left" data-diagram="Neck"/>
						<rect x="130" y="225" width="35" height="30" fill="rgba(100,255,100,0.1)" stroke="#4ad94a" stroke-dasharray="3,3" class="clickable-region" data-region="neck-cervical" data-side="Right" data-diagram="Neck"/>
						<ellipse cx="125" y="210" rx="15" ry="10" fill="rgba(255,100,100,0.2)" stroke="#d94a4a" stroke-dasharray="3,3" class="clickable-region" data-region="neck-submental" data-side="Midline" data-diagram="Neck"/>
						
						<!-- Labels -->
						<text x="125" y="195" text-anchor="middle" class="region-label">Submental</text>
						<text x="100" y="205" text-anchor="middle" class="region-label">L</text>
						<text x="150" y="205" text-anchor="middle" class="region-label">R</text>
						<text x="100" y="245" text-anchor="middle" class="region-label">Cervical L</text>
						<text x="150" y="245" text-anchor="middle" class="region-label">Cervical R</text>
						
						<!-- Markers container -->
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
						
						<!-- Upper Lip -->
						<path d="M50,70 Q140,30 230,70 L220,85 Q140,55 60,85 Z" fill="url(#lipGradient)" stroke="#993333" stroke-width="1" class="clickable-region" data-region="upper-lip" data-side="Midline" data-diagram="Oral Cavity"/>
						
						<!-- Lower Lip -->
						<path d="M50,190 Q140,230 230,190 L220,175 Q140,205 60,175 Z" fill="url(#lipGradient)" stroke="#993333" stroke-width="1" class="clickable-region" data-region="lower-lip" data-side="Midline" data-diagram="Oral Cavity"/>
						
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
						
						<!-- Gingiva/Alveolus Upper -->
						<path d="M55,95 Q140,85 225,95 L220,100 Q140,92 60,100 Z" fill="#ffb6c1" stroke="#cc8888" class="clickable-region" data-region="upper-alveolus" data-side="Midline" data-diagram="Oral Cavity"/>
						
						<!-- Gingiva/Alveolus Lower -->
						<path d="M55,165 Q140,175 225,165 L220,160 Q140,168 60,160 Z" fill="#ffb6c1" stroke="#cc8888" class="clickable-region" data-region="lower-alveolus" data-side="Midline" data-diagram="Oral Cavity"/>
						
						<!-- Buccal Mucosa Left -->
						<ellipse cx="55" cy="130" rx="20" ry="35" fill="rgba(255,182,193,0.4)" stroke="#cc8888" stroke-width="1" class="clickable-region" data-region="buccal-mucosa" data-side="Left" data-diagram="Oral Cavity"/>
						<text x="55" y="135" text-anchor="middle" class="region-label" fill="#993333">L</text>
						
						<!-- Buccal Mucosa Right -->
						<ellipse cx="225" cy="130" rx="20" ry="35" fill="rgba(255,182,193,0.4)" stroke="#cc8888" stroke-width="1" class="clickable-region" data-region="buccal-mucosa" data-side="Right" data-diagram="Oral Cavity"/>
						<text x="225" y="135" text-anchor="middle" class="region-label" fill="#993333">R</text>
						
						<!-- Hard Palate -->
						<ellipse cx="140" cy="105" rx="50" ry="20" fill="rgba(255,200,200,0.5)" stroke="#cc8888" stroke-width="1" class="clickable-region" data-region="hard-palate" data-side="Midline" data-diagram="Oral Cavity"/>
						<text x="140" y="108" text-anchor="middle" class="region-label" fill="#993333">Hard Palate</text>
						
						<!-- Soft Palate / Uvula -->
						<path d="M100,95 Q140,85 180,95 L175,100 Q140,92 105,100 Z" fill="rgba(255,150,150,0.5)" stroke="#cc6666" class="clickable-region" data-region="soft-palate" data-side="Midline" data-diagram="Oral Cavity"/>
						
						<!-- Tongue -->
						<ellipse cx="140" cy="140" rx="55" ry="40" fill="url(#tongueGradient)" stroke="#cc4444" stroke-width="2" class="clickable-region" data-region="tongue-dorsum" data-side="Midline" data-diagram="Tongue"/>
						<line x1="140" y1="100" x2="140" y2="175" stroke="#cc4444" stroke-width="1" stroke-dasharray="3,3"/>
						<text x="140" y="145" text-anchor="middle" class="region-label" fill="#fff">Tongue</text>
						
						<!-- Tongue Lateral Regions -->
						<ellipse cx="95" cy="140" rx="15" ry="25" fill="rgba(255,100,100,0.2)" stroke="#cc4444" stroke-dasharray="2,2" class="clickable-region" data-region="tongue-lateral" data-side="Left" data-diagram="Tongue"/>
						<ellipse cx="185" cy="140" rx="15" ry="25" fill="rgba(255,100,100,0.2)" stroke="#cc4444" stroke-dasharray="2,2" class="clickable-region" data-region="tongue-lateral" data-side="Right" data-diagram="Tongue"/>
						
						<!-- Floor of Mouth -->
						<ellipse cx="140" cy="175" rx="45" ry="12" fill="rgba(200,100,100,0.3)" stroke="#993333" class="clickable-region" data-region="floor-of-mouth" data-side="Midline" data-diagram="Oral Cavity"/>
						<text x="140" y="178" text-anchor="middle" class="region-label" fill="#fff">Floor</text>
						
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
							${[18,17,16,15,14,13,12,11,21,22,23,24,25,26,27,28].map((num, i) => `
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
							${[48,47,46,45,44,43,42,41,31,32,33,34,35,36,37,38].map((num, i) => `
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
				
				<!-- NECK LYMPH NODES -->
				<div class="diagram-card">
					<h6><i class="fa fa-project-diagram"></i> Neck - Lymph Node Regions</h6>
					<svg viewBox="0 0 250 280" style="width: 100%; max-width: 280px; display: block; margin: 0 auto;">
						<defs>
							<radialGradient id="neckSkin" cx="50%" cy="30%" r="70%">
								<stop offset="0%" style="stop-color:#ffe4c4"/>
								<stop offset="100%" style="stop-color:#deb887"/>
							</radialGradient>
						</defs>
						
						<!-- Neck outline -->
						<path d="M75,30 Q125,20 175,30 L190,250 Q125,270 60,250 Z" fill="url(#neckSkin)" stroke="#c9a77a" stroke-width="2"/>
						
						<!-- Jaw line -->
						<path d="M60,35 Q125,50 190,35" fill="none" stroke="#c9a77a" stroke-width="2"/>
						
						<!-- Clavicle -->
						<path d="M40,250 Q125,235 210,250" fill="none" stroke="#c9a77a" stroke-width="3"/>
						
						<!-- Level I - Submental -->
						<ellipse cx="125" cy="55" rx="25" ry="12" fill="rgba(255,100,100,0.3)" stroke="#ff6666" stroke-width="2" class="clickable-region" data-region="level-i-submental" data-side="Midline" data-diagram="Neck"/>
						<text x="125" y="58" text-anchor="middle" font-size="8" fill="#cc3333">Ia</text>
						
						<!-- Level I - Submandibular -->
						<ellipse cx="85" cy="65" rx="18" ry="15" fill="rgba(255,150,100,0.3)" stroke="#ff9966" stroke-width="2" class="clickable-region" data-region="level-i-submandibular" data-side="Left" data-diagram="Neck"/>
						<ellipse cx="165" cy="65" rx="18" ry="15" fill="rgba(255,150,100,0.3)" stroke="#ff9966" stroke-width="2" class="clickable-region" data-region="level-i-submandibular" data-side="Right" data-diagram="Neck"/>
						<text x="85" y="68" text-anchor="middle" font-size="8" fill="#cc6633">Ib</text>
						<text x="165" y="68" text-anchor="middle" font-size="8" fill="#cc6633">Ib</text>
						
						<!-- Level II - Upper Jugular -->
						<ellipse cx="80" cy="100" rx="20" ry="25" fill="rgba(255,255,100,0.3)" stroke="#cccc00" stroke-width="2" class="clickable-region" data-region="level-ii-upper-jugular" data-side="Left" data-diagram="Neck"/>
						<ellipse cx="170" cy="100" rx="20" ry="25" fill="rgba(255,255,100,0.3)" stroke="#cccc00" stroke-width="2" class="clickable-region" data-region="level-ii-upper-jugular" data-side="Right" data-diagram="Neck"/>
						<text x="80" y="103" text-anchor="middle" font-size="8" fill="#999900">II</text>
						<text x="170" y="103" text-anchor="middle" font-size="8" fill="#999900">II</text>
						
						<!-- Level III - Middle Jugular -->
						<ellipse cx="82" cy="150" rx="18" ry="25" fill="rgba(100,255,100,0.3)" stroke="#66cc66" stroke-width="2" class="clickable-region" data-region="level-iii-middle-jugular" data-side="Left" data-diagram="Neck"/>
						<ellipse cx="168" cy="150" rx="18" ry="25" fill="rgba(100,255,100,0.3)" stroke="#66cc66" stroke-width="2" class="clickable-region" data-region="level-iii-middle-jugular" data-side="Right" data-diagram="Neck"/>
						<text x="82" y="153" text-anchor="middle" font-size="8" fill="#339933">III</text>
						<text x="168" y="153" text-anchor="middle" font-size="8" fill="#339933">III</text>
						
						<!-- Level IV - Lower Jugular -->
						<ellipse cx="85" cy="200" rx="18" ry="25" fill="rgba(100,200,255,0.3)" stroke="#66aacc" stroke-width="2" class="clickable-region" data-region="level-iv-lower-jugular" data-side="Left" data-diagram="Neck"/>
						<ellipse cx="165" cy="200" rx="18" ry="25" fill="rgba(100,200,255,0.3)" stroke="#66aacc" stroke-width="2" class="clickable-region" data-region="level-iv-lower-jugular" data-side="Right" data-diagram="Neck"/>
						<text x="85" y="203" text-anchor="middle" font-size="8" fill="#3388aa">IV</text>
						<text x="165" y="203" text-anchor="middle" font-size="8" fill="#3388aa">IV</text>
						
						<!-- Level V - Posterior Triangle -->
						<path d="M55,90 L45,180 L70,180 Z" fill="rgba(200,100,255,0.3)" stroke="#aa66cc" stroke-width="2" class="clickable-region" data-region="level-v-posterior" data-side="Left" data-diagram="Neck"/>
						<path d="M195,90 L205,180 L180,180 Z" fill="rgba(200,100,255,0.3)" stroke="#aa66cc" stroke-width="2" class="clickable-region" data-region="level-v-posterior" data-side="Right" data-diagram="Neck"/>
						<text x="55" y="140" text-anchor="middle" font-size="8" fill="#8833aa">V</text>
						<text x="195" y="140" text-anchor="middle" font-size="8" fill="#8833aa">V</text>
						
						<!-- Level VI - Anterior/Central -->
						<ellipse cx="125" cy="180" rx="20" ry="30" fill="rgba(255,200,200,0.3)" stroke="#cc9999" stroke-width="2" class="clickable-region" data-region="level-vi-central" data-side="Midline" data-diagram="Neck"/>
						<text x="125" y="183" text-anchor="middle" font-size="8" fill="#996666">VI</text>
						
						<!-- Thyroid -->
						<path d="M110,210 Q125,195 140,210 L145,235 Q125,245 105,235 Z" fill="rgba(100,150,255,0.3)" stroke="#6699cc" stroke-width="2" class="clickable-region" data-region="thyroid" data-side="Midline" data-diagram="Neck"/>
						<text x="125" y="225" text-anchor="middle" font-size="7" fill="#336699">Thyroid</text>
						
						<!-- Markers container -->
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
	wrapper.find('.clickable-region').on('click', function(e) {
		let region = $(this).data('region');
		let side = $(this).data('side') || 'Midline';
		let diagram = $(this).data('diagram') || 'Face';
		
		add_lesion_marking(frm, region, side, diagram, e);
	});
}

// Add lesion from diagram click
function add_lesion_marking(frm, region, side, diagram, event) {
	// Format region name for display
	let region_display = region.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
	
	let d = new frappe.ui.Dialog({
		title: __('Mark Lesion - {0} ({1})', [region_display, side]),
		size: 'large',
		fields: [
			{
				fieldtype: 'Section Break',
				label: 'Location Details'
			},
			{
				fieldname: 'diagram_type',
				fieldtype: 'Data',
				label: 'Diagram',
				default: diagram,
				read_only: 1
			},
			{
				fieldname: 'location',
				fieldtype: 'Data',
				label: 'Location',
				default: region_display,
				read_only: 1
			},
			{
				fieldname: 'side',
				fieldtype: 'Select',
				label: 'Side',
				options: 'Left\nRight\nMidline\nBilateral',
				default: side
			},
			{
				fieldtype: 'Section Break',
				label: 'Lesion Characteristics'
			},
			{
				fieldname: 'lesion_type',
				fieldtype: 'Select',
				label: 'Lesion Type',
				options: '\nWhite Patch (Leukoplakia)\nRed Patch (Erythroplakia)\nMixed White-Red\nUlcer - Superficial\nUlcer - Deep\nNodule/Lump\nSwelling\nFibrous Bands\nVesicle\nPapule\nPlaque\nMacule\nPustule\nPigmentation\nErosion\nFissure\nGrowth/Mass\nLymph Node\nOther',
				reqd: 1
			},
			{
				fieldname: 'size_mm',
				fieldtype: 'Data',
				label: 'Size (L x W x H in mm)',
				description: 'Example: 10 x 5 x 2'
			},
			{
				fieldname: 'color',
				fieldtype: 'Select',
				label: 'Color',
				options: '\nWhite\nRed\nBlack\nBrown\nMixed\nNormal'
			},
			{
				fieldtype: 'Section Break',
				label: 'Notes'
			},
			{
				fieldname: 'description',
				fieldtype: 'Small Text',
				label: 'Description'
			},
			{
				fieldname: 'note',
				fieldtype: 'Small Text',
				label: 'Clinical Note'
			}
		],
		primary_action_label: __('Add Lesion'),
		primary_action: function() {
			let values = d.get_values();
			
			// Get current lesion count
			let lesion_count = (frm.doc.exam_diagram_lesions || []).length + 1;
			
			// Add to lesions table
			let row = frm.add_child('exam_diagram_lesions');
			row.lesion_number = lesion_count;
			row.diagram_type = values.diagram_type;
			row.location = values.location;
			row.side = values.side;
			row.lesion_type = values.lesion_type;
			row.size_mm = values.size_mm;
			row.color = values.color;
			row.description = values.description;
			row.note = values.note;
			row.diagram_region = region;
			
			frm.refresh_field('exam_diagram_lesions');
			d.hide();
			
			frappe.show_alert({
				message: __('Lesion #{0} added: {1} - {2}', [lesion_count, region_display, side]),
				indicator: 'green'
			});
		}
	});
	d.show();
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
	wrapper.find('.clickable-region').on('click', function() {
		let region = $(this).data('region');
		add_lesion_from_diagram(frm, region);
	});
	
	// Style clickable regions
	wrapper.find('.clickable-region').css({
		'cursor': 'pointer',
		'transition': 'all 0.2s ease'
	}).hover(
		function() { $(this).css({'opacity': '0.7', 'stroke-width': '3'}); },
		function() { $(this).css({'opacity': '1', 'stroke-width': ''}); }
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
		primary_action: function() {
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
	wrapper.find('.image-upload-card').on('click', function() {
		let category = $(this).data('category');
		let card = $(this);
		
		new frappe.ui.FileUploader({
			doctype: frm.doctype,
			docname: frm.docname,
			folder: 'Home/Attachments',
			on_success: function(file_doc) {
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
		function() { $(this).css({'transform': 'scale(1.02)', 'box-shadow': '0 4px 15px rgba(0,0,0,0.1)'}); },
		function() { $(this).css({'transform': 'scale(1)', 'box-shadow': 'none'}); }
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
	// Get the HTML field wrapper
	let field = frm.get_field('exam_pictures_html');
	if (!field || !field.$wrapper) {
		return;
	}
	
	let wrapper = field.$wrapper;
	wrapper.empty();
	
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
				padding: 20px;
				background: linear-gradient(145deg, #1e3c72 0%, #2a5298 100%);
				border-radius: 16px;
				margin: 10px 0;
			}
			.step4-header {
				color: #fff;
				text-align: center;
				margin-bottom: 20px;
				padding-bottom: 15px;
				border-bottom: 1px solid rgba(255,255,255,0.2);
			}
			.pictures-grid {
				display: grid;
				grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
				gap: 15px;
			}
			.picture-card {
				background: #fff;
				border-radius: 12px;
				overflow: hidden;
				box-shadow: 0 4px 15px rgba(0,0,0,0.2);
				transition: all 0.3s ease;
			}
			.picture-card:hover {
				transform: translateY(-5px);
				box-shadow: 0 8px 25px rgba(0,0,0,0.3);
			}
			.picture-card-header {
				background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
				color: #fff;
				padding: 10px;
				font-size: 11px;
				font-weight: 600;
				text-align: center;
			}
			.picture-card-body {
				padding: 10px;
				min-height: 150px;
				display: flex;
				flex-direction: column;
				align-items: center;
				justify-content: center;
				background: #f8f9fa;
			}
			.picture-placeholder {
				width: 100%;
				height: 120px;
				border: 2px dashed #ccc;
				border-radius: 8px;
				display: flex;
				flex-direction: column;
				align-items: center;
				justify-content: center;
				cursor: pointer;
				transition: all 0.2s ease;
				background: #fff;
			}
			.picture-placeholder:hover {
				border-color: #667eea;
				background: rgba(102, 126, 234, 0.05);
			}
			.picture-placeholder i {
				font-size: 32px;
				color: #ccc;
				margin-bottom: 8px;
			}
			.picture-placeholder span {
				font-size: 11px;
				color: #888;
			}
			.picture-preview {
				width: 100%;
				position: relative;
			}
			.picture-preview img {
				width: 100%;
				height: 120px;
				object-fit: cover;
				border-radius: 8px;
				cursor: pointer;
			}
			.picture-actions {
				position: absolute;
				top: 5px;
				right: 5px;
				display: flex;
				gap: 5px;
			}
			.picture-action-btn {
				width: 28px;
				height: 28px;
				border-radius: 50%;
				border: none;
				cursor: pointer;
				display: flex;
				align-items: center;
				justify-content: center;
				font-size: 12px;
				transition: all 0.2s ease;
			}
			.btn-view {
				background: rgba(0,123,255,0.9);
				color: #fff;
			}
			.btn-replace {
				background: rgba(255,193,7,0.9);
				color: #333;
			}
			.btn-delete {
				background: rgba(220,53,69,0.9);
				color: #fff;
			}
			.picture-action-btn:hover {
				transform: scale(1.1);
			}
			.upload-status {
				margin-top: 8px;
				font-size: 10px;
				color: #28a745;
				display: none;
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
											<button class="picture-action-btn btn-replace" title="Replace"><i class="fa fa-sync"></i></button>
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
	
	wrapper.html(html);
	
	// Add click handlers for upload
	wrapper.find('.picture-placeholder').on('click', function() {
		let card = $(this).closest('.picture-card');
		let field = card.data('field');
		let name = card.data('name');
		upload_picture(frm, card, field, name);
	});
	
	// View full image
	wrapper.find('.btn-view').on('click', function(e) {
		e.stopPropagation();
		let img_src = $(this).closest('.picture-preview').find('img').attr('src');
		let name = $(this).closest('.picture-card').data('name');
		
		let d = new frappe.ui.Dialog({
			title: name,
			size: 'extra-large'
		});
		d.$body.html(`<img src="${img_src}" style="width: 100%; max-height: 80vh; object-fit: contain;"/>`);
		d.show();
	});
	
	// Replace image
	wrapper.find('.btn-replace').on('click', function(e) {
		e.stopPropagation();
		let card = $(this).closest('.picture-card');
		let field = card.data('field');
		let name = card.data('name');
		upload_picture(frm, card, field, name);
	});
	
	// Delete image
	wrapper.find('.btn-delete').on('click', function(e) {
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
				card.find('.picture-placeholder').on('click', function() {
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
		on_success: function(file_doc) {
			// Set field value
			frm.set_value(field, file_doc.file_url);
			
			// Update card UI
			card.find('.picture-card-body').html(`
				<div class="picture-preview">
					<img src="${file_doc.file_url}" alt="${name}" class="preview-img"/>
					<div class="picture-actions">
						<button class="picture-action-btn btn-view" title="View Full"><i class="fa fa-expand"></i></button>
						<button class="picture-action-btn btn-replace" title="Replace"><i class="fa fa-sync"></i></button>
						<button class="picture-action-btn btn-delete" title="Delete"><i class="fa fa-trash"></i></button>
					</div>
				</div>
				<div class="upload-status show"><i class="fa fa-check"></i> Uploaded</div>
			`);
			
			// Re-bind action handlers
			card.find('.btn-view').on('click', function(e) {
				e.stopPropagation();
				let d = new frappe.ui.Dialog({
					title: name,
					size: 'extra-large'
				});
				d.$body.html(`<img src="${file_doc.file_url}" style="width: 100%; max-height: 80vh; object-fit: contain;"/>`);
				d.show();
			});
			
			card.find('.btn-replace').on('click', function(e) {
				e.stopPropagation();
				upload_picture(frm, card, field, name);
			});
			
			card.find('.btn-delete').on('click', function(e) {
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
