function copyText() {
    let box = document.getElementById("asciiBox");
    navigator.clipboard.writeText(box.value).then(() => {
        const toast = document.createElement("div");
        toast.textContent = "Copied";
        toast.classList.add("toast");

        const rect = document.getElementById("copyBtn").getBoundingClientRect();
        toast.style.top = (window.scrollY + rect.top + 2) + "px";
        toast.style.left = (window.scrollX + rect.left + 64) + "px";

        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 1500);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.querySelector('input[type="file"]');
    const dropZone = document.getElementById("dropZone");
    const preview = document.querySelector('.preview-image');
    const resetBtn = document.querySelector('button[name="reset"]');
    const dragField = document.querySelector(".custom-input");
    
    if (dropZone && fileInput) {
        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });

        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("dragover");
        });

        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith("image/")) {
                fileInput.files = e.dataTransfer.files;
                fileInput.dispatchEvent(new Event("change")); // trigger preview logic
            }
        });
    }

    // ✅ Restore preview from localStorage
    const cachedPreview = localStorage.getItem("previewImage");
    if (cachedPreview && preview) {
        preview.src = cachedPreview;
        preview.style.display = "block";
    }

    // ✅ Preview on file select
    if (fileInput && preview) {
        fileInput.addEventListener("change", () => {
            const file = fileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const dataURL = e.target.result;
                    preview.src = dataURL;
                    preview.style.display = "block";
                    localStorage.setItem("previewImage", dataURL);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ✅ Clear preview on reset
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            localStorage.removeItem("previewImage");
        });
    }

    // ✅ Click-and-drag + scroll on custom input
    if (dragField) {
        let isDragging = false;
        let startX = 0;
        let startValue = 0;

        dragField.addEventListener("mousedown", (e) => {
            isDragging = false;
            startX = e.clientX;
            startValue = parseInt(dragField.value) || 0;

            const onMouseMove = (moveEvent) => {
                const diff = moveEvent.clientX - startX;
                if (!isDragging && Math.abs(diff) >= 2) {
                    isDragging = true;
                    document.body.style.cursor = "ew-resize";
                }

                if (isDragging) {
                    const step = 10;
                    const raw = startValue + diff;
                    const snapped = Math.round(raw / step) * step;
                    const newVal = Math.max(10, Math.min(300, snapped));
                    dragField.value = newVal;
                }
            };

            const onMouseUp = () => {
                isDragging = false;
                document.body.style.cursor = "";
                document.removeEventListener("mousemove", onMouseMove);
                document.removeEventListener("mouseup", onMouseUp);
            };

            document.addEventListener("mousemove", onMouseMove);
            document.addEventListener("mouseup", onMouseUp);
        });


        document.addEventListener("mousemove", (e) => {
            if (isDragging) {
                const diff = e.clientX - startX;
                const newVal = Math.max(10, Math.min(300, startValue + diff));
                dragField.value = newVal;
            }
        });

        document.addEventListener("mouseup", () => {
            if (isDragging) {
                isDragging = false;
                document.body.style.cursor = "";
            }
        });

        dragField.addEventListener("wheel", (e) => {
            e.preventDefault();
            const delta = e.deltaY < 0 ? 1 : -1;
            let val = parseInt(dragField.value) || 60;
            dragField.value = Math.max(10, Math.min(300, val + delta));
        });
    }
});
