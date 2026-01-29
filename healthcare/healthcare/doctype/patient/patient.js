// Copyright (c) 2016, ESS LLP and contributors
// For license information, please see license.txt
{% include 'healthcare/regional/india/abdm/js/patient.js' %}

frappe.ui.form.on('Patient', {
	refresh: function (frm) {
		// Setup insurance card preview handlers
		setup_insurance_card_previews(frm);
		// Setup diagnosis category filters
		setup_diagnosis_filters(frm);
		
		// Render Quick Diagnosis Selection Panel above Medical History table
		if (!frm.is_new()) {
			render_diagnosis_quick_select_panel(frm);
		}
		
		// Add custom CSS for diagnosis panel and card image preview
		add_custom_styles();
		
		// Show insurance card summary with image previews
		if (frm.doc.patient_insurance && frm.doc.patient_insurance.length > 0) {
			render_insurance_summary(frm);
		}
		
		frm.set_query('patient', 'patient_relation', function () {
			return {
				filters: [
					['Patient', 'name', '!=', frm.doc.name]
				]
			};
		});
		frm.set_query('customer_group', {'is_group': 0});
		frm.set_query('default_price_list', { 'selling': 1});
		
		// Set query for allergen field in patient_allergy child table based on category
		if (frm.fields_dict.patient_allergy) {
			frm.set_query('allergen', 'patient_allergy', function(doc, cdt, cdn) {
				const row = locals[cdt][cdn];
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

		if (frappe.defaults.get_default('patient_name_by') != 'Naming Series') {
			frm.toggle_display('naming_series', false);
		} else {
			erpnext.toggle_naming_series();
		}

		if (frappe.defaults.get_default('collect_registration_fee') && frm.doc.status == 'Disabled') {
			frm.add_custom_button(__('Invoice Patient Registration'), function () {
				invoice_registration(frm);
			});
		}

		if (frm.doc.patient_name && frappe.user.has_role('Physician')) {
			frm.add_custom_button(__('Patient Progress'), function() {
				frappe.route_options = {'patient': frm.doc.name};
				frappe.set_route('patient-progress');
			}, __('View'));

			frm.add_custom_button(__('Patient History'), function() {
				frappe.route_options = {'patient': frm.doc.name};
				frappe.set_route('patient_history');
			}, __('View'));
		}

		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Patient'};
		frm.toggle_display(['address_html', 'contact_html'], !frm.is_new());

		if (!frm.is_new()) {
			if ((frappe.user.has_role('Nursing User') || frappe.user.has_role('Physician'))) {
				frm.add_custom_button(__('Medical Record'), function () {
					create_medical_record(frm);
				}, __('Create'));
				frm.toggle_enable(['customer'], 0);
			}
			frappe.contacts.render_address_and_contact(frm);
			erpnext.utils.set_party_dashboard_indicators(frm);
		} else {
			frappe.contacts.clear_address_and_contact(frm);
		}
	},

	onload: function (frm) {
		if (frm.doc.dob) {
			$(frm.fields_dict['age_html'].wrapper).html(`${__('AGE')} : ${get_age(frm.doc.dob)}`);
		} else {
			$(frm.fields_dict['age_html'].wrapper).html('');
		}
	}
});

frappe.ui.form.on('Patient', 'dob', function(frm) {
	if (frm.doc.dob) {
		let today = new Date();
		let birthDate = new Date(frm.doc.dob);
		if (today < birthDate) {
			frappe.msgprint(__('Please select a valid Date'));
			frappe.model.set_value(frm.doctype,frm.docname, 'dob', '');
		} else {
			let age_str = get_age(frm.doc.dob);
			$(frm.fields_dict['age_html'].wrapper).html(`${__('AGE')} : ${age_str}`);
		}
	} else {
		$(frm.fields_dict['age_html'].wrapper).html('');
	}
});

frappe.ui.form.on('Patient Relation', {
	patient_relation_add: function(frm){
		frm.fields_dict['patient_relation'].grid.get_field('patient').get_query = function(doc){
			let patient_list = [];
			if(!doc.__islocal) patient_list.push(doc.name);
			$.each(doc.patient_relation, function(idx, val){
				if (val.patient) patient_list.push(val.patient);
			});
			return { filters: [['Patient', 'name', 'not in', patient_list]] };
		};
	}
});

// Patient Medical History child table events
frappe.ui.form.on('Patient Medical History', {
	diagnosis_category: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Clear diagnosis when category changes
		frappe.model.set_value(cdt, cdn, 'diagnosis', '');
		frappe.model.set_value(cdt, cdn, 'diagnosis_name', '');
	},
	diagnosis: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.diagnosis) {
			// Auto-fill category when diagnosis is selected
			frappe.db.get_value('Diagnosis', row.diagnosis, ['diagnosis_category', 'diagnosis'], function(r) {
				if (r) {
					if (r.diagnosis_category && !row.diagnosis_category) {
						frappe.model.set_value(cdt, cdn, 'diagnosis_category', r.diagnosis_category);
					}
					frappe.model.set_value(cdt, cdn, 'diagnosis_name', r.diagnosis);
				}
			});
		}
	},
	when: function(frm, cdt, cdn) {
		validate_when_field(frm, cdt, cdn);
	}
});

