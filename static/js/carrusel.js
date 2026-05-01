let slideActual = 0;
let intervalo = null;
const totalSlides = 5;
const DURACION = 5000;

function mostrarSlide(n) {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    slides.forEach(s => s.classList.remove('active'));
    dots.forEach(d => d.classList.remove('active'));
    slideActual = (n + totalSlides) % totalSlides;
    slides[slideActual].classList.add('active');
    dots[slideActual].classList.add('active');
}

function cambiarSlide(direccion) {
    mostrarSlide(slideActual + direccion);
    reiniciarIntervalo();
}

function irASlide(n) {
    mostrarSlide(n);
    reiniciarIntervalo();
}

function iniciarIntervalo() {
    if (intervalo) clearInterval(intervalo);
    intervalo = setInterval(() => {
        mostrarSlide(slideActual + 1);
    }, DURACION);
}

function reiniciarIntervalo() {
    if (intervalo) clearInterval(intervalo);
    intervalo = null;
    iniciarIntervalo();
}

function pararIntervalo() {
    if (intervalo) clearInterval(intervalo);
    intervalo = null;
}

function reanudarIntervalo() {
    if (!intervalo) iniciarIntervalo();
}

document.addEventListener('DOMContentLoaded', function () {
    const carrusel = document.getElementById('carrusel');
    if (carrusel) {
        carrusel.addEventListener('mouseenter', pararIntervalo);
        carrusel.addEventListener('mouseleave', reanudarIntervalo);
        iniciarIntervalo();
    }
});