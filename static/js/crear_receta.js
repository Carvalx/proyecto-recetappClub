// ── AUTOCOMPLETADO Open Food Facts ──────────────────────────
function configurarAutocompletado(input, idSugerencias) {
    let timer;
    const caja = document.getElementById(idSugerencias);
    if (!caja) return;

    input.addEventListener('input', () => {
        clearTimeout(timer);
        const q = input.value.trim();
        if (q.length < 2) {
            caja.innerHTML = '';
            caja.classList.remove('activa');
            return;
        }

        timer = setTimeout(async () => {
            try {
                const url = `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(q)}&search_simple=1&action=process&json=1&page_size=6&lc=es`;
                const res = await fetch(url);
                const data = await res.json();
                const productos = data.products || [];

                const nombres = [...new Set(
                    productos
                        .map(p => p.product_name_es || p.product_name || '')
                        .filter(n => n.length > 0 && n.length < 60)
                )].slice(0, 6);

                if (nombres.length === 0) {
                    caja.innerHTML = '';
                    caja.classList.remove('activa');
                    return;
                }

                caja.innerHTML = nombres
                    .map(n => `<div class="sugerencia-item" onmousedown="elegirSugerencia(this)">${n}</div>`)
                    .join('');
                caja.classList.add('activa');
            } catch (e) {
                caja.innerHTML = '';
                caja.classList.remove('activa');
            }
        }, 350);
    });

    input.addEventListener('blur', () => {
        setTimeout(() => {
            caja.innerHTML = '';
            caja.classList.remove('activa');
        }, 200);
    });
}

function elegirSugerencia(el) {
    const fila = el.closest('.ingrediente-fila');
    const input = fila.querySelector('input[name$="-nombre"]');
    const caja = fila.querySelector('.ingrediente-sugerencias');
    input.value = el.textContent;
    caja.innerHTML = '';
    caja.classList.remove('activa');
}

// ── AÑADIR / ELIMINAR FILAS ──────────────────────────────────
function getTotalForms() {
    return parseInt(document.getElementById('id_ingredientes-TOTAL_FORMS').value);
}

function setTotalForms(n) {
    document.getElementById('id_ingredientes-TOTAL_FORMS').value = n;
}

function añadirFila() {
    const total = getTotalForms();
    const lista = document.getElementById('ingredientes-lista');
    const idSug = `sugerencias-${total}`;

    const fila = document.createElement('div');
    fila.className = 'ingrediente-fila';
    fila.id = `fila-${total}`;
    fila.innerHTML = `
        <div class="ingrediente-nombre-wrap">
            <input type="text"
                   name="ingredientes-${total}-nombre"
                   id="id_ingredientes-${total}-nombre"
                   placeholder="Nombre del ingrediente"
                   maxlength="100"
                   autocomplete="off">
            <div class="ingrediente-sugerencias" id="${idSug}"></div>
        </div>
        <div class="ingrediente-cantidad-wrap">
            <input type="text"
                   name="ingredientes-${total}-cantidad"
                   id="id_ingredientes-${total}-cantidad"
                   placeholder="Ej: 200g, 2 tazas, 1/2 kg"
                   maxlength="50">
        </div>
        <button type="button" class="btn-eliminar-fila" onclick="eliminarFila(this)" title="Eliminar ingrediente">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
        <input type="hidden" name="ingredientes-${total}-id" id="id_ingredientes-${total}-id">
    `;

    lista.appendChild(fila);
    setTotalForms(total + 1);

    const inputNombre = fila.querySelector('input[name$="-nombre"]');
    configurarAutocompletado(inputNombre, idSug);
    inputNombre.focus();
}

function eliminarFila(btn) {
    const fila = btn.closest('.ingrediente-fila');
    const checkbox = fila.querySelector('input[type="checkbox"]');
    if (checkbox) {
        checkbox.checked = true;
        fila.style.display = 'none';
    } else {
        fila.remove();
        setTotalForms(getTotalForms() - 1);
    }
}

// ── INICIALIZAR en filas existentes ─────────────────────────
document.querySelectorAll('.ingrediente-fila').forEach((fila, i) => {
    const input = fila.querySelector('input[name$="-nombre"]');
    const idSug = `sugerencias-${i}`;
    if (input) configurarAutocompletado(input, idSug);
});

// ── IMAGEN: PREVISUALIZACIÓN, RECORTE Y ELIMINAR ─────────────
const inputImagen = document.getElementById('id_imagen');
const preview = document.getElementById('imagen-preview');
const previewWrap = document.getElementById('imagen-preview-wrap');
const hint = document.getElementById('imagen-hint');
const sub = document.getElementById('imagen-sub');
const uploadArea = document.getElementById('imagen-upload-area');
const inputRecortada = document.getElementById('imagen_recortada');
const clearBtn = document.getElementById('imagen-clear-btn');
const clearCheck = document.getElementById('imagen-clear');

const cropperModal = document.getElementById('cropper-modal');
const cropperImg = document.getElementById('cropper-img');
const btnConfirmar = document.getElementById('cropper-confirmar');
const btnCancelar = document.getElementById('cropper-cancelar');

let cropperInstance = null;

if (uploadArea) {
    uploadArea.addEventListener('click', (e) => {
        if (e.target.closest('.imagen-clear-x')) return;
        if (previewWrap && previewWrap.style.display !== 'none') return;
        inputImagen.click();
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) abrirRecortador(file);
    });

    inputImagen.addEventListener('change', () => {
        if (inputImagen.files[0]) abrirRecortador(inputImagen.files[0]);
    });
}

function abrirRecortador(file) {
    const formatos = ['image/jpeg', 'image/png', 'image/webp'];
    if (!formatos.includes(file.type)) {
        alert('Formato no soportado. Usa JPG, PNG o WebP.');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        cropperImg.src = e.target.result;
        cropperModal.classList.add('activo');

        if (cropperInstance) cropperInstance.destroy();
        cropperInstance = new Cropper(cropperImg, {
            aspectRatio: 800 / 600,
            viewMode: 2,
            autoCropArea: 1,
        });
    };
    reader.readAsDataURL(file);
}

if (btnConfirmar) {
    btnConfirmar.addEventListener('click', () => {
        if (!cropperInstance) return;

        const canvas = cropperInstance.getCroppedCanvas({ width: 800, height: 600 });
        const base64 = canvas.toDataURL('image/jpeg', 0.88);

        preview.src = base64;
        previewWrap.style.display = 'block';
        if (hint) hint.style.display = 'none';
        if (sub) sub.style.display = 'none';
        inputRecortada.value = base64;

        cerrarRecortador();
    });
}

if (btnCancelar) {
    btnCancelar.addEventListener('click', cerrarRecortador);
}

function cerrarRecortador() {
    cropperModal.classList.remove('activo');
    if (cropperInstance) { cropperInstance.destroy(); cropperInstance = null; }
    inputImagen.value = '';
}

if (clearBtn) {
    clearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        preview.src = '';
        previewWrap.style.display = 'none';
        if (hint) hint.style.display = 'block';
        if (sub) sub.style.display = 'block';
        inputRecortada.value = '';
        inputImagen.value = '';
        if (clearCheck) clearCheck.checked = true;
    });
}