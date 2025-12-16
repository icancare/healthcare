// Copyright (c) 2024, ICanCare and contributors
// For license information, please see license.txt

frappe.ui.form.on("Clinical Examination", {
	refresh(frm) {
		// Render interactive diagram
		if (frm.doc.examination_template) {
			render_interactive_diagram(frm);
		}
		
		// Add print button
		if (!frm.is_new() && frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Print Report"), function() {
				frappe.set_route("print", "Clinical Examination", frm.doc.name);
			});
		}
	},
	
	examination_template(frm) {
		if (frm.doc.examination_template) {
			// Load template configuration
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Clinical Examination Template",
					name: frm.doc.examination_template
				},
				callback: function(r) {
					if (r.message) {
						let template = r.message;
						
						// Set examination type
						frm.set_value("examination_type", template.examination_type);
						
						// Setup special tests if enabled
						if (template.enable_special_tests && template.special_tests) {
							let tests = template.special_tests.split("\n").filter(t => t.trim());
							frm.clear_table("special_tests");
							tests.forEach(test => {
								let row = frm.add_child("special_tests");
								row.test_name = test.trim();
							});
							frm.refresh_field("special_tests");
						}
						
						// Render diagram
						render_interactive_diagram(frm);
					}
				}
			});
		}
	},
	
	patient(frm) {
		if (frm.doc.patient) {
			// Show patient history
			frappe.call({
				method: "healthcare.healthcare.doctype.clinical_examination.clinical_examination.get_clinical_examinations_for_patient",
				args: { patient: frm.doc.patient },
				callback: function(r) {
					if (r.message && r.message.length > 0) {
						let html = '<div class="alert alert-info">';
						html += '<strong>' + __("Previous Examinations:") + '</strong><br>';
						r.message.forEach(exam => {
							html += `<a href="/app/clinical-examination/${exam.name}">${exam.examination_date} - ${exam.examination_type}</a><br>`;
						});
						html += '</div>';
						// Could show this in a field or dialog
					}
				}
			});
		}
	}
});

function render_interactive_diagram(frm) {
	// Get the diagram HTML field wrapper
	let wrapper = frm.fields_dict.diagram_html.$wrapper;
	wrapper.empty();
	
	if (!frm.doc.examination_template) {
		wrapper.html('<p class="text-muted">' + __("Select an examination template to load the diagram") + '</p>');
		return;
	}
	
	// Fetch template to get diagram type
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Clinical Examination Template",
			filters: { name: frm.doc.examination_template },
			fieldname: ["diagram_type", "enable_diagram_marking"]
		},
		callback: function(r) {
			if (r.message && r.message.enable_diagram_marking) {
				let diagram_type = r.message.diagram_type;
				render_svg_diagram(frm, wrapper, diagram_type);
			} else {
				wrapper.html('<p class="text-muted">' + __("Diagram marking is not enabled for this template") + '</p>');
			}
		}
	});
}

