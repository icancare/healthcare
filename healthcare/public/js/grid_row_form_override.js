// Override Grid Row Form button labels
// This changes button labels for all child table forms

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
						
						// Change button labels
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
						
						$gridForm.find('.grid-append-row').each(function() {
							const $btn = $(this);
							if ($btn.text().trim() === 'Insert Below') {
								$btn.contents().filter(function() {
									return this.nodeType === 3;
								}).replaceWith('Update & New Before');
							}
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

