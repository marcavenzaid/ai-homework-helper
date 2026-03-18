document.addEventListener("DOMContentLoaded", (event) => {

    initializeColorTheme("light")
    textAreaAutoGrow();
    
});


document.getElementById("darkModeToggle").addEventListener("click", () => {
    toggleDarkMode();
});

function initializeColorTheme(colorTheme) {
    const rootElement = document.documentElement;
    const navbarElement = document.getElementById("navbar-id");

    if (colorTheme == "light") {
        rootElement.setAttribute("data-bs-theme", "light");
        navbarElement.classList.add("navbar-glassmorphism-light");
    } else if (colorTheme == "dark") {
        rootElement.setAttribute("data-bs-theme", "dark");
        navbarElement.classList.add("navbar-glassmorphism-dark");
    }
}

function toggleDarkMode() {
    const rootElement = document.documentElement;
    const navbarElement = document.getElementById("navbar-id");

    if (rootElement.getAttribute("data-bs-theme") == "light") {
        // Switch to dark mode
        navbarElement.classList.remove("navbar-glassmorphism-light");
        initializeColorTheme("dark")
    } else if (rootElement.getAttribute("data-bs-theme") == "dark") {
        // Switch to light mode
        navbarElement.classList.remove("navbar-glassmorphism-dark");
        initializeColorTheme("light");
    }
}

/**
 * Automatically adjusts the height of the text area to show all text inside it.
 */
function textAreaAutoGrow() {
    const textarea = document.querySelector("#inputMessage");

    if (textarea !== undefined && textarea !== null) {
        // Call autoResize function initially, to apply the auto resize.
        autoResize.call(textarea);

        // Add event listener.
        textarea.addEventListener("input", autoResize, false);

        function autoResize() {
            this.style.height = "auto";
            this.style.height = this.scrollHeight + "px";
        }
    }
}


/**
 * This will disable the submit button when the form was submitted to prevent double submission.
 * After submission Flask will redirect to the route, so no need to reenable the button.
 * This also shows a message telling the user that the AI is thinking.
 */
function onSubmitHandler() {
    // Disable the submit button to prevent multiple submissions
    document.getElementById("submitBtn").disabled = true;
    document.getElementById("loadingStatus").style.visibility = "visible";
    document.getElementById("statusMessage").textContent = "AI is thinking, please wait...";
}


