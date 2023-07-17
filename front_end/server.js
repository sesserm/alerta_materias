// Importo librerias a utilizar
const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const dotenv = require("dotenv");
dotenv.config();
const nodemailer = require('nodemailer');


// Configura la conexión a la base de datos PostgreSQL
const pool = new Pool({
  user: process.env.PGUSER,
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  password: process.env.PGPASSWORD,
  port: process.env.PGPORT, 
});

const app = express();
const port = process.env.SERVERPORT;
app.use(express.json());
app.use(cors()); // Habilita los encabezados CORS en las respuestas del servidor

let email = "";

app.post('/api/guardar-datos', (req, res) => {
  const formulario = req.body.formulario;
  const nuevo_formulario = [];
  let materiasSeleccionadas = []; // Variable para almacenar las materias seleccionadas

  for (const clave in formulario) {
    if (formulario.hasOwnProperty(clave)) {
      const elemento = formulario[clave];
      const materia = elemento.materia;
      email = elemento.email;
      const medio = elemento.medio;
      const codigo = clave;
      let fechaString = elemento.fecha;
      const [dia, mes, anio] = fechaString.split('-');
      // Crea una nueva cadena de texto con el formato correcto
      const fechaFormateada = `${anio}-${mes}-${dia}`;

      nuevo_formulario.push({
        materia: materia,
        email: email,
        medio: medio,
        codigo: codigo,
        fecha: fechaFormateada
      });
      materiasSeleccionadas.push({ materia: materia, codigo: codigo, fecha: fechaFormateada });
    }
  }

  const promises = nuevo_formulario.map((elemento) => {
    const materia = elemento.materia;
    const email = elemento.email;
    const medio = elemento.medio;
    const codigo = elemento.codigo;
    let fecha = elemento.fecha;

    return pool.query('INSERT INTO alerta_facultad.usuarios (usuario, codigo, materia, medio, fecha_evaluacion) VALUES ($1, $2, $3, $4, $5)', [email, codigo, materia, medio, fecha]);
  });
  
  let transporter = nodemailer.createTransport({
                            service: "gmail",
                            auth: {
                            user: process.env.MAIL,
                            pass: process.env.PASSMAIL
                                }
                            })

  Promise.all(promises)
    .then(() => {
      res.sendStatus(200); // Responde con un código 200 para indicar que se guardaron los datos correctamente
      let textoMaterias = ""; // Variable para almacenar el texto de las materias seleccionadas

      for (const materiaSeleccionada of materiasSeleccionadas) {
        const materia = materiaSeleccionada.materia;
        const codigo = materiaSeleccionada.codigo;
        const fecha = materiaSeleccionada.fecha;
        textoMaterias += `Materia: ${materia}\nCódigo: ${codigo}\nFecha: ${fecha}\n\n`;
      }

      let configuracion = {
                            from: process.env.MAIL,
                            to: email,
                            subject: "Confirmación de alerta",
                            text: `Gracias por utilizar el sistema de alertas.\n\nLas alertas generadas son:\n\n${textoMaterias}\n\nTen en cuenta que este sistema no pretende sustituir la página oficial. El objetivo es meramente informativo.\n\nRecuerda siempre verificar en la página oficial dado que pueden existir modificaciones posteriores a la notificación.\n\nIMPORTANTE:Esta es una versión de prueba y puede fallar. Se sugiere revisar la grilla oficial de forma diaria para evitar inconvenientes.`
    };
    transporter.sendMail(configuracion, (error, info) => {
        if (error) {
          res.sendStatus(500); // Responde con un código 500 para indicar un error en el servidor
        } else {
          res.sendStatus(200); // Responde con un código 200 para indicar que se guardaron los datos correctamente
        }
      });
})
    .catch((error) => {
      res.sendStatus(500); // Responde con un código 500 para indicar un error en el servidor
    });
});

app.listen(port, () => {
  console.log(`Servidor Node.js en ejecución en http://localhost:${port}`);
});
