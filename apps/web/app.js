'use strict';
document.getElementById('print')?.addEventListener('click', () => {
  document.querySelector('.printable').open = true;
  window.print();
});
document.getElementById('language')?.addEventListener('click', event => {
  const form = document.querySelector('form');
  form.querySelector('input[name=language]').value = event.currentTarget.dataset.language;
  form.requestSubmit();
});
