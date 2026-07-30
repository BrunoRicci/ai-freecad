/**
 * Capa de interacción con la planilla. Solo lee/escribe celdas y llama
 * al motor de GastosEngine.js — no contiene lógica de cálculo.
 */

function leerPersonasDesdeHoja(spreadsheetId, nombreHoja = 'Gastos') {
  const sheet = obtenerHoja(spreadsheetId, nombreHoja);
  const [, ...filas] = sheet.getDataRange().getValues();
  return filas
    .filter(fila => fila[0])
    .map(fila => ({ nombre: fila[0], puso: Number(fila[1]) || 0, consumio: Number(fila[2]) || 0 }));
}

function escribirResultadoEnHoja(transacciones, spreadsheetId, nombreHoja = 'Resultado') {
  const sheet = obtenerHoja(spreadsheetId, nombreHoja, true);
  sheet.clearContents();
  sheet.appendRow(['De', 'Para', 'Monto']);
  transacciones.forEach(t => sheet.appendRow([t.de, t.para, t.monto]));
}

function calcularDeudasDesdeHoja(spreadsheetId) {
  const personas = leerPersonasDesdeHoja(spreadsheetId);
  const transacciones = calcularDivisionGastos(personas);
  escribirResultadoEnHoja(transacciones, spreadsheetId);
  return transacciones;
}

function obtenerHoja(spreadsheetId, nombreHoja, crearSiNoExiste = false) {
  const ss = SpreadsheetApp.openById(spreadsheetId);
  let sheet = ss.getSheetByName(nombreHoja);
  if (!sheet && crearSiNoExiste) sheet = ss.insertSheet(nombreHoja);
  if (!sheet) throw new Error(`Hoja "${nombreHoja}" no encontrada`);
  return sheet;
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Gastos')
    .addItem('Calcular deudas', 'menuCalcularDeudas')
    .addToUi();
}

function menuCalcularDeudas() {
  const spreadsheetId = SpreadsheetApp.getActiveSpreadsheet().getId();
  const transacciones = calcularDeudasDesdeHoja(spreadsheetId);
  SpreadsheetApp.getUi().alert(`Listo. ${transacciones.length} transacción(es) calculada(s).`);
}
