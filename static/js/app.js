/**
 * One Clever Monkey Application JavaScript
 * 
 * This file contains compiled JavaScript functionality that cannot be replaced with Alpine.js.
 * It includes essential functionality for the application, such as progress tracking,
 * service worker integration, and complex UI interactions.
 * 
 * Most UI interactions have been migrated to Alpine.js directives in the HTML templates.
 */

// Execute when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('app.js loaded successfully!');

    // Scroll to top on page load/refresh
    window.scrollTo(0, 0);

    // Set up back to top button functionality
    setupBackToTopButton();
});

/**
 * Set up back to top button functionality
 * Shows/hides the button based on scroll position and handles click events
 */
function setupBackToTopButton() {
    // Get the button
    let mybutton = document.getElementById("myBtn");

    if (!mybutton) return; // Exit if button not found

    // When the user scrolls down 20px from the top of the document, show the button
    window.onscroll = function() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            mybutton.style.display = "block";
        } else {
            mybutton.style.display = "none";
        }
    };

    // When the user clicks on the button, scroll to the top of the document
    mybutton.addEventListener('click', function() {
        document.body.scrollTop = 0; // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    });
}

/**
 * TinyMCE Editor Integration
 * Handles showing/hiding the editor and focusing it when shown
 * 
 * @param {string} editorId - The ID of the editor container
 * @param {string} displayId - The ID of the display container
 */
function showEditor(editorId, displayId) {
    console.log(`Showing editor ${editorId}, hiding display ${displayId}`);

    const editor = document.getElementById(editorId);
    const display = document.getElementById(displayId);

    if (editor && display) {
        display.classList.add('hidden');
        editor.classList.remove('hidden');

        // If using TinyMCE, focus the editor
        const textareaId = editorId === 'outline-editor' ? 
            'id_outline_content' : 'id_content';

        if (window.tinymce) {
            const tinyEditor = tinymce.get(textareaId);
            if (tinyEditor) {
                console.log(`TinyMCE editor found for ${textareaId}`);
                // Focus the editor
                setTimeout(() => {
                    tinyEditor.focus();
                }, 100);
            }
        }
    }
}

/**
 * Progress Tracking for PDF Generation
 * Uses AJAX to periodically check generation progress and update UI
 */
function setupProgressTracking() {
    console.log('Setting up progress tracking');

    // Check if we have a progress bar
    const progressBar = document.querySelector('.progress');
    if (!progressBar) return; // Exit if no progress bar found

    // Get the current progress value
    let currentProgress = parseInt(progressBar.value || 0);
    console.log(`Initial progress: ${currentProgress}%`);

    // Store the original button if it exists
    const generateAllBtn = document.querySelector('.generate-all-btn');
    let originalBtnHTML = '';
    if (generateAllBtn) {
        // Disable the button while generation is in progress
        generateAllBtn.disabled = true;
        originalBtnHTML = generateAllBtn.innerHTML;
        generateAllBtn.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Generating All Content...';
    }

    // Hide the sections card and show the loading indicator
    const sectionsCard = document.getElementById('sections-card');
    const loadingIndicator = document.getElementById('generation-loading-indicator');

    if (sectionsCard) sectionsCard.classList.add('hidden');
    if (loadingIndicator) loadingIndicator.classList.remove('hidden');

    // Set up an interval to refresh the page every 3 seconds
    const refreshInterval = setInterval(() => {
        // Make an AJAX request to get the current progress
        fetch(window.location.href)
            .then(response => response.text())
            .then(html => {
                // Create a temporary element to parse the HTML
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;

                // Extract the progress value from the response
                const newProgressBar = tempDiv.querySelector('.progress');
                if (newProgressBar) {
                    const newProgress = parseInt(newProgressBar.getAttribute('value') || 0);

                    // Update the progress bar if the value has changed
                    if (newProgress !== currentProgress) {
                        // Update all progress bars on the page
                        document.querySelectorAll('.progress').forEach(bar => {
                            bar.value = newProgress;
                        });

                        // Update all progress text elements
                        document.querySelectorAll('.progress + span').forEach(span => {
                            span.textContent = `${newProgress}%`;
                        });

                        document.querySelectorAll('#progress-status').forEach(p => {
                            p.textContent = `${newProgress}% complete`;
                        });

                        currentProgress = newProgress;
                    }

                    // Check if the generation is complete
                    if (newProgress >= 100) {
                        clearInterval(refreshInterval);

                        // Show the sections card and hide the loading indicator
                        if (sectionsCard) sectionsCard.classList.remove('hidden');
                        if (loadingIndicator) loadingIndicator.classList.add('hidden');

                        // Reload the page to show the final result
                        window.location.reload();
                    }

                    // Check if the project status has changed
                    const projectStatus = tempDiv.querySelector('[data-project-status]');
                    if (projectStatus && projectStatus.dataset.projectStatus === 'completed') {
                        clearInterval(refreshInterval);

                        // Show the sections card and hide the loading indicator
                        if (sectionsCard) sectionsCard.classList.remove('hidden');
                        if (loadingIndicator) loadingIndicator.classList.add('hidden');

                        // Reload the page to show the final result
                        window.location.reload();
                    }
                } else {
                    // Progress bar no longer exists, which means the process is complete
                    clearInterval(refreshInterval);

                    // Show the sections card and hide the loading indicator
                    if (sectionsCard) sectionsCard.classList.remove('hidden');
                    if (loadingIndicator) loadingIndicator.classList.add('hidden');

                    // Reload the page to show the final result
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error fetching progress:', error);
            });
    }, 3000);

    // Store the interval ID in a data attribute on the progress bar
    progressBar.dataset.refreshInterval = refreshInterval;
}

/**
 * Generate All Content Button Handler
 * Handles confirmation dialog and form submission
 * 
 * @param {Event} e - The click event
 * @param {HTMLElement} button - The button element
 */
function handleGenerateAllContent(e, button) {
    e.preventDefault();

    // Confirm with the user
    if (!confirm('This will generate content for all incomplete sections. This process may take several minutes. Continue?')) {
        return false;
    }

    // Disable the button
    button.disabled = true;

    // Store original text
    const originalText = button.innerHTML;

    // Replace with loading spinner
    button.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Generating All Content...';

    // Get the form and submit it
    const form = button.closest('form');
    if (form) {
        setTimeout(() => {
            form.submit();
        }, 100);

        // Set up progress tracking
        setupProgressTracking();
    } else {
        // Re-enable the button if no form found
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

/**
 * Show Loading Overlay
 * Displays a loading overlay to prevent double-clicking and provide visual feedback
 * 
 * @param {Event} e - The click event
 */
function showLoadingOverlay(e) {
    // Dispatch the page-loading event to show the overlay
    const event = new CustomEvent('page-loading');
    window.dispatchEvent(event);
}

/**
 * Toggle Section Content
 * Shows/hides the content of a section
 * 
 * @param {string} sectionId - The ID of the section to toggle
 */
function toggleSectionContent(sectionId) {
    console.log(`Toggling content for section ${sectionId}`);

    // Get the section content element
    const contentElement = document.getElementById(`section-content-${sectionId}`);
    if (!contentElement) return;

    // Toggle the hidden-content class
    contentElement.classList.toggle('hidden-content');

    // Get the button that was clicked
    const button = document.querySelector(`[data-section-id="${sectionId}"] .card-title`);
    if (!button) return;

    // Toggle the chevron icons
    const upIcon = button.querySelector('.fa-chevron-up');
    const downIcon = button.querySelector('.fa-chevron-down');

    if (upIcon && downIcon) {
        upIcon.classList.toggle('hidden');
        downIcon.classList.toggle('hidden');
    }
}

/**
 * Toggle All Sections
 * Collapses or expands all sections
 */
function toggleAllSections() {
    console.log('Toggling all sections');

    // Get all section cards
    const sectionCards = document.querySelectorAll('[data-section-id]');

    // Determine if we should collapse or expand based on the first section
    let shouldCollapse = true;
    if (sectionCards.length > 0) {
        const firstSection = sectionCards[0];
        const firstContent = document.getElementById(`section-content-${firstSection.dataset.sectionId}`);
        if (firstContent && firstContent.classList.contains('hidden-content')) {
            shouldCollapse = false; // If first section is already collapsed, we should expand
        }
    }

    // Update the button text and icon
    const collapseAllBtn = document.getElementById('collapse-all-btn');
    if (collapseAllBtn) {
        const icon = collapseAllBtn.querySelector('i');
        if (icon) {
            if (shouldCollapse) {
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
                collapseAllBtn.innerHTML = collapseAllBtn.innerHTML.replace('Collapse All', 'Expand All');
            } else {
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
                collapseAllBtn.innerHTML = collapseAllBtn.innerHTML.replace('Expand All', 'Collapse All');
            }
        }
    }

    // Toggle each section
    sectionCards.forEach(card => {
        const sectionId = card.dataset.sectionId;
        const contentElement = document.getElementById(`section-content-${sectionId}`);
        const button = card.querySelector('.card-title');
        const upIcon = button?.querySelector('.fa-chevron-up');
        const downIcon = button?.querySelector('.fa-chevron-down');

        if (contentElement) {
            if (shouldCollapse) {
                contentElement.classList.add('hidden-content');
                if (upIcon && downIcon) {
                    upIcon.classList.add('hidden');
                    downIcon.classList.remove('hidden');
                }
            } else {
                contentElement.classList.remove('hidden-content');
                if (upIcon && downIcon) {
                    upIcon.classList.remove('hidden');
                    downIcon.classList.add('hidden');
                }
            }
        }
    });
}

/**
 * Toggle Section Edit
 * Shows/hides the edit form for a section
 * 
 * @param {string} sectionId - The ID of the section to toggle edit mode
 */
function toggleSectionEdit(sectionId) {
    console.log(`Toggling edit mode for section ${sectionId}`);

    // Get the section content and edit form elements
    const contentElement = document.getElementById(`section-content-${sectionId}`);
    const editElement = document.getElementById(`section-edit-${sectionId}`);

    if (contentElement && editElement) {
        // Toggle visibility
        const isEditing = !editElement.classList.contains('hidden');

        if (isEditing) {
            // Hide edit form, show content
            editElement.classList.add('hidden');
            contentElement.querySelector('.prose').style.display = 'block';
        } else {
            // Show edit form, hide content
            editElement.classList.remove('hidden');
            contentElement.querySelector('.prose').style.display = 'none';
        }
    }
}

// Make functions available globally for use in HTML
window.showEditor = showEditor;
window.setupProgressTracking = setupProgressTracking;
window.handleGenerateAllContent = handleGenerateAllContent;
window.showLoadingOverlay = showLoadingOverlay;
window.toggleSectionContent = toggleSectionContent;
window.toggleAllSections = toggleAllSections;
window.toggleSectionEdit = toggleSectionEdit;
