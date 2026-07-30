/**
 * Servidor MCP (Model Context Protocol) sobre JSON-RPC 2.0, un único endpoint.
 * method "tools/list" expone el "card"/schema de cada tool.
 * method "tools/call" ejecuta una tool con sus argumentos.
 */

function manejarMcpRequest(body) {
  const { id, method, params } = body;

  if (method === 'initialize') {
    return mcpResponse(id, {
      protocolVersion: '2024-11-05',
      capabilities: { tools: {} },
      serverInfo: { name: 'gastos-mcp', version: '1.0.0' }
    });
  }

  if (method === 'tools/list') {
    return mcpResponse(id, { tools: obtenerToolsMcp() });
  }

  if (method === 'tools/call') {
    return ejecutarToolMcp(id, params);
  }

  return mcpError(id, -32601, 'Método no soportado: ' + method);
}

function obtenerToolsMcp() {
  return [
    {
      name: 'calcularDivisionGastos',
      description: 'Calcula el número mínimo de transacciones para saldar gastos compartidos entre un grupo de personas, dado lo que cada una puso y consumió.',
      inputSchema: {
        type: 'object',
        properties: {
          personas: {
            type: 'array',
            description: 'Lista de personas del grupo',
            items: {
              type: 'object',
              properties: {
                nombre: { type: 'string' },
                puso: { type: 'number', description: 'Dinero aportado por la persona' },
                consumio: { type: 'number', description: 'Opcional. Si se omite, se reparte equitativo el total restante entre quienes no lo especifican.' }
              },
              required: ['nombre', 'puso']
            }
          },
          consumoTotal: {
            type: 'number',
            description: 'Opcional. Total consumido por el grupo. Si se omite, se toma como la suma de "puso" de todos.'
          }
        },
        required: ['personas']
      }
    }
  ];
}

function ejecutarToolMcp(id, params) {
  try {
    if (!params || params.name !== 'calcularDivisionGastos') {
      return mcpError(id, -32602, 'Tool desconocida: ' + (params && params.name));
    }
    const args = params.arguments || {};
    const transacciones = calcularDivisionGastos(args.personas, args.consumoTotal);
    return mcpResponse(id, {
      content: [{ type: 'text', text: JSON.stringify(transacciones) }],
      isError: false
    });
  } catch (err) {
    return mcpResponse(id, {
      content: [{ type: 'text', text: 'Error: ' + err.message }],
      isError: true
    });
  }
}

function mcpResponse(id, result) {
  return { jsonrpc: '2.0', id, result };
}

function mcpError(id, code, message) {
  return { jsonrpc: '2.0', id, error: { code, message } };
}