// Patient Family Medical History child table events
frappe.ui.form.on('Patient Family Medical History', {
	diagnosis_category: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Clear diagnosis when category changes
		frappe.model.set_value(cdt, cdn, 'diagnosis', '');
		frappe.model.set_value(cdt, cdn, 'diagnosis_name', '');
	},
	diagnosis: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.diagnosis) {
			// Auto-fill category when diagnosis is selected
			frappe.db.get_value('Diagnosis', row.diagnosis, ['diagnosis_category', 'diagnosis'], function(r) {
				if (r) {
					if (r.diagnosis_category && !row.diagnosis_category) {
						frappe.model.set_value(cdt, cdn, 'diagnosis_category', r.diagnosis_category);
					}
					frappe.model.set_value(cdt, cdn, 'diagnosis_name', r.diagnosis);
				}
			});
		}
	},
	when: function(frm, cdt, cdn) {
		validate_when_field(frm, cdt, cdn);
	}
});

// Setup diagnosis category filters for child tables
function setup_diagnosis_filters(frm) {
	// Filter for Patient Medical History
	if (frm.fields_dict.patient_medical_history) {
		frm.fields_dict.patient_medical_history.grid.get_field('diagnosis').get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			let filters = {};
			if (row.diagnosis_category) {
				filters['diagnosis_category'] = row.diagnosis_category;
			}
			return { filters: filters };
		};
	}
	
	// Filter for Patient Family Medical History
	if (frm.fields_dict.patient_family_medical_history) {
		frm.fields_dict.patient_family_medical_history.grid.get_field('diagnosis').get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			let filters = {};
			if (row.diagnosis_category) {
				filters['diagnosis_category'] = row.diagnosis_category;
			}
			return { filters: filters };
		};
	}
}

// ============================================
// QUICK DIAGNOSIS SELECTION PANEL
// ============================================

// Common diagnoses to show in quick selection - as per client's ICanCaRe TOBACCO USERS ORAL Screening Form
// Updated to match actual Diagnosis data imported from client CSV (Diagnosis_List.csv)
const QUICK_DIAGNOSES = [
	// Medical History - as per client document, linked to actual Diagnosis DocType records
	{ category: "Cardiovascular", name: "Essential hypertension", short: "Blood Pressure (Hypertension)" },
	{ category: "Endocrine/Metabolic", name: "Type 2 diabetes mellitus", short: "Diabetes" },
	{ category: "Cardiovascular", name: "Ischaemic heart disease", short: "Heart Disease - Cardiovascular Disease" },
	{ category: "Neurology", name: "Epilepsy", short: "Neurological disease (Epilepsy)" },
	{ category: "Respiratory", name: "Asthma", short: "Respiratory Disease (e.g., COPD, Asthma)" },
	{ category: "Respiratory", name: "COPD", short: "COPD" },
	{ category: "Gastrointestinal", name: "Liver cirrhosis", short: "Liver Disease" },
	{ category: "Genitourinary", name: "Chronic kidney disease", short: "Renal Disease" },
	{ category: "Eye", name: "Cataract", short: "Eye Problem" },
	{ category: "Immunosuppression", name: "HIV infection", short: "Immunosuppressive Condition" },
	{ category: "Immunosuppression", name: "Systemic lupus erythematosus", short: "Other Relevant Conditions" },
	{ category: "Allergy", name: "Drug allergy", short: "Allergies (Drug/Food/Chemical)" },
	{ category: "Medical Disease", name: "Fibromyalgia", short: "Medical Disease" },
	{ category: "Trauma/Orthopaedics", name: "Fracture wrist", short: "Any Surgery Done" },
	{ category: "Obstetrics/Gynaecology", name: "Female infertility", short: "Infertility" },
	{ category: "Cancer", name: "Oral cancer", short: "ORAL PML - on treatment" },
	{ category: "Gastrointestinal", name: "Achalasia", short: "Restricted Mouth Opening" },
	{ category: "Cancer", name: "Breast cancer", short: "CANCER PAST - on treatment" }
];

