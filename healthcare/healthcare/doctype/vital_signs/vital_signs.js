// Copyright (c) 2016, ESS LLP and contributors
frappe.ui.form.on('Vital Signs', {
	refresh: function(frm) {
		render_table(frm);
		render_vital_signs_table(frm);
		render_tobacco_health_table(frm);
		render_diagnostic_previews(frm);
		render_ecog_status(frm);
		toggle_skinfold_fields(frm);
	},
	onload: function(frm) {
		render_table(frm);
		render_vital_signs_table(frm);
		render_tobacco_health_table(frm);
		render_diagnostic_previews(frm);
		render_ecog_status(frm);
		toggle_skinfold_fields(frm);
	},
	patient: function(frm) {
		if (frm.doc.patient) {
			frappe.call({
				method: 'frappe.client.get',
				args: { doctype: 'Patient', name: frm.doc.patient },
				callback: function(r) {
					if (r.message) {
						// Set age from DOB or default to 30
						if (r.message.dob) {
							let b = new Date(r.message.dob), t = new Date();
							let age = t.getFullYear() - b.getFullYear();
							if (t.getMonth() < b.getMonth() || (t.getMonth() === b.getMonth() && t.getDate() < b.getDate())) age--;
							frm.set_value('patient_age', age);
						} else {
							frm.set_value('patient_age', 30); // Default age if DOB not available
						}
						// Set sex
						if (r.message.sex) {
							frm.set_value('patient_sex', r.message.sex);
						}
						// Trigger calculations after values are set
						frm.refresh_fields();
						toggle_skinfold_fields(frm);
						setTimeout(() => { 
							calc_all(frm); 
							render_table(frm); 
						}, 300);
					}
				}
			});
		}
	},
	height: function(frm) { calc_all(frm); render_table(frm); },
	height_unit: function(frm) { calc_all(frm); render_table(frm); },
	weight: function(frm) { calc_all(frm); render_table(frm); },
	weight_unit: function(frm) { calc_all(frm); render_table(frm); },
	waist_circumference: function(frm) { calc_all(frm); render_table(frm); },
	waist_unit: function(frm) { calc_all(frm); render_table(frm); },
	hip_circumference: function(frm) { calc_all(frm); render_table(frm); },
	hip_unit: function(frm) { calc_all(frm); render_table(frm); },
	skinfold_chest: function(frm) { calc_all(frm); render_table(frm); },
	skinfold_abdomen: function(frm) { calc_all(frm); render_table(frm); },
	skinfold_thigh: function(frm) { calc_all(frm); render_table(frm); },
	skinfold_triceps: function(frm) { calc_all(frm); render_table(frm); },
	skinfold_suprailiac: function(frm) { calc_all(frm); render_table(frm); },
	muac: function(frm) { calc_all(frm); render_table(frm); },
	bp_systolic: function(frm) {
		if (frm.doc.bp_systolic && frm.doc.bp_diastolic)
			frm.set_value('bp', frm.doc.bp_systolic + '/' + frm.doc.bp_diastolic + ' mmHg');
		render_vital_signs_table(frm);
	},
	bp_diastolic: function(frm) {
		if (frm.doc.bp_systolic && frm.doc.bp_diastolic)
			frm.set_value('bp', frm.doc.bp_systolic + '/' + frm.doc.bp_diastolic + ' mmHg');
		render_vital_signs_table(frm);
	},
	temperature: function(frm) { render_vital_signs_table(frm); },
	pulse: function(frm) { render_vital_signs_table(frm); },
	spo2: function(frm) { render_vital_signs_table(frm); },
	respiratory_rate: function(frm) { render_vital_signs_table(frm); },
	blood_sugar: function(frm) { render_vital_signs_table(frm); },
	// Spirometer
	spirometer_fvc: function(frm) { calc_spirometer(frm); render_tobacco_health_table(frm); },
	spirometer_fev1: function(frm) { calc_spirometer(frm); render_tobacco_health_table(frm); },
	spirometer_pef: function(frm) { render_tobacco_health_table(frm); },
	// Diagnostic tests
	ecg_done: function(frm) { render_tobacco_health_table(frm); },
	ecg_attachment: function(frm) { render_diagnostic_previews(frm); },
	echo_done: function(frm) { render_tobacco_health_table(frm); },
	echo_attachment: function(frm) { render_diagnostic_previews(frm); },
	dexascan_done: function(frm) { render_tobacco_health_table(frm); },
	dexascan_attachment: function(frm) { render_diagnostic_previews(frm); },
	// Oral exam
	mouth_opening_fingers: function(frm) { render_tobacco_health_table(frm); },
	mouth_opening_mm: function(frm) { render_tobacco_health_table(frm); },
	// Peak flow
	peak_flow_current: function(frm) { calc_peak_flow(frm); render_tobacco_health_table(frm); },
	peak_flow_personal_best: function(frm) { calc_peak_flow(frm); render_tobacco_health_table(frm); },
	// Breath & CO Monitor
	breath_holding_time: function(frm) { render_tobacco_health_table(frm); },
	co_reading: function(frm) { render_tobacco_health_table(frm); },
	cohb_percentage: function(frm) { render_tobacco_health_table(frm); },
	urinal_nicotine: function(frm) { render_tobacco_health_table(frm); },
	// Audiometry & Optical
	left_ear_abnormality: function(frm) { render_tobacco_health_table(frm); },
	right_ear_abnormality: function(frm) { render_tobacco_health_table(frm); },
	left_eye_pupil_dilation: function(frm) { render_tobacco_health_table(frm); },
	left_eye_opacity: function(frm) { render_tobacco_health_table(frm); },
	left_eye_sightedness: function(frm) { render_tobacco_health_table(frm); },
	right_eye_pupil_dilation: function(frm) { render_tobacco_health_table(frm); },
	right_eye_opacity: function(frm) { render_tobacco_health_table(frm); },
	right_eye_sightedness: function(frm) { render_tobacco_health_table(frm); },
	// ECOG
	ecog_score: function(frm) { render_ecog_status(frm); }
});

