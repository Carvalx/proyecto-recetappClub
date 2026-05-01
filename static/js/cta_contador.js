function animarContador(elemento, objetivo, duracion) {
    let inicio = 0;
    const incremento = objetivo / (duracion / 16);

    const timer = setInterval(() => {
        inicio += incremento;
        if (inicio >= objetivo) {
            inicio = objetivo;
            clearInterval(timer);
        }
        elemento.textContent = '+' + Math.floor(inicio);
    }, 16);
}

function iniciarContadores() {
    const stats = document.querySelectorAll('.cta-stat-num[data-objetivo]');

    stats.forEach(el => {
        const objetivo = parseInt(el.dataset.objetivo);
        const prefijo = el.dataset.prefijo || '';
        const sufijo = el.dataset.sufijo || '';
        let inicio = 0;
        const duracion = 1500;
        const incremento = objetivo / (duracion / 16);

        const timer = setInterval(() => {
            inicio += incremento;
            if (inicio >= objetivo) {
                inicio = objetivo;
                clearInterval(timer);
            }
            el.textContent = prefijo + Math.floor(inicio) + sufijo;
        }, 16);
    });
}

// Arranca cuando el bloque CTA entra en pantalla
const ctaSection = document.querySelector('.cta-section');
if (ctaSection) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                iniciarContadores();
                observer.disconnect(); // solo una vez
            }
        });
    }, { threshold: 0.3 });

    observer.observe(ctaSection);
}