function render_diagnosis_quick_select_panel(frm) {
	// Find the Medical History table - this is a custom field
	if (!frm.fields_dict.patient_medical_history) {
		return;
	}
	
	let table_wrapper = frm.fields_dict.patient_medical_history.$wrapper;
	
	// Remove existing panel if any
	table_wrapper.parent().find('.diagnosis-quick-panel').remove();
	
	// Get existing diagnoses in both tables
	let existing_self = (frm.doc.patient_medical_history || []).map(d => d.diagnosis);
	let existing_family = (frm.doc.patient_family_medical_history || []).map(d => d.diagnosis);
	
	// Create the panel HTML
	let panel_html = `
		<div class="diagnosis-quick-panel">
			<div class="panel-header">
				<h5>📋 Medical History & Comorbidities - Quick Selection</h5>
				<p class="text-muted">Click YES to add diagnosis. A dialog will open to enter details.</p>
			</div>
			<div class="diagnosis-table">
				<table class="table table-bordered">
					<thead>
						<tr>
							<th style="width: 50%;">DIAGNOSIS</th>
							<th class="self-column-header" style="width: 25%; text-align: center; background: rgba(59, 130, 246, 0.15);">SELF<br><small>NO / YES</small></th>
							<th class="family-column-header" style="width: 25%; text-align: center; background: rgba(34, 197, 94, 0.15);">FAMILY<br><small>NO / YES</small></th>
						</tr>
					</thead>
					<tbody>
	`;
	
	QUICK_DIAGNOSES.forEach((diag, idx) => {
		let is_self = existing_self.includes(diag.name);
		let is_family = existing_family.includes(diag.name);
		let display_name = diag.short || diag.name;
		
		panel_html += `
			<tr class="diagnosis-row" data-diagnosis="${diag.name}" data-category="${diag.category}">
				<td class="diagnosis-name">${display_name}</td>
				<td class="text-center self-column" style="background: rgba(59, 130, 246, 0.05);">
					<div class="btn-group btn-group-sm" role="group">
						<button type="button" class="btn ${!is_self ? 'btn-outline-secondary' : 'btn-secondary'} btn-self-no" data-type="self" data-value="no">NO</button>
						<button type="button" class="btn ${is_self ? 'btn-primary' : 'btn-outline-primary'} btn-self-yes" data-type="self" data-value="yes">YES</button>
					</div>
				</td>
				<td class="text-center family-column" style="background: rgba(34, 197, 94, 0.05);">
					<div class="btn-group btn-group-sm" role="group">
						<button type="button" class="btn ${!is_family ? 'btn-outline-secondary' : 'btn-secondary'} btn-family-no" data-type="family" data-value="no">NO</button>
						<button type="button" class="btn ${is_family ? 'btn-success' : 'btn-outline-success'} btn-family-yes" data-type="family" data-value="yes">YES</button>
					</div>
				</td>
			</tr>
		`;
	});
	
	panel_html += `
					</tbody>
				</table>
			</div>
			<div class="panel-footer">
				<small class="text-muted">
					<strong>Note:</strong> Clicking YES will automatically add the diagnosis to the respective table below.
				</small>
			</div>
		</div>
	`;
	
	// Insert panel BEFORE the Medical History table
	table_wrapper.before(panel_html);
	
	// Attach event handlers
	attach_quick_panel_events(frm, table_wrapper.parent());
}

function attach_quick_panel_events(frm, wrapper) {
	// Handle SELF YES click
	wrapper.find('.btn-self-yes').off('click').on('click', function() {
		let row = $(this).closest('.diagnosis-row');
		let diagnosis = row.data('diagnosis');
		let category = row.data('category');
		
		// Check if already exists
		let exists = (frm.doc.patient_medical_history || []).some(d => d.diagnosis === diagnosis);
		if (exists) {
			frappe.show_alert({message: __('Already added to Medical History'), indicator: 'orange'});
			return;
		}
		
		// Show dialog for SELF history
		show_self_history_dialog(frm, diagnosis, category, $(this), row);
	});
	
	// Handle SELF NO click
	wrapper.find('.btn-self-no').off('click').on('click', function() {
		let row = $(this).closest('.diagnosis-row');
		let diagnosis = row.data('diagnosis');
		
		// Remove from Medical History if exists
		remove_from_medical_history(frm, diagnosis);
		
		// Update button states
		$(this).removeClass('btn-outline-secondary').addClass('btn-secondary');
		row.find('.btn-self-yes').removeClass('btn-primary').addClass('btn-outline-primary');
	});
	
	// Handle FAMILY YES click
	wrapper.find('.btn-family-yes').off('click').on('click', function() {
		let row = $(this).closest('.diagnosis-row');
		let diagnosis = row.data('diagnosis');
		let category = row.data('category');
		
		// Check if already exists
		let exists = (frm.doc.patient_family_medical_history || []).some(d => d.diagnosis === diagnosis);
		if (exists) {
			frappe.show_alert({message: __('Already added to Family Medical History'), indicator: 'orange'});
			return;
		}
		
		// Show relation dialog
		show_family_relation_dialog(frm, diagnosis, category, $(this), row);
	});
	
	// Handle FAMILY NO click
	wrapper.find('.btn-family-no').off('click').on('click', function() {
		let row = $(this).closest('.diagnosis-row');
		let diagnosis = row.data('diagnosis');
		
		// Remove from Family Medical History if exists
		remove_from_family_history(frm, diagnosis);
		
		// Update button states
		$(this).removeClass('btn-outline-secondary').addClass('btn-secondary');
		row.find('.btn-family-yes').removeClass('btn-success').addClass('btn-outline-success');
	});
}

function show_self_history_dialog(frm, diagnosis, category, btn, row) {
	let d = new frappe.ui.Dialog({
		title: __('Add to Medical History (Self)'),
		fields: [
			{
				fieldname: 'diagnosis_display',
				fieldtype: 'Data',
				label: __('Diagnosis'),
				default: diagnosis,
				read_only: 1
			},
			{
				fieldname: 'when',
				fieldtype: 'Data',
				label: __('Since When'),
				description: __('Enter year (YYYY), month-year (MM/YYYY or M/YYYY). Year must be <= current year'),
				onchange: function() {
					validate_when_field_in_dialog(d, 'when');
				}
			},
			{
				fieldname: 'undergoing_treatment',
				fieldtype: 'Check',
				label: __('Ongoing Treatment'),
				default: 0
			},
			{
				fieldname: 'is_hereditary',
				fieldtype: 'Check',
				label: __('Is Hereditary'),
				description: __('Check if this condition has hereditary/genetic factors'),
				default: 0
			}
		],
		primary_action_label: __('Add'),
		primary_action: function(values) {
			// Validate when field before adding
			if (values.when && !validate_when_format(values.when)) {
				return false;
			}
			
			// Add to Medical History
			let new_row = frm.add_child('patient_medical_history', {
				diagnosis_category: category,
				diagnosis: diagnosis,
				when: values.when || '',
				undergoing_treatment: values.undergoing_treatment ? 1 : 0,
				is_hereditary: values.is_hereditary ? 1 : 0
			});
			
			// Fetch diagnosis name
			frappe.db.get_value('Diagnosis', diagnosis, 'diagnosis', function(r) {
				if (r) {
					frappe.model.set_value(new_row.doctype, new_row.name, 'diagnosis_name', r.diagnosis);
				}
			});
			
			frm.refresh_field('patient_medical_history');
			frm.dirty();
			
			// Update button states
			btn.removeClass('btn-outline-primary').addClass('btn-primary');
			row.find('.btn-self-no').removeClass('btn-secondary').addClass('btn-outline-secondary');
			
			frappe.show_alert({
				message: __('Added {0} to Medical History', [diagnosis]),
				indicator: 'green'
			});
			
			d.hide();
		}
	});
	
	d.show();
}

