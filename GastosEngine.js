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

function calcularDivisionGastos(personas) {
  // Función de entrada única para RPC/agentes: personas -> transacciones
  const balances = calcularBalances(personas);
  return simplificarDeudas(balances);
}

function redondear(n) {
  return Math.round(n * 100) / 100;
}
