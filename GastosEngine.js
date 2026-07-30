/**
 * Motor de cálculo de división de gastos. Sin dependencias de SpreadsheetApp
 * ni de ningún servicio de GAS: recibe/devuelve solo objetos planos, así que
 * es invocable directo vía RPC (scripts.run) o por un agente de IA.
 */

function calcularBalances(personas) {
  // personas: [{ nombre, puso, consumio }]
  return personas.map(p => ({
    persona: p.nombre,
    balance: redondear(p.puso - p.consumio)
  }));
}

function simplificarDeudas(balances) {
  // balances: [{ persona, balance }] -> [{ de, para, monto }]
  const deudores = balances
    .filter(b => b.balance < 0)
    .map(b => ({ ...b }))
    .sort((a, b) => a.balance - b.balance);
  const acreedores = balances
    .filter(b => b.balance > 0)
    .map(b => ({ ...b }))
    .sort((a, b) => b.balance - a.balance);

  const transacciones = [];
  let i = 0, j = 0;

  while (i < deudores.length && j < acreedores.length) {
    const deudor = deudores[i];
    const acreedor = acreedores[j];
    const monto = redondear(Math.min(-deudor.balance, acreedor.balance));

    if (monto > 0) {
      transacciones.push({ de: deudor.persona, para: acreedor.persona, monto });
      deudor.balance = redondear(deudor.balance + monto);
      acreedor.balance = redondear(acreedor.balance - monto);
    }

    if (Math.abs(deudor.balance) < 0.01) i++;
    if (Math.abs(acreedor.balance) < 0.01) j++;
  }

  return transacciones;
}

function simplificarDeudasOptimo(balances) {
  // balances: [{ persona, balance }] -> [{ de, para, monto }]
  // Búsqueda exacta (backtracking) del número mínimo de transacciones.
  // El greedy (simplificarDeudas) no siempre logra el mínimo real.
  const cuentas = balances
    .filter(b => Math.abs(b.balance) >= 0.01)
    .map(b => ({ persona: b.persona, balance: b.balance }));

  let mejor = null;

  function backtrack(cuentas, transacciones) {
    if (mejor !== null && transacciones.length >= mejor.length) return;

    const idx = cuentas.findIndex(c => Math.abs(c.balance) >= 0.01);
    if (idx === -1) {
      mejor = transacciones;
      return;
    }

    const actual = cuentas[idx];
    for (let k = 0; k < cuentas.length; k++) {
      if (k === idx) continue;
      const otro = cuentas[k];
      if (actual.balance * otro.balance >= 0) continue; // mismo signo, no aplica

      const de = actual.balance < 0 ? actual.persona : otro.persona;
      const para = actual.balance < 0 ? otro.persona : actual.persona;
      const monto = redondear(Math.abs(actual.balance));

      const copia = cuentas.map(c => ({ ...c }));
      copia[idx].balance = 0;
      copia[k].balance = redondear(otro.balance + actual.balance);

      backtrack(copia, [...transacciones, { de, para, monto }]);
    }
  }

  backtrack(cuentas, []);
  return mejor || [];
}

function calcularDivisionGastos(personas, consumoTotal) {
  // Función de entrada única para RPC/agentes: personas -> transacciones
  // consumoTotal es opcional: si no se pasa, se toma como la suma de "puso" de todos.
  // El consumo individual es opcional por persona: si falta, se reparte equitativo
  // el total restante (descontando lo ya especificado por otras personas) entre
  // quienes no lo especificaron — el consumo especificado nunca se modifica.
  const total = (consumoTotal !== undefined && consumoTotal !== null)
    ? consumoTotal
    : personas.reduce((suma, p) => suma + p.puso, 0);

  const especificados = personas.filter(p => p.consumio !== undefined && p.consumio !== null);
  const sinEspecificar = personas.filter(p => p.consumio === undefined || p.consumio === null);
  const sumaEspecificada = especificados.reduce((suma, p) => suma + p.consumio, 0);
  const consumoEquitativo = sinEspecificar.length > 0
    ? redondear((total - sumaEspecificada) / sinEspecificar.length)
    : 0;

  const personasCompletas = personas.map(p => ({
    nombre: p.nombre,
    puso: p.puso,
    consumio: (p.consumio !== undefined && p.consumio !== null) ? p.consumio : consumoEquitativo
  }));

  const balances = calcularBalances(personasCompletas);
  return simplificarDeudasOptimo(balances);
}

function redondear(n) {
  return Math.round(n * 100) / 100;
}