function add_to_medical_history(frm, diagnosis, category, years, treatment) {
	let row = frm.add_child('patient_medical_history', {
		diagnosis_category: category,
		diagnosis: diagnosis,
		when: years || '',
		undergoing_treatment: treatment ? 1 : 0
	});
	
	// Fetch diagnosis name
	frappe.db.get_value('Diagnosis', diagnosis, 'diagnosis', function(r) {
		if (r) {
			frappe.model.set_value(row.doctype, row.name, 'diagnosis_name', r.diagnosis);
		}
	});
	
	frm.refresh_field('patient_medical_history');
	frm.dirty();
	
	frappe.show_alert({
		message: __('Added {0} to Medical History', [diagnosis]),
		indicator: 'green'
	});
}

function remove_from_medical_history(frm, diagnosis) {
	let rows = frm.doc.patient_medical_history || [];
	let idx_to_remove = rows.findIndex(d => d.diagnosis === diagnosis);
	
	if (idx_to_remove > -1) {
		frm.doc.patient_medical_history.splice(idx_to_remove, 1);
		frm.refresh_field('patient_medical_history');
		frm.dirty();
		
		frappe.show_alert({
			message: __('Removed {0} from Medical History', [diagnosis]),
			indicator: 'orange'
		});
	}
}

function update_existing_medical_history_row(frm, diagnosis, field, value) {
	// Check in Medical History (Self)
	let rows = frm.doc.patient_medical_history || [];
	let existing_row = rows.find(d => d.diagnosis === diagnosis);
	
	if (existing_row) {
		frappe.model.set_value(existing_row.doctype, existing_row.name, field, value);
		frm.refresh_field('patient_medical_history');
		frm.dirty();
		return true;
	}
	
	// Check in Family Medical History
	let family_rows = frm.doc.patient_family_medical_history || [];
	let existing_family_row = family_rows.find(d => d.diagnosis === diagnosis);
	
	if (existing_family_row) {
		frappe.model.set_value(existing_family_row.doctype, existing_family_row.name, field, value);
		frm.refresh_field('patient_family_medical_history');
		frm.dirty();
		return true;
	}
	
	return false;
}

function show_family_relation_dialog(frm, diagnosis, category, btn, row) {
	let d = new frappe.ui.Dialog({
		title: __('Add to Family Medical History'),
		fields: [
			{
				fieldname: 'diagnosis_display',
				fieldtype: 'Data',
				label: __('Diagnosis'),
				default: diagnosis,
				read_only: 1
			},
			{
				fieldname: 'relation',
				fieldtype: 'Link',
				label: __('Relation'),
				options: 'Relation Type',
				reqd: 1,
				description: __('Select the family member relation (e.g., Father, Mother, etc.)')
			},
			{
				fieldname: 'when',
				fieldtype: 'Data',
				label: __('Since When'),
				description: __('Enter year (YYYY), month-year (MM/YYYY or M/YYYY). Year must be <= current year'),
				onchange: function() {
					validate_when_field_in_dialog(d, 'when');
				}
			},
			{
				fieldname: 'undergoing_treatment',
				fieldtype: 'Check',
				label: __('Ongoing Treatment'),
				default: 0
			},
			{
				fieldname: 'is_hereditary',
				fieldtype: 'Check',
				label: __('Is Hereditary'),
				description: __('Check if this condition has hereditary/genetic factors'),
				default: 0
			}
		],
		primary_action_label: __('Add'),
		primary_action: function(values) {
			// Validate when field before adding
			if (values.when && !validate_when_format(values.when)) {
				return false;
			}
			
			// Add to Family Medical History
			let new_row = frm.add_child('patient_family_medical_history', {
				diagnosis_category: category,
				diagnosis: diagnosis,
				relation: values.relation,
				when: values.when || '',
				undergoing_treatment: values.undergoing_treatment ? 1 : 0,
				is_hereditary: values.is_hereditary ? 1 : 0
			});
			
			// Fetch diagnosis name
			frappe.db.get_value('Diagnosis', diagnosis, 'diagnosis', function(r) {
				if (r) {
					frappe.model.set_value(new_row.doctype, new_row.name, 'diagnosis_name', r.diagnosis);
				}
			});
			
			frm.refresh_field('patient_family_medical_history');
			frm.dirty();
			
			// Update button states
			btn.removeClass('btn-outline-success').addClass('btn-success');
			row.find('.btn-family-no').removeClass('btn-secondary').addClass('btn-outline-secondary');
			
			frappe.show_alert({
				message: __('Added {0} to Family Medical History ({1})', [diagnosis, values.relation]),
				indicator: 'green'
			});
			
			d.hide();
		}
	});
	
	d.show();
}

