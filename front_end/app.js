const input1 = document.getElementById('input1');
const input2 = document.getElementById('input2');
const table = document.querySelector('table');
const botonLimpiar = document.getElementById('limpiar-btn');
const continuarBtn = document.getElementById("continuar-btn");
let filasSeleccionadas = {};

// Ordena las filas por estado de selección
function ordenarFilas() {
  const filasSeleccionadas = [];
  const filasNoSeleccionadas = [];

  filas.forEach((fila) => {
    const checkbox = fila.querySelector("input[type='checkbox']");
    if (checkbox.checked) {
      filasSeleccionadas.push({fila: fila, seleccionada: true});
    } else {
      filasNoSeleccionadas.push({fila: fila, seleccionada: false});
    }
  });

  const filasOrdenadas = [...filasSeleccionadas, ...filasNoSeleccionadas];
  table.tBodies[0].innerHTML = '';
  filasOrdenadas.forEach((fila) => {
    table.tBodies[0].appendChild(fila.fila);
  });
}

// Llama a la función de ordenamiento cuando se actualice la selección
function actualizarCantidadSeleccionada() {
  const checkboxes = table.querySelectorAll('input[type="checkbox"]');
  let cantidadSeleccionada = 0;

  checkboxes.forEach((checkbox) => {
    if (checkbox.checked) {
      cantidadSeleccionada++;
      const fila = checkbox.closest('tr');
      const codigo = fila.cells[0].textContent.trim();
      const materia = fila.cells[1].textContent.trim();
      filasSeleccionadas[codigo] = {materia: materia, seleccionada: true};
    } else {
      const fila = checkbox.closest('tr');
      const codigo = fila.cells[0].textContent.trim();
      if (filasSeleccionadas.hasOwnProperty(codigo)) {
        delete filasSeleccionadas[codigo];
      }
    }
  });



  
  // Ordena las filas por estado de selección
  ordenarFilas();

  botonLimpiar.innerText = `Limpiar Seleccion (${cantidadSeleccionada}) seleccionados`;
  //console.log(filasSeleccionadas);
  
}



// Agrega un event listener para el evento `click` en cada fila de la tabla
const filas = document.querySelectorAll("tbody tr");
filas.forEach((fila) => {
  // Manejador de clic para la fila
  fila.addEventListener("click", (event) => {
    // Verificar si se hizo clic en la columna "FECHA" o en el <select>
    const fechaCelda = fila.querySelector("td:nth-child(4)"); // Ajusta el selector si la columna "FECHA" tiene un índice diferente
    const selectElement = event.target.closest("select");

    if (!fechaCelda.isSameNode(event.target) && !selectElement) {
      // No se hizo clic en la columna "FECHA" ni en el <select>
      // Buscar el checkbox correspondiente a la fila
      const checkbox = fila.querySelector("input[type='checkbox']");

      // Cambiar el estado del checkbox
      checkbox.checked = !checkbox.checked;
      actualizarCantidadSeleccionada();
    }
  });


  
  // Manejador de clic para el checkbox
  const checkbox = fila.querySelector("input[type='checkbox']");
  checkbox.addEventListener("click", (event) => {
    // Detener la propagación del evento
    event.stopPropagation();
  });
});



// Agrega un event listener para el evento `change` en cada checkbox
const checkboxes = table.querySelectorAll('input[type="checkbox"]');
checkboxes.forEach((checkbox) => {
  checkbox.addEventListener('change', actualizarCantidadSeleccionada);
});



// Define la función de filtrado
function filtrarTabla() {
  const valor1 = input1.value.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const valor2 = input2.value.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");

  // Itera por cada fila de la tabla, omitiendo la primera fila de encabezados
  for (let i = 1; i < table.rows.length; i++) {
    const fila = table.rows[i];
    const codigo = fila.cells[0].textContent.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const materia = fila.cells[1].textContent.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const checkbox = fila.cells[2].querySelector('input[type="checkbox"]');

    // Omitir las filas seleccionadas
    if (checkbox && checkbox.checked) {
      continue;
    }

    // Oculta las filas que no coinciden con los valores de filtro
    if (codigo.includes(valor1) && materia.includes(valor2)) {
      fila.style.display = '';
    } else {
      fila.style.display = 'none';
    }
  }
  ordenarFilas();
}

// Llama a la función de filtrado cuando se modifica cualquier input
input1.addEventListener('input', filtrarTabla);
input2.addEventListener('input', filtrarTabla);

continuarBtn.addEventListener('click', () => {
  const checkboxes = table.querySelectorAll('input[type="checkbox"]');
  const datosSeleccionados = {};

  checkboxes.forEach((checkbox) => {
    if (checkbox.checked) {
      const fila = checkbox.closest('tr');
      const codigo = fila.cells[0].textContent.trim();
      const materia = fila.cells[1].textContent.trim();
      const selectElement = fila.querySelector("select"); // Get the select element
      const selectedDate = selectElement.value; // Get the selected date from the select element

      datosSeleccionados[codigo] = {
        materia: materia,
        fecha: selectedDate
      };
    }
  });

  localStorage.setItem('datosSeleccionados', JSON.stringify(datosSeleccionados));
  if (Object.keys(datosSeleccionados).length === 0) {
  alert('Por favor selecciona al menos una materia para continuar')
} else {
  window.location.href = 'front_end/tabla_envio.html';
}
  
});


botonLimpiar.addEventListener('click', () => {
  const checkboxes = table.querySelectorAll('input[type="checkbox"]');
  let cantidadSeleccionada = 0;

  // Desmarca todos los checkboxes
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });

  // Actualiza el texto del botón
  botonLimpiar.innerText = `Limpiar Seleccion (${cantidadSeleccionada}) seleccionados`;
});

window.addEventListener('load', () => {
  const checkboxes = table.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });
});

