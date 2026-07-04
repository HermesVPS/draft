/**
 * Ideation Process JavaScript
 *
 * This file contains all the JavaScript functionality for the ideation process,
 * including problem selection, validation, research, and title selection.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Problem Selection functionality
    initProblemSelection();

    // PDF Title Selection functionality
    initPDFTitleSelection();
});

/**
 * Initialize the problem selection functionality
 * Handles the radio button selection and visual feedback
 */
function initProblemSelection() {
    // Get all problem radio buttons
    const problemRadios = document.querySelectorAll('input[name="problem"]');

    if (problemRadios.length === 0) return; // Exit if no problem radios found

    // Set initial state for the selected radio button
    updateSelectedProblemCard();

    // Add change event listeners to all radio buttons
    problemRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateSelectedProblemCard();
        });
    });
}

/**
 * Update the visual state of problem cards based on radio selection
 */
function updateSelectedProblemCard() {
    // Get all cards that are not already in progress or completed
    const regularCards = document.querySelectorAll('.problem-card:not([class*="bg-primary"]):not([class*="bg-success"])');

    // Reset all regular cards to default state
    regularCards.forEach(card => {
        card.classList.remove('bg-primary/10', 'border-2', 'border-primary');
        card.classList.add('bg-base-100', 'border', 'border-base-300', 'hover:bg-base-200');
    });

    // Add highlighting to selected card if it's a regular card
    const checkedInput = document.querySelector('input[name="problem"]:checked');
    if (checkedInput) {
        const card = checkedInput.closest('.problem-card');
        if (card && !card.classList.contains('bg-primary/5') && !card.classList.contains('bg-success/5')) {
            card.classList.remove('bg-base-100', 'border', 'border-base-300');
            card.classList.add('bg-primary/10', 'border-2', 'border-primary');
        }
    }
}

/**
 * Initialize the PDF title selection functionality
 * Handles the radio button selection and visual feedback
 */
function initPDFTitleSelection() {
    // Get all title radio buttons
    const titleRadios = document.querySelectorAll('input[name="title"]');

    if (titleRadios.length === 0) return; // Exit if no title radios found

    // Set initial state for the selected radio button
    updateSelectedTitleCard();

    // Add change event listeners to all radio buttons
    titleRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateSelectedTitleCard();
        });
    });
}

/**
 * Update the visual state of title cards based on radio selection
 */
function updateSelectedTitleCard() {
    // Remove highlighting from all cards
    document.querySelectorAll('.title-card').forEach(card => {
        card.classList.remove('bg-yellow-100', 'border-2', 'border-yellow-500');
        card.classList.add('bg-base-100', 'border', 'border-base-300');
    });

    // Add highlighting to selected card
    const checkedInput = document.querySelector('input[name="title"]:checked');
    if (checkedInput) {
        const card = checkedInput.closest('.title-card');
        if (card) {
            card.classList.remove('bg-base-100', 'border', 'border-base-300');
            card.classList.add('bg-yellow-100', 'border-2', 'border-yellow-500');
        }
    }
}