function remove_from_family_history(frm, diagnosis) {
	let rows = frm.doc.patient_family_medical_history || [];
	let idx_to_remove = rows.findIndex(d => d.diagnosis === diagnosis);
	
	if (idx_to_remove > -1) {
		frm.doc.patient_family_medical_history.splice(idx_to_remove, 1);
		frm.refresh_field('patient_family_medical_history');
		frm.dirty();
		
		frappe.show_alert({
			message: __('Removed {0} from Family Medical History', [diagnosis]),
			indicator: 'orange'
		});
	}
}

// ============================================
// STYLES
// ============================================

function add_custom_styles() {
	if ($('#patient-custom-styles').length) return;
	
	$('head').append(`
		<style id="patient-custom-styles">
			/* Diagnosis Quick Panel Styles */
			.diagnosis-quick-panel {
				background: var(--card-bg);
				border: 1px solid var(--border-color);
				border-radius: 8px;
				margin: 15px 0;
				padding: 15px;
				box-shadow: 0 2px 8px rgba(0,0,0,0.05);
			}
			
			.diagnosis-quick-panel .panel-header {
				border-bottom: 1px solid var(--border-color);
				padding-bottom: 10px;
				margin-bottom: 15px;
			}
			
			.diagnosis-quick-panel .panel-header h5 {
				margin: 0 0 5px 0;
				color: var(--heading-color);
				font-weight: 600;
			}
			
			.diagnosis-quick-panel .panel-header p {
				margin: 0;
				font-size: 12px;
			}
			
			.diagnosis-quick-panel .diagnosis-table {
				overflow-x: auto;
			}
			
			.diagnosis-quick-panel table {
				margin-bottom: 0;
				font-size: 13px;
			}
			
			.diagnosis-quick-panel table th {
				background: var(--bg-color);
				font-weight: 600;
				font-size: 11px;
				text-transform: uppercase;
				letter-spacing: 0.5px;
				padding: 10px 8px;
				border-bottom: 2px solid var(--border-color);
			}
			
			.diagnosis-quick-panel table td {
				vertical-align: middle;
				padding: 8px;
			}
			
			.diagnosis-quick-panel .diagnosis-name {
				font-weight: 500;
				color: var(--text-color);
			}
			
			.diagnosis-quick-panel .diagnosis-row:hover {
				background: var(--bg-light-gray);
			}
			
			.diagnosis-quick-panel .btn-group .btn {
				padding: 4px 8px;
				font-size: 11px;
				font-weight: 600;
			}
			
			.diagnosis-quick-panel .years-input {
				text-align: center;
				font-size: 12px;
			}
			
			.diagnosis-quick-panel .panel-footer {
				border-top: 1px solid var(--border-color);
				padding-top: 10px;
				margin-top: 15px;
			}
			
			/* Insurance Card Preview Styles */
			.insurance-card-preview {
				display: inline-block;
				margin: 5px;
				border-radius: 8px;
				padding: 8px;
				cursor: pointer;
				transition: all 0.3s ease;
				position: relative;
				overflow: hidden;
			}
			.insurance-card-preview::before {
				content: '';
				position: absolute;
				top: 0;
				left: 0;
				right: 0;
				bottom: 0;
				background: linear-gradient(135deg, rgba(36,144,239,0.1) 0%, rgba(118,75,162,0.1) 100%);
				opacity: 0;
				transition: opacity 0.3s ease;
				pointer-events: none;
			}
			.insurance-card-preview:hover::before {
				opacity: 1;
			}
			.insurance-card-preview:hover {
				border-color: #2490ef !important;
				box-shadow: 0 8px 25px rgba(36,144,239,0.4);
				transform: translateY(-5px) scale(1.03);
			}
			.insurance-card-preview img {
				display: block;
				max-width: 300px;
				max-height: 200px;
				width: auto;
				height: auto;
				border-radius: 6px;
				position: relative;
				z-index: 1;
			}
			.insurance-card-label {
				font-size: 11px;
				margin-top: 8px;
				text-align: center;
				font-weight: 600;
				text-transform: uppercase;
				letter-spacing: 0.5px;
				position: relative;
				z-index: 1;
			}
			.insurance-card-modal {
				display: none;
				position: fixed;
				z-index: 9999;
				left: 0;
				top: 0;
				width: 100%;
				height: 100%;
				background-color: rgba(0,0,0,0.9);
				cursor: zoom-out;
			}
			.insurance-card-modal img {
				position: absolute;
				top: 50%;
				left: 50%;
				transform: translate(-50%, -50%);
				max-width: 90%;
				max-height: 90%;
				border-radius: 8px;
				box-shadow: 0 4px 20px rgba(0,0,0,0.5);
			}
			.insurance-card-modal .close-modal {
				position: absolute;
				top: 20px;
				right: 40px;
				color: #fff;
				font-size: 40px;
				font-weight: bold;
				cursor: pointer;
			}
			.insurance-card-modal .modal-caption {
				position: absolute;
				bottom: 20px;
				left: 50%;
				transform: translateX(-50%);
				color: #fff;
				font-size: 16px;
				background: rgba(0,0,0,0.7);
				padding: 10px 20px;
				border-radius: 4px;
			}
		</style>
	`);
}

// ============================================
// INSURANCE SUMMARY
// ============================================