function render_svg_diagram(frm, wrapper, diagram_type) {
	let svg_content = get_svg_for_type(diagram_type);
	
	let html = `
		<div class="clinical-diagram-container" style="background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 10px 0;">
			<div class="row">
				<div class="col-md-8">
					<h5 style="margin-bottom: 15px; color: #333;">
						<i class="fa fa-pencil"></i> ${__("Click on the diagram to mark lesions")}
					</h5>
					<div id="diagram-svg-container" style="position: relative; display: inline-block; cursor: crosshair;">
						${svg_content}
					</div>
				</div>
				<div class="col-md-4">
					<div class="lesion-legend" style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
						<h6 style="margin-bottom: 10px;"><i class="fa fa-list"></i> ${__("Marked Lesions")}</h6>
						<div id="lesion-list"></div>
						<hr>
						<div class="lesion-type-selector" style="margin-top: 10px;">
							<label>${__("Lesion Type")}:</label>
							<select id="current-lesion-type" class="form-control form-control-sm">
								<option value="Ulcer">Ulcer</option>
								<option value="White Patch">White Patch</option>
								<option value="Red Patch">Red Patch</option>
								<option value="Swelling">Swelling</option>
								<option value="Nodule">Nodule</option>
								<option value="Fibrous Band">Fibrous Band</option>
								<option value="Other">Other</option>
							</select>
						</div>
						<button class="btn btn-sm btn-danger mt-3" id="clear-all-lesions" style="width: 100%;">
							<i class="fa fa-trash"></i> ${__("Clear All")}
						</button>
					</div>
				</div>
			</div>
		</div>
	`;
	
	wrapper.html(html);
	
	// Initialize lesion markers from existing data
	let existing_lesions = [];
	try {
		if (frm.doc.lesion_markings_json) {
			existing_lesions = JSON.parse(frm.doc.lesion_markings_json);
		}
	} catch(e) {}
	
	// Setup click handler for SVG
	let svg_container = wrapper.find('#diagram-svg-container');
	let lesion_counter = existing_lesions.length;
	
	// Render existing lesions
	existing_lesions.forEach((lesion, idx) => {
		add_lesion_marker(svg_container, lesion.x, lesion.y, idx + 1, lesion.type);
	});
	update_lesion_list(wrapper, existing_lesions);
	
	svg_container.on('click', function(e) {
		if (frm.doc.docstatus === 1) return; // Don't allow editing submitted docs
		
		let offset = $(this).offset();
		let x = e.pageX - offset.left;
		let y = e.pageY - offset.top;
		
		lesion_counter++;
		let lesion_type = wrapper.find('#current-lesion-type').val();
		
		// Add marker to SVG
		add_lesion_marker(svg_container, x, y, lesion_counter, lesion_type);
		
		// Add to lesions array
		existing_lesions.push({
			number: lesion_counter,
			x: x,
			y: y,
			type: lesion_type,
			region: get_region_at_point(x, y)
		});
		
		// Update JSON field
		frm.set_value('lesion_markings_json', JSON.stringify(existing_lesions));
		
		// Add to child table
		let row = frm.add_child('lesions');
		row.lesion_number = lesion_counter;
		row.x_coordinate = x;
		row.y_coordinate = y;
		row.lesion_type = lesion_type;
		row.diagram_region = get_region_at_point(x, y);
		frm.refresh_field('lesions');
		
		// Update legend
		update_lesion_list(wrapper, existing_lesions);
	});
	
	// Clear all button
	wrapper.find('#clear-all-lesions').on('click', function() {
		if (frm.doc.docstatus === 1) return;
		
		frappe.confirm(__("Are you sure you want to clear all marked lesions?"), function() {
			svg_container.find('.lesion-marker').remove();
			existing_lesions = [];
			lesion_counter = 0;
			frm.set_value('lesion_markings_json', '[]');
			frm.clear_table('lesions');
			frm.refresh_field('lesions');
			update_lesion_list(wrapper, []);
		});
	});
}

function add_lesion_marker(container, x, y, number, type) {
	let color = get_lesion_color(type);
	let marker = $(`
		<div class="lesion-marker" data-number="${number}" style="
			position: absolute;
			left: ${x - 12}px;
			top: ${y - 12}px;
			width: 24px;
			height: 24px;
			background: ${color};
			border: 2px solid #fff;
			border-radius: 50%;
			color: #fff;
			font-size: 11px;
			font-weight: bold;
			display: flex;
			align-items: center;
			justify-content: center;
			box-shadow: 0 2px 4px rgba(0,0,0,0.3);
			cursor: pointer;
			z-index: 100;
		">${number}</div>
	`);
	container.append(marker);
}

function get_lesion_color(type) {
	const colors = {
		'Ulcer': '#e74c3c',
		'White Patch': '#95a5a6',
		'Red Patch': '#c0392b',
		'Swelling': '#3498db',
		'Nodule': '#9b59b6',
		'Fibrous Band': '#f39c12',
		'Other': '#34495e'
	};
	return colors[type] || '#34495e';
}

function update_lesion_list(wrapper, lesions) {
	let list_html = '';
	if (lesions.length === 0) {
		list_html = '<p class="text-muted small">' + __("No lesions marked yet") + '</p>';
	} else {
		lesions.forEach(l => {
			let color = get_lesion_color(l.type);
			list_html += `
				<div class="lesion-item" style="padding: 5px 0; border-bottom: 1px solid #eee;">
					<span style="display: inline-block; width: 20px; height: 20px; background: ${color}; 
						border-radius: 50%; color: #fff; text-align: center; line-height: 20px; 
						font-size: 10px; margin-right: 8px;">${l.number}</span>
					<span style="font-size: 12px;">${l.type}</span>
				</div>
			`;
		});
	}
	wrapper.find('#lesion-list').html(list_html);
}

