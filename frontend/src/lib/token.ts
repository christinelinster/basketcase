const ALPHA = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';

export function makeToken(rand?: () => number): string {
  let s = '';
  for (let i = 0; i < 7; i++) s += ALPHA[Math.floor((rand ? rand() : Math.random()) * ALPHA.length)];
  return s;
}
