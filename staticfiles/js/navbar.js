const icon = document.querySelector('.icon');
const menu = document.querySelector('.menu');

function toggleNavbar() {
    menu.classList.toggle('active');
    icon.classList.toggle('active');
}

document.querySelector('.toggle-btn').addEventListener('click', toggleNavbar);
