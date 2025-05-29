selector_to_html = {"a[href=\"usage.html\"]": "<h1 class=\"tippy-header\" id=\"usage\" style=\"margin-top: 0;\">Usage<a class=\"headerlink\" href=\"#usage\" title=\"Link to this heading\">\u00b6</a></h1><p>In order to use the scripts described in this chapter, you need the <a class=\"reference external\" href=\"https://github.com/antmicro/audio-latency-tester-board\">Audio latency tester board</a> flashed with firmware from the <a class=\"reference internal\" href=\"installation.html#flashing-hardware\"><span class=\"std std-ref\"><code class=\"docutils literal notranslate\"><span class=\"pre\">flashing</span> <span class=\"pre\">hardware</span></code></span></a> section.</p><p>The <a class=\"reference external\" href=\"https://github.com/antmicro/audio-latency-tester\">scripts</a> require Python packages from the <a class=\"reference internal\" href=\"installation.html#installing-dependencies\"><span class=\"std std-ref\">installing dependencies</span></a> chapter and sufficient access rights to the connected USB devices.</p>", "a[href=\"overview.html\"]": "<h1 class=\"tippy-header\" id=\"project-overview\" style=\"margin-top: 0;\">Project overview<a class=\"headerlink\" href=\"#project-overview\" title=\"Link to this heading\">\u00b6</a></h1><p>Audio latency is a key factor in determining the quality of the user experience in communication services.\nA controlled delay is necessary for responsive and natural communication as it helps mitigate problems such as echo, timing issues, or a fragmented user experience.</p><p>The aim of this project is to provide a hardware and software test framework for measurement and characterization of audio latencies.</p>", "a[href=\"installation.html\"]": "<h1 class=\"tippy-header\" id=\"installation-and-setup\" style=\"margin-top: 0;\">Installation and setup<a class=\"headerlink\" href=\"#installation-and-setup\" title=\"Link to this heading\">\u00b6</a></h1><p><a class=\"reference external\" href=\"https://cmake.org/cmake/help/latest/release/3.20.html\">CMake (3.20 or newer)</a>, <a class=\"reference external\" href=\"https://www.python.org/\">Python3</a> and an <a class=\"reference external\" href=\"https://developer.arm.com/downloads/-/gnu-rm\">ARM toolchain</a> are required to build the project.</p><p>To install the dependencies on Debian Bookworm, run:</p>"}
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
