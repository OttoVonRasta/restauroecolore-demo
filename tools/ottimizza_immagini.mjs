// Riduce le foto originali di sito-originale/media in src/assets/media
// (lato lungo max 1920 px, JPEG ricompresso). Le varianti responsive le genera poi Astro.
// Uso: npm run foto   — rilanciabile, salta i file gia' pronti.
import { copyFile, mkdir, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const SRC = 'sito-originale/media';
const DST = 'src/assets/media';
const MAX = 1920;
const PARALLELI = 4;

async function* elenca(dir) {
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* elenca(p);
    else yield p;
  }
}

const coda = [];
for await (const src of elenca(SRC)) {
  if (['.jpg', '.jpeg', '.png'].includes(path.extname(src).toLowerCase())) coda.push(src);
}

let nuovi = 0, saltati = 0, bytes = 0;
async function lavora() {
  for (let src; (src = coda.pop()); ) {
    const dst = path.join(DST, path.relative(SRC, src));
    const pronto = await stat(dst).catch(() => null);
    if (pronto) {
      saltati++;
      bytes += pronto.size;
      continue;
    }
    await mkdir(path.dirname(dst), { recursive: true });
    if (path.extname(src).toLowerCase() === '.png') {
      await copyFile(src, dst);
    } else {
      await sharp(src)
        .rotate()
        .resize({ width: MAX, height: MAX, fit: 'inside', withoutEnlargement: true })
        .jpeg({ quality: 82, mozjpeg: true })
        .toFile(dst);
    }
    bytes += (await stat(dst)).size;
    nuovi++;
  }
}
await Promise.all(Array.from({ length: PARALLELI }, lavora));
console.log(`foto: ${nuovi} nuove, ${saltati} gia' pronte, totale ${(bytes / 1e6).toFixed(1)} MB in ${DST}`);
