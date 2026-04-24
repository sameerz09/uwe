/** UWE Sign Dialog — Auto / Draw / Load signature */
(function () {
    'use strict';

    /* ─── State ─────────────────────────────────────── */
    let currentTab = 'auto';
    let isDrawing  = false;
    let lastX = 0, lastY = 0;
    let docId = null;

    /* ─── Canvas helpers ─────────────────────────────── */
    function canvas(id)  { return document.getElementById(id); }
    function ctx(id)     { return canvas(id).getContext('2d'); }

    function clearCanvas(id) {
        const c = canvas(id);
        if (!c) return;
        c.getContext('2d').clearRect(0, 0, c.width, c.height);
    }

    function resizeCanvas(id) {
        const c  = canvas(id);
        const w  = c.parentElement.clientWidth || 740;
        c.width  = w;
    }

    /* ─── Auto tab ───────────────────────────────────── */
    function renderAutoSignature(name) {
        const c  = canvas('uweCanvasAuto');
        const cx = c.getContext('2d');
        cx.clearRect(0, 0, c.width, c.height);
        if (!name.trim()) return;

        // Draw baseline
        cx.strokeStyle = '#ccc';
        cx.lineWidth   = 1;
        cx.beginPath();
        cx.moveTo(20, c.height - 40);
        cx.lineTo(c.width - 20, c.height - 40);
        cx.stroke();

        // Draw name in cursive style
        cx.fillStyle   = '#1a1a2e';
        cx.textBaseline = 'alphabetic';

        const fonts = [
            'italic 52px "Brush Script MT", cursive',
            'italic 52px "Comic Sans MS", cursive',
            'italic 52px cursive',
        ];
        cx.font = fonts[0];
        const measured = cx.measureText(name);
        const fontSize = Math.min(52, Math.floor(52 * (c.width - 40) / (measured.width + 40)));
        cx.font = `italic ${fontSize}px "Brush Script MT", cursive`;
        cx.fillText(name, 30, c.height - 50);
    }

    /* ─── Draw tab ───────────────────────────────────── */
    function getPos(e, c) {
        const r = c.getBoundingClientRect();
        const src = e.touches ? e.touches[0] : e;
        return {
            x: (src.clientX - r.left) * (c.width  / r.width),
            y: (src.clientY - r.top)  * (c.height / r.height),
        };
    }

    function drawStart(e) {
        isDrawing = true;
        const c = canvas('uweCanvasDraw');
        const p = getPos(e, c);
        lastX = p.x; lastY = p.y;
        e.preventDefault();
    }

    function drawMove(e) {
        if (!isDrawing) return;
        e.preventDefault();
        const c  = canvas('uweCanvasDraw');
        const cx = c.getContext('2d');
        const p  = getPos(e, c);

        cx.strokeStyle = '#1a1a2e';
        cx.lineWidth   = 2.5;
        cx.lineCap     = 'round';
        cx.lineJoin    = 'round';
        cx.beginPath();
        cx.moveTo(lastX, lastY);
        cx.lineTo(p.x, p.y);
        cx.stroke();

        lastX = p.x; lastY = p.y;
    }

    function drawEnd(e) { isDrawing = false; }

    function bindDrawEvents() {
        const c = canvas('uweCanvasDraw');
        if (!c || c._uweBound) return;
        c._uweBound = true;

        c.addEventListener('mousedown',  drawStart);
        c.addEventListener('mousemove',  drawMove);
        c.addEventListener('mouseup',    drawEnd);
        c.addEventListener('mouseleave', drawEnd);
        c.addEventListener('touchstart', drawStart, { passive: false });
        c.addEventListener('touchmove',  drawMove,  { passive: false });
        c.addEventListener('touchend',   drawEnd);
    }

    /* ─── Load tab ───────────────────────────────────── */
    function bindLoadEvents() {
        const inp = document.getElementById('uweSignFile');
        if (!inp || inp._uweBound) return;
        inp._uweBound = true;

        inp.addEventListener('change', function () {
            const file = inp.files[0];
            if (!file) return;
            inp.nextElementSibling.textContent = file.name;
            const reader = new FileReader();
            reader.onload = function (ev) {
                const img = new Image();
                img.onload = function () {
                    const c  = canvas('uweCanvasLoad');
                    const cx = c.getContext('2d');
                    cx.clearRect(0, 0, c.width, c.height);
                    const scale = Math.min(c.width / img.width, c.height / img.height, 1);
                    const w = img.width  * scale;
                    const h = img.height * scale;
                    cx.drawImage(img, (c.width - w) / 2, (c.height - h) / 2, w, h);
                };
                img.src = ev.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    /* ─── Active canvas data URL ─────────────────────── */
    function getSignatureDataURL() {
        const map = { auto: 'uweCanvasAuto', draw: 'uweCanvasDraw', load: 'uweCanvasLoad' };
        const c = canvas(map[currentTab]);
        return c ? c.toDataURL('image/png') : null;
    }

    function isCanvasEmpty(id) {
        const c = canvas(id);
        if (!c) return true;
        const data = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
        return !data.some(v => v !== 0);
    }

    /* ─── Tab switching ──────────────────────────────── */
    function switchTab(tab) {
        currentTab = tab;
        document.querySelectorAll('.uwe-sign-tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });
        document.querySelectorAll('.uwe-sign-tab-panel').forEach(panel => {
            panel.classList.add('d-none');
        });
        const panels = { auto: 'uweTabAuto', draw: 'uweTabDraw', load: 'uweTabLoad' };
        const el = document.getElementById(panels[tab]);
        if (el) el.classList.remove('d-none');

        if (tab === 'draw') bindDrawEvents();
        if (tab === 'load') bindLoadEvents();
    }

    /* ─── Submit ─────────────────────────────────────── */
    function submitSignature() {
        const map = { auto: 'uweCanvasAuto', draw: 'uweCanvasDraw', load: 'uweCanvasLoad' };

        if (currentTab === 'auto') {
            const name = (document.getElementById('uweSignName') || {}).value || '';
            if (!name.trim()) { alert('Please type your name to generate a signature.'); return; }
            renderAutoSignature(name);
        }

        if (isCanvasEmpty(map[currentTab])) {
            alert('Please provide a signature before adopting.');
            return;
        }

        const dataURL = getSignatureDataURL();
        const btn     = document.getElementById('uweAdoptAndSign');
        btn.disabled  = true;
        btn.textContent = 'Saving…';

        fetch(`/my/sign/${docId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                id: 1,
                params: { signature: dataURL },
            }),
        })
        .then(r => r.json())
        .then(data => {
            const result = data.result || {};
            if (result.success) {
                // Hide modal then reload
                const modal = document.getElementById('uweSignModal');
                if (typeof $ !== 'undefined') {
                    $(modal).modal('hide');
                } else {
                    modal.style.display = 'none';
                    document.body.classList.remove('modal-open');
                }
                window.location.href = `/my/sign/${docId}?success=1`;
            } else {
                alert(result.error || 'An error occurred. Please try again.');
                btn.disabled    = false;
                btn.textContent = 'Adopt & Sign';
            }
        })
        .catch(() => {
            alert('Network error. Please try again.');
            btn.disabled    = false;
            btn.textContent = 'Adopt & Sign';
        });
    }

    /* ─── Clear button ───────────────────────────────── */
    function clearCurrent() {
        const map = { auto: 'uweCanvasAuto', draw: 'uweCanvasDraw', load: 'uweCanvasLoad' };
        clearCanvas(map[currentTab]);
        if (currentTab === 'auto') {
            const inp = document.getElementById('uweSignName');
            if (inp) inp.value = '';
        }
        if (currentTab === 'load') {
            const inp = document.getElementById('uweSignFile');
            if (inp) { inp.value = ''; inp.nextElementSibling.textContent = 'Choose image file…'; }
        }
    }

    /* ─── Init ───────────────────────────────────────── */
    function init() {
        // Open dialog
        document.querySelectorAll('.uwe-sign-open-dialog').forEach(btn => {
            btn.addEventListener('click', function () {
                docId = this.dataset.docId;
                const userName = this.dataset.userName || '';

                // Reset dialog state
                switchTab('auto');
                clearCanvas('uweCanvasAuto');
                clearCanvas('uweCanvasDraw');
                clearCanvas('uweCanvasLoad');

                // Pre-fill name and render
                const nameInp = document.getElementById('uweSignName');
                if (nameInp) {
                    nameInp.value = userName;
                    renderAutoSignature(userName);
                }

                // Resize canvases to container width
                ['uweCanvasAuto', 'uweCanvasDraw', 'uweCanvasLoad'].forEach(id => {
                    const c = canvas(id);
                    if (c) {
                        const w = c.parentElement.clientWidth;
                        if (w > 0) c.width = w;
                    }
                });
                if (nameInp) renderAutoSignature(nameInp.value);

                const modal = document.getElementById('uweSignModal');
                if (typeof $ !== 'undefined') {
                    $(modal).modal('show');
                } else {
                    modal.style.display = 'flex';
                    document.body.classList.add('modal-open');
                }
            });
        });

        // Tab buttons
        document.querySelectorAll('.uwe-sign-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => switchTab(btn.dataset.tab));
        });

        // Auto: re-render on input
        const nameInp = document.getElementById('uweSignName');
        if (nameInp) {
            nameInp.addEventListener('input', () => renderAutoSignature(nameInp.value));
        }

        // Clear
        const clearBtn = document.querySelector('.uwe-sign-clear-btn');
        if (clearBtn) clearBtn.addEventListener('click', clearCurrent);

        // Adopt & Sign
        const adoptBtn = document.getElementById('uweAdoptAndSign');
        if (adoptBtn) adoptBtn.addEventListener('click', submitSignature);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
