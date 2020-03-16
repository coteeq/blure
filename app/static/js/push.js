const progress_radius = 20;
const progress_len = progress_radius * 2 * Math.PI;

window.addEventListener('DOMContentLoaded', function() {
    let pusher = document.getElementById('push-image-btn');

    let total = 0;
    let processed = 0;
    let page_hard_lock = 1;

    pusher.addEventListener('click', function(e) {
        let input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.multiple = true;
        input.addEventListener('change', (input_event) => {
            console.log(input_event.target.files);
            Array.prototype.forEach.call(input_event.target.files, file => {
                let data = new FormData();
                data.append('im', file);

                let fileno = total;
                total += 1;
                let wrapper = append_template_for_file (file, fileno);
                let progress = wrapper.querySelector('.progress-path');
                let status = wrapper.querySelector('.progress-status');

                let req = new XMLHttpRequest();
                req.addEventListener('load', (e) => {
                    let bg = wrapper.querySelector('.progress-bg');
                    bg.style.filter = 'none';
                    progress.style.stroke = '#0000';
                    
                    processed += 1;
                    if (processed == total && !page_hard_lock) {
                        location.reload();
                    }
                });
                req.upload.addEventListener('progress', (e) => {
                    let complete = 0;
                    if (e.lengthComputable) {
                        complete = e.loaded / e.total;
                    }
                    status.innerHTML = (e.loaded / 1000000).toFixed(2) + '/' + (e.total / 1000000).toFixed(2) + 'M';
                    progress.style.strokeDasharray = (complete * Math.PI * 2 * progress_radius).toString () + ',' + progress_len.toString();

                });

                req.open('POST', '/c/push');
                req.send(data);
            });
            page_hard_lock = 0;
        });

        input.click();
    });
});

function append_template_for_file (file, fileno) {
    let imageurl = URL.createObjectURL(file);
    let tmpl = document.querySelector('#progress-template');
    let root = document.querySelector('#template-goes-here');
    let newnode = document.importNode(tmpl.content, true);
    let style = newnode.querySelector('.progress-bg').style;
    style.background = 'url(' + imageurl + ')';
    style.backgroundSize = 'cover';
    style.backgroundPosition = 'center';
    style.backgroundRepeat = 'no-repeat';
    root.appendChild(newnode);
    let appended = root.lastChild.previousSibling;
    appended.setAttribute('id', 'progress-files-' + fileno.toString());

    return appended;
}
