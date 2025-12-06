// Copyright (c) 2016, ESS LLP and contributors
frappe.ui.form.on('Vital Signs', {
	refresh: function(frm) {
		render_table(frm);
		render_vital_signs_table(frm);
		toggle_skinfold_fields(frm);
	},
	onload: function(frm) {
		render_table(frm);
		render_vital_signs_table(frm);
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
	blood_sugar: function(frm) { render_vital_signs_table(frm); }
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
	
	// Waist status
	let waist_cm = to_cm(frm.doc.waist_circumference, frm.doc.waist_unit);
	let waist_status = '-';
	if (waist_cm > 0 && sex) {
		if (sex === 'M') {
			waist_status = waist_cm < 94 ? 'Normal' : waist_cm <= 102 ? 'Abnormal' : 'High';
		} else {
			waist_status = waist_cm < 80 ? 'Normal' : waist_cm <= 88 ? 'Abnormal' : 'High';
		}
	}
	
	let data = [
		{ p: 'BMI', u: 'kg/m²', e: frm.doc.bmi, m: 'bmi_manual', n: '18.5-24.9', f: 'Weight/(Height²)', show: true },
		{ p: 'Waist Circumference', u: 'cm', e: waist_cm || '-', m: 'waist_circumference', n: sex === 'M' ? '<94' : '<80', f: 'Measured', show: true, st: waist_status },
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
	} else if (param === 'Waist Circumference') {
		// Already handled via st parameter
		return `<span class="av-st av-y">-</span>`;
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
