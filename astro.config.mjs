import { readdir, readFile, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'astro/config';

// src/lib/foto.ts importa tutte le foto con un glob, quindi Vite copia in dist anche
// gli originali che nessuna pagina usa: li togliamo a fine build.
function rimuoviFotoNonUsate() {
  return {
    name: 'rimuovi-foto-non-usate',
    hooks: {
      'astro:build:done': async ({ dir, logger }) => {
        const voci = await readdir(fileURLToPath(dir), { recursive: true, withFileTypes: true });
        const file = voci.filter((v) => v.isFile()).map((v) => path.join(v.parentPath, v.name));
        const testi = await Promise.all(
          file.filter((f) => /\.(html|css|js|xml|json)$/.test(f)).map((f) => readFile(f, 'utf8')),
        );
        const testo = testi.join('\n');
        let tolte = 0;
        for (const f of file) {
          if (path.basename(path.dirname(f)) !== '_astro' || !/\.(jpe?g|png|webp|avif)$/i.test(f)) continue;
          const nome = path.basename(f);
          if (testo.includes(nome) || testo.includes(encodeURI(nome))) continue;
          await rm(f);
          tolte++;
        }
        logger.info(`${tolte} foto non usate rimosse da dist`);
      },
    },
  };
}

export default defineConfig({
  site: 'https://www.restauroecolore.com',
  // Stessi indirizzi del vecchio sito WordPress (/servizi/ponteggi/), per non perdere i link esistenti.
  trailingSlash: 'always',
  integrations: [rimuoviFotoNonUsate()],
});
