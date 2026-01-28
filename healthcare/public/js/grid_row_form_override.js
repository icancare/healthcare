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
						
						// Get the grid row object
						const $gridRow = $gridForm.closest('.grid-row');
						const gridRowObj = $gridRow.data('grid_row');
						
						if (!gridRowObj) return;
						
						// Store original doc values when form opens
						if (!gridRowObj._original_doc) {
							gridRowObj._original_doc = JSON.parse(JSON.stringify(gridRowObj.doc));
						}
						
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
						// Change functionality to discard changes without saving
						const $collapseBtn = $gridForm.find('.grid-collapse-row');
						if ($collapseBtn.length && !$collapseBtn.data('close-modified')) {
							$collapseBtn.data('close-modified', true);
							
							// Change icon to close (X)
							const $icon = $collapseBtn.find('svg, .icon');
							if ($icon.length) {
								$icon.replaceWith(frappe.utils.icon("close"));
							} else {
								$collapseBtn.empty().html(frappe.utils.icon("close"));
							}
							
							// Replace click handler to discard changes and close
							$collapseBtn.off('click');
							$collapseBtn.on('click', function(e) {
								e.preventDefault();
								e.stopImmediatePropagation();
								
								// Restore original values from stored doc
								if (gridRowObj._original_doc) {
									Object.keys(gridRowObj._original_doc).forEach(function(key) {
										gridRowObj.doc[key] = gridRowObj._original_doc[key];
									});
									
									// Clear the stored original
									delete gridRowObj._original_doc;
								}
								
								// Refresh the row display and close
								gridRowObj.refresh();
								gridRowObj.toggle_view(false);
								
								return false;
							});
						}
						
						// 3. Modify footer "Insert Below" button to "Update"
						$gridForm.find('.grid-append-row').each(function() {
							const $btn = $(this);
							
							if ($btn.data('save-modified')) {
								return;
							}
							$btn.data('save-modified', true);
							
							// Change label to "Update"
							$btn.text('Update');
							
							// Change to primary button style
							$btn.removeClass('btn-secondary').addClass('btn-primary');
							
							// Replace click handler to save + close (without inserting new row)
							$btn.off('click');
							
							$btn.on('click', function(e) {
								e.preventDefault();
								e.stopImmediatePropagation();
								
								// Clear stored original values since we're saving
								if (gridRowObj._original_doc) {
									delete gridRowObj._original_doc;
								}
								
								// Refresh and close the form (this saves the changes)
								gridRowObj.refresh();
								gridRowObj.toggle_view(false);
								
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

