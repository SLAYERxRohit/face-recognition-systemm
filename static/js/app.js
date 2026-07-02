// Viesta: The Face Recognition App - Frontend Interaction Script

document.addEventListener('DOMContentLoaded', () => {
    // 1. Drag and Drop Image Uploader
    const dropZone = document.getElementById('upload-container');
    const fileInput = document.getElementById('image-file-input');
    const previewWrapper = document.getElementById('preview-wrapper');
    const filePreview = document.getElementById('file-preview');
    const uploadPrompt = document.getElementById('upload-prompt');
    const predictForm = document.getElementById('predict-form');

    if (dropZone && fileInput) {
        // Trigger click on file input when clicking dropZone
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });

        // Drag events
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'dragend', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            }, false);
        });

        // Drop event
        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                handleFiles(files);
            }
        });

        // File input change
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                handleFiles(fileInput.files);
            }
        });
    }

    function handleFiles(files) {
        const file = files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                filePreview.src = e.target.result;
                previewWrapper.style.display = 'block';
                uploadPrompt.innerHTML = `<strong>Selected file:</strong> ${file.name}<br><span class="text-muted">Click or drag another to replace</span>`;
            };
            reader.readAsDataURL(file);
        }
    }

    // 2. Simulated Multi-Step Prediction Loading Overlay
    if (predictForm) {
        predictForm.addEventListener('submit', (e) => {
            // Check if file is selected
            if (!fileInput.files || fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please select or drop an image file first.');
                return;
            }

            // Show loading overlay
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.classList.add('active');
                
                // Animate loading steps
                const steps = document.querySelectorAll('.loading-step');
                if (steps.length > 0) {
                    // Step 1 active immediately
                    steps[0].classList.add('active');
                    
                    // Step 2 active after 800ms
                    setTimeout(() => {
                        steps[0].classList.remove('active');
                        steps[0].classList.add('completed');
                        steps[1].classList.add('active');
                    }, 800);

                    // Step 3 active after 1600ms
                    setTimeout(() => {
                        steps[1].classList.remove('active');
                        steps[1].classList.add('completed');
                        steps[2].classList.add('active');
                    }, 1600);

                    // Step 4 active after 2400ms
                    setTimeout(() => {
                        steps[2].classList.remove('active');
                        steps[2].classList.add('completed');
                        steps[3].classList.add('active');
                    }, 2400);
                }
            }
        });
    }
});
