// Copyright (c) 2024, healthcare and contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient Insurance', {
	onload: function(frm) {
		// Show previews on load if images exist
		setup_card_preview_on_load(frm);
	},
	
	refresh: function(frm) {
		// Setup card previews
		setup_card_preview_on_load(frm);
	},
	
	card_front_photo: function(frm) {
		// Show preview when card is uploaded
		setTimeout(() => {
			show_card_preview(frm, 'card_front_photo', frm.doc.card_front_photo, 'Front Card');
		}, 300);
	},
	
	card_back_photo: function(frm) {
		// Show preview when card is uploaded
		setTimeout(() => {
			show_card_preview(frm, 'card_back_photo', frm.doc.card_back_photo, 'Back Card');
		}, 300);
	}
});

function setup_card_preview_on_load(frm) {
	// Show existing images on form load
	setTimeout(() => {
		if (frm.doc.card_front_photo) {
			show_card_preview(frm, 'card_front_photo', frm.doc.card_front_photo, 'Front Card');
		}
		if (frm.doc.card_back_photo) {
			show_card_preview(frm, 'card_back_photo', frm.doc.card_back_photo, 'Back Card');
		}
	}, 500);
}

function show_card_preview(frm, fieldname, image_url, label) {
	if (!image_url) return;
	
	const field_wrapper = frm.fields_dict[fieldname]?.$wrapper;
	if (!field_wrapper) return;
	
	// Remove old preview
	field_wrapper.find('.insurance-card-inline-preview').remove();
	
	// Create new preview box ABOVE the file path
	const preview_html = `
		<div class="insurance-card-inline-preview" style="
			margin-bottom: 15px;
			padding: 15px;
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
			border-radius: 12px;
			box-shadow: 0 4px 15px rgba(0,0,0,0.2);
		">
			<div style="
				background: white;
				border-radius: 8px;
				padding: 10px;
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
						"
						 onmouseover="this.style.transform='scale(1.02)'; this.style.boxShadow='0 8px 20px rgba(0,0,0,0.3)';"
						 onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';"
						 onclick="show_fullscreen_image('${image_url}', '${label}')" />
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
	
	// Insert preview BEFORE the control wrapper (above file path)
	const control_wrapper = field_wrapper.find('.control-input-wrapper');
	if (control_wrapper.length) {
		control_wrapper.before(preview_html);
	} else {
		field_wrapper.prepend(preview_html);
	}
	
	// Hide the ugly file path link
	field_wrapper.find('.control-value a').css({
		'font-size': '11px',
		'color': '#999',
		'text-decoration': 'none'
	});
}

window.show_fullscreen_image = function(image_url, label) {
	const d = new frappe.ui.Dialog({
		title: `Insurance Card - ${label}`,
		size: 'extra-large',
		fields: [{
			fieldtype: 'HTML',
			fieldname: 'image_preview',
			options: `
				<div style="
					text-align: center;
					padding: 30px;
					background: #f8f9fa;
					border-radius: 8px;
				">
					<div style="
						background: white;
						display: inline-block;
						padding: 20px;
						border-radius: 12px;
						box-shadow: 0 8px 30px rgba(0,0,0,0.15);
					">
						<img src="${image_url}" 
							 style="
								max-width: 90vw;
								max-height: 75vh;
								border-radius: 8px;
								display: block;
							" />
					</div>
					<div style="margin-top: 20px;">
						<a href="${image_url}" target="_blank" class="btn btn-primary btn-md">
							<i class="fa fa-external-link"></i> Open in New Tab
						</a>
						<button class="btn btn-secondary btn-md" onclick="cur_dialog.hide();" style="margin-left: 10px;">
							<i class="fa fa-times"></i> Close
						</button>
					</div>
				</div>
			`
		}]
	});
	d.show();
	
	// Make dialog draggable
	d.$wrapper.find('.modal-dialog').css({
		'max-width': '95%',
		'width': 'auto'
	});
}

