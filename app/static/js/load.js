import EternalLoad from './eternalload.js'

let load = new EternalLoad()
                .use_local('/c/push')
                .use_remote('/c/push_url')
                .attach(document.querySelector('#template-goes-here'));
