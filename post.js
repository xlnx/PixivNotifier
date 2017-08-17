var key = "f0face8a77848147f3194e028fe42b07"
var msg = "op=notify&tt=" + key
fetch(new Request('/rpc/notify.php',{
    method:'POST',
    headers: {
        "Content-Length": msg.length + "",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
        "Referer": "https://www.pixiv.net/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    },
    credentials: 'include', 
    body: msg
})).then((resp)=>{console.log(resp)}) 
