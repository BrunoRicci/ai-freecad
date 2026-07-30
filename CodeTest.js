function testSumar() {
  const resultado = sumar(2, 3);
  if (resultado === 5) {
    Logger.log('✅ Test PASÓ: sumar(2, 3) = 5');
    return true;
  } else {
    Logger.log('❌ Test FALLÓ: sumar(2, 3) = ' + resultado + ', esperado 5');
    return false;
  }
}

function testCargarDatos() {
  const datosTest = [
    ['Nombre', 'Edad', 'País'],
    ['Juan', 30, 'Argentina'],
    ['María', 25, 'España'],
    ['Carlos', 35, 'México']
  ];

  try {
    const resultado = cargarDatosAHoja(datosTest);
    if (resultado.exito && resultado.filasInsertadas === 4) {
      Logger.log('✅ Test PASÓ: cargarDatosAHoja funcionó correctamente');
      Logger.log('   ' + resultado.mensaje);
      return true;
    } else {
      Logger.log('❌ Test FALLÓ: resultado inesperado');
      return false;
    }
  } catch (error) {
    Logger.log('❌ Test FALLÓ: ' + error.message);
    return false;
  }
}

function runAllTests() {
  Logger.log('🧪 Iniciando tests...');
  testSumar();
  testCargarDatos();
  Logger.log('✅ Tests completados');
}
