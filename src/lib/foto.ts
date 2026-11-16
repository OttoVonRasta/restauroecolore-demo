import type { ImageMetadata } from 'astro';

const tutte = import.meta.glob<{ default: ImageMetadata }>('/src/assets/media/**/*.{jpg,jpeg,png,JPG,JPEG,PNG}', {
  eager: true,
});

/** Foto di src/assets/media a partire dal percorso usato nell'archivio (es. "2016/10/006.jpg"). */
export function foto(rel: string): ImageMetadata {
  const modulo = tutte[`/src/assets/media/${rel}`];
  if (!modulo) throw new Error(`Foto non trovata in src/assets/media: ${rel}`);
  return modulo.default;
}
