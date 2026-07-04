document.addEventListener("DOMContentLoaded", function () {
    console.log('progress.js loaded successfully!');

    // Find all forms
    const forms = document.querySelectorAll('form');

    forms.forEach((form) => {
        form.addEventListener('submit', function (event) {
            console.log('Form submitted:', form);

            // Disable the submit button
            const submitButton = form.querySelector("button[type='submit']");

            if (submitButton) {
                console.log('Found submit button:', submitButton);
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
                    Processing...
                `;
            } else {
                console.warn('No submit button found in the form.');
            }
        });
    });
});