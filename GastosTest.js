function testCalcularBalances() {
  const personas = [
    { nombre: 'A', puso: 240, consumio: 400 },
    { nombre: 'B', puso: 350, consumio: 190 }
  ];
  const balances = calcularBalances(personas);
  const ok = balances[0].balance === -160 && balances[1].balance === 160;
  Logger.log(ok ? '✅ testCalcularBalances PASÓ' : '❌ testCalcularBalances FALLÓ: ' + JSON.stringify(balances));
  return ok;
}

function testSimplificarDeudas() {
  const balances = [
    { persona: 'A', balance: -160 },
    { persona: 'B', balance: 60 },
    { persona: 'C', balance: 100 }
  ];
  const transacciones = simplificarDeudas(balances);
  const total = transacciones.reduce((sum, t) => sum + t.monto, 0);
  const ok = total === 160 && transacciones.length <= 2;
  Logger.log(ok ? '✅ testSimplificarDeudas PASÓ' : '❌ testSimplificarDeudas FALLÓ: ' + JSON.stringify(transacciones));
  return ok;
}

function testCalcularDivisionGastos() {
  const personas = [
    { nombre: 'A', puso: 240, consumio: 500 },
    { nombre: 'B', puso: 460, consumio: 200 }
  ];
  const transacciones = calcularDivisionGastos(personas);
  const ok = transacciones.length === 1 && transacciones[0].de === 'A' && transacciones[0].para === 'B' && transacciones[0].monto === 260;
  Logger.log(ok ? '✅ testCalcularDivisionGastos PASÓ' : '❌ testCalcularDivisionGastos FALLÓ: ' + JSON.stringify(transacciones));
  return ok;
}

function runGastosTests() {
  Logger.log('🧪 Iniciando tests de Gastos...');
  testCalcularBalances();
  testSimplificarDeudas();
  testCalcularDivisionGastos();
  Logger.log('✅ Tests de Gastos completados');
}
