/**
 * PDF Ideation JavaScript
 *
 * This file contains all the JavaScript functionality for the PDF ideation process,
 * including outline editing, section management, and content generation.
 */

// Execute immediately and also on DOMContentLoaded
(function() {
    // Run setup when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        setupEventListeners();
    });

    // Also run immediately in case the DOM is already loaded
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setupEventListeners();
    }

    function setupEventListeners() {
        console.log('Setting up PDF Ideation event listeners');

        // Outline editing functionality
        setupOutlineEditor();

        // Section highlighting
        setupSectionHighlighting();

        // Generate content button functionality
        setupGenerateContentButtons();
    }

    function setupGenerateContentButtons() {
        console.log('Setting up generate content buttons');

        // Get all generate content buttons
        const generateButtons = document.querySelectorAll('.generate-content-btn');
        console.log(`Found ${generateButtons.length} generate content buttons`);

        if (generateButtons.length === 0) return; // Exit if no buttons found

        // Add click event listeners to all buttons
        generateButtons.forEach(button => {
            console.log('Adding click listener to button:', button);

            // Remove any existing listeners to prevent duplicates
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);

            // Add the click event listener
            newButton.addEventListener('click', function(e) {
                console.log('Generate content button clicked');

                // Disable the button
                this.disabled = true;
                console.log('Button disabled');

                // Store original text
                const originalText = this.innerHTML;
                console.log('Original text stored:', originalText);

                // Replace with loading spinner
                this.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Generating...';
                console.log('Button text replaced with spinner');

                // Get the form and submit it
                const form = this.closest('form');
                if (form) {
                    console.log('Form found, submitting...');
                    setTimeout(() => {
                        form.submit();
                    }, 100);
                } else {
                    console.error('No form found for the button');
                    // Re-enable the button if no form found
                    this.disabled = false;
                    this.innerHTML = originalText;
                }

                // Prevent default button behavior to let our code handle it
                e.preventDefault();
                return false;
            });
        });

        // Also set up the Generate All Content button
        setupGenerateAllButton();
    }

    function setupGenerateAllButton() {
        console.log('Setting up generate all content button');

        // Get the generate all button
        const generateAllButton = document.querySelector('.generate-all-btn');
        if (!generateAllButton) return; // Exit if button not found

        console.log('Found generate all button:', generateAllButton);

        // Remove any existing listeners to prevent duplicates
        const newButton = generateAllButton.cloneNode(true);
        generateAllButton.parentNode.replaceChild(newButton, generateAllButton);

        // Add the click event listener
        newButton.addEventListener('click', function(e) {
            console.log('Generate all content button clicked');

            // Confirm with the user
            if (!confirm('This will generate content for all incomplete sections. This process may take several minutes. Continue?')) {
                e.preventDefault();
                return false;
            }

            // Disable the button
            this.disabled = true;
            console.log('Button disabled');

            // Store original text
            const originalText = this.innerHTML;
            console.log('Original text stored:', originalText);

            // Replace with loading spinner
            this.innerHTML = '<span class="loading loading-spinner loading-xs"></span> Generating All Content...';
            console.log('Button text replaced with spinner');

            // Get the form and submit it
            const form = this.closest('form');
            if (form) {
                console.log('Form found, submitting...');
                setTimeout(() => {
                    form.submit();
                }, 100);
            } else {
                console.error('No form found for the button');
                // Re-enable the button if no form found
                this.disabled = false;
                this.innerHTML = originalText;
            }

            // Prevent default button behavior to let our code handle it
            e.preventDefault();
            return false;
        });

        // Set up auto-refresh for progress tracking
        setupProgressTracking();
    }

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
            console.log('Disabled generate all button and added spinner');
        }

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
                        console.log(`New progress from server: ${newProgress}%`);

                        // Update the progress bar if the value has changed
                        if (newProgress !== currentProgress) {
                            progressBar.value = newProgress;
                            document.querySelector('.progress + p').textContent = `${newProgress}% complete`;
                            currentProgress = newProgress;
                            console.log(`Updated progress bar to ${newProgress}%`);
                        }

                        // Check if the generation is complete
                        if (newProgress >= 100) {
                            clearInterval(refreshInterval);
                            console.log('Generation complete, clearing interval');

                            // Reload the page to show the final result
                            window.location.reload();
                        }

                        // Check if the project status has changed
                        const statusAlert = tempDiv.querySelector('.alert-warning');
                        if (!statusAlert) {
                            // The alert is gone, which means the process is complete
                            clearInterval(refreshInterval);
                            console.log('Alert no longer present, clearing interval');

                            // Reload the page to show the final result
                            window.location.reload();
                        }
                    } else {
                        // Progress bar no longer exists, which means the process is complete
                        clearInterval(refreshInterval);
                        console.log('Progress bar no longer exists, clearing interval');

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

    function setupOutlineEditor() {
        console.log('Setup handled by editor.js');
        // The outline editor setup is now handled by editor.js
        // This function is kept as a placeholder to avoid breaking existing code
    }

    function setupSectionHighlighting() {
        const sectionCards = document.querySelectorAll('[id^="section-card-"]');

        sectionCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.classList.add('bg-base-200');
            });

            card.addEventListener('mouseleave', function() {
                this.classList.remove('bg-base-200');
            });
        });
    }

    // The event listeners are already set up at the beginning of this IIFE
})();