// ============================================================
// Configuration
// ============================================================

const API_URL = "https://kg93cjr4je.execute-api.ap-southeast-1.amazonaws.com";

const COGNITO_DOMAIN =
    "https://kaviyan-serverless-app-dev.auth.ap-southeast-1.amazoncognito.com";

const CLIENT_ID = "1ebr66qudoj1rlspj29dhug5nk";

// Resolves to:
// Local:      http://localhost:8000
// CloudFront: https://xxxxx.cloudfront.net
const REDIRECT_URI = window.location.origin;


// ============================================================
// DOM elements
// ============================================================

const taskForm = document.getElementById("task-form");
const taskInput = document.getElementById("task-input");
const taskList = document.getElementById("task-list");

const loginButton = document.getElementById("login-button");
const logoutButton = document.getElementById("logout-button");

const app = document.getElementById("app");
const loginMessage = document.getElementById("login-message");


// ============================================================
// Authentication helpers
// ============================================================

function getAccessToken() {
    return sessionStorage.getItem("access_token");
}


// Generate a cryptographically random string for PKCE
function generateRandomString(length) {

    const characters =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";

    let result = "";

    const randomValues = new Uint32Array(length);

    crypto.getRandomValues(randomValues);

    for (let i = 0; i < length; i++) {
        result += characters[
            randomValues[i] % characters.length
        ];
    }

    return result;
}


// Convert the PKCE code verifier into a SHA-256 code challenge
async function createCodeChallenge(verifier) {

    const data =
        new TextEncoder().encode(verifier);

    const digest =
        await crypto.subtle.digest(
            "SHA-256",
            data
        );

    return btoa(
        String.fromCharCode(
            ...new Uint8Array(digest)
        )
    )
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
}


// ============================================================
// Login
// ============================================================

async function login() {

    // Generate a new PKCE verifier for this login attempt
    const codeVerifier =
        generateRandomString(64);

    // Hash the verifier to create the challenge
    const codeChallenge =
        await createCodeChallenge(codeVerifier);

    // Save the verifier because we need it after Cognito
    // redirects the browser back to our application
    sessionStorage.setItem(
        "pkce_code_verifier",
        codeVerifier
    );

    const params =
        new URLSearchParams({
            response_type: "code",
            client_id: CLIENT_ID,
            redirect_uri: REDIRECT_URI,
            scope: "openid email profile",
            code_challenge: codeChallenge,
            code_challenge_method: "S256"
        });

    // Redirect the browser to Cognito
    window.location.href =
        `${COGNITO_DOMAIN}/oauth2/authorize?${params}`;
}


// ============================================================
// Authorization code → tokens
// ============================================================

async function exchangeCodeForTokens(code) {

    const codeVerifier =
        sessionStorage.getItem(
            "pkce_code_verifier"
        );

    if (!codeVerifier) {
        throw new Error(
            "PKCE code verifier not found"
        );
    }

    const body =
        new URLSearchParams({
            grant_type: "authorization_code",
            client_id: CLIENT_ID,
            code: code,
            redirect_uri: REDIRECT_URI,
            code_verifier: codeVerifier
        });

    const response =
        await fetch(
            `${COGNITO_DOMAIN}/oauth2/token`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/x-www-form-urlencoded"
                },

                body: body
            }
        );

    if (!response.ok) {
        throw new Error(
            "Failed to exchange authorization code"
        );
    }

    const tokens =
        await response.json();


    // Store tokens for the current browser session
    sessionStorage.setItem(
        "access_token",
        tokens.access_token
    );

    sessionStorage.setItem(
        "id_token",
        tokens.id_token
    );

    if (tokens.refresh_token) {
        sessionStorage.setItem(
            "refresh_token",
            tokens.refresh_token
        );
    }


    // We no longer need the PKCE verifier
    sessionStorage.removeItem(
        "pkce_code_verifier"
    );

    return tokens;
}


// ============================================================
// Handle Cognito redirect
// ============================================================

async function handleAuthentication() {

    const params =
        new URLSearchParams(
            window.location.search
        );

    const code =
        params.get("code");

    // If Cognito redirected us back with an authorization code,
    // exchange it for tokens.
    if (code) {

        try {

            await exchangeCodeForTokens(code);

            // Remove ?code=... from the browser URL
            window.history.replaceState(
                {},
                document.title,
                window.location.pathname
            );

        } catch (error) {

            console.error(
                "Authentication failed:",
                error
            );
        }
    }

    updateUI();
}


