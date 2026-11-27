// ガリ勉：インストールアプリ用。
// アプリ自身のファイルは毎回新しい版を確かめる。辞書データ（*.bin）と、手書き・カメラの読み取り部品（外部）は一度取ったら保存して使う
const CACHE = "gariben-v172";
const DATA = "gariben-data";   // 辞書データ（*.bin）は名前ごとに中身が変わらないので、別の箱に取っておく
const EXT = "gariben-ext";     // ver.1.24：手書き・カメラの読み取り部品（電波のない所でも使えるように保存）
const EXT_HOSTS = ["huggingface.co", "cdn.jsdelivr.net", "tessdata.projectnaptha.com", "fonts.googleapis.com", "fonts.gstatic.com"];
const isExt = u => EXT_HOSTS.includes(u.hostname) || u.hostname.endsWith(".hf.co") || u.hostname.endsWith(".huggingface.co");
self.addEventListener("install", e => self.skipWaiting());
const OLD_DATA = ["kvg-1.bin"];   // 新しくした辞書データの古い方（スマホの容量を空けるため消す）
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== DATA && k !== EXT).map(k => caches.delete(k))))
    .then(() => caches.open(DATA)).then(c => c.keys().then(rs => Promise.all(rs.filter(r => OLD_DATA.some(n => r.url.endsWith("/" + n))).map(r => c.delete(r)))))
    .catch(() => {}).then(() => self.clients.claim())
));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) {
    if (!isExt(url) || e.request.headers.has("range")) return;   // それ以外の外部（Wikipedia・フォームなど）はブラウザに任せる
    e.respondWith(caches.open(EXT).then(c => c.match(e.request.url).then(hit => hit || fetch(e.request).then(res => {
      if (res.ok || res.type === "opaque") c.put(e.request.url, res.clone()).catch(() => {});
      return res;
    }))));
    return;
  }
  if (url.pathname.endsWith(".bin")) {               // 辞書データ：保存してあればそれを使う（通信しない）
    e.respondWith(caches.open(DATA).then(c => c.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      if (res.ok) c.put(e.request, res.clone());
      return res;
    }))));
    return;
  }
  // アプリ本体は毎回「新しい版が出ていないか」をGitHubに確かめる（電波がなければ保存してある版を使う）
  // ver.1.64：電波が弱くて3秒たっても返事がない時は、保存してある版ですぐ開く。新しい版は裏で受け取って次から使う
  let store = Promise.resolve();
  const net = fetch(e.request, { cache: "no-cache" }).then(res => {
    if (res.ok) { const copy = res.clone(); store = caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return res;
  });
  const saved = () => caches.match(e.request, { ignoreSearch: true }).then(r => r || caches.match("./index.html"));
  e.respondWith(new Promise(resolve => {
    let done = false;
    const give = r => { if (!done && r) { done = true; resolve(r); } };
    const t = setTimeout(() => saved().then(r => give(r)), 3000);
    net.then(r => { clearTimeout(t); give(r); })
       .catch(() => { clearTimeout(t); saved().then(r => { if (r) give(r); else if (!done) { done = true; resolve(Response.error()); } }); });
  }));
  e.waitUntil(net.then(() => store).catch(() => {}));
});