function to_cm(v, u) { return !v ? 0 : u === 'inch' ? v * 2.54 : u === 'feet' ? v * 30.48 : v; }
function to_kg(v, u) { return !v ? 0 : u === 'lbs' ? v * 0.453592 : v; }
function get_sex(frm) {
	if (!frm.doc.patient_sex) return null;
	let s = frm.doc.patient_sex.toLowerCase();
	return s.includes('female') ? 'F' : s.includes('male') ? 'M' : null;
}

function toggle_skinfold_fields(frm) {
	let sex = get_sex(frm);
	// Male: Chest, Abdomen, Thigh
	// Female: Triceps, Suprailiac, Thigh
	
	if (sex === 'F') {
		// Female: Hide Chest, Abdomen. Show Triceps, Suprailiac, Thigh
		frm.toggle_display('skinfold_chest', false);
		frm.toggle_display('skinfold_abdomen', false);
		frm.toggle_display('skinfold_triceps', true);
		frm.toggle_display('skinfold_suprailiac', true);
		frm.toggle_display('skinfold_thigh', true);
	} else if (sex === 'M') {
		// Male: Show Chest, Abdomen, Thigh. Hide Triceps, Suprailiac
		frm.toggle_display('skinfold_chest', true);
		frm.toggle_display('skinfold_abdomen', true);
		frm.toggle_display('skinfold_triceps', false);
		frm.toggle_display('skinfold_suprailiac', false);
		frm.toggle_display('skinfold_thigh', true);
	} else {
		// No sex selected: Show all
		frm.toggle_display('skinfold_chest', true);
		frm.toggle_display('skinfold_abdomen', true);
		frm.toggle_display('skinfold_triceps', true);
		frm.toggle_display('skinfold_suprailiac', true);
		frm.toggle_display('skinfold_thigh', true);
	}
}

function calc_all(frm) {
	let h = to_cm(frm.doc.height, frm.doc.height_unit);
	let w = to_kg(frm.doc.weight, frm.doc.weight_unit);
	let waist = to_cm(frm.doc.waist_circumference, frm.doc.waist_unit);
	let hip = to_cm(frm.doc.hip_circumference, frm.doc.hip_unit);
	let hm = h / 100, age = frm.doc.patient_age || 30, sex = get_sex(frm) || 'M';

	// BMI - works without age/sex
	if (hm > 0 && w > 0) {
		frm.doc.bmi = (w / (hm * hm)).toFixed(2);
	}
	
	// WHR - works without age/sex
	if (waist > 0 && hip > 0) {
		frm.doc.whr = (waist / hip).toFixed(2);
	}
	
	// Body Fat % using BMI formula (works with BMI + age)
	if (frm.doc.bmi && age) {
		let sf = sex === 'M' ? 1 : 0;
		frm.doc.body_fat_percentage = Math.max(0, (1.20 * frm.doc.bmi) + (0.23 * age) - (10.8 * sf) - 5.4).toFixed(2);
	}
	
	// Lean Body Mass (Boer) - needs height, weight, sex
	if (h > 0 && w > 0) {
		frm.doc.lean_body_mass = Math.max(0, sex === 'M' ? 
			(0.407 * w) + (0.267 * h) - 19.2 : 
			(0.252 * w) + (0.473 * h) - 48.3).toFixed(2);
	}
	
	// Muscle Mass (Lee) - needs all params
	if (hm > 0 && w > 0 && age) {
		let sf = sex === 'M' ? 1 : 0;
		frm.doc.muscle_mass = Math.max(0, (0.244 * w) + (7.8 * hm) + (6.6 * sf) - (0.098 * age) - 4.5).toFixed(2);
	}
	
	// Bone Mass (Hume)
	if (w > 0) {
		frm.doc.bone_mass = ((sex === 'M' ? 0.10 : 0.086) * w).toFixed(2);
	}
	
	// Bone Mineral Content (Hologic)
	if (h > 0 && w > 0) {
		let sf = sex === 'M' ? 2.07 : 0;
		frm.doc.bone_mineral_content = Math.max(0, (0.0029 * (h * h) / 100) + (0.0056 * w) + sf - 3.11).toFixed(2);
		// Simple estimate if formula gives 0
		if (parseFloat(frm.doc.bone_mineral_content) <= 0) {
			frm.doc.bone_mineral_content = (0.0056 * h).toFixed(2); // Ruff et al method
		}
	}
	
	// Total Body Water (Watson)
	if (h > 0 && w > 0 && age) {
		let tbw_l = sex === 'M' ? 
			2.447 - (0.09516 * age) + (0.1074 * h) + (0.3362 * w) : 
			-2.097 + (0.1069 * h) + (0.2466 * w);
		frm.doc.total_body_water = ((tbw_l / w) * 100).toFixed(2);
	}
	
	// Protein %
	if (frm.doc.lean_body_mass && w > 0) {
		frm.doc.protein_percentage = ((frm.doc.lean_body_mass * 0.20 / w) * 100).toFixed(2);
	}
	
	// BMR (Mifflin-St Jeor)
	if (h > 0 && w > 0 && age) {
		frm.doc.bmr = Math.round(sex === 'M' ? 
			(10 * w) + (6.25 * h) - (5 * age) + 5 : 
			(10 * w) + (6.25 * h) - (5 * age) - 161);
	}
	
	// Metabolic Age - Compare BMR with average for age
	if (frm.doc.bmr && age) {
		// Average BMR decreases with age: ~1750 at 20, decreasing ~100 per decade
		let avg_bmr = sex === 'M' ? (1800 - ((age - 20) * 10)) : (1500 - ((age - 20) * 8));
		avg_bmr = Math.max(avg_bmr, 1000); // Minimum baseline
		// Metabolic Age = Actual Age adjusted by BMR ratio
		let bmr_ratio = frm.doc.bmr / avg_bmr;
		frm.doc.metabolic_age = Math.max(15, Math.min(80, age / bmr_ratio)).toFixed(1);
	}
	
	// Subcutaneous Fat (Jackson-Pollock)
	if (age) {
		let sum = 0, bd = 0;
		if (sex === 'M' && frm.doc.skinfold_chest && frm.doc.skinfold_abdomen && frm.doc.skinfold_thigh) {
			sum = parseFloat(frm.doc.skinfold_chest) + parseFloat(frm.doc.skinfold_abdomen) + parseFloat(frm.doc.skinfold_thigh);
			bd = 1.10938 - (0.0008267 * sum) + (0.0000016 * sum * sum) - (0.0002574 * age);
		} else if (sex === 'F' && frm.doc.skinfold_triceps && frm.doc.skinfold_suprailiac && frm.doc.skinfold_thigh) {
			sum = parseFloat(frm.doc.skinfold_triceps) + parseFloat(frm.doc.skinfold_suprailiac) + parseFloat(frm.doc.skinfold_thigh);
			bd = 1.0994921 - (0.0009929 * sum) + (0.0000023 * sum * sum) - (0.0001392 * age);
		}
		if (bd > 0) {
			frm.doc.subcutaneous_fat = Math.max(0, ((495 / bd) - 450) * 0.85).toFixed(2);
		}
	}
}