function render_insurance_summary(frm) {
	let insurance_html = '<div style="margin-top: 15px;">';
	
	frm.doc.patient_insurance.forEach((insurance, idx) => {
		const isDarkTheme = document.body.classList.contains('dark') || 
							document.documentElement.getAttribute('data-theme') === 'dark';
		
		const cardBg = isDarkTheme ? 'rgba(30, 30, 30, 0.8)' : '#fff';
		const cardBorder = isDarkTheme ? 'rgba(255, 255, 255, 0.1)' : '#d1d8dd';
		const textColor = isDarkTheme ? '#e0e0e0' : '#333';
		const labelColor = isDarkTheme ? '#b0b0b0' : '#6c757d';
		
		insurance_html += `
			<div style="
				border: 1px solid ${cardBorder}; 
				border-radius: 12px; 
				padding: 20px; 
				margin-bottom: 15px; 
				background: ${cardBg};
				backdrop-filter: blur(10px);
				box-shadow: 0 4px 15px rgba(0,0,0,${isDarkTheme ? '0.5' : '0.1'});
				transition: all 0.3s ease;
			">
				<div style="display: flex; justify-content: space-between; align-items: start; gap: 20px;">
					<div style="flex: 1; min-width: 0;">
						<h4 style="margin: 0 0 15px 0; color: #2490ef; font-size: 18px; font-weight: 600;">
							📋 ${insurance.insurance_company || 'Insurance Company'}
						</h4>
						<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; color: ${textColor};">
							<div style="padding: 8px; background: ${isDarkTheme ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)'}; border-radius: 6px;">
								<span style="color: ${labelColor}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">Member Number</span><br>
								<strong style="font-size: 14px;">${insurance.member_number || 'N/A'}</strong>
							</div>
							<div style="padding: 8px; background: ${isDarkTheme ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)'}; border-radius: 6px;">
								<span style="color: ${labelColor}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">Status</span><br>
								<span class="indicator ${insurance.status === 'Active' ? 'green' : 'orange'}">
									${insurance.status || 'Pending'}
								</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		`;
	});
	
	insurance_html += '</div>';
	
	if (frm.fields_dict.primary_insurance_html) {
		frm.fields_dict.primary_insurance_html.$wrapper.html(insurance_html);
	}
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function set_who_field_query(frm, fieldname) {
	if (!frm.fields_dict[fieldname] || !frm.fields_dict[fieldname].grid.get_field('who')) {
		return;
	}
	frm.fields_dict[fieldname].grid.get_field('who').get_query = function(doc) {
		let patient_list = [doc.name];
		if (doc.patient_relation) {
			doc.patient_relation.forEach(function(rel) {
				if (rel.patient) {
					patient_list.push(rel.patient);
				}
			});
		}
		return {
			filters: [['Patient', 'name', 'in', patient_list]]
		};
	};
}

let create_medical_record = function (frm) {
	frappe.route_options = {
		'patient': frm.doc.name,
		'status': 'Open',
		'reference_doctype': 'Patient Medical Record',
		'reference_owner': frm.doc.owner
	};
	frappe.new_doc('Patient Medical Record');
};

let get_age = function (birth) {
	let birth_moment = moment(birth);
	let current_moment = moment(Date());
	let diff = moment.duration(current_moment.diff(birth_moment));
	return `${diff.years()} ${__('Year(s)')} ${diff.months()} ${__('Month(s)')} ${diff.days()} ${__('Day(s)')}`
};

let create_vital_signs = function (frm) {
	if (!frm.doc.name) {
		frappe.throw(__('Please save the patient first'));
	}
	frappe.route_options = {
		'patient': frm.doc.name,
	};
	frappe.new_doc('Vital Signs');
};

let create_encounter = function (frm) {
	if (!frm.doc.name) {
		frappe.throw(__('Please save the patient first'));
	}
	frappe.route_options = {
		'patient': frm.doc.name,
	};
	frappe.new_doc('Patient Encounter');
};

let invoice_registration = function (frm) {
	frappe.call({
		doc: frm.doc,
		method: 'invoice_patient_registration',
		callback: function(data) {
			if (!data.exc) {
				if (data.message.invoice) {
					frappe.set_route('Form', 'Sales Invoice', data.message.invoice);
				}
				cur_frm.reload_doc();
			}
		}
	});
};

// Insurance Card Preview Handler for Child Table
frappe.ui.form.on('Patient Insurance', {
	form_render: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		setTimeout(() => {
			show_insurance_card_in_dialog(row, cdn);
		}, 500);
	},
	
	card_front_photo: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		setTimeout(() => {
			show_insurance_card_in_dialog(row, cdn);
		}, 300);
	},
	
	card_back_photo: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		setTimeout(() => {
			show_insurance_card_in_dialog(row, cdn);
		}, 300);
	}
});

