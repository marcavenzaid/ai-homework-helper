import MarkdownIt from 'https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/+esm';

const md = MarkdownIt({
    breaks: true,
    // html: true,
});

// Add escapeTex rule to Markdown-it
// md.inline.ruler.before('emphasis', 'escapeTeX', escapeTeX);
md.inline.ruler.before('text', 'escapeTeX', escapeTeX);

// console.log(md.inline.ruler.__rules__);
// console.log(md.block.ruler.__rules__);

document.addEventListener("DOMContentLoaded", (event) => {
    
    setupMathjax(["#answerBody", "#stepByStepSolutionBody"]);

    renderMarkdown("answerBodyHiddenTextArea", "answerBody");
    renderMarkdown("stepByStepSolutionBodyHiddenTextArea", "stepByStepSolutionBody");

    ////////////////////////////////
    // let answerBody = document.getElementById("answerBody").innerHTML;
    // document.getElementById("answerBody").innerHTML = answerBody + `image:[file-OUaVnybF6RLS72BGyj08Kabq.png]`;
    ////////////////////////////////

    renderImages("answerBody");
    renderImages("stepByStepSolutionBody");
})

// Define a custom rule for inline text escaping
/**
 * Ignore text from being rendered when it is inside \\[ and \\] or \\( and \\).
 * Don't worry about the parameters, they are handled by markdown-it.
 * @param {*} state 
 * @param {*} silent 
 * @returns 
 */
function escapeTeX(state, silent) {
    const start = state.pos;

    if (state.src.charAt(start) !== '\\') {
        return false;
    }

    if (state.src.charAt(start + 1) !== '\\') {
        return false;
    }

    const afterStart = state.src.charAt(start + 2);
    if (afterStart !== '[' && afterStart !== '(') {
        return false;
    }

    let endChar = (afterStart === '[') ? ']' : ')';
    let end = state.src.indexOf('\\\\' + endChar, start + 4); // start + 4 is the character after the \\[ or \\(.

    if (end === -1) {
        return false; // not found.
    }

    if (!silent) {
        const token = state.push('text', '', 0);
        token.content = state.src.slice(start, end + 3); // get the content from \\[ and \\] or \\( and \\) inclusively.
    }

    state.pos = end + 3; // move past the end marker.
    return true;
}

function setupMathjax(elementsArray) {
    // Yes this should come before the dynamic import of mathjax.
    window.MathJax = {
        startup: {
            elements: elementsArray,            // The elements to typeset (default is document body)
            typeset: true,                      // Perform initial typeset?
        },
        tex: {
            inlineMath: [['\\\\(', '\\\\)']],
            displayMath: [['\\\\[', '\\\\]']],
        },
        chtml: {
            scale: 1,
            displayAlign: 'left',
        },
        // svg: {
        //     displayAlign: 'left',
        // }
        options: {
            enableMenu: false,
            renderActions: {
                assistiveMml: [],  // disable assistive mathml
            },
        }
    };

    // Since MathJax script is required to be loaded, dynamically import it.
    // To ensure proper functioning, the MathJax script should indeed be dynamically loaded **after** you configure `window.MathJax`. 
    // This sequence is important because the configuration must be set before MathJax begins processing the page content. 
    // When the MathJax script is loaded, it will look at the configuration object `window.MathJax` to determine how to behave 
    // and which parts of your document to typeset.
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
    script.async = true;
    document.head.appendChild(script);  
}

function renderMarkdown(hiddenTextAreaId, targetId) {
    const hiddenTextArea = document.getElementById(hiddenTextAreaId);
    const hiddenTextAreaText = hiddenTextArea.value;
    const rendered = md.render(hiddenTextAreaText);
    document.getElementById(targetId).innerHTML = rendered;
}

/**
 * Convert all image:[image_name] to image html tags with the respective image src.
 */
function renderImages(id) {
    const contentDiv = document.getElementById(id);
    let contentText = contentDiv.innerHTML; // Use innerHTML to preserve existing HTML content.

    // Regular expression to find the pattern "image:[filename]" globally
    const regex = /image:\[(.*?)\]/g;
    let match;

    // Loop through all instances of the pattern
    while ((match = regex.exec(contentText)) !== null) {
        const imageName = match[1];
        const imagePath = `/static/output/images/${imageName}`;

        // Create an img element
        const imgHTML = 
        `<div class="row">
            <div class="col"></div>
            <div class="col-12 col-lg-8">
                <img src="${imagePath}" alt="${imageName}" style="max-width: 100%; height: auto;">
            </div>
            <div class="col"></div>
        </div>`;

        // Replace each matched text with the corresponding img element
        contentText = contentText.replace(match[0], imgHTML);
    }

    // Update the content of the DIV to show all images
    contentDiv.innerHTML = contentText;
}