function render_table(frm) {
	let sex = get_sex(frm);
	let age = frm.doc.patient_age;
	
	let data = [
		{ p: 'BMI', u: 'kg/m²', e: frm.doc.bmi, m: 'bmi_manual', n: '18.5-24.9', f: 'Weight/(Height²)', show: true },
		{ p: 'Waist to Hip Ratio', u: 'ratio', e: frm.doc.whr, m: 'whr_manual', n: sex === 'M' ? '<0.95' : '<0.80', f: 'Waist/Hip', show: true },
		{ p: 'Body Fat %', u: '%', e: frm.doc.body_fat_percentage, m: 'bfp_manual', n: sex === 'M' ? '10-20' : '18-28', f: '1.20×BMI+0.23×Age-10.8×Sex-5.4', show: true },
		{ p: 'Lean Body Mass', u: 'kg', e: frm.doc.lean_body_mass, m: 'lbm_manual', n: 'Varies', f: 'Boer Formula', show: true },
		{ p: 'Skeletal Muscle Mass', u: 'kg', e: frm.doc.muscle_mass, m: 'muscle_mass_manual', n: sex === 'M' ? '33-40%' : '24-30%', f: 'Lee Formula', show: true },
		{ p: 'Bone Mass', u: 'kg', e: frm.doc.bone_mass, m: 'bone_mass_manual', n: sex === 'M' ? '2.5-3.5' : '1.8-2.5', f: 'Hume Formula', show: true },
		{ p: 'Bone Mineral Content', u: 'kg', e: frm.doc.bone_mineral_content, m: 'bmc_manual', n: 'Varies', f: 'Hologic Formula', show: true },
		{ p: 'Total Body Water', u: '%', e: frm.doc.total_body_water, m: 'tbw_manual', n: sex === 'M' ? '50-65' : '45-60', f: 'Watson Formula', show: true },
		{ p: 'Protein %', u: '%', e: frm.doc.protein_percentage, m: 'protein_manual', n: '16-20', f: 'LBM×0.20/Weight×100', show: true },
		{ p: 'BMR', u: 'kcal/day', e: frm.doc.bmr, m: 'bmr_manual', n: 'Varies', f: 'Mifflin-St Jeor', show: true },
		{ p: 'Metabolic Age', u: 'years', e: frm.doc.metabolic_age, m: 'metabolic_age_manual', n: '=Actual Age', f: '70-(BMR/(24×LBM))×100', show: true },
		{ p: 'Subcutaneous Fat', u: '%', e: frm.doc.subcutaneous_fat, m: 'subcutaneous_fat_manual', n: sex === 'M' ? '8-15' : '18-25', f: 'Jackson-Pollock 3-site', show: true }
	];

	// MUAC status
	if (frm.doc.muac) {
		let mc = frm.doc.muac / 10;
		let st = mc >= 13.5 ? 'Adequate' : mc >= 12.5 ? 'Mild' : mc >= 11.5 ? 'Moderate' : 'Severe';
		data.push({ p: 'MUAC Status', u: 'cm', e: mc.toFixed(1), m: null, n: '>13.5', f: 'Mid-Upper Arm', show: true, st: st });
	}
	
	// Bilateral Pitting Edema
	if (frm.doc.bilateral_pitting_edema === 'Yes') {
		data.push({ p: 'Bilateral Pitting Edema', u: '', e: 'Present', m: null, n: 'No', f: '-', show: true, st: 'Severe' });
	}

	let html = `<style>
		.av-tbl { width:100%; border-collapse:collapse; font-size:12px; }
		.av-tbl th, .av-tbl td { padding:6px 8px; border:1px solid var(--border-color); text-align:left; }
		.av-tbl th { background:var(--subtle-fg); color:var(--text-muted); font-weight:600; font-size:11px; text-transform:uppercase; }
		.av-tbl td { background:var(--card-bg); color:var(--text-color); }
		.av-tbl tr:hover td { background:var(--bg-color); }
		.av-inp { width:60px; padding:2px 4px; border:1px solid var(--border-color); border-radius:3px; font-size:11px; background:var(--control-bg); color:var(--text-color); }
		.av-st { padding:2px 6px; border-radius:3px; font-size:10px; font-weight:600; }
		.av-g { background:#28a745; color:#fff; }
		.av-r { background:#dc3545; color:#fff; }
		.av-y { background:#6c757d; color:#fff; }
		.av-o { background:#fd7e14; color:#fff; }
		.av-help { cursor:pointer; color:var(--primary); font-size:10px; }
		.av-note { width:100%; margin-top:8px; padding:4px 8px; border:1px solid var(--border-color); border-radius:3px; font-size:11px; background:var(--control-bg); color:var(--text-color); }
	</style>
	<table class="av-tbl">
		<thead><tr>
			<th style="width:22%">Parameter</th>
			<th style="width:8%">Unit</th>
			<th style="width:12%">Estimated</th>
			<th style="width:12%">Manual</th>
			<th style="width:12%">Normal (${sex === 'M' ? 'Male' : sex === 'F' ? 'Female' : '-'})</th>
			<th style="width:14%">Status</th>
			<th style="width:20%">Formula <a class="av-help" href="https://docs.google.com/spreadsheets/d/1RwUyadin-T0vOEDTJdeplhww8-Njscl8hgujP2W-1Qk/edit" target="_blank">📊</a></th>
		</tr></thead><tbody>`;

	data.forEach(r => {
		if (!r.show) return;
		let est = r.e || '-';
		let status = r.st ? get_status_badge(r.st) : get_status(r.p, r.e, r.n, sex, frm);
		let manual_inp = r.m ? `<input type="number" class="av-inp" data-field="${r.m}" value="${frm.doc[r.m] || ''}" step="0.01">` : '-';
		html += `<tr>
			<td><strong>${r.p}</strong></td>
			<td>${r.u}</td>
			<td>${est}</td>
			<td>${manual_inp}</td>
			<td><small>${r.n}</small></td>
			<td>${status}</td>
			<td><small>${r.f}</small></td>
		</tr>`;
	});

	html += `</tbody></table>
	<textarea class="av-note" data-field="anthropometric_note" placeholder="Notes...">${frm.doc.anthropometric_note || ''}</textarea>`;

	if (frm.fields_dict.computed_values_html) {
		frm.fields_dict.computed_values_html.$wrapper.html(html);
		frm.fields_dict.computed_values_html.$wrapper.find('.av-inp, .av-note').on('change', function() {
			let field = $(this).data('field');
			let val = $(this).val();
			frm.set_value(field, val || null);
		});
	}
}

