// static/script.js

// Copy ASCII to clipboard with toast notification
targetCopyBtnId = 'copyBtn';
function copyText() {
    let box = document.getElementById("asciiBox");
    navigator.clipboard.writeText(box.value).then(() => {
        const toast = document.createElement("div");
        toast.textContent = "Copied to Clipboard";
        toast.classList.add("toast");

        const rect = document.getElementById(targetCopyBtnId).getBoundingClientRect();
        toast.style.top = (window.scrollY + rect.top + 40) + "px";
        toast.style.left = (window.scrollX + rect.left) + "px";

        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 1500);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.querySelector('input[type="file"]');
    const dropZone   = document.getElementById("dropZone");
    const preview    = document.querySelector('.preview-image');
    const dragField  = document.querySelector(".custom-input");
    const copyBtn    = document.getElementById(targetCopyBtnId);
    const resetBtn = document.getElementById("resetBtn");

    // Attach copy handler
    if (copyBtn) {
        copyBtn.addEventListener('click', copyText);
    }

    // File drag & drop
    if (dropZone && fileInput) {
        dropZone.addEventListener("dragover", e => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });
        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("dragover");
        });
        dropZone.addEventListener("drop", e => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith("image/")) {
                fileInput.files = e.dataTransfer.files;
                fileInput.dispatchEvent(new Event("change"));
            }
        });
    }

    // Restore image preview from localStorage
    const cachedPreview = localStorage.getItem("previewImage");
    if (cachedPreview && preview) {
        preview.src = cachedPreview;
        preview.style.display = "block";
    }

    // Preview on file select
    if (fileInput && preview) {
        fileInput.addEventListener("change", () => {
            const file = fileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = e => {
                    const dataURL = e.target.result;
                    preview.src = dataURL;
                    preview.style.display = "block";
                    localStorage.setItem("previewImage", dataURL);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Clear preview on reset
    if (resetBtn) {
        localStorage.removeItem("previewImage");
        resetBtn.addEventListener("click", () => location.reload());
    }

    // Click-and-drag + wheel adjust for custom width input
    if (dragField) {
        let isDragging = false;
        let startX = 0;
        let startValue = 0;

        dragField.addEventListener("mousedown", e => {
            startX = e.clientX;
            startValue = parseInt(dragField.value) || 0;
            const onMove = moveEvent => {
                const diff = moveEvent.clientX - startX;
                if (!isDragging && Math.abs(diff) >= 2) {
                    isDragging = true;
                    document.body.style.cursor = "ew-resize";
                }
                if (isDragging) {
                    const snapped = Math.round((startValue + diff) / 10) * 10;
                    dragField.value = Math.max(10, Math.min(300, snapped));
                }
            };
            const onUp = () => {
                isDragging = false;
                document.body.style.cursor = "";
                document.removeEventListener("mousemove", onMove);
                document.removeEventListener("mouseup", onUp);
            };
            document.addEventListener("mousemove", onMove);
            document.addEventListener("mouseup", onUp);
        });
        dragField.addEventListener("wheel", e => {
            e.preventDefault();
            const delta = e.deltaY < 0 ? 1 : -1;
            let val = parseInt(dragField.value) || 60;
            dragField.value = Math.max(10, Math.min(300, val + delta));
        });
    }

    // ——— Live preview ———
    const form      = document.getElementById('ascii-form');
    const outputBox = document.getElementById('asciiBox');
    if (form && outputBox) {
        let timer;
        form.addEventListener('input', () => {
            clearTimeout(timer);
            timer = setTimeout(async () => {
                const fd = new FormData(form);
                const res = await fetch('/preview', { method: 'POST', body: fd });
                const { result } = await res.json();
                outputBox.value = result;
            }, 300);
        });
    }
});