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

function runAllTests() {
  Logger.log('🧪 Iniciando tests...');
  testSumar();
  Logger.log('✅ Tests completados');
}