function get_status_badge(label) {
	let cls = 'av-y';
	if (label === 'Normal' || label === 'Adequate') cls = 'av-g';
	else if (label === 'High' || label === 'Severe' || label === 'Obese' || label === 'Highly Abnormal') cls = 'av-r';
	else if (label === 'Abnormal' || label === 'Overweight' || label === 'Mild' || label === 'Moderate') cls = 'av-o';
	return `<span class="av-st ${cls}">${label}</span>`;
}

function get_status(param, val, normal, sex, frm) {
	if (!val || val === '-') return '<span class="av-st av-y">-</span>';
	val = parseFloat(val);
	let label = '', cls = 'av-y';

	if (param === 'BMI') {
		if (val < 15) { label = 'Very Severely Underweight'; cls = 'av-r'; }
		else if (val < 16) { label = 'Severely Underweight'; cls = 'av-r'; }
		else if (val < 18.5) { label = 'Underweight'; cls = 'av-o'; }
		else if (val < 25) { label = 'Normal'; cls = 'av-g'; }
		else if (val < 30) { label = 'Overweight'; cls = 'av-o'; }
		else if (val < 35) { label = 'Obese I'; cls = 'av-r'; }
		else if (val < 40) { label = 'Obese II'; cls = 'av-r'; }
		else { label = 'Obese III'; cls = 'av-r'; }
	} else if (param === 'Waist to Hip Ratio') {
		if (sex === 'M') {
			if (val < 0.95) { label = 'Normal'; cls = 'av-g'; }
			else if (val <= 1.0) { label = 'Abnormal'; cls = 'av-o'; }
			else { label = 'Highly Abnormal'; cls = 'av-r'; }
		} else {
			if (val < 0.80) { label = 'Normal'; cls = 'av-g'; }
			else if (val <= 0.85) { label = 'Abnormal'; cls = 'av-o'; }
			else { label = 'Highly Abnormal'; cls = 'av-r'; }
		}
	} else if (param === 'Body Fat %') {
		let lo = sex === 'M' ? 10 : 18, mid = sex === 'M' ? 20 : 28, hi = sex === 'M' ? 25 : 32;
		if (val < lo) { label = 'Low'; cls = 'av-o'; }
		else if (val <= mid) { label = 'Normal'; cls = 'av-g'; }
		else if (val <= hi) { label = 'Abnormal'; cls = 'av-o'; }
		else { label = 'High'; cls = 'av-r'; }
	} else if (param === 'Skeletal Muscle Mass') {
		let lo = sex === 'M' ? 33 : 24;
		let w = frm && frm.doc ? to_kg(frm.doc.weight, frm.doc.weight_unit) : 70;
		let pct = w > 0 ? (val / w) * 100 : 0;
		if (pct >= lo) { label = 'Normal'; cls = 'av-g'; }
		else { label = 'Low (Sarcopenia Risk)'; cls = 'av-o'; }
	} else if (param === 'Bone Mass') {
		let lo = sex === 'M' ? 2.5 : 1.8;
		if (val >= lo) { label = 'Normal'; cls = 'av-g'; }
		else { label = 'Low'; cls = 'av-o'; }
	} else if (param === 'Total Body Water') {
		let lo = sex === 'M' ? 50 : 45, hi = sex === 'M' ? 65 : 60;
		if (val < lo) { label = 'Low'; cls = 'av-o'; }
		else if (val <= hi) { label = 'Normal'; cls = 'av-g'; }
		else { label = 'High'; cls = 'av-o'; }
	} else if (param === 'Protein %') {
		if (val >= 16 && val <= 20) { label = 'Normal'; cls = 'av-g'; }
		else if (val < 16) { label = 'Low'; cls = 'av-o'; }
		else { label = 'High'; cls = 'av-o'; }
	} else if (param === 'Subcutaneous Fat') {
		let hi = sex === 'M' ? 15 : 25;
		if (val <= hi) { label = 'Normal'; cls = 'av-g'; }
		else { label = 'High'; cls = 'av-r'; }
	} else if (param === 'Metabolic Age') {
		let age = frm && frm.doc ? (frm.doc.patient_age || 30) : 30;
		if (val <= age) { label = 'Good'; cls = 'av-g'; }
		else { label = 'Poor Fitness'; cls = 'av-o'; }
	} else if (param === 'Lean Body Mass') {
		// LBM varies - just show calculated
		label = 'Calculated'; cls = 'av-g';
	} else if (param === 'Bone Mineral Content') {
		// BMC varies by height
		label = 'Calculated'; cls = 'av-g';
	} else if (param === 'BMR') {
		// BMR varies by individual
		label = 'Calculated'; cls = 'av-g';
	} else {
		return `<span class="av-st av-y">-</span>`;
	}

	return `<span class="av-st ${cls}">${label}</span>`;
}

