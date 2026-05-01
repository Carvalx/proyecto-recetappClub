const btnScrollTop = document.getElementById('btn-scroll-top');

window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
        btnScrollTop.classList.add('visible');
    } else {
        btnScrollTop.classList.remove('visible');
    }
});

btnScrollTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});