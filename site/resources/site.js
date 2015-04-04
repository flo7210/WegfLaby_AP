function createLink(href, innerHTML) {
    var a = document.createElement('a');
    a.setAttribute('href', href);
    a.innerHTML = innerHTML;
    return a;
}

function generateTOC(toc) {
    var i2 = 0, i3 = 0, needToc = false;
    var elements = document.getElementsByTagName('article')[0];
    toc = toc.appendChild(document.createElement('ol'));

    for (var i = 0; i < elements.childNodes.length; ++i) {
        var node = elements.childNodes[i];
        var tagName = node.nodeName.toLowerCase();

        if (tagName == 'h3') {
            needToc = true;
            if (++i3 == 1) toc.lastChild.appendChild(document.createElement('ol'));
            toc.lastChild.lastChild.appendChild(document.createElement('li')).appendChild(createLink('#' + node.id, node.innerHTML));
        } else if (tagName == 'h2') {
            ++i2, i3 = 0;
            toc.appendChild(document.createElement('li')).appendChild(createLink('#' + node.id, node.innerHTML));
        }
    }

    if (needToc) {
        document.body.className += ' hastoc';
    }
}

generateTOC(document.getElementById('toc'));
hljs.initHighlightingOnLoad();
renderMathInElement(document.body);