function show_insurance_card_in_dialog(row, cdn) {
	if (!cur_dialog) return;
	
	const fields = ['card_front_photo', 'card_back_photo'];
	
	fields.forEach(fieldname => {
		const image_url = row[fieldname];
		if (!image_url) return;
		
		const label = fieldname === 'card_front_photo' ? 'Front Card' : 'Back Card';
		const field_wrapper = cur_dialog.fields_dict[fieldname]?.$wrapper;
		
		if (!field_wrapper) return;
		
		field_wrapper.find('.insurance-card-inline-preview').remove();
		
		const preview_html = `
			<div class="insurance-card-inline-preview" style="
				margin-bottom: 15px;
				padding: 12px;
				background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
				border-radius: 12px;
				box-shadow: 0 4px 15px rgba(0,0,0,0.2);
			">
				<div style="
					background: white;
					border-radius: 8px;
					padding: 12px;
					box-shadow: 0 2px 8px rgba(0,0,0,0.1);
				">
					<div style="
						text-align: center;
						font-weight: 600;
						color: #667eea;
						margin-bottom: 10px;
						font-size: 13px;
						text-transform: uppercase;
						letter-spacing: 1px;
					">
						📄 ${label}
					</div>
					<div style="text-align: center;">
						<img src="${image_url}" 
							 style="
								max-width: 100%;
								max-height: 350px;
								width: auto;
								height: auto;
								border-radius: 6px;
								border: 3px solid #f0f0f0;
								cursor: zoom-in;
								transition: all 0.3s ease;
								display: inline-block;
							"
							 onclick="show_card_fullscreen('${image_url}', '${label}')" />
					</div>
				</div>
			</div>
		`;
		
		const control_wrapper = field_wrapper.find('.control-input-wrapper');
		if (control_wrapper.length) {
			control_wrapper.before(preview_html);
		} else {
			field_wrapper.find('.frappe-control').prepend(preview_html);
		}
	});
}

window.show_card_fullscreen = function(image_url, label) {
	frappe.msgprint({
		title: `Insurance Card - ${label}`,
		message: `
			<div style="text-align: center; padding: 20px;">
				<div style="
					background: white;
					display: inline-block;
					padding: 15px;
					border-radius: 12px;
					box-shadow: 0 8px 30px rgba(0,0,0,0.15);
				">
					<img src="${image_url}" 
						 style="max-width: 80vw; max-height: 70vh; border-radius: 8px; display: block;" />
				</div>
			</div>
		`,
		wide: true
	});
};

function setup_insurance_card_previews(frm) {
	if (frm.fields_dict.patient_insurance) {
		frm.fields_dict.patient_insurance.grid.wrapper.on('click', '.grid-row', function() {
			setTimeout(() => {
				if (cur_dialog) {
					const row_index = $(this).attr('data-idx');
					const row = frm.fields_dict.patient_insurance.grid.grid_rows[row_index - 1];
					if (row && row.doc) {
						show_insurance_card_in_dialog(row.doc, row.doc.name);
					}
				}
			}, 600);
		});
	}
}

// Allergen Category Filtering
frappe.ui.form.on('Patient Allergy', {
	allergen_category: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		
		// Check if allergen exists and validate against new category
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
		
		// Always refresh allergen field when category changes to apply new filter
		// This ensures dropdown shows only allergens from selected category
		setTimeout(function() {
			if (frm.fields_dict.patient_allergy && frm.fields_dict.patient_allergy.grid) {
				const grid_row = frm.fields_dict.patient_allergy.grid.grid_rows_by_docname[cdn];
				if (grid_row) {
					// Refresh the field in grid form (when editing in popup)
					if (grid_row.grid_form) {
						grid_row.grid_form.refresh_field('allergen');
					}
					// Also refresh in inline grid
					grid_row.refresh_field('allergen');
				}
			}
		}, 100);
	},
	
	allergen: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		
		// When allergen is selected, auto-fill category from backend (only if category is empty)
		if (row.allergen && !row.allergen_category) {
			frappe.db.get_value('Allergen', row.allergen, 'allergen_category')
				.then(r => {
					if (r && r.message && r.message.allergen_category) {
						frappe.model.set_value(cdt, cdn, 'allergen_category', r.message.allergen_category);
					}
				})
				.catch(err => {
					console.error('Error fetching allergen category:', err);
				});
		}
	}
	
});

// Patient Alcohol History - Computation Logic
frappe.ui.form.on('Patient Alcohol History', {
	quantity: function(frm, cdt, cdn) {
		compute_alcohol_years(frm, cdt, cdn);
	},
	years_of_use: function(frm, cdt, cdn) {
		compute_alcohol_years(frm, cdt, cdn);
	},
	frequency: function(frm, cdt, cdn) {
		compute_alcohol_years(frm, cdt, cdn);
	}
});

function compute_alcohol_years(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	
	if (row.quantity && row.years_of_use) {
		// Convert quantity to daily based on frequency
		let daily_quantity = get_daily_quantity(row.quantity, row.frequency);
		
		// Alcohol Years = Daily Quantity × Years of Use
		const alcohol_years = daily_quantity * row.years_of_use;
		frappe.model.set_value(cdt, cdn, 'alcohol_years', alcohol_years.toFixed(2));
	} else {
		frappe.model.set_value(cdt, cdn, 'alcohol_years', 0);
	}
}

// Smoking Tobacco History - Age Computation and Pack Years
frappe.ui.form.on('Patient Smoking Tobacco History', {
	started_at_age: function(frm, cdt, cdn) {
		compute_used_years_smoking(frm, cdt, cdn);
	},
	discontinued_at_age: function(frm, cdt, cdn) {
		compute_used_years_smoking(frm, cdt, cdn);
	},
	quantity: function(frm, cdt, cdn) {
		compute_pack_years(frm, cdt, cdn);
	},
	frequency: function(frm, cdt, cdn) {
		compute_pack_years(frm, cdt, cdn);
	},
	type: function(frm, cdt, cdn) {
		compute_pack_years(frm, cdt, cdn);
		toggle_pack_years_visibility(frm, cdt, cdn);
	},
	form_render: function(frm, cdt, cdn) {
		toggle_pack_years_visibility(frm, cdt, cdn);
	}
});

