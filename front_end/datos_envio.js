// Se traen los datos a ingresar en el DW
const datosSeleccionados = JSON.parse(localStorage.getItem('datosSeleccionados'));

//  Envio el formulario al servidor
const formulario = {};
let puerto = 3000
function enviarDatos(formulario) {
  fetch(`http://localhost:${puerto}/guardar-datos`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ formulario }),
  })
    .then((response) => {
      if (response.ok) {
        alert('Datos guardados exitosamente!');
        window.location.href = '../index.html';
      } else {
        alert('Error al guardar los datos. Ya existe una alerta generada para esa asignatura en esa fecha.');
      }
    })
    .catch((error) => {
      alert('Error al guardar los datos');
    });
}


if (datosSeleccionados) {
  const table = document.querySelector('table');

  // Agregar las filas correspondientes a la tabla
  Object.entries(datosSeleccionados).forEach(([codigo, datos]) => {
    const row = table.insertRow(-1);
    const cellCodigo = row.insertCell(0);
    const cellMateria = row.insertCell(1);
    const cellFecha = row.insertCell(2);

    cellCodigo.textContent = codigo;
    cellMateria.textContent = datos.materia;
    cellFecha.textContent = datos.fecha;

    formulario[codigo] = {
      materia: datos.materia,
      email: "",
      codigo:codigo,
      fecha:datos.fecha
    };
  });
  
}

function validarFormulario() {
  const emailInput = document.getElementById("email");
  const emailValue = emailInput.value;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(emailValue)) {
    alert("Correo electrónico inválido");
    return false;
  }

  // Enviar formulario si el correo electrónico es válido
  for (const codigo in formulario) {
    if (formulario.hasOwnProperty(codigo)) {
      if (emailValue.includes('@')) {
        formulario[codigo].medio = "MAIL";
      } else {
        formulario[codigo].medio = "MOVIL";
      }
      formulario[codigo].email = emailValue;
    }
  }

enviarDatos(formulario);
}


