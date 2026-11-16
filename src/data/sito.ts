// Dati aziendali usati in tutto il sito: si correggono qui una volta sola.

const ANNO_FONDAZIONE = 1991;

export const azienda = {
  nome: 'Restauro & Colore',
  ragioneSociale: 'Restauro & Colore Srl',
  annoFondazione: ANNO_FONDAZIONE,
  // Calcolato a ogni pubblicazione, cosi' non resta indietro.
  anniAttivita: new Date().getFullYear() - ANNO_FONDAZIONE,
  indirizzo: 'Via Rio Orcone, 30',
  localita: '35010 Santa Giustina in Colle PD',
  telefono: '049-5793023',
  telefonoLink: '+390495793023',
  fax: '049-9316273',
  email: 'info@restauroecolore.com',
  piva: '04507850289',
  registroImprese: 'Iscr. Registro Imprese di Padova n. 04507850289',
  capitaleSociale: 'Cap. Soc. € 100.000,00 iv',
  facebook: 'https://www.facebook.com/RestauroeColore/',
  instagram: 'https://www.instagram.com/restauroecolore/',
};

export const filiali = [
  { nome: 'Filiale di Noale', indirizzo: 'Via Coppadoro, 1/19 - Noale VE' },
  { nome: 'Filiale di Mestre', indirizzo: 'Via Motta, 4/A - Mestre VE' },
  { nome: 'Filiale di Marghera', indirizzo: 'Via Domenico Fabris - Marghera VE', telefono: '041-5385165' },
  { nome: 'Filiale di Jesolo', indirizzo: 'Via Olanda, 164 - Jesolo VE' },
];

export const clienti = ['Rete Ferroviaria Italiana', 'Unicredit', 'Enel', 'KIKO Makeup Milano', 'Banca Santo Stefano'];

export const menu = [
  { titolo: 'Azienda', href: '/azienda/' },
  { titolo: 'Servizi', href: '/servizi/' },
  { titolo: 'Realizzazioni', href: '/realizzazioni/' },
  { titolo: 'Prima e Dopo', href: '/prima-e-dopo/' },
  { titolo: 'Contatti', href: '/contattaci/' },
];

export const menuAzienda = [
  { titolo: 'Assicurazioni', href: '/azienda/assicurazioni/' },
  { titolo: 'Attestazione SOA', href: '/azienda/certificazione-soa/' },
  { titolo: 'Certificato ISO 9001', href: '/azienda/certificato-iso-9001/' },
  { titolo: 'Finanziamenti', href: '/azienda/finanziamenti/' },
  { titolo: 'Garanzie', href: '/azienda/garanzie/' },
  { titolo: 'Sicurezza', href: '/azienda/sicurezza/' },
  { titolo: 'Staff', href: '/azienda/staff/' },
];