// Smokeless Tobacco History - Age Computation
frappe.ui.form.on('Patient Smokeless Tobacco History', {
	started_at_age: function(frm, cdt, cdn) {
		compute_used_years(frm, cdt, cdn);
	},
	discontinued_at_age: function(frm, cdt, cdn) {
		compute_used_years(frm, cdt, cdn);
	}
});

// Substance Abuse History - Age Computation
frappe.ui.form.on('Patient Substance Abuse History', {
	started_at_age: function(frm, cdt, cdn) {
		compute_used_years(frm, cdt, cdn);
	},
	discontinued_at_age: function(frm, cdt, cdn) {
		compute_used_years(frm, cdt, cdn);
	}
});

// Helper function to convert quantity to daily based on frequency
function get_daily_quantity(quantity, frequency) {
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

function compute_used_years(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	
	if (row.started_at_age) {
		let years_used = 0;
		
		if (row.discontinued_at_age) {
			// Discontinued - calculate difference + 1
			years_used = row.discontinued_at_age - row.started_at_age + 1;
		} else {
			// Ongoing - calculate from current age using patient DOB
			if (frm.doc.dob) {
				const current_age = Math.floor(frappe.datetime.get_diff(frappe.datetime.nowdate(), frm.doc.dob) / 365.25);
				years_used = current_age - row.started_at_age + 1;
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

// Smoking-specific computation (includes pack years)
function compute_used_years_smoking(frm, cdt, cdn) {
	compute_used_years(frm, cdt, cdn);
	compute_pack_years(frm, cdt, cdn);
}

// Pack Years computation for Smoking Tobacco
function compute_pack_years(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	
	// Reset both fields first
	frappe.model.set_value(cdt, cdn, 'pack_years', 0);
	frappe.model.set_value(cdt, cdn, 'bidi_pack_years', 0);
	
	if (!row.quantity || !row.used_for_years || row.used_for_years <= 0) {
		return;
	}
	
	// Convert quantity to daily
	let daily_quantity = get_daily_quantity(row.quantity, row.frequency);
	
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

// Toggle Pack Years field visibility based on type
function toggle_pack_years_visibility(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	
	if (!row) return;
	
	// Get the grid row
	const grid_row = frm.fields_dict.patient_smoking_tobacco_history?.grid.grid_rows_by_docname[cdn];
	
	if (grid_row) {
		if (row.type) {
			const type_lower = row.type.toLowerCase();
			
			if (type_lower.includes('cigarette')) {
				// Show pack_years, hide bidi_pack_years
				grid_row.toggle_display('pack_years', true);
				grid_row.toggle_display('bidi_pack_years', false);
			} else if (type_lower.includes('bidi')) {
				// Show bidi_pack_years, hide pack_years
				grid_row.toggle_display('pack_years', false);
				grid_row.toggle_display('bidi_pack_years', true);
			} else {
				// Hide both if type is something else
				grid_row.toggle_display('pack_years', false);
				grid_row.toggle_display('bidi_pack_years', false);
			}
		} else {
			// No type selected, hide both
			grid_row.toggle_display('pack_years', false);
			grid_row.toggle_display('bidi_pack_years', false);
		}
	}
}

// Validate 'when' field format for Medical History
function validate_when_field(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	
	if (!row.when) return true;
	
	return validate_when_format(row.when, function(valid) {
		if (!valid) {
			frappe.model.set_value(cdt, cdn, 'when', '');
		}
	});
}

// Common validation function for 'when' field format
function validate_when_format(value, callback) {
	if (!value) return true;
	
	const trimmed_value = value.trim();
	const current_year = new Date().getFullYear();
	
	// Pattern 1: YYYY (4 digits)
	const pattern_year = /^(\d{4})$/;
	// Pattern 2: MM/YYYY or M/YYYY
	const pattern_month_year = /^(\d{1,2})\/(\d{4})$/;
	
	const match_year = trimmed_value.match(pattern_year);
	const match_month_year = trimmed_value.match(pattern_month_year);
	
	if (match_year) {
		const year = parseInt(match_year[1]);
		if (year > current_year) {
			frappe.msgprint(__("Year in 'Since When' field cannot be greater than current year ({0})", [current_year]));
			if (callback) callback(false);
			return false;
		}
	} else if (match_month_year) {
		const month = parseInt(match_month_year[1]);
		const year = parseInt(match_month_year[2]);
		
		if (month < 1 || month > 12) {
			frappe.msgprint(__("Month in 'Since When' field must be between 1 and 12"));
			if (callback) callback(false);
			return false;
		}
		
		if (year > current_year) {
			frappe.msgprint(__("Year in 'Since When' field cannot be greater than current year ({0})", [current_year]));
			if (callback) callback(false);
			return false;
		}
	} else {
		frappe.msgprint(__("'Since When' field must be in format YYYY (e.g., 2023) or MM/YYYY (e.g., 01/2023, 1/2023)"));
		if (callback) callback(false);
		return false;
	}
	
	if (callback) callback(true);
	return true;
}

// Validate 'when' field in dialog
function validate_when_field_in_dialog(dialog, fieldname) {
	const value = dialog.get_value(fieldname);
	if (value) {
		validate_when_format(value, function(valid) {
			if (!valid) {
				dialog.set_value(fieldname, '');
			}
		});
	}
}