function render_vital_signs_table(frm) {
	let data = [];
	
	// Pulse / Heart Rate
	if (frm.doc.pulse) {
		let v = parseFloat(frm.doc.pulse);
		let st = v >= 60 && v <= 100 ? 'Normal' : v < 60 ? 'Low' : 'High';
		let cls = st === 'Normal' ? 'av-g' : 'av-r';
		data.push({ p: 'Pulse (Heart Rate)', u: 'bpm', v: v, n: '60-100', st: st, cls: cls });
	}
	
	// SpO2
	if (frm.doc.spo2) {
		let v = parseFloat(frm.doc.spo2);
		let st = v >= 95 ? 'Normal' : v >= 90 ? 'Low' : 'Critical';
		let cls = st === 'Normal' ? 'av-g' : st === 'Low' ? 'av-o' : 'av-r';
		data.push({ p: 'SpO2', u: '%', v: v, n: '95-100%', st: st, cls: cls });
	}
	
	// Temperature
	if (frm.doc.temperature) {
		let v = parseFloat(frm.doc.temperature);
		let st = v >= 36.1 && v <= 37.2 ? 'Normal' : v > 38.5 ? 'Fever' : v > 37.2 ? 'Elevated' : 'Low';
		let cls = st === 'Normal' ? 'av-g' : st === 'Fever' ? 'av-r' : 'av-o';
		data.push({ p: 'Temperature', u: '°C', v: v, n: '36.1-37.2', st: st, cls: cls });
	}
	
	// Respiratory Rate
	if (frm.doc.respiratory_rate) {
		let v = parseFloat(frm.doc.respiratory_rate);
		let st = v >= 12 && v <= 20 ? 'Normal' : v < 12 ? 'Low' : 'High';
		let cls = st === 'Normal' ? 'av-g' : 'av-o';
		data.push({ p: 'Respiratory Rate', u: '/min', v: v, n: '12-20', st: st, cls: cls });
	}
	
	// Blood Pressure
	if (frm.doc.bp_systolic && frm.doc.bp_diastolic) {
		let sys = parseFloat(frm.doc.bp_systolic);
		let dia = parseFloat(frm.doc.bp_diastolic);
		let st = 'Normal';
		let cls = 'av-g';
		if (sys >= 180 || dia >= 120) { st = 'Crisis'; cls = 'av-r'; }
		else if (sys >= 140 || dia >= 90) { st = 'Stage 2'; cls = 'av-r'; }
		else if (sys >= 130 || dia >= 80) { st = 'Stage 1'; cls = 'av-o'; }
		else if (sys >= 120 && sys < 130 && dia < 80) { st = 'Elevated'; cls = 'av-o'; }
		data.push({ p: 'Blood Pressure', u: 'mmHg', v: sys + '/' + dia, n: '<120/<80', st: st, cls: cls });
	}
	
	// Blood Sugar
	if (frm.doc.blood_sugar) {
		let v = parseFloat(frm.doc.blood_sugar);
		let st = v >= 80 && v <= 110 ? 'Normal' : v > 200 ? 'Diabetic' : v > 110 ? 'Prediabetic' : 'Low';
		let cls = st === 'Normal' ? 'av-g' : st === 'Diabetic' ? 'av-r' : 'av-o';
		data.push({ p: 'Blood Sugar', u: 'mg/dl', v: v, n: '80-110', st: st, cls: cls });
	}
	
	if (data.length === 0) {
		if (frm.fields_dict.vital_signs_html) {
			frm.fields_dict.vital_signs_html.$wrapper.html('<p style="color:var(--text-muted);font-size:12px;">Enter vital signs below to see summary</p>');
		}
		return;
	}
	
	let html = `<style>
		.vs-tbl { width:100%; border-collapse:collapse; font-size:12px; margin-bottom:10px; }
		.vs-tbl th, .vs-tbl td { padding:6px 10px; border:1px solid var(--border-color); text-align:left; }
		.vs-tbl th { background:var(--subtle-fg); color:var(--text-muted); font-weight:600; font-size:11px; text-transform:uppercase; }
		.vs-tbl td { background:var(--card-bg); color:var(--text-color); }
		.vs-tbl tr:hover td { background:var(--bg-color); }
	</style>
	<table class="vs-tbl">
		<thead><tr>
			<th style="width:30%">Parameter</th>
			<th style="width:15%">Value</th>
			<th style="width:10%">Unit</th>
			<th style="width:20%">Normal Range</th>
			<th style="width:25%">Status</th>
		</tr></thead><tbody>`;
	
	data.forEach(r => {
		html += `<tr>
			<td><strong>${r.p}</strong></td>
			<td>${r.v}</td>
			<td>${r.u}</td>
			<td><small>${r.n}</small></td>
			<td><span class="av-st ${r.cls}">${r.st}</span></td>
		</tr>`;
	});
	
	html += `</tbody></table>`;
	
	if (frm.fields_dict.vital_signs_html) {
		frm.fields_dict.vital_signs_html.$wrapper.html(html);
	}
}

