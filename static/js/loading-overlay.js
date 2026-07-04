/**
 * Loading Overlay Handler
 * 
 * This script attaches event listeners to form submit buttons to show a loading overlay
 * when the form is submitted, preventing double-clicking and providing visual feedback.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Hide loading overlay when the page initially loads
    // This ensures the overlay is hidden when the page first loads
    const hideEvent = new CustomEvent('hide-loading');
    window.dispatchEvent(hideEvent);

    // Hide loading overlay when page is loaded from browser cache (back button navigation)
    // This fixes the issue where the overlay remains visible after using the browser back button
    window.addEventListener('pageshow', function(event) {
        // Always hide the overlay on pageshow, but especially important when loaded from cache
        const hideEvent = new CustomEvent('hide-loading');
        window.dispatchEvent(hideEvent);
    });

    // Listen for the popstate event (browser back/forward buttons)
    window.addEventListener('popstate', function() {
        // Hide the loading overlay by dispatching a custom event
        const hideEvent = new CustomEvent('hide-loading');
        window.dispatchEvent(hideEvent);
    });
    // Find all form submit buttons and add the loading overlay
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Don't show overlay for buttons with specific classes that should be excluded
            if (button.classList.contains('no-overlay')) {
                return;
            }

            // Get the form element
            const form = button.closest('form');
            if (!form) return;

            // Check if this is a title selection form (has title radio buttons)
            const titleRadios = form.querySelectorAll('input[name="title"]');
            if (titleRadios.length > 0) {
                // Check if any title radio is selected
                const isTitleSelected = Array.from(titleRadios).some(radio => radio.checked);

                // If no title is selected, don't show the overlay
                if (!isTitleSelected) {
                    console.log('No title selected, not showing overlay');
                    return;
                }
            }

            // Check if this is a form with an action (submitting to server)
            // If it has an action attribute, we need to be careful not to interfere with submission
            const hasFormAction = form.hasAttribute('action') && form.getAttribute('action').trim() !== '';

            // Allow the form submission to proceed
            // We'll show the overlay but not prevent the default action

            // Show loading overlay
            if (typeof showLoadingOverlay === 'function') {
                showLoadingOverlay(e);
            } else {
                console.error('showLoadingOverlay function not found');
            }

            // For forms with an action attribute (submitting to server), we need to be more careful
            if (hasFormAction) {
                // Show the loading overlay but don't disable the button immediately
                // This allows the form submission to proceed normally

                // Update the button appearance to show it's processing
                // if (!button.innerHTML.includes('loading-spinner')) {
                //     button.dataset.originalText = button.innerHTML;
                //     button.innerHTML = '<span class="loading loading-spinner loading-xs mr-2"></span>' +
                //                       (button.dataset.loadingText || 'Processing...');
                // }

                // We won't disable the button for forms submitting to server
                // This ensures the form submission completes properly
            } else {
                // For JavaScript-handled forms, we can disable the button after a short delay
                setTimeout(() => {
                    // Disable the button to prevent double-clicking
                    // button.disabled = true;

                    // Store original text if not already storing a loading spinner
                    // if (!button.innerHTML.includes('loading-spinner')) {
                    //     button.dataset.originalText = button.innerHTML;
                    //     button.innerHTML = '<span class="loading loading-spinner loading-xs mr-2"></span>' +
                    //                       (button.dataset.loadingText || 'Processing...');
                    // }
                }, 50); // Small delay to ensure form submission starts
            }
        });
    });
});
