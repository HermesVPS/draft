/**
 * Rich Text Editor JavaScript
 *
 * This file contains all the JavaScript functionality for the WYSIWYG editor,
 * including initialization, markdown conversion, and form submission handling.
 */

// UI controls for editor
const EditorUI = {
    // Show editor, hide display
    showEditor: function(editorId, displayId) {
        console.log(`Showing editor ${editorId}, hiding display ${displayId}`);
        
        const editor = document.getElementById(editorId);
        const display = document.getElementById(displayId);
        
        if (editor && display) {
            display.classList.add('hidden');
            editor.classList.remove('hidden');
            
            // If using Django TinyMCE, it's already initialized
            // Just make sure the content is loaded
            const textareaId = editorId === 'outline-editor' ? 
                'id_outline_content' : 'id_content';
            
            // TinyMCE should be initialized by Django
            if (window.tinymce) {
                const tinyEditor = tinymce.get(textareaId);
                if (tinyEditor) {
                    console.log(`TinyMCE editor found for ${textareaId}`);
                    // Focus the editor
                    setTimeout(() => {
                        tinyEditor.focus();
                    }, 100);
                } else {
                    console.warn(`TinyMCE editor not found for ${textareaId}`);
                }
            }
        } else {
            console.error(`Editor ${editorId} or display ${displayId} not found`);
        }
    },
    
    // Hide editor, show display
    hideEditor: function(editorId, displayId) {
        console.log(`Hiding editor ${editorId}, showing display ${displayId}`);
        
        const editor = document.getElementById(editorId);
        const display = document.getElementById(displayId);
        
        if (editor && display) {
            editor.classList.add('hidden');
            display.classList.remove('hidden');
        } else {
            console.error(`Editor ${editorId} or display ${displayId} not found`);
        }
    },
    
    // Setup edit and cancel buttons
    setupButtons: function(editBtnId, cancelBtnId, editorId, displayId) {
        console.log(`Setting up buttons: edit=${editBtnId}, cancel=${cancelBtnId}, editor=${editorId}, display=${displayId}`);
        
        const editBtn = document.getElementById(editBtnId);
        const cancelBtn = document.getElementById(cancelBtnId);
        
        if (editBtn) {
            // Remove any existing listeners to prevent duplicates
            const newEditBtn = editBtn.cloneNode(true);
            editBtn.parentNode.replaceChild(newEditBtn, editBtn);
            
            newEditBtn.addEventListener('click', () => {
                console.log(`Edit button ${editBtnId} clicked`);
                this.showEditor(editorId, displayId);
            });
        } else {
            console.error(`Edit button ${editBtnId} not found`);
        }
        
        if (cancelBtn) {
            // Remove any existing listeners to prevent duplicates
            const newCancelBtn = cancelBtn.cloneNode(true);
            cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
            
            newCancelBtn.addEventListener('click', () => {
                console.log(`Cancel button ${cancelBtnId} clicked`);
                this.hideEditor(editorId, displayId);
            });
        } else {
            console.error(`Cancel button ${cancelBtnId} not found`);
        }
    }
};

// Form handling for editor content
const EditorForm = {
    // Initialize form with editor
    init: function(formId, textareaSelector) {
        console.log(`Initializing form ${formId} with textarea ${textareaSelector}`);
        
        const form = document.getElementById(formId);
        if (!form) {
            console.error(`Form with ID ${formId} not found`);
            return;
        }
        
        // With Django TinyMCE, form handling is simpler
        // The textarea is automatically updated by TinyMCE
        console.log(`Form ${formId} initialized with Django TinyMCE`);
    }
};

// Document ready handler
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing editors');
    
    // Setup UI buttons for section editor if present
    if (document.getElementById('content-editor')) {
        console.log('Found section editor');
        EditorUI.setupButtons('edit-content-btn', 'cancel-rich-edit-btn', 'content-editor', 'content-display');
    }
    
    // Setup UI buttons for outline editor if present
    if (document.getElementById('outline-editor')) {
        console.log('Found outline editor');
        EditorUI.setupButtons('edit-outline-btn', 'cancel-edit-btn', 'outline-editor', 'outline-display');
    }
});