// Spirometer calculations
function calc_spirometer(frm) {
	if (frm.doc.spirometer_fvc && frm.doc.spirometer_fev1) {
		let ratio = (frm.doc.spirometer_fev1 / frm.doc.spirometer_fvc) * 100;
		frm.set_value('spirometer_fev1_fvc', ratio.toFixed(1));
	}
}

// Peak Flow calculations
function calc_peak_flow(frm) {
	if (frm.doc.peak_flow_current && frm.doc.peak_flow_personal_best) {
		let pct = (frm.doc.peak_flow_current / frm.doc.peak_flow_personal_best) * 100;
		frm.set_value('peak_flow_percentage', pct.toFixed(1));
		
		let zone = 'Green Zone';
		if (pct < 50) zone = 'Red Zone';
		else if (pct < 80) zone = 'Yellow Zone';
		frm.set_value('peak_flow_status', zone);
	}
}

// Render Tobacco Health Summary Table
function render_tobacco_health_table(frm) {
	let data = [];
	
	// Spirometer - FEV1/FVC Ratio
	if (frm.doc.spirometer_fev1_fvc) {
		let v = parseFloat(frm.doc.spirometer_fev1_fvc);
		let st = v >= 70 ? 'Normal' : v >= 60 ? 'Mild Obstruction' : v >= 50 ? 'Moderate' : 'Severe';
		let cls = st === 'Normal' ? 'av-g' : st === 'Mild Obstruction' ? 'av-o' : 'av-r';
		data.push({ p: 'FEV1/FVC Ratio', u: '%', v: v.toFixed(1), n: '>70%', st: st, cls: cls, cat: 'Spirometer' });
	}
	
	// Spirometer - FVC
	if (frm.doc.spirometer_fvc) {
		data.push({ p: 'FVC', u: 'L', v: frm.doc.spirometer_fvc, n: 'Varies', st: 'Recorded', cls: 'av-g', cat: 'Spirometer' });
	}
	
	// Spirometer - FEV1
	if (frm.doc.spirometer_fev1) {
		data.push({ p: 'FEV1', u: 'L', v: frm.doc.spirometer_fev1, n: 'Varies', st: 'Recorded', cls: 'av-g', cat: 'Spirometer' });
	}
	
	// Spirometer - PEF
	if (frm.doc.spirometer_pef) {
		data.push({ p: 'PEF (Spirometer)', u: 'L/min', v: frm.doc.spirometer_pef, n: 'Varies', st: 'Recorded', cls: 'av-g', cat: 'Spirometer' });
	}
	
	// ECG
	if (frm.doc.ecg_done === 'Yes') {
		let st = frm.doc.ecg_attachment ? 'Done ✓' : 'Pending Upload';
		let cls = frm.doc.ecg_attachment ? 'av-g' : 'av-o';
		data.push({ p: 'ECG', u: '-', v: 'Yes', n: '-', st: st, cls: cls, cat: 'Diagnostic' });
	}
	
	// ECHO
	if (frm.doc.echo_done === 'Yes') {
		let st = frm.doc.echo_attachment ? 'Done ✓' : 'Pending Upload';
		let cls = frm.doc.echo_attachment ? 'av-g' : 'av-o';
		data.push({ p: 'ECHO', u: '-', v: 'Yes', n: '-', st: st, cls: cls, cat: 'Diagnostic' });
	}
	
	// DExascan
	if (frm.doc.dexascan_done === 'Yes') {
		let st = frm.doc.dexascan_attachment ? 'Done ✓' : 'Pending Upload';
		let cls = frm.doc.dexascan_attachment ? 'av-g' : 'av-o';
		data.push({ p: 'DExascan', u: '-', v: 'Yes', n: '-', st: st, cls: cls, cat: 'Diagnostic' });
	}
	
	// Mouth Opening
	if (frm.doc.mouth_opening_mm || frm.doc.mouth_opening_fingers) {
		let v = frm.doc.mouth_opening_mm ? frm.doc.mouth_opening_mm + ' mm' : '';
		if (frm.doc.mouth_opening_fingers) {
			v = v ? v + ' (' + frm.doc.mouth_opening_fingers + ')' : frm.doc.mouth_opening_fingers;
		}
		let st = 'Normal';
		let cls = 'av-g';
		if (frm.doc.mouth_opening_mm) {
			let mm = parseFloat(frm.doc.mouth_opening_mm);
			if (mm < 20) { st = 'Severe Restriction'; cls = 'av-r'; }
			else if (mm < 30) { st = 'Moderate Restriction'; cls = 'av-o'; }
			else if (mm < 35) { st = 'Mild Restriction'; cls = 'av-o'; }
		}
		data.push({ p: 'Mouth Opening', u: 'mm/fingers', v: v, n: '>35mm / 3+ fingers', st: st, cls: cls, cat: 'Oral' });
	}
	
	// Peak Flow
	if (frm.doc.peak_flow_current) {
		let v = frm.doc.peak_flow_current;
		let st = 'Recorded';
		let cls = 'av-g';
		if (frm.doc.peak_flow_percentage) {
			let pct = parseFloat(frm.doc.peak_flow_percentage);
			if (pct >= 80) { st = 'Green Zone'; cls = 'av-g'; }
			else if (pct >= 50) { st = 'Yellow Zone'; cls = 'av-o'; }
			else { st = 'Red Zone'; cls = 'av-r'; }
			v = v + ' (' + pct.toFixed(0) + '%)';
		}
		data.push({ p: 'Peak Flow', u: 'L/min', v: v, n: '>80% of best', st: st, cls: cls, cat: 'Peak Flow' });
	}
	
	// Personal Best
	if (frm.doc.peak_flow_personal_best) {
		data.push({ p: 'Personal Best', u: 'L/min', v: frm.doc.peak_flow_personal_best, n: 'Reference', st: 'Stored', cls: 'av-g', cat: 'Peak Flow' });
	}
	
	// Breath Holding Time
	if (frm.doc.breath_holding_time) {
		let v = parseFloat(frm.doc.breath_holding_time);
		let st = v > 40 ? 'Normal' : v >= 30 ? 'Mild Respiratory Disorder' : 'Severe Respiratory Disorder';
		let cls = st === 'Normal' ? 'av-g' : st.includes('Mild') ? 'av-o' : 'av-r';
		data.push({ p: 'Breath Holding Time', u: 'sec', v: v, n: '>40s', st: st, cls: cls, cat: 'Breath & CO Tests' });
	}
	
	// CO Reading
	if (frm.doc.co_reading) {
		let v = parseFloat(frm.doc.co_reading);
		let st = 'Non Smoker';
		let cls = 'av-g';
		if (v > 30) { st = 'Very Heavy Smoker'; cls = 'av-r'; }
		else if (v >= 25) { st = 'Heavy Smoker'; cls = 'av-r'; }
		else if (v >= 10) { st = 'Regular Smoker'; cls = 'av-o'; }
		else if (v >= 7) { st = 'Light Smoker'; cls = 'av-o'; }
		else if (v > 6) { st = 'Light Smoker'; cls = 'av-o'; }
		data.push({ p: 'CO Reading', u: 'ppm', v: v, n: '0-6 ppm', st: st, cls: cls, cat: 'Breath & CO Tests' });
	}
	
	// COHb Percentage
	if (frm.doc.cohb_percentage) {
		let v = parseFloat(frm.doc.cohb_percentage);
		let st = 'Non Smoker';
		let cls = 'av-g';
		if (v > 3) { st = 'Very Heavy Smoker'; cls = 'av-r'; }
		else if (v >= 2) { st = 'Heavy Smoker'; cls = 'av-r'; }
		else if (v >= 1) { st = 'Regular Smoker'; cls = 'av-o'; }
		else if (v >= 0.01) { st = 'Light Smoker'; cls = 'av-o'; }
		data.push({ p: '% Carboxyhaemoglobin', u: '%COHb', v: v, n: '<1%', st: st, cls: cls, cat: 'Breath & CO Tests' });
	}
	
	// Urinal Nicotine
	if (frm.doc.urinal_nicotine) {
		let v = parseFloat(frm.doc.urinal_nicotine);
		let st = 'Non Smoker';
		let cls = 'av-g';
		if (v > 500) { st = 'Heavy Smoker'; cls = 'av-r'; }
		else if (v >= 100) { st = 'Light/Passive Smoker'; cls = 'av-o'; }
		data.push({ p: 'Urinal Nicotine', u: 'ng/ml', v: v, n: '<100', st: st, cls: cls, cat: 'Breath & CO Tests' });
	}
	
	// Audiometry - Left Ear
	if (frm.doc.left_ear_abnormality === 'Yes') {
		data.push({ p: 'Left Ear Abnormality', u: '-', v: 'Yes', n: 'No', st: 'Abnormal', cls: 'av-r', cat: 'Audiometry & Optical' });
	}
	
	// Audiometry - Right Ear
	if (frm.doc.right_ear_abnormality === 'Yes') {
		data.push({ p: 'Right Ear Abnormality', u: '-', v: 'Yes', n: 'No', st: 'Abnormal', cls: 'av-r', cat: 'Audiometry & Optical' });
	}
	
	// Left Eye
	let leftEyeIssues = [];
	if (frm.doc.left_eye_pupil_dilation === 'Yes') leftEyeIssues.push('Pupil Dilation');
	if (frm.doc.left_eye_opacity === 'Yes') leftEyeIssues.push('Opacity');
	if (frm.doc.left_eye_sightedness && frm.doc.left_eye_sightedness !== 'Normal') leftEyeIssues.push(frm.doc.left_eye_sightedness + ' Sighted');
	if (leftEyeIssues.length > 0) {
		data.push({ p: 'Left Eye', u: '-', v: leftEyeIssues.join(', '), n: 'Normal', st: 'Abnormal', cls: 'av-o', cat: 'Audiometry & Optical' });
	}
	
	// Right Eye
	let rightEyeIssues = [];
	if (frm.doc.right_eye_pupil_dilation === 'Yes') rightEyeIssues.push('Pupil Dilation');
	if (frm.doc.right_eye_opacity === 'Yes') rightEyeIssues.push('Opacity');
	if (frm.doc.right_eye_sightedness && frm.doc.right_eye_sightedness !== 'Normal') rightEyeIssues.push(frm.doc.right_eye_sightedness + ' Sighted');
	if (rightEyeIssues.length > 0) {
		data.push({ p: 'Right Eye', u: '-', v: rightEyeIssues.join(', '), n: 'Normal', st: 'Abnormal', cls: 'av-o', cat: 'Audiometry & Optical' });
	}
	
	if (data.length === 0) {
		if (frm.fields_dict.tobacco_health_html) {
			frm.fields_dict.tobacco_health_html.$wrapper.html('<p style="color:var(--text-muted);font-size:12px;">Enter tobacco health checkup data below to see summary</p>');
		}
		return;
	}
	
	let html = `<style>
		.th-tbl { width:100%; border-collapse:collapse; font-size:12px; margin-bottom:10px; }
		.th-tbl th, .th-tbl td { padding:6px 10px; border:1px solid var(--border-color); text-align:left; }
		.th-tbl th { background:var(--subtle-fg); color:var(--text-muted); font-weight:600; font-size:11px; text-transform:uppercase; }
		.th-tbl td { background:var(--card-bg); color:var(--text-color); }
		.th-tbl tr:hover td { background:var(--bg-color); }
		.th-cat { font-size:10px; color:var(--text-muted); text-transform:uppercase; }
	</style>
	<table class="th-tbl">
		<thead><tr>
			<th style="width:25%">Parameter</th>
			<th style="width:20%">Value</th>
			<th style="width:12%">Unit</th>
			<th style="width:18%">Normal</th>
			<th style="width:25%">Status</th>
		</tr></thead><tbody>`;
	
	let lastCat = '';
	data.forEach(r => {
		if (r.cat !== lastCat) {
			html += `<tr><td colspan="5" style="background:var(--bg-color);padding:4px 10px;"><span class="th-cat">${r.cat}</span></td></tr>`;
			lastCat = r.cat;
		}
		html += `<tr>
			<td><strong>${r.p}</strong></td>
			<td>${r.v}</td>
			<td>${r.u}</td>
			<td><small>${r.n}</small></td>
			<td><span class="av-st ${r.cls}">${r.st}</span></td>
		</tr>`;
	});
	
	html += `</tbody></table>`;
	
	if (frm.fields_dict.tobacco_health_html) {
		frm.fields_dict.tobacco_health_html.$wrapper.html(html);
	}
}

