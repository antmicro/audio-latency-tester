selector_to_html = {"a[href=\"#id6\"]": "<figure class=\"align-default\" id=\"id6\">\n<img alt=\"\" src=\"_images/example-audio-latancy.png\"/>\n<figcaption>\n<p><span class=\"caption-number\">Figure 9 </span><span class=\"caption-text\"><span class=\"caption-text\">\nRecorded and reference audio waveforms</span><a class=\"headerlink\" href=\"#id6\" title=\"Permalink to this image\">\u00b6</a></span></p></figcaption>\n</figure>", "a[href=\"#id2\"]": "<figure class=\"align-default\" id=\"id2\">\n<img alt=\"\" src=\"_images/connection-audio-microphone-board.png\"/>\n<figcaption>\n<p><span class=\"caption-number\">Figure 5 </span><span class=\"caption-text\"><span class=\"caption-text\">\nFFC connections</span><a class=\"headerlink\" href=\"#id2\" title=\"Permalink to this image\">\u00b6</a></span></p></figcaption>\n</figure>", "a[href=\"references.html#j4\"]": "<img alt=\"_images/J4.png\" id=\"j4\" src=\"_images/J4.png\"/>", "a[href=\"references.html#j7\"]": "<img alt=\"_images/J7.png\" id=\"j7\" src=\"_images/J7.png\"/>", "a[href=\"#id5\"]": "<figure class=\"align-default\" id=\"id5\">\n<img alt=\"\" src=\"_images/latency-recordings.png\"/>\n<figcaption>\n<p><span class=\"caption-number\">Figure 8 </span><span class=\"caption-text\"><span class=\"caption-text\">\nRecorded and processed audio waveforms</span><a class=\"headerlink\" href=\"#id5\" title=\"Permalink to this image\">\u00b6</a></span></p></figcaption>\n</figure>", "a[href=\"#id1\"]": "<figure class=\"align-default\" id=\"id1\">\n<img alt=\"\" src=\"_images/microphone-channel-selection.png\"/>\n<figcaption>\n<p><span class=\"caption-number\">Figure 4 </span><span class=\"caption-text\"><span class=\"caption-text\">\nMicrophone board left/right channel selection</span><a class=\"headerlink\" href=\"#id1\" title=\"Permalink to this image\">\u00b6</a></span></p></figcaption>\n</figure>", "a[href=\"#id3\"]": "<figure class=\"align-default\" id=\"id3\">\n<img alt=\"\" src=\"_images/speaker-conn.png\"/>\n<figcaption>\n<p><span class=\"caption-number\">Figure 6 </span><span class=\"caption-text\"><span class=\"caption-text\">\nSpeaker connectors</span><a class=\"headerlink\" href=\"#id3\" title=\"Permalink to this image\">\u00b6</a></span></p></figcaption>\n</figure>", "a[href=\"#id4\"]": "<figure class=\"align-default\" id=\"id4\">\n<img alt=\"\" src=\"_images/headset-testing-setup.png\"/>\n<figcaption>\n<p><span class=\"caption-number\">Figure 7 </span><span class=\"caption-text\"><span class=\"caption-text\">\nWireless headset testing setup</span><a class=\"headerlink\" href=\"#id4\" title=\"Permalink to this image\">\u00b6</a></span></p></figcaption>\n</figure>", "a[href=\"references.html#j5\"]": "<img alt=\"_images/J5.png\" id=\"j5\" src=\"_images/J5.png\"/>", "a[href=\"references.html#j6\"]": "<img alt=\"_images/J6.png\" id=\"j6\" src=\"_images/J6.png\"/>"}
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
