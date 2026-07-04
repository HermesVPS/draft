/**
 * Section Viewer Component
 * Alpine.js component for managing PDF section viewing and editing
 */
function sectionViewer() {
    return {
        sections: [],
        currentSectionId: null,
        currentSection: null,
        editing: false,
        editTitle: "",
        editContent: "",
        
        init() {
            // Initialize with the first section if available
            if (this.sections.length > 0) {
                this.selectSection(this.sections[0].id);
            }
        },
        
        selectSection(id) {
            this.currentSectionId = id;
            this.currentSection = this.sections.find(s => s.id === id);
            this.editing = false;
            // Reset edit form values
            this.editTitle = this.currentSection.title;
            this.editContent = this.currentSection.content;
        },
        
        startEditing() {
            this.editTitle = this.currentSection.title;
            this.editContent = this.currentSection.content;
            this.editing = true;
        },
        
        statusLabel(status) {
            switch(status) {
                case 'completed': return 'Complete';
                case 'in_progress': return 'In Progress';
                case 'failed': return 'Failed';
                default: return 'Pending';
            }
        },
        
        saveEdit() {
            // Submit form via AJAX
            const formData = new FormData();
            formData.append('title', this.editTitle);
            formData.append('content', this.editContent);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
            
            console.log(`Saving section ${this.currentSection.id} with title: ${this.editTitle} and content length: ${this.editContent.length}`);
            
            fetch(`/pdf/section/${this.currentSection.id}/edit/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (response.redirected) {
                    console.log('Redirected to:', response.url);
                    window.location.href = response.url;
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    console.log('Response data:', data);
                    if (data.success) {
                        // Update local data
                        const index = this.sections.findIndex(s => s.id === this.currentSection.id);
                        this.sections[index].title = this.editTitle;
                        this.sections[index].content = this.editContent;
                        this.sections[index].content_html = data.content_html;
                        this.currentSection = this.sections[index];
                        this.editing = false;
                    }
                }
            })
            .catch(error => {
                console.error('Error saving section:', error);
            });
        },
        
        cancelEdit() {
            this.editing = false;
        }
    };
}

// document.body.addEventListener('htmx:afterOnLoad', function(evt) {
//     // Check if the response has a progress value of 100
//     if (evt.detail.xhr.responseText.includes('value="100"')) {
//         // Refresh the page
//         window.location.reload();
//     }
// });