// Render ECOG Performance Status
function render_ecog_status(frm) {
	if (!frm.fields_dict.ecog_status_html) return;
	
	const ecogData = [
		{ score: 0, status: 'Asymptomatic', desc: 'Fully active, able to carry on all pre-disease activities without restriction', cls: 'av-g' },
		{ score: 1, status: 'Symptomatic but ambulatory', desc: 'Restricted in physically strenuous activity but ambulatory and able to carry out light work', cls: 'av-g' },
		{ score: 2, status: 'Symptomatic, <50% in bed', desc: 'Ambulatory and capable of all self-care but unable to carry out any work activities; up and about >50% of waking hours', cls: 'av-o' },
		{ score: 3, status: 'Symptomatic, >50% in bed', desc: 'Capable of only limited self-care; confined to bed or chair >50% of waking hours', cls: 'av-o' },
		{ score: 4, status: 'Bedbound', desc: 'Completely disabled; cannot carry on any self-care; totally confined to bed or chair', cls: 'av-r' },
		{ score: 5, status: 'Death', desc: 'Dead', cls: 'av-r' }
	];
	
	let html = `<style>
		.ecog-tbl { width:100%; border-collapse:collapse; font-size:12px; margin-top:10px; }
		.ecog-tbl th, .ecog-tbl td { padding:8px 10px; border:1px solid var(--border-color); text-align:left; }
		.ecog-tbl th { background:var(--subtle-fg); color:var(--text-muted); font-weight:600; font-size:11px; text-transform:uppercase; }
		.ecog-tbl td { background:var(--card-bg); color:var(--text-color); }
		.ecog-tbl tr.ecog-active td { background:var(--yellow-highlight); font-weight:600; }
		.ecog-tbl tr:hover td { background:var(--bg-color); }
	</style>
	<table class="ecog-tbl">
		<thead><tr>
			<th style="width:10%">Score</th>
			<th style="width:25%">Status</th>
			<th style="width:50%">Description</th>
			<th style="width:15%">Indicator</th>
		</tr></thead><tbody>`;
	
	let currentScore = frm.doc.ecog_score;
	ecogData.forEach(e => {
		let isActive = currentScore !== null && currentScore !== undefined && parseInt(currentScore) === e.score;
		html += `<tr class="${isActive ? 'ecog-active' : ''}">
			<td><strong>${e.score}</strong></td>
			<td>${e.status}</td>
			<td><small>${e.desc}</small></td>
			<td>${isActive ? `<span class="av-st ${e.cls}">${e.status}</span>` : ''}</td>
		</tr>`;
	});
	
	html += `</tbody></table>`;
	
	if (currentScore !== null && currentScore !== undefined && currentScore >= 0 && currentScore <= 5) {
		let selected = ecogData[currentScore];
		html = `<div style="padding:10px;background:var(--bg-color);border-radius:4px;margin-bottom:10px;">
			<strong>Current Score: ${currentScore}</strong> - <span class="av-st ${selected.cls}">${selected.status}</span>
			<p style="margin:5px 0 0;font-size:12px;color:var(--text-muted);">${selected.desc}</p>
		</div>` + html;
	}
	
	frm.fields_dict.ecog_status_html.$wrapper.html(html);
}

