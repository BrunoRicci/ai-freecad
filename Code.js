function myFunction() {
  Logger.log('Pushed from local dev environment via clasp.');
}

function pruebaConexionClaude() {
  Logger.log('Conexión con Claude Code funcionando correctamente. ' + new Date());
}

function sumar(a, b) {
  return a + b;
}

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents || '{}');
    const transacciones = calcularDivisionGastos(body.personas);
    return ContentService.createTextOutput(JSON.stringify({ ok: true, transacciones }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function cargarDatosAHoja(datos, spreadsheetId = '1kw1MFJ1pgY4gIUV-gmR3oUj-Kfyl7cf9rmk0iGkUO6A', nombreHoja = 'Sheet1') {
  const sheet = SpreadsheetApp.openById(spreadsheetId).getSheetByName(nombreHoja);

  if (!sheet) {
    throw new Error(`Hoja "${nombreHoja}" no encontrada`);
  }

  if (!datos || datos.length === 0) {
    throw new Error('Los datos no pueden estar vacíos');
  }

  // Limpiar datos previos
  sheet.clearContents();

  // Cargar nuevos datos
  sheet.getRange(1, 1, datos.length, datos[0].length).setValues(datos);

  return {
    exito: true,
    filasInsertadas: datos.length,
    columnasInsertadas: datos[0].length,
    mensaje: `Datos cargados: ${datos.length} filas, ${datos[0].length} columnas`
  };
}
