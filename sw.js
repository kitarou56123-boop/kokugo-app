// ガリ勉：インストールアプリ用。
// アプリ自身のファイル（同じ場所のもの）だけを扱い、辞書や手書き認識など外部のデータには一切さわらない
const CACHE = "gariben-v121";
const DATA = "gariben-data";   // 辞書データ（*.bin）は名前ごとに中身が変わらないので、別の箱に取っておく
self.addEventListener("install", e => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== DATA).map(k => caches.delete(k)))).then(() => self.clients.claim())
));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;   // 外部のデータはブラウザにそのまま任せる
  if (url.pathname.endsWith(".bin")) {               // 辞書データ：保存してあればそれを使う（通信しない）
    e.respondWith(caches.open(DATA).then(c => c.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      if (res.ok) c.put(e.request, res.clone());
      return res;
    }))));
    return;
  }
  // アプリ本体は毎回「新しい版が出ていないか」をGitHubに確かめる（ブラウザの一時保存に古い版が残っていても使わない）
  e.respondWith(
    fetch(e.request, { cache: "no-cache" }).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    }).catch(() => caches.match(e.request).then(r => r || Response.error()))
  );
});
