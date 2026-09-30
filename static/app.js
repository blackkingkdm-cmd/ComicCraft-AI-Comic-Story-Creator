let currentComic = null;

async function generateStory() {
    const idea = document.getElementById("idea").value.trim();
    const genre = document.getElementById("genre").value;
    const panels = document.getElementById("panels").value;
    const characters = document.getElementById("characters").value.trim();

    if (!idea) {
        setStatus("Please enter a story idea.", true);
        return;
    }

    const button = document.getElementById("generateBtn");
    button.disabled = true;
    setStatus("Gemini is creating your story...");

    try {
        const response = await fetch("/api/generate-story", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                idea, genre, characters, panels
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Story generation failed.");
        }

        currentComic = data;
        renderComic(data);
        setStatus("Story created successfully.");
    } catch (error) {
        setStatus(error.message, true);
    } finally {
        button.disabled = false;
    }
}


function renderComic(comic) {
    document.getElementById("result").classList.remove("hidden");
    document.getElementById("title").textContent = comic.title || "Untitled Comic";
    document.getElementById("logline").textContent = comic.logline || "";

    const chars = document.getElementById("charactersOutput");
    chars.innerHTML = "";

    (comic.characters || []).forEach(character => {
        const div = document.createElement("div");
        div.className = "character";
        div.innerHTML = `
            <strong>${escapeHtml(character.name)}</strong>
            <p>${escapeHtml(character.description)}</p>
        `;
        chars.appendChild(div);
    });

    const panels = document.getElementById("panelsOutput");
    panels.innerHTML = "";

    (comic.panels || []).forEach(panel => {
        const card = document.createElement("article");
        card.className = "panel card";

        const dialogue = (panel.dialogue || []).map(line =>
            `<p><strong>${escapeHtml(line.speaker)}:</strong> ${escapeHtml(line.text)}</p>`
        ).join("");

        card.innerHTML = `
            <div class="panel-header">
                <h3>Panel ${panel.panel}</h3>
                <button onclick="generateImage(${panel.panel})">Generate Image</button>
            </div>

            <div id="image-${panel.panel}" class="image-box">
                <span>Image not generated yet</span>
            </div>

            <p><strong>Scene:</strong> ${escapeHtml(panel.scene || "")}</p>
            <div class="dialogue">${dialogue}</div>
            ${panel.caption ? `<p><strong>Caption:</strong> ${escapeHtml(panel.caption)}</p>` : ""}
        `;

        panels.appendChild(card);
    });
}


async function generateImage(panelNumber) {
    const panel = currentComic.panels.find(
        p => Number(p.panel) === Number(panelNumber)
    );

    if (!panel) return;

    const box = document.getElementById(`image-${panelNumber}`);
    box.innerHTML = "<span>Generating image...</span>";

    try {
        const response = await fetch("/api/generate-image", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                prompt: panel.image_prompt,
                panel_number: panelNumber
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 429) {
                throw new Error(
                    "Image generation is currently unavailable on your free API tier. " +
                    "The comic story was generated successfully."
                );
            }

            throw new Error(data.error || "Image generation failed.");
        }

        box.innerHTML = `
            <img src="${data.image_url}" alt="Comic panel ${panelNumber}">
        `;

    } catch (error) {
        box.innerHTML = `
            <span class="error">${escapeHtml(error.message)}</span>
        `;
    }
}


function downloadStory() {
    if (!currentComic) return;

    let text = `${currentComic.title}\n\n${currentComic.logline}\n\n`;

    text += "CHARACTERS\n";
    (currentComic.characters || []).forEach(c => {
        text += `${c.name}: ${c.description}\n`;
    });

    text += "\nPANELS\n";
    (currentComic.panels || []).forEach(p => {
        text += `\nPanel ${p.panel}\n`;
        text += `Scene: ${p.scene}\n`;
        if (p.caption) text += `Caption: ${p.caption}\n`;
        (p.dialogue || []).forEach(d => {
            text += `${d.speaker}: ${d.text}\n`;
        });
    });

    const blob = new Blob([text], {type: "text/plain"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${currentComic.title || "comic"}.txt`;
    link.click();
    URL.revokeObjectURL(url);
}


function setStatus(message, error = false) {
    const status = document.getElementById("status");
    status.textContent = message;
    status.className = error ? "error" : "";
}


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
