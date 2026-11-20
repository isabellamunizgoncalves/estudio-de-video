#!/usr/bin/env node
/* Converte SVG em PNG com fundo transparente, para a colagem entrar por baixo.
 *
 * Não há cairosvg, rsvg-convert nem inkscape no ambiente; o Chromium do
 * Playwright já vem instalado e desenha SVG igual ao navegador, que é onde a
 * animação vai rodar de qualquer forma.
 *
 * Uso: node ferramentas/video/rasterizar.js <arquivo.svg|pasta> [--escala 2]
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const args = process.argv.slice(2);
  const alvo = args[0];
  const i = args.indexOf('--escala');
  const escala = i >= 0 ? Number(args[i + 1]) : 2;
  if (!alvo) { console.error('uso: rasterizar.js <arquivo.svg|pasta> [--escala N]'); process.exit(1); }

  const arquivos = fs.statSync(alvo).isDirectory()
    ? fs.readdirSync(alvo).filter(f => f.endsWith('.svg')).map(f => path.join(alvo, f))
    : [alvo];
  if (!arquivos.length) { console.error('nenhum .svg encontrado'); process.exit(1); }

  const navegador = await chromium.launch();
  for (const svg of arquivos) {
    const texto = fs.readFileSync(svg, 'utf8');
    const largura = Number((texto.match(/width="(\d+)"/) || [])[1] || 900);
    const altura = Number((texto.match(/height="(\d+)"/) || [])[1] || 700);
    const pagina = await navegador.newPage({
      viewport: { width: largura, height: altura },
      deviceScaleFactor: escala,
    });
    await pagina.setContent(
      `<body style="margin:0;background:transparent">${texto}</body>`,
      { waitUntil: 'load' });
    const saida = svg.replace(/\.svg$/, '.png');
    await pagina.screenshot({ path: saida, omitBackground: true });
    await pagina.close();
    console.log(`${path.basename(saida)}  ${largura * escala}x${altura * escala}`);
  }
  await navegador.close();
}

main().catch(e => { console.error(e); process.exit(1); });
