/**
 * Common JavaScript snippets and utilities
 */

// Scroll to top on page load/refresh
document.addEventListener('DOMContentLoaded', function(event) {
    window.scrollTo(0, 0);

    // Prevent multiple form submissions for regular forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButtons = form.querySelectorAll('button[type="submit"]');
            submitButtons.forEach(button => {
                if (!button.disabled) {
                    button.disabled = true;

                    // Store original text
                    const originalText = button.innerHTML;

                    // Replace with loading spinner
                    button.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Processing...';

                    // Re-enable after a timeout in case the form submission fails
                    setTimeout(() => {
                        button.disabled = false;
                        button.innerHTML = originalText;
                    }, 10000);
                }
            });
        });
    });
    
    // Set up section content toggles
    setupSectionToggles();
});

// Common functionality for all pages

/**
 * Toggle visibility of section content and chevron icons
 * @param {string} sectionId - The ID of the section to toggle
 */
function toggleSectionContent(sectionId) {
    console.log(`Toggling content for section ${sectionId}`);
    const contentElement = document.getElementById(`section-content-${sectionId}`);
    if (contentElement) {
        contentElement.classList.toggle('hidden');
        
        // Find the button that triggered this action
        // Look for the button within the same card as the content
        const card = contentElement.closest('.card[data-section-id="' + sectionId + '"]');
        if (card) {
            const button = card.querySelector('button.card-title');
            if (button) {
                const chevronDown = button.querySelector('.fa-chevron-down');
                const chevronUp = button.querySelector('.fa-chevron-up');
                
                if (chevronDown) chevronDown.classList.toggle('hidden');
                if (chevronUp) chevronUp.classList.toggle('hidden');
            }
        }
    } else {
        console.error(`Content element not found for section ${sectionId}`);
    }
}

/**
 * Toggle visibility of section edit form
 * @param {string} sectionId - The ID of the section to edit
 */
function toggleSectionEdit(sectionId) {
    console.log(`Toggling edit form for section ${sectionId}`);
    const editElement = document.getElementById(`section-edit-${sectionId}`);
    if (editElement) {
        editElement.classList.toggle('hidden');
    } else {
        console.error(`Edit element not found for section ${sectionId}`);
    }
}

/**
 * Set up event listeners for section toggles on page load
 */
function setupSectionToggles() {
    console.log('Setting up section toggles');
    
    // Add click handlers to section toggle buttons
    document.querySelectorAll('.card[data-section-id] button.card-title').forEach(button => {
        const sectionId = button.closest('.card').dataset.sectionId;
        if (sectionId) {
            console.log(`Adding click handler for section content toggle ${sectionId}`);
            // Remove existing handler to prevent duplicates
            button.removeEventListener('click', () => toggleSectionContent(sectionId));
            // Add new handler
            button.addEventListener('click', () => toggleSectionContent(sectionId));
        }
    });
    
    // Add click handlers to edit buttons
    document.querySelectorAll('.card[data-section-id] button.btn-outline:has(.fa-pen)').forEach(button => {
        const sectionId = button.closest('.card').dataset.sectionId;
        if (sectionId) {
            console.log(`Adding click handler for section edit toggle ${sectionId}`);
            // Remove existing handler to prevent duplicates
            button.removeEventListener('click', () => toggleSectionEdit(sectionId));
            // Add new handler
            button.addEventListener('click', () => toggleSectionEdit(sectionId));
        }
    });
}

// Make sure setupSectionToggles runs when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupSectionToggles();
    
    // Also run when HTMX content is loaded (if using HTMX)
    document.body.addEventListener('htmx:afterSwap', function(event) {
        setupSectionToggles();
    });
});

// Add any additional JavaScript functionality here

