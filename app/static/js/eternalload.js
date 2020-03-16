const progress_width = 100;
const progress_radius = 20;
const progress_len = progress_radius * 2 * Math.PI;

const PREVIEW_TEMPLATE = `
<div class="eternal-progress-wrapper">
    <div class="eternal-progress-bg"></div>
    <svg class="eternal-progress-svg">
        <circle class="eternal-progress-path"
                cx="${progress_width / 2}"
                cy="${progress_width / 2}"
                r="${progress_radius}"
                fill="none"
                stroke-width="5"
                stroke-miterlimit="10" />
    </svg>
    <pre class="eternal-progress-status"></pre>
</div>
`

const REMOTE_LOAD_TEMPLATE = `
<form method='POST' autocomplete="off">
  <input class="eternal-url-input" type="text" placeholder="Remote image">
  <span class="eternal-url-span"></span>
</form>
`.trim();

function append_template_for_file (node, file, fileno) {
    const imageurl = URL.createObjectURL(file);
    node.insertAdjacentHTML('beforeend', PREVIEW_TEMPLATE);
    let newnode = node.lastChild.previousSibling;
    console.log(newnode);
    let style = newnode.querySelector('.eternal-progress-bg').style;
    style.background = 'url(' + imageurl + ')';
    style.backgroundSize = 'cover';
    style.backgroundPosition = 'center';
    style.backgroundRepeat = 'no-repeat';
    newnode.setAttribute('id', 'progress-files-' + fileno.toString());

    return newnode;
}

class EternalLoad {
    constructor (node) {
        this.root = document.createElement('div');
        this.root.setAttribute('id', 'eternal-root');
        this.local = {};
        this.remote = {};
    }

    attach (target) {
        if (this.local.btn)
            this.root.appendChild(this.local.btn);
        target.appendChild(this.root);

        return this;
    }

    use_local (url) {
        this.local.btn = document.createElement('button');
        this.local.btn.setAttribute('class', 'btn');
        this.local.btn.textContent = 'local file';
        
        this.local.total = 0;
        this.local.processed = 0;
        this.local.page_hard_lock = 1;

        this.local.btn.addEventListener('click', (e) => {
            let input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.multiple = true;
            input.addEventListener('change', (input_event) => {
                Array.prototype.forEach.call(input_event.target.files, file => {
                    let data = new FormData();
                    data.append('im', file);

                    let fileno = this.local.total;
                    this.local.total += 1;
                    let wrapper = append_template_for_file (this.root, file, fileno);
                    let progress = wrapper.querySelector('.eternal-progress-path');
                    let status = wrapper.querySelector('.eternal-progress-status');

                    let req = new XMLHttpRequest();
                    req.addEventListener('load', (e) => {
                        let bg = wrapper.querySelector('.eternal-progress-bg');
                        bg.style.filter = 'none';
                        progress.style.stroke = '#0000';
                        
                        this.local.processed += 1;
                        if (this.local.processed == this.local.total && !this.local.page_hard_lock)
                            location.reload();
                    });
                    req.upload.addEventListener('progress', (e) => {
                        let complete = 0;
                        if (e.lengthComputable)
                            complete = e.loaded / e.total;
                        status.innerHTML = `${(e.loaded / 1000000).toFixed(2)}/${(e.total / 1000000).toFixed(2)}M`;
                        progress.style.strokeDasharray = `${(complete * Math.PI * 2 * progress_radius)},${progress_len}`;

                    });

                    req.open('POST', url);
                    req.send(data);
                });
                this.local.page_hard_lock = 0;
            });

            input.click();
        });

        return this;
    }

    use_remote (url) {
        return this;
    }
}

export default EternalLoad;
