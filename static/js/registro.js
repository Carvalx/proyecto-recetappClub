// Validación de nombre de usuario
const userInput = document.querySelector('input[name="username"]');
const userTooltip = document.createElement('div');
userTooltip.className = 'pass-tooltip';
userTooltip.innerHTML = `
    <p id="req-user-len">✗ Máximo 30 caracteres</p>
    <p id="req-user-chars">✗ Solo letras, dígitos y @/./+/-/_</p>
`;
userInput.parentNode.insertBefore(userTooltip, userInput.nextSibling);

userInput.addEventListener('focus', () => userTooltip.style.display = 'block');
userInput.addEventListener('blur', () => userTooltip.style.display = 'none');
userInput.addEventListener('input', () => {
    const val = userInput.value;

    const lenOk = val.length <= 30 && val.length > 0;
    document.getElementById('req-user-len').innerHTML =
        (lenOk ? '✓' : '✗') + ' Máximo 30 caracteres';
    document.getElementById('req-user-len').style.color = lenOk ? 'green' : 'red';

    const charsOk = /^[\w@.+\-]+$/.test(val);
    document.getElementById('req-user-chars').innerHTML =
        (charsOk ? '✓' : '✗') + ' Solo letras, dígitos y @/./+/-/_';
    document.getElementById('req-user-chars').style.color = charsOk ? 'green' : 'red';
});

// Validación de contraseña
const passInput = document.querySelector('input[name="password1"]');
const tooltip = document.createElement('div');
tooltip.className = 'pass-tooltip';
tooltip.innerHTML = `
    <p id="req-len">✗ Mínimo 8 caracteres</p>
    <p id="req-num">✗ No puede ser solo números</p>
    <p id="req-common">✗ No puede ser demasiado común</p>
    `;
passInput.parentNode.insertBefore(tooltip, passInput.nextSibling);

passInput.addEventListener('focus', () => tooltip.style.display = 'block');
passInput.addEventListener('blur', () => tooltip.style.display = 'none');
passInput.addEventListener('input', () => {
    const val = passInput.value;
    document.getElementById('req-len').innerHTML =
        (val.length >= 8 ? '✓' : '✗') + ' Mínimo 8 caracteres';
    document.getElementById('req-len').style.color =
        val.length >= 8 ? 'green' : 'red';
    document.getElementById('req-num').innerHTML =
        (isNaN(val) ? '✓' : '✗') + ' No puede ser solo números';
    document.getElementById('req-num').style.color =
        isNaN(val) ? 'green' : 'red';
});
