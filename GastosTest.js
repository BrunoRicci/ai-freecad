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

function testConsumoIndividualPorDefecto() {
  // Sin consumio en ninguna persona: total = suma de puso, repartido equitativo entre 2
  const personas = [
    { nombre: 'A', puso: 100 },
    { nombre: 'B', puso: 300 }
  ];
  const transacciones = calcularDivisionGastos(personas);
  const ok = transacciones.length === 1 && transacciones[0].de === 'A' && transacciones[0].para === 'B' && transacciones[0].monto === 100;
  Logger.log(ok ? '✅ testConsumoIndividualPorDefecto PASÓ' : '❌ testConsumoIndividualPorDefecto FALLÓ: ' + JSON.stringify(transacciones));
  return ok;
}

function testConsumoTotalExplicito() {
  // Si consumoTotal explícito no coincide con la suma de "puso" (500 vs 400),
  // el dinero no se conserva (no cierra en 0 entre todos) y no hay forma de
  // saldar completamente al grupo: el motor devuelve [] en vez de un resultado
  // parcial engañoso.
  const personas = [
    { nombre: 'A', puso: 100 },
    { nombre: 'B', puso: 300 }
  ];
  const transacciones = calcularDivisionGastos(personas, 500);
  const ok = transacciones.length === 0;
  Logger.log(ok ? '✅ testConsumoTotalExplicito PASÓ' : '❌ testConsumoTotalExplicito FALLÓ: ' + JSON.stringify(transacciones));
  return ok;
}

function testSimplificarDeudasOptimo() {
  // Caso donde el algoritmo greedy da 4 transacciones pero el óptimo da 3
  // (dos subgrupos independientes: {A,B,C} y {D,E}, greedy los mezcla mal)
  const balances = [
    { persona: 'A', balance: -5 },
    { persona: 'B', balance: 3 },
    { persona: 'C', balance: 2 },
    { persona: 'D', balance: -4 },
    { persona: 'E', balance: 4 }
  ];
  const greedy = simplificarDeudas(balances);
  const optimo = simplificarDeudasOptimo(balances);
  const sumaOptimo = optimo.reduce((s, t) => s + t.monto, 0);
  const ok = greedy.length === 4 && optimo.length === 3 && sumaOptimo === 11;
  Logger.log(ok ? '✅ testSimplificarDeudasOptimo PASÓ' : '❌ testSimplificarDeudasOptimo FALLÓ: greedy=' + JSON.stringify(greedy) + ' optimo=' + JSON.stringify(optimo));
  return ok;
}

function runGastosTests() {
  Logger.log('🧪 Iniciando tests de Gastos...');
  testCalcularBalances();
  testSimplificarDeudas();
  testCalcularDivisionGastos();
  testConsumoIndividualPorDefecto();
  testConsumoTotalExplicito();
  testSimplificarDeudasOptimo();
  Logger.log('✅ Tests de Gastos completados');
}
