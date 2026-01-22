// Override Grid Row Form button labels and behavior
// Changes footer button to "Save" and header collapse to "Close (X)"

$(document).ready(function() {
	// Use MutationObserver to detect when grid forms are added to DOM
	const observer = new MutationObserver(function(mutations) {
		mutations.forEach(function(mutation) {
			mutation.addedNodes.forEach(function(node) {
				if (node.nodeType === 1) { // Element node
					// Check if this is a grid form or contains grid forms
					const gridForms = $(node).find('.form-in-grid').addBack('.form-in-grid');
					
					gridForms.each(function() {
						const $gridForm = $(this);
						
						// Only modify if not already modified
						if ($gridForm.data('buttons-modified')) {
							return;
						}
						$gridForm.data('buttons-modified', true);
						
						// 1. Keep header buttons as they are (Update & New, Update & New Before)
						$gridForm.find('.grid-insert-row').each(function() {
							const $btn = $(this);
							if ($btn.text().trim() === 'Insert Above') {
								$btn.contents().filter(function() {
									return this.nodeType === 3;
								}).replaceWith('Update & New');
							}
						});
						
						$gridForm.find('.grid-insert-row-below').each(function() {
							const $btn = $(this);
							if ($btn.text().trim() === 'Insert Below') {
								$btn.contents().filter(function() {
									return this.nodeType === 3;
								}).replaceWith('Update & New Before');
							}
						});
						
						// 2. Modify header collapse button to Close (X)
						// Keep original functionality (save + close), just change icon
						const $collapseBtn = $gridForm.find('.grid-collapse-row');
						if ($collapseBtn.length && !$collapseBtn.data('close-modified')) {
							$collapseBtn.data('close-modified', true);
							
							// Change icon to close (X) but keep the original functionality
							const $icon = $collapseBtn.find('svg, .icon');
							if ($icon.length) {
								$icon.replaceWith(frappe.utils.icon("close"));
							} else {
								$collapseBtn.empty().html(frappe.utils.icon("close"));
							}
							
							// Don't modify click handler - keep original Frappe behavior (save + close)
						}
						
						// 3. Modify footer "Insert Below" button to "Save"
						$gridForm.find('.grid-append-row').each(function() {
							const $btn = $(this);
							
							if ($btn.data('save-modified')) {
								return;
							}
							$btn.data('save-modified', true);
							
							// Change label to "Save"
							$btn.text('Save');
							
							// Change to primary button style
							$btn.removeClass('btn-secondary').addClass('btn-primary');
							
							// Replace click handler to save + close (without inserting new row)
							$btn.off('click');
							
							$btn.on('click', function(e) {
								e.preventDefault();
								e.stopPropagation();
								
								// Trigger the collapse button click (which saves and closes)
								const $collapse = $gridForm.find('.grid-collapse-row');
								if ($collapse.length) {
									// Use native DOM click to properly trigger the event
									$collapse[0].click();
								}
								
								return false;
							});
						});
					});
				}
			});
		});
	});
	
	// Start observing the document body for changes
	observer.observe(document.body, {
		childList: true,
		subtree: true
	});
});