function get_region_at_point(x, y) {
	// This would be enhanced to detect which SVG region was clicked
	// For now, return a generic region based on coordinates
	return "Region at (" + Math.round(x) + ", " + Math.round(y) + ")";
}

function get_svg_for_type(diagram_type) {
	if (diagram_type === 'Oral Cavity') {
		return get_oral_cavity_svg();
	} else if (diagram_type === 'Face Front') {
		return get_face_front_svg();
	} else if (diagram_type === 'Teeth Chart') {
		return get_teeth_chart_svg();
	}
	
	// Default placeholder
	return `
		<svg width="500" height="400" style="background: #fafafa; border: 1px solid #ddd;">
			<text x="250" y="200" text-anchor="middle" fill="#999">
				${diagram_type || 'Diagram'} - Click to mark lesions
			</text>
		</svg>
	`;
}

function get_oral_cavity_svg() {
	return `
		<svg width="500" height="450" viewBox="0 0 500 450" style="background: #fff;">
			<!-- Outer lips -->
			<ellipse cx="250" cy="225" rx="200" ry="180" fill="#ffcccc" stroke="#cc6666" stroke-width="3"/>
			
			<!-- Inner mouth cavity -->
			<ellipse cx="250" cy="225" rx="160" ry="140" fill="#ff9999" stroke="#cc6666" stroke-width="2"/>
			
			<!-- Tongue -->
			<ellipse cx="250" cy="280" rx="80" ry="60" fill="#ff6666" stroke="#cc3333" stroke-width="2" id="tongue"/>
			<text x="250" y="285" text-anchor="middle" fill="#fff" font-size="12">Tongue</text>
			
			<!-- Upper teeth row -->
			<g id="upper-teeth">
				<rect x="100" y="100" width="20" height="30" fill="#fff" stroke="#999" rx="3"/>
				<rect x="125" y="95" width="20" height="35" fill="#fff" stroke="#999" rx="3"/>
				<rect x="150" y="90" width="22" height="40" fill="#fff" stroke="#999" rx="3"/>
				<rect x="177" y="88" width="22" height="42" fill="#fff" stroke="#999" rx="3"/>
				<rect x="204" y="85" width="20" height="45" fill="#fff" stroke="#999" rx="3"/>
				<rect x="229" y="83" width="22" height="47" fill="#fff" stroke="#999" rx="3"/>
				<rect x="256" y="83" width="22" height="47" fill="#fff" stroke="#999" rx="3"/>
				<rect x="283" y="85" width="20" height="45" fill="#fff" stroke="#999" rx="3"/>
				<rect x="308" y="88" width="22" height="42" fill="#fff" stroke="#999" rx="3"/>
				<rect x="335" y="90" width="22" height="40" fill="#fff" stroke="#999" rx="3"/>
				<rect x="362" y="95" width="20" height="35" fill="#fff" stroke="#999" rx="3"/>
				<rect x="387" y="100" width="20" height="30" fill="#fff" stroke="#999" rx="3"/>
			</g>
			
			<!-- Lower teeth row -->
			<g id="lower-teeth">
				<rect x="100" y="350" width="20" height="30" fill="#fff" stroke="#999" rx="3"/>
				<rect x="125" y="350" width="20" height="35" fill="#fff" stroke="#999" rx="3"/>
				<rect x="150" y="350" width="22" height="38" fill="#fff" stroke="#999" rx="3"/>
				<rect x="177" y="350" width="22" height="40" fill="#fff" stroke="#999" rx="3"/>
				<rect x="204" y="350" width="20" height="42" fill="#fff" stroke="#999" rx="3"/>
				<rect x="229" y="350" width="22" height="44" fill="#fff" stroke="#999" rx="3"/>
				<rect x="256" y="350" width="22" height="44" fill="#fff" stroke="#999" rx="3"/>
				<rect x="283" y="350" width="20" height="42" fill="#fff" stroke="#999" rx="3"/>
				<rect x="308" y="350" width="22" height="40" fill="#fff" stroke="#999" rx="3"/>
				<rect x="335" y="350" width="22" height="38" fill="#fff" stroke="#999" rx="3"/>
				<rect x="362" y="350" width="20" height="35" fill="#fff" stroke="#999" rx="3"/>
				<rect x="387" y="350" width="20" height="30" fill="#fff" stroke="#999" rx="3"/>
			</g>
			
			<!-- Palate -->
			<path d="M 120 150 Q 250 200 380 150" fill="none" stroke="#cc9999" stroke-width="2" stroke-dasharray="5,5"/>
			<text x="250" y="175" text-anchor="middle" fill="#996666" font-size="11">Hard Palate</text>
			
			<!-- Soft palate / uvula -->
			<path d="M 180 160 Q 250 190 320 160" fill="#ffaaaa" stroke="#cc6666" stroke-width="2"/>
			<ellipse cx="250" cy="200" rx="15" ry="25" fill="#ff8888" stroke="#cc6666" stroke-width="2"/>
			<text x="250" y="240" text-anchor="middle" fill="#fff" font-size="10">Uvula</text>
			
			<!-- Left buccal mucosa -->
			<ellipse cx="100" cy="225" rx="30" ry="80" fill="#ffbbbb" stroke="#cc9999" stroke-width="1" id="left-buccal"/>
			<text x="70" y="225" text-anchor="middle" fill="#996666" font-size="9" transform="rotate(-90 70 225)">L Buccal</text>
			
			<!-- Right buccal mucosa -->
			<ellipse cx="400" cy="225" rx="30" ry="80" fill="#ffbbbb" stroke="#cc9999" stroke-width="1" id="right-buccal"/>
			<text x="430" y="225" text-anchor="middle" fill="#996666" font-size="9" transform="rotate(90 430 225)">R Buccal</text>
			
			<!-- Floor of mouth -->
			<ellipse cx="250" cy="340" rx="100" ry="20" fill="#ff8888" stroke="#cc6666" stroke-width="1"/>
			<text x="250" y="345" text-anchor="middle" fill="#fff" font-size="10">Floor of Mouth</text>
			
			<!-- Labels -->
			<text x="250" y="30" text-anchor="middle" fill="#333" font-size="14" font-weight="bold">ORAL CAVITY DIAGRAM</text>
			<text x="250" y="440" text-anchor="middle" fill="#666" font-size="11">Click anywhere to mark lesions</text>
		</svg>
	`;
}