// ============================================================
// UI authentication state
// ============================================================

function updateUI() {

    const accessToken =
        getAccessToken();

    if (accessToken) {

        // User is logged in
        loginButton.hidden = true;
        logoutButton.hidden = false;

        app.hidden = false;
        loginMessage.hidden = true;

        loadTasks();

    } else {

        // User is logged out
        loginButton.hidden = false;
        logoutButton.hidden = true;

        app.hidden = true;
        loginMessage.hidden = false;
    }
}


// ============================================================
// Logout
// ============================================================

function logout() {

    // Remove local tokens
    sessionStorage.removeItem(
        "access_token"
    );

    sessionStorage.removeItem(
        "id_token"
    );

    sessionStorage.removeItem(
        "refresh_token"
    );

    const params =
        new URLSearchParams({
            client_id: CLIENT_ID,
            logout_uri: REDIRECT_URI
        });

    // Also terminate the Cognito managed-login session
    window.location.href =
        `${COGNITO_DOMAIN}/logout?${params}`;
}


// ============================================================
// Load tasks
// GET /tasks
// ============================================================

async function loadTasks() {

    const response =
        await fetch(
            `${API_URL}/tasks`,
            {
                headers: {
                    "Authorization":
                        `Bearer ${getAccessToken()}`
                }
            }
        );

    if (!response.ok) {

        console.error(
            "Failed to load tasks"
        );

        return;
    }

    const tasks =
        await response.json();

    taskList.innerHTML = "";


    for (const task of tasks) {

        const item =
            document.createElement("li");


        // ----------------------------------------------------
        // Checkbox
        // ----------------------------------------------------

        const checkbox =
            document.createElement("input");

        checkbox.type = "checkbox";
        checkbox.checked = task.completed;


        // ----------------------------------------------------
        // Task title
        // ----------------------------------------------------

        const title =
            document.createElement("span");

        title.textContent =
            task.title;


        // ----------------------------------------------------
        // Delete button
        // ----------------------------------------------------

        const deleteButton =
            document.createElement("button");

        deleteButton.textContent =
            "Delete";


        // ----------------------------------------------------
        // PATCH task
        // ----------------------------------------------------

        checkbox.addEventListener(
            "change",
            async () => {

                const response =
                    await fetch(
                        `${API_URL}/tasks/${task.task_id}`,
                        {
                            method: "PATCH",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Authorization":
                                    `Bearer ${getAccessToken()}`
                            },

                            body:
                                JSON.stringify({
                                    completed:
                                        checkbox.checked
                                })
                        }
                    );

                if (!response.ok) {

                    console.error(
                        "Failed to update task"
                    );

                    // Restore previous checkbox state
                    checkbox.checked =
                        !checkbox.checked;
                }
            }
        );


        // ----------------------------------------------------
        // DELETE task
        // ----------------------------------------------------

        deleteButton.addEventListener(
            "click",
            async () => {

                const response =
                    await fetch(
                        `${API_URL}/tasks/${task.task_id}`,
                        {
                            method: "DELETE",

                            headers: {
                                "Authorization":
                                    `Bearer ${getAccessToken()}`
                            }
                        }
                    );

                if (!response.ok) {

                    console.error(
                        "Failed to delete task"
                    );

                    return;
                }

                await loadTasks();
            }
        );


        // Add everything to the task row
        item.appendChild(checkbox);
        item.appendChild(title);
        item.appendChild(deleteButton);

        // Add task row to the list
        taskList.appendChild(item);
    }
}


// ============================================================
// Create task
// POST /tasks
// ============================================================

taskForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        const title =
            taskInput.value.trim();

        if (!title) {
            return;
        }

        const response =
            await fetch(
                `${API_URL}/tasks`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${getAccessToken()}`
                    },

                    body:
                        JSON.stringify({
                            title: title
                        })
                }
            );

        if (!response.ok) {

            console.error(
                "Failed to create task"
            );

            return;
        }

        taskInput.value = "";

        await loadTasks();
    }
);


// ============================================================
// Login / Logout buttons
// ============================================================

loginButton.addEventListener(
    "click",
    login
);

logoutButton.addEventListener(
    "click",
    logout
);


// ============================================================
// Application startup
// ============================================================

// Instead of immediately calling loadTasks(), first determine
// whether Cognito has redirected us back from authentication.
handleAuthentication();