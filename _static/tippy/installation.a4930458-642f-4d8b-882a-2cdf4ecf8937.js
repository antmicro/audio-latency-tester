selector_to_html = {"a[href=\"references.html#sw3\"]": "<img alt=\"_images/SW3.png\" id=\"sw3\" src=\"_images/SW3.png\"/>", "a[href=\"#id2\"]": "<figure class=\"align-default\" id=\"id2\">\n<img alt=\"\" src=\"_images/mcu-2-usb.png\"/>\n<figcaption>\n<p><span class=\"caption-number\">Figure 3 </span><span class=\"caption-text\"><span class=\"caption-text\">\nMCU-2 USB-C connection</span><a class=\"headerlink\" href=\"#id2\" title=\"Permalink to this image\">\u00b6</a></span></p></figcaption>\n</figure>", "a[href=\"#id1\"]": "<figure class=\"align-default\" id=\"id1\">\n<img alt=\"\" src=\"_images/mcu-1-usb.png\"/>\n<figcaption>\n<p><span class=\"caption-number\">Figure 2 </span><span class=\"caption-text\"><span class=\"caption-text\">\nMCU-1 USB-C connection</span><a class=\"headerlink\" href=\"#id1\" title=\"Permalink to this image\">\u00b6</a></span></p></figcaption>\n</figure>", "a[href=\"references.html#sw4\"]": "<img alt=\"_images/SW4.png\" id=\"sw4\" src=\"_images/SW4.png\"/>", "a[href=\"references.html#sw2\"]": "<img alt=\"_images/SW2.png\" id=\"sw2\" src=\"_images/SW2.png\"/>", "a[href=\"references.html#sw1\"]": "<img alt=\"_images/SW1.png\" id=\"sw1\" src=\"_images/SW1.png\"/>"}
skip_classes = ["headerlink", "sd-stretched-link"]

window.onload = function () {
    for (const [select, tip_html] of Object.entries(selector_to_html)) {
        const links = document.querySelectorAll(` ${select}`);
        for (const link of links) {
            if (skip_classes.some(c => link.classList.contains(c))) {
                continue;
            }

            tippy(link, {
                content: tip_html,
                allowHTML: true,
                arrow: true,
                placement: 'top-start', maxWidth: 1200, interactive: false, duration: [200, 100], delay: [200, 500],

            });
        };
    };
    console.log("tippy tips loaded!");
};