function get_face_front_svg() {
	return `
		<svg width="400" height="500" viewBox="0 0 400 500" style="background: #fff;">
			<!-- Face outline -->
			<ellipse cx="200" cy="200" rx="150" ry="180" fill="#ffe4c4" stroke="#d4a574" stroke-width="2"/>
			
			<!-- Forehead -->
			<path d="M 80 120 Q 200 50 320 120" fill="none" stroke="#d4a574" stroke-width="1" stroke-dasharray="3,3"/>
			<text x="200" y="90" text-anchor="middle" fill="#996633" font-size="10">Forehead</text>
			
			<!-- Left Eye -->
			<ellipse cx="140" cy="170" rx="30" ry="15" fill="#fff" stroke="#333" stroke-width="2"/>
			<circle cx="140" cy="170" r="8" fill="#4a3728"/>
			<text x="140" y="200" text-anchor="middle" fill="#666" font-size="9">L Eye</text>
			
			<!-- Right Eye -->
			<ellipse cx="260" cy="170" rx="30" ry="15" fill="#fff" stroke="#333" stroke-width="2"/>
			<circle cx="260" cy="170" r="8" fill="#4a3728"/>
			<text x="260" y="200" text-anchor="middle" fill="#666" font-size="9">R Eye</text>
			
			<!-- Nose -->
			<path d="M 200 160 L 190 230 Q 200 245 210 230 L 200 160" fill="#f5d5b5" stroke="#d4a574" stroke-width="1"/>
			<text x="200" y="260" text-anchor="middle" fill="#666" font-size="9">Nose</text>
			
			<!-- Left Cheek -->
			<ellipse cx="100" cy="250" rx="40" ry="50" fill="#ffd5c5" stroke="#d4a574" stroke-width="1" stroke-dasharray="3,3"/>
			<text x="100" y="255" text-anchor="middle" fill="#996633" font-size="9">L Cheek</text>
			
			<!-- Right Cheek -->
			<ellipse cx="300" cy="250" rx="40" ry="50" fill="#ffd5c5" stroke="#d4a574" stroke-width="1" stroke-dasharray="3,3"/>
			<text x="300" y="255" text-anchor="middle" fill="#996633" font-size="9">R Cheek</text>
			
			<!-- Mouth/Lips -->
			<ellipse cx="200" cy="310" rx="50" ry="20" fill="#cc6666" stroke="#993333" stroke-width="2"/>
			<text x="200" y="315" text-anchor="middle" fill="#fff" font-size="10">Mouth</text>
			
			<!-- Chin -->
			<ellipse cx="200" cy="360" rx="40" ry="25" fill="#ffe4c4" stroke="#d4a574" stroke-width="1" stroke-dasharray="3,3"/>
			<text x="200" y="365" text-anchor="middle" fill="#996633" font-size="9">Chin</text>
			
			<!-- Neck -->
			<rect x="140" y="380" width="120" height="80" fill="#ffe4c4" stroke="#d4a574" stroke-width="2"/>
			<text x="200" y="420" text-anchor="middle" fill="#996633" font-size="10">Neck</text>
			
			<!-- Left Ear -->
			<ellipse cx="55" cy="190" rx="15" ry="35" fill="#ffe4c4" stroke="#d4a574" stroke-width="2"/>
			<text x="55" y="195" text-anchor="middle" fill="#996633" font-size="8">L Ear</text>
			
			<!-- Right Ear -->
			<ellipse cx="345" cy="190" rx="15" ry="35" fill="#ffe4c4" stroke="#d4a574" stroke-width="2"/>
			<text x="345" y="195" text-anchor="middle" fill="#996633" font-size="8">R Ear</text>
			
			<!-- Title -->
			<text x="200" y="25" text-anchor="middle" fill="#333" font-size="14" font-weight="bold">FACE - FRONT VIEW</text>
			<text x="200" y="485" text-anchor="middle" fill="#666" font-size="11">Click anywhere to mark lesions</text>
		</svg>
	`;
}

