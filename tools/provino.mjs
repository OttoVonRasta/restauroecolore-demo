// Provino numerato per scegliere le foto a colpo d'occhio.
// Uso: node tools/provino.mjs uscita.jpg 2016/10/006.jpg 2016/10/095.jpg ...
// (percorsi relativi a sito-originale/media)
import sharp from 'sharp';

const [out, ...rels] = process.argv.slice(2);
const W = 400, H = 280, COLS = 5;

const tessere = await Promise.all(
  rels.map(async (rel, i) => {
    const img = await sharp(`sito-originale/media/${rel}`)
      .rotate()
      .resize(W, H, { fit: 'contain', background: '#222' })
      .toBuffer();
    const etichetta = Buffer.from(
      `<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg"><rect width="${W}" height="26" fill="rgba(0,0,0,.7)"/>` +
        `<text x="6" y="18" font-family="Arial" font-size="15" fill="#fff">${i + 1}. ${rel.replace(/&/g, '&amp;')}</text></svg>`,
    );
    return {
      input: await sharp(img).composite([{ input: etichetta }]).jpeg().toBuffer(),
      left: (i % COLS) * W,
      top: Math.floor(i / COLS) * H,
    };
  }),
);

await sharp({
  create: { width: COLS * W, height: Math.ceil(rels.length / COLS) * H, channels: 3, background: '#222' },
})
  .composite(tessere)
  .jpeg({ quality: 72 })
  .toFile(out);
console.log(`provino: ${rels.length} foto -> ${out}`);
