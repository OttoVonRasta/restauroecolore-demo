// I servizi, nell'ordine del vecchio sito. `foto` e' un percorso dentro src/assets/media.

export interface Servizio {
  slug: string;
  titolo: string;
  voci: string[];
  foto: string;
  alt: string;
}

export const servizi: Servizio[] = [
  {
    slug: 'restauro-e-tinteggiature',
    titolo: 'Restauro e tinteggiature',
    voci: ['Intonaci e cemento armato', 'Opere in ferro', 'Marmorini', 'Pulizia superfici a vista'],
    foto: '2016/10/006.jpg',
    alt: 'Operaio che vernicia a pennello una ringhiera metallica',
  },
  {
    slug: 'ponteggi',
    titolo: 'Ponteggi',
    voci: ['Piattaforme aeree', 'Pantografi', 'Parapetti', 'Antifurto'],
    foto: '2016/10/095.jpg',
    alt: 'Ponteggio con telo di protezione montato sulla facciata di un condominio',
  },
  {
    slug: 'rifacimento-tetti',
    titolo: 'Rifacimento tetti',
    voci: ['Antipiccione'],
    foto: '2016/10/047-1.jpg',
    alt: 'Operaio al lavoro sul manto di copertura di un tetto',
  },
  {
    slug: 'isolamenti-e-impermeabilizzazioni',
    titolo: 'Isolamenti e impermeabilizzazioni',
    voci: ['Coperture', 'Coibentazioni'],
    foto: '2018/03/009-web.jpg',
    alt: 'Posa di pannelli isolanti su una copertura piana',
  },
  {
    slug: 'isolamento-a-cappotto',
    titolo: 'Isolamento a cappotto',
    voci: ['Applicazione pannelli isolanti'],
    foto: '2016/11/148.jpg',
    alt: 'Operaio che applica un pannello isolante su una parete esterna',
  },
  {
    slug: 'pavimentazione',
    titolo: 'Pavimentazione',
    voci: ['Poggioli e terrazze'],
    foto: '2016/10/047.jpg',
    alt: 'Posa di piastrelle sul pavimento di un poggiolo',
  },
  {
    slug: 'amianto',
    titolo: 'Amianto',
    voci: ['Rimozione, confezionamento, trasporto e smaltimento'],
    foto: '2016/09/image019-1.jpg',
    alt: 'Nuova copertura in lamiera accanto a una vecchia copertura da bonificare',
  },
  {
    slug: 'opere-fognarie',
    titolo: 'Opere fognarie',
    voci: ['Rifacimento e integrazione opere fognarie'],
    foto: '2016/10/018.jpg',
    alt: 'Operaio in cantiere durante lavori di scavo e sottofondo',
  },
  {
    slug: 'opere-in-ferro-e-lattonerie',
    titolo: 'Opere in ferro e lattonerie',
    voci: ['Rivestimenti metallici e grondaie', 'Pluviali'],
    foto: '2016/10/082.jpg',
    alt: 'Operaio imbragato che posa una lattoneria in copertura',
  },
  {
    slug: 'interni',
    titolo: 'Interni',
    voci: ['Dipinture', 'Parquet', 'Pavimenti', 'Infissi'],
    foto: '2018/03/carta-da-parati-web.jpg',
    alt: 'Operaio che rimuove una vecchia carta da parati',
  },
  {
    slug: 'realizzazione-bagni',
    titolo: 'Realizzazione bagni',
    voci: [],
    foto: '2016/11/117.jpg',
    alt: 'Piastrellista al lavoro nel rifacimento di un bagno',
  },
];