function get_teeth_chart_svg() {
	return `
		<svg width="600" height="300" viewBox="0 0 600 300" style="background: #fff;">
			<text x="300" y="25" text-anchor="middle" fill="#333" font-size="14" font-weight="bold">TEETH CHART</text>
			
			<!-- Upper Right -->
			<text x="150" y="60" text-anchor="middle" fill="#666" font-size="11">Upper Right</text>
			<g transform="translate(50, 70)">
				${[18,17,16,15,14,13,12,11].map((n, i) => `
					<g transform="translate(${i * 25}, 0)">
						<rect width="22" height="35" fill="#fff" stroke="#999" rx="3"/>
						<text x="11" y="50" text-anchor="middle" fill="#666" font-size="8">${n}</text>
					</g>
				`).join('')}
			</g>
			
			<!-- Upper Left -->
			<text x="450" y="60" text-anchor="middle" fill="#666" font-size="11">Upper Left</text>
			<g transform="translate(300, 70)">
				${[21,22,23,24,25,26,27,28].map((n, i) => `
					<g transform="translate(${i * 25}, 0)">
						<rect width="22" height="35" fill="#fff" stroke="#999" rx="3"/>
						<text x="11" y="50" text-anchor="middle" fill="#666" font-size="8">${n}</text>
					</g>
				`).join('')}
			</g>
			
			<!-- Lower Right -->
			<text x="150" y="180" text-anchor="middle" fill="#666" font-size="11">Lower Right</text>
			<g transform="translate(50, 190)">
				${[48,47,46,45,44,43,42,41].map((n, i) => `
					<g transform="translate(${i * 25}, 0)">
						<rect width="22" height="35" fill="#fff" stroke="#999" rx="3"/>
						<text x="11" y="50" text-anchor="middle" fill="#666" font-size="8">${n}</text>
					</g>
				`).join('')}
			</g>
			
			<!-- Lower Left -->
			<text x="450" y="180" text-anchor="middle" fill="#666" font-size="11">Lower Left</text>
			<g transform="translate(300, 190)">
				${[31,32,33,34,35,36,37,38].map((n, i) => `
					<g transform="translate(${i * 25}, 0)">
						<rect width="22" height="35" fill="#fff" stroke="#999" rx="3"/>
						<text x="11" y="50" text-anchor="middle" fill="#666" font-size="8">${n}</text>
					</g>
				`).join('')}
			</g>
			
			<!-- Center line -->
			<line x1="300" y1="50" x2="300" y2="250" stroke="#ccc" stroke-width="2" stroke-dasharray="5,5"/>
			
			<text x="300" y="285" text-anchor="middle" fill="#666" font-size="11">Click on teeth to mark issues</text>
		</svg>
	`;
}

