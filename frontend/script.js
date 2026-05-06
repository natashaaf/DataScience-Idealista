// Toggle cards
document.querySelectorAll('.toggle-card').forEach(el => {
  el.addEventListener('click', () => el.classList.toggle('on'));
});

function isOn(id) {
  const element = document.querySelector(`.toggle-card[data-id="${id}"]`);
  return element && element.classList.contains('on') ? 1 : 0;
}

// Intersection observer for fade-in
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

async function calcular() {
  const btn = document.getElementById('calcBtn');
  const errBox = document.getElementById('errorBox');
  
  if (errBox) errBox.classList.remove('show');

  const metros = parseFloat(document.getElementById('metros').value) || 80;
  const habs = parseInt(document.getElementById('habitaciones').value) || 2;
  const banos = parseInt(document.getElementById('banos').value) || 1;
  const planta = parseInt(document.getElementById('planta').value) || 1;
  const zonaEl = document.getElementById('zona');
  const zona = zonaEl.value;
  const zonaNombre = zonaEl.options[zonaEl.selectedIndex].text;

  // UI Loading state
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Calculando…';

  const payload = {
    metros,
    habitaciones: habs,
    baños: banos,
    zona,
    ascensor_S: isOn('ascensor'),
    es_exterior: isOn('exterior'),
    planta_num: planta,
    extra_piscina: 0,
    extra_terraza: 0,
    extra_garaje: isOn('garaje'),
    extra_reformado: isOn('reformado'),
    metros_por_hab: metros / (habs || 1),
    ratio_banos: banos / (habs || 1)
  };

  try {
    const res = await fetch('http://localhost:8000/prever', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error del servidor');

    const precio = data["Precio estimado"];
    const fmt = n => new Intl.NumberFormat('es-ES', { 
      style: 'currency', 
      currency: 'EUR', 
      maximumFractionDigits: 0 
    }).format(n);

    // Update results in DOM
    const resultContent = document.getElementById('resultContent');
    if (resultContent) {
      resultContent.innerHTML = `
        <div style="text-align: center; padding: 2.5rem;">
          <div class="result-label-sm">Precio estimado</div>
          <div class="result-price">${fmt(precio)}</div>
          <div class="result-sqm">${fmt(Math.round(precio / metros))} / m²</div>
        </div>`;
    }

    // Update metadata
    const updateText = (id, text) => {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    };

    updateText('metaZona', zonaNombre);
    updateText('metaMetros', metros + ' m²');
    updateText('metaHabs', habs + (habs === 1 ? ' hab.' : ' habs.'));
    updateText('metaPlanta', planta === 0 ? 'Baja' : planta + 'ª');
    
    const resultBody = document.getElementById('resultBody');
    if (resultBody) resultBody.style.display = 'block';

  } catch (err) {
    if (errBox) {
      errBox.textContent = err.message.includes('fetch') 
        ? '⚠ No se pudo conectar con el servidor. Comprueba que uvicorn esté corriendo en localhost:8000.' 
        : '⚠ ' + err.message;
      errBox.classList.add('show');
    }
    console.error(err);
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Estimar precio con IA →';
  }
}

// Expose function to global scope if needed for inline onclick attributes
window.calcular = calcular;
