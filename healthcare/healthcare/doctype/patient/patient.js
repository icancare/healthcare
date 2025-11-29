// Copyright (c) 2016, ESS LLP and contributors
// For license information, please see license.txt
{% include 'healthcare/regional/india/abdm/js/patient.js' %}

frappe.ui.form.on('Patient', {
	refresh: function (frm) {
		// Setup insurance card preview handlers
		setup_insurance_card_previews(frm);
		// Add custom CSS for card image preview
		if (!$('#insurance-card-preview-css').length) {
			$('head').append(`
				<style id="insurance-card-preview-css">
					.insurance-card-preview {
						display: inline-block;
						margin: 5px;
						border: 2px solid #d1d8dd;
						border-radius: 6px;
						padding: 5px;
						background: #f5f7fa;
						cursor: pointer;
						transition: all 0.3s;
					}
					.insurance-card-preview:hover {
						border-color: #2490ef;
						box-shadow: 0 2px 8px rgba(36,144,239,0.3);
						transform: scale(1.02);
					}
					.insurance-card-preview img {
						display: block;
						max-width: 300px;
						max-height: 200px;
						width: auto;
						height: auto;
						border-radius: 4px;
					}
					.insurance-card-label {
						font-size: 11px;
						color: #6c757d;
						margin-top: 5px;
						text-align: center;
						font-weight: 600;
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
		
		// Show insurance card summary with image previews
		if (frm.doc.patient_insurance && frm.doc.patient_insurance.length > 0) {
			let insurance_html = '<div style="margin-top: 15px;">';
			
			frm.doc.patient_insurance.forEach((insurance, idx) => {
				insurance_html += `
					<div style="border: 1px solid #d1d8dd; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fff;">
						<div style="display: flex; justify-content: space-between; align-items: start;">
							<div style="flex: 1;">
								<h4 style="margin: 0 0 10px 0; color: #2490ef;">
									${insurance.insurance_company || 'Insurance Company'}
								</h4>
								<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
									<div>
										<strong>Member Number:</strong> ${insurance.member_number || 'N/A'}
									</div>
									<div>
										<strong>Status:</strong> 
										<span class="indicator ${insurance.status === 'Active' ? 'green' : 'orange'}">
											${insurance.status || 'Pending'}
										</span>
									</div>
									${insurance.policy_start_date ? `
										<div><strong>Valid From:</strong> ${frappe.datetime.str_to_user(insurance.policy_start_date)}</div>
									` : ''}
									${insurance.policy_end_date ? `
										<div><strong>Valid Till:</strong> ${frappe.datetime.str_to_user(insurance.policy_end_date)}</div>
									` : ''}
									${insurance.coverage_amount ? `
										<div><strong>Coverage:</strong> ${format_currency(insurance.coverage_amount)}</div>
									` : ''}
									${insurance.verified ? `
										<div><span class="indicator green">✓ Verified</span></div>
									` : ''}
								</div>
							</div>
							<div style="display: flex; gap: 10px;">
								${insurance.card_front_photo ? `
									<div class="insurance-card-preview" data-image="${insurance.card_front_photo}" data-label="Card Front - ${insurance.insurance_company}">
										<img src="${insurance.card_front_photo}" alt="Card Front" />
										<div class="insurance-card-label">📄 Front</div>
									</div>
								` : '<div style="width: 150px; text-align: center; color: #999;">No Front Card</div>'}
								
								${insurance.card_back_photo ? `
									<div class="insurance-card-preview" data-image="${insurance.card_back_photo}" data-label="Card Back - ${insurance.insurance_company}">
										<img src="${insurance.card_back_photo}" alt="Card Back" />
										<div class="insurance-card-label">📄 Back</div>
									</div>
								` : '<div style="width: 150px; text-align: center; color: #999;">No Back Card</div>'}
							</div>
						</div>
					</div>
				`;
			});
			
			insurance_html += '</div>';
			
			// Update Insurance Summary section
			frm.fields_dict.primary_insurance_html.$wrapper.html(insurance_html);
			
			// Add click handlers for image preview modal
			$('.insurance-card-preview').off('click').on('click', function() {
				const imageUrl = $(this).data('image');
				const label = $(this).data('label');
				
				// Create modal if not exists
				if (!$('#insurance-card-modal').length) {
					$('body').append(`
						<div id="insurance-card-modal" class="insurance-card-modal">
							<span class="close-modal">&times;</span>
							<img id="modal-insurance-img" src="" alt="Insurance Card">
							<div class="modal-caption" id="modal-caption"></div>
						</div>
					`);
					
					// Close modal on click
					$('#insurance-card-modal, .close-modal').on('click', function() {
						$('#insurance-card-modal').fadeOut(300);
					});
				}
				
				// Show modal with image
				$('#modal-insurance-img').attr('src', imageUrl);
				$('#modal-caption').text(label);
				$('#insurance-card-modal').fadeIn(300);
			});
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

// Set query for "who" field in Medical History to show related patients
frappe.ui.form.on('Patient Medical History', {
	medical_history_add: function(frm) {
		set_who_field_query(frm, 'medical_history');
	}
});

frappe.ui.form.on('Patient Surgical History', {
	surgical_history_add: function(frm) {
		set_who_field_query(frm, 'surgical_history');
	}
});

// Set query for "who" field in Social History to show related patients
frappe.ui.form.on('Patient Smokeless Tobacco History', {
	patient_smokeless_tobacco_history_add: function(frm) {
		set_who_field_query(frm, 'patient_smokeless_tobacco_history');
	}
});

frappe.ui.form.on('Patient Smoking Tobacco History', {
	patient_smoking_tobacco_history_add: function(frm) {
		set_who_field_query(frm, 'patient_smoking_tobacco_history');
	}
});

frappe.ui.form.on('Patient Substance Abuse History', {
	patient_substance_abuse_history_add: function(frm) {
		set_who_field_query(frm, 'patient_substance_abuse_history');
	}
});

// Extended Social History - Oral Habits
frappe.ui.form.on('Patient Oral Habits History', {
	patient_oral_habits_history_add: function(frm) {
		set_who_field_query(frm, 'patient_oral_habits_history');
	}
});

// Extended Social History - Diet
frappe.ui.form.on('Patient Diet History', {
	patient_diet_history_add: function(frm) {
		set_who_field_query(frm, 'patient_diet_history');
	}
});

// Extended Social History - Occupational Exposure
frappe.ui.form.on('Patient Occupational Exposure History', {
	patient_occupational_exposure_history_add: function(frm) {
		set_who_field_query(frm, 'patient_occupational_exposure_history');
	}
});

// Extended Social History - Environmental Factors
frappe.ui.form.on('Patient Environmental Factors History', {
	patient_environmental_factors_history_add: function(frm) {
		set_who_field_query(frm, 'patient_environmental_factors_history');
	}
});

function set_who_field_query(frm, fieldname) {
	frm.fields_dict[fieldname].grid.get_field('who').get_query = function(doc) {
		// Get list of related patients from patient_relation
		let patient_list = [doc.name]; // Include self
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
	
	// Find the dialog fields for card photos
	const fields = ['card_front_photo', 'card_back_photo'];
	
	fields.forEach(fieldname => {
		const image_url = row[fieldname];
		if (!image_url) return;
		
		const label = fieldname === 'card_front_photo' ? 'Front Card' : 'Back Card';
		const field_wrapper = cur_dialog.fields_dict[fieldname]?.$wrapper;
		
		if (!field_wrapper) return;
		
		// Remove old preview
		field_wrapper.find('.insurance-card-inline-preview').remove();
		
		// Create beautiful card preview box
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
							 onmouseover="this.style.transform='scale(1.02)'; this.style.boxShadow='0 8px 20px rgba(0,0,0,0.3)';"
							 onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';"
							 onclick="show_card_fullscreen('${image_url}', '${label}')" />
					</div>
					<div style="
						text-align: center;
						margin-top: 10px;
						padding: 8px;
						background: #f8f9fa;
						border-radius: 6px;
					">
						<span style="font-size: 11px; color: #6c757d;">
							🔍 Click image to view full size
						</span>
					</div>
				</div>
			</div>
		`;
		
		// Insert preview BEFORE the control wrapper
		const control_wrapper = field_wrapper.find('.control-input-wrapper');
		if (control_wrapper.length) {
			control_wrapper.before(preview_html);
		} else {
			field_wrapper.find('.frappe-control').prepend(preview_html);
		}
		
		// Style the file path to be less prominent
		field_wrapper.find('.control-value a').css({
			'font-size': '10px',
			'color': '#999',
			'text-decoration': 'none'
		});
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
				<div style="margin-top: 20px;">
					<a href="${image_url}" target="_blank" class="btn btn-primary btn-sm">
						<i class="fa fa-external-link"></i> Open in New Tab
					</a>
				</div>
			</div>
		`,
		wide: true
	});
};

function setup_insurance_card_previews(frm) {
	// Setup grid to show card previews
	if (frm.fields_dict.patient_insurance) {
		frm.fields_dict.patient_insurance.grid.wrapper.on('click', '.grid-row', function() {
			// When row is clicked, wait for dialog to open then show previews
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