// Render diagnostic image previews
function render_diagnostic_previews(frm) {
	// ECG Preview
	if (frm.fields_dict.ecg_preview_html) {
		if (frm.doc.ecg_attachment) {
			frm.fields_dict.ecg_preview_html.$wrapper.html(`
				<div style="margin:5px 0;">
					<a href="${frm.doc.ecg_attachment}" target="_blank">
						<img src="${frm.doc.ecg_attachment}" style="max-width:100%;max-height:200px;border:1px solid var(--border-color);border-radius:4px;cursor:pointer;" title="Click to view full size">
					</a>
				</div>
			`);
		} else {
			frm.fields_dict.ecg_preview_html.$wrapper.html('');
		}
	}
	
	// ECHO Preview
	if (frm.fields_dict.echo_preview_html) {
		if (frm.doc.echo_attachment) {
			frm.fields_dict.echo_preview_html.$wrapper.html(`
				<div style="margin:5px 0;">
					<a href="${frm.doc.echo_attachment}" target="_blank">
						<img src="${frm.doc.echo_attachment}" style="max-width:100%;max-height:200px;border:1px solid var(--border-color);border-radius:4px;cursor:pointer;" title="Click to view full size">
					</a>
				</div>
			`);
		} else {
			frm.fields_dict.echo_preview_html.$wrapper.html('');
		}
	}
	
	// DExascan Preview
	if (frm.fields_dict.dexascan_preview_html) {
		if (frm.doc.dexascan_attachment) {
			frm.fields_dict.dexascan_preview_html.$wrapper.html(`
				<div style="margin:5px 0;">
					<a href="${frm.doc.dexascan_attachment}" target="_blank">
						<img src="${frm.doc.dexascan_attachment}" style="max-width:100%;max-height:200px;border:1px solid var(--border-color);border-radius:4px;cursor:pointer;" title="Click to view full size">
					</a>
				</div>
			`);
		} else {
			frm.fields_dict.dexascan_preview_html.$wrapper.html('');
		}
	}
}
