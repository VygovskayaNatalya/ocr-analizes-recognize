// Функции для управления спиннером
function showSpinner() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideSpinner() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Обновите функцию анализа
async function analyzeStructure(ocrText) {
    showSpinner();
    try {
        const response = await fetch("http://127.0.0.1:8000/structure_analysis", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: ocrText })
        });

        const data = await response.json();
        localStorage.setItem("analysisTable", data.structured_analysis);
        window.open("http://127.0.0.1:8000/analysis", "_blank");
    } catch (error) {
        console.error("Error during analysis:", error);
    } finally {
        hideSpinner();